#!/usr/bin/env python3
"""
LPIC Essentials — Topic 1.2 Simulation (Finding Your Way on a Linux System)

What this is:
- Scenario-based simulation (not just flashcards)
- Focus areas (Topic 1.2):
  * Filesystem hierarchy concepts (/ /home /etc /var /tmp /usr /bin)
  * Absolute vs relative paths, ., ..
  * Hidden files (dotfiles)
  * "Everything is a file" concept
  * Basic navigation reasoning: where would you go to find X?

Gameplay:
- You move through a simulated filesystem (no real file changes)
- Missions ask you to choose paths/commands/interpretations
- Score + concept feedback + weak-spot report

Run:
  python3 lpic_essentials_topic_1_2_sim.py

Options:
  --seed 123    Deterministic order
  --short       Short run
"""

from __future__ import annotations

import argparse
import random
import textwrap
from dataclasses import dataclass
from typing import Dict, List, Tuple, Callable


WRAP = 78


def w(text: str) -> str:
    return "\n".join(textwrap.wrap(text, width=WRAP))


def hr() -> None:
    print("\n" + "=" * WRAP)


def ask_choice(options: List[str]) -> int:
    while True:
        print()
        for i, opt in enumerate(options, start=1):
            print(f"  {i}) {opt}")
        raw = input("\nChoose (number) or Q to quit: ").strip().lower()
        if raw in ("q", "quit", "exit"):
            raise SystemExit(0)
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return idx
        print("Invalid choice.")


@dataclass
class Outcome:
    points: int
    tags: List[str]
    feedback: str


@dataclass
class Mission:
    id: str
    title: str
    scenario: str
    options: List[str]
    evaluate: Callable[[int], Outcome]


class VirtualFS:
    """
    Minimal simulated filesystem model for navigation reasoning.
    """
    def __init__(self):
        # Nodes: directory -> children directories
        self.tree: Dict[str, List[str]] = {
            "/": ["home", "etc", "var", "tmp", "usr", "bin", "dev", "proc"],
            "/home": ["cannon", "guest"],
            "/home/cannon": ["projects", "Downloads"],
            "/etc": ["ssh", "network", "systemd"],
            "/var": ["log", "cache", "spool"],
            "/var/log": ["syslog", "auth.log", "kern.log"],
            "/tmp": [],
            "/usr": ["bin", "lib", "share"],
            "/bin": [],
            "/dev": ["sda", "null", "tty0"],
            "/proc": ["cpuinfo", "meminfo", "1"],
        }
        self.cwd = "/home/cannon"

    def _normalize(self, path: str) -> str:
        # Convert relative paths to absolute based on cwd
        if not path.startswith("/"):
            if path == ".":
                path = self.cwd
            elif path.startswith("./"):
                path = self.cwd.rstrip("/") + "/" + path[2:]
            else:
                path = self.cwd.rstrip("/") + "/" + path

        # Normalize /./ and /../
        parts = []
        for part in path.split("/"):
            if part == "" or part == ".":
                continue
            if part == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(part)
        return "/" + "/".join(parts) if parts else "/"

    def exists_dir(self, path: str) -> bool:
        p = self._normalize(path)
        return p in self.tree

    def cd(self, path: str) -> Tuple[bool, str]:
        p = self._normalize(path)
        if self.exists_dir(p):
            self.cwd = p
            return True, p
        return False, p

    def pwd(self) -> str:
        return self.cwd

    def ls(self) -> List[str]:
        return self.tree.get(self.cwd, [])


class Topic12Sim:
    def __init__(self, rng: random.Random, short: bool):
        self.rng = rng
        self.short = short
        self.fs = VirtualFS()
        self.score = 0
        self.max_score = 0
        self.missed: Dict[str, int] = {}
        self.covered: Dict[str, int] = {}

    def hit(self, tag: str) -> None:
        self.covered[tag] = self.covered.get(tag, 0) + 1

    def miss(self, tag: str) -> None:
        self.missed[tag] = self.missed.get(tag, 0) + 1

    def apply_outcome(self, out: Outcome) -> None:
        self.score += out.points
        self.max_score += 5
        for t in out.tags:
            if out.points >= 4:
                self.hit(t)
            elif out.points <= 2:
                self.miss(t)

    def run_mission(self, m: Mission) -> None:
        hr()
        print(f"{m.title} [{m.id}]")
        print("-" * WRAP)
        print(w(m.scenario))
        idx = ask_choice(m.options)
        out = m.evaluate(idx)
        self.apply_outcome(out)
        print("\n" + "-" * WRAP)
        print(w(out.feedback))
        print(f"\nPoints: {out.points}/5")

    def report(self) -> None:
        hr()
        pct = (self.score / self.max_score * 100) if self.max_score else 0.0
        print("TOPIC 1.2 SIMULATION REPORT")
        print("-" * WRAP)
        print(f"Score: {self.score}/{self.max_score} ({pct:.1f}%)")
        if pct >= 85:
            print("Readiness: Exam-ready for Topic 1.2")
        elif pct >= 70:
            print("Readiness: Close — review weak spots")
        else:
            print("Readiness: Needs more reps")

        if self.missed:
            print("\nConcepts to review:")
            for tag, n in sorted(self.missed.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {tag} (missed {n}x)")
        else:
            print("\nNo major weak concepts detected.")

        tips = []
        if self.missed.get("fs-hierarchy", 0) > 0:
            tips.append("Review what lives in /etc, /var, /home, /tmp, /usr, /bin.")
        if self.missed.get("paths", 0) > 0:
            tips.append("Review absolute vs relative paths and how '.', '..' change location.")
        if self.missed.get("dotfiles", 0) > 0:
            tips.append("Review hidden files (dotfiles) and why they exist.")
        if self.missed.get("everything-file", 0) > 0:
            tips.append("Review the concept: devices/system info exposed as files (e.g., /dev, /proc).")
        if tips:
            print("\nTargeted next steps:")
            for t in tips:
                print(f"  • {t}")

        hr()


# ------------------------ Missions ------------------------ #

def missions(sim: Topic12Sim) -> List[Mission]:
    fs = sim.fs

    def m1_eval(choice: int) -> Outcome:
        # Where to find system-wide config
        correct = 0  # /etc
        pts = 5 if choice == correct else 1
        return Outcome(
            points=pts,
            tags=["fs-hierarchy"],
            feedback=(
                "Correct. /etc is the standard location for system-wide configuration."
                if pts == 5 else
                "Not quite. For system-wide configuration, /etc is the best answer in most Linux systems."
            ),
        )

    def m2_eval(choice: int) -> Outcome:
        # Logs
        correct = 1  # /var/log
        pts = 5 if choice == correct else 1
        return Outcome(
            points=pts,
            tags=["fs-hierarchy"],
            feedback=(
                "Correct. Logs are commonly stored under /var/log."
                if pts == 5 else
                "Not quite. /var/log is the standard place for log files."
            ),
        )

    def m3_eval(choice: int) -> Outcome:
        # Navigation simulation: from /home/cannon to /home using cd ..
        correct = 2  # cd .. twice
        pts = 5 if choice == correct else 2
        return Outcome(
            points=pts,
            tags=["paths"],
            feedback=(
                "Correct. /home/cannon → cd .. → /home → cd .. → /"
                if choice == 2 else
                "Close. Remember: cd .. moves up one level. Two times from /home/cannon reaches /."
            ),
        )

    def m4_eval(choice: int) -> Outcome:
        # absolute vs relative path recognition
        correct = 0  # /etc/hosts
        pts = 5 if choice == correct else 1
        return Outcome(
            points=pts,
            tags=["paths"],
            feedback=(
                "Correct. /etc/hosts is absolute because it starts with '/'."
                if pts == 5 else
                "Not quite. Absolute paths begin with '/'."
            ),
        )

    def m5_eval(choice: int) -> Outcome:
        # dotfiles meaning
        correct = 1
        pts = 5 if choice == correct else 1
        return Outcome(
            points=pts,
            tags=["dotfiles"],
            feedback=(
                "Correct. Dotfiles are hidden by default and often store configuration."
                if pts == 5 else
                "Not quite. Files beginning with '.' are hidden by default and often config-related."
            ),
        )

    def m6_eval(choice: int) -> Outcome:
        # everything is a file concept
        correct = 2
        pts = 5 if choice == correct else 1
        return Outcome(
            points=pts,
            tags=["everything-file"],
            feedback=(
                "Correct. Many system resources (devices, process info) are exposed via file-like interfaces."
                if pts == 5 else
                "Not quite. The idea means resources like devices and system info are represented as files (e.g., /dev, /proc)."
            ),
        )

    def m7_eval(choice: int) -> Outcome:
        # navigation lab: user must choose correct cd target
        # Start: /home/cannon. Goal: /var/log
        # best is: cd /var/log
        correct = 0
        pts = 5 if choice == correct else 2
        return Outcome(
            points=pts,
            tags=["paths", "fs-hierarchy"],
            feedback=(
                "Correct. Using an absolute path (cd /var/log) is fastest and avoids confusion."
                if pts == 5 else
                "That works sometimes, but the most direct, least error-prone method is cd /var/log."
            ),
        )

    def m8_eval(choice: int) -> Outcome:
        # /tmp use
        correct = 1
        pts = 5 if choice == correct else 1
        return Outcome(
            points=pts,
            tags=["fs-hierarchy"],
            feedback=(
                "Correct. /tmp is for temporary files; contents may be cleared automatically."
                if pts == 5 else
                "Not quite. /tmp is intended for temporary files and may be cleaned automatically."
            ),
        )

    def m9_eval(choice: int) -> Outcome:
        # relative path resolution
        # cwd: /home/cannon/projects, path: ../Downloads
        correct = 0
        pts = 5 if choice == correct else 2
        return Outcome(
            points=pts,
            tags=["paths"],
            feedback=(
                "Correct. From /home/cannon/projects, ../Downloads resolves to /home/cannon/Downloads."
                if pts == 5 else
                "Close. .. goes up one directory: /home/cannon/projects → /home/cannon."
            ),
        )

    # Missions list (8 full, 5 short)
    mlist = [
        Mission(
            "1.2-A",
            "Mission 1: Where is system configuration stored?",
            "You need to change a system-wide configuration file for a service. Where would you look first?",
            ["/etc", "/var", "/home", "/tmp"],
            m1_eval,
        ),
        Mission(
            "1.2-B",
            "Mission 2: Where are logs stored?",
            "You’re troubleshooting an authentication issue. Where are system logs most likely stored?",
            ["/etc", "/var/log", "/home", "/usr/bin"],
            m2_eval,
        ),
        Mission(
            "1.2-C",
            "Mission 3: Path navigation reasoning",
            "Starting at /home/cannon, what is the BEST set of actions to reach / (root directory)?",
            ["cd /", "cd ../..", "cd .. twice", "cd ~"],
            m3_eval,
        ),
        Mission(
            "1.2-D",
            "Mission 4: Absolute vs relative paths",
            "Which of these is an ABSOLUTE path?",
            ["/etc/hosts", "../etc/hosts", "./etc/hosts", "etc/hosts"],
            m4_eval,
        ),
        Mission(
            "1.2-E",
            "Mission 5: Hidden files",
            "You see a file named .bashrc in a user’s home directory. What is MOST accurate?",
            ["It is a virus by definition", "It is a hidden configuration file by naming convention", "It is a system log file", "It is always executable"],
            m5_eval,
        ),
        Mission(
            "1.2-F",
            "Mission 6: “Everything is a file”",
            "What does “everything is a file” MOST accurately mean in Linux?",
            ["All files are plain text", "All programs are stored in /bin", "Many devices and system info are exposed as files (e.g., /dev, /proc)", "Only root can access files"],
            m6_eval,
        ),
        Mission(
            "1.2-G",
            "Mission 7: Navigation lab — choose the best cd",
            f"Your current directory is {fs.pwd()}. You need to quickly go to /var/log. What is the BEST command?",
            ["cd /var/log", "cd var/log", "cd ../../var/log", "cd ~ /var/log"],
            m7_eval,
        ),
        Mission(
            "1.2-H",
            "Mission 8: /tmp meaning",
            "You need a place to store temporary files for a short-lived process. Which directory is MOST appropriate?",
            ["/etc", "/tmp", "/home", "/bin"],
            m8_eval,
        ),
        Mission(
            "1.2-I",
            "Mission 9: Resolve a relative path",
            "You are in /home/cannon/projects. What does the relative path ../Downloads resolve to?",
            ["/home/cannon/Downloads", "/home/Downloads", "/Downloads", "/home/cannon/projects/Downloads"],
            m9_eval,
        ),
    ]

    sim.rng.shuffle(mlist)
    return mlist


def main() -> int:
    ap = argparse.ArgumentParser(description="LPIC Essentials Topic 1.2 — Simulation App")
    ap.add_argument("--seed", type=int, default=None, help="Deterministic mission order")
    ap.add_argument("--short", action="store_true", help="Short run (fewer missions)")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    sim = Topic12Sim(rng=rng, short=args.short)

    hr()
    print("LPIC Essentials — Topic 1.2 Simulation")
    print("-" * WRAP)
    print(w(
        "You’ll complete scenario missions aligned to Topic 1.2 (Finding Your Way on a Linux System). "
        "Focus: filesystem hierarchy, paths, dotfiles, and Linux navigation logic."
    ))
    hr()

    mlist = missions(sim)
    run_count = 5 if args.short else 8
    for m in mlist[:run_count]:
        sim.run_mission(m)

    sim.report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
