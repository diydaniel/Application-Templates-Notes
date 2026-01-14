#!/usr/bin/env python3
"""
LPIC Essentials — Topic 1.5 Simulation (Security & Permissions)

What this is:
- Scenario + lab style simulator (not just Q&A)
- Focus areas (Topic 1.5):
  * Root vs regular users, sudo concept, least privilege
  * Permissions: r/w/x meaning (files + directories concept)
  * Ownership + groups (why they matter)
  * Safe practices: updates, backups (concept), firewall meaning
  * Spot-the-risk: insecure choices (world-writable, running as root, etc.)

Gameplay:
- SAFE simulated system (no real permission changes)
- Missions include:
  * interpret `ls -l` output
  * choose correct permission sets
  * decide when to use sudo
  * identify risky configurations
- Score + weak-spot report

Run:
  python3 lpic_essentials_topic_1_5_sim.py

Options:
  --seed 123       Deterministic mission order
  --short          Short run (fewer missions)
"""

from __future__ import annotations

import argparse
import random
import textwrap
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple


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
    mid: str
    title: str
    scenario: str
    options: List[str]
    evaluate: Callable[[int], Outcome]


# --------------------------- Permission Helpers --------------------------- #

def explain_perm(triple: str, is_dir: bool) -> str:
    """
    Explain rwx triple meaning for file vs directory (Essentials-level).
    triple must be length 3 containing r,w,x or '-'.
    """
    r, w_, x = triple
    parts = []
    if is_dir:
        if r == "r":
            parts.append("read = list directory contents")
        if w_ == "w":
            parts.append("write = create/delete/rename entries (subject to execute)")
        if x == "x":
            parts.append("execute = enter/traverse directory (cd) and access inodes")
    else:
        if r == "r":
            parts.append("read = view file contents")
        if w_ == "w":
            parts.append("write = modify file contents")
        if x == "x":
            parts.append("execute = run as a program/script (if applicable)")
    return ", ".join(parts) if parts else "no permissions"


# --------------------------- Simulated Security State --------------------------- #

@dataclass
class FileMeta:
    path: str
    owner: str
    group: str
    perms: str  # like -rwxr-xr--
    is_dir: bool = False


class SimSec:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.current_user = "cannon"
        self.groups = {"cannon": ["cannon", "dev"], "root": ["root"], "www-data": ["www-data"]}
        self.files: Dict[str, FileMeta] = {
            "/etc/shadow": FileMeta("/etc/shadow", "root", "root", "-rw-------", False),
            "/etc/ssh/sshd_config": FileMeta("/etc/ssh/sshd_config", "root", "root", "-rw-r--r--", False),
            "/var/log/auth.log": FileMeta("/var/log/auth.log", "root", "adm", "-rw-r-----", False),
            "/home/cannon/script.sh": FileMeta("/home/cannon/script.sh", "cannon", "cannon", "-rwxr-xr--", False),
            "/home/cannon/public": FileMeta("/home/cannon/public", "cannon", "cannon", "drwxr-xr-x", True),
            "/tmp": FileMeta("/tmp", "root", "root", "drwxrwxrwt", True),
        }

    def ls_l(self, path: str) -> str:
        fm = self.files.get(path)
        if not fm:
            return f"ls: cannot access '{path}': No such file or directory\n"
        # mimic ls -l (simplified)
        return f"{fm.perms}  1 {fm.owner} {fm.group}  4096 Jan 13 12:00 {path.split('/')[-1]}\n"

    def is_world_writable(self, fm: FileMeta) -> bool:
        # perms positions: [0] type, [1-3] owner, [4-6] group, [7-9] other
        other = fm.perms[7:10]
        return "w" in other

    def set_user(self, user: str) -> None:
        self.current_user = user


# --------------------------- Simulator Core --------------------------- #

class Topic15Sim:
    def __init__(self, rng: random.Random, short: bool):
        self.rng = rng
        self.short = short
        self.sys = SimSec(rng)
        self.score = 0
        self.max_score = 0
        self.missed: Dict[str, int] = {}
        self.covered: Dict[str, int] = {}

    def hit(self, tag: str) -> None:
        self.covered[tag] = self.covered.get(tag, 0) + 1

    def miss(self, tag: str) -> None:
        self.missed[tag] = self.missed.get(tag, 0) + 1

    def apply(self, out: Outcome) -> None:
        self.score += out.points
        self.max_score += 5
        for t in out.tags:
            if out.points >= 4:
                self.hit(t)
            elif out.points <= 2:
                self.miss(t)

    def run_mission(self, m: Mission) -> None:
        hr()
        print(f"{m.title} [{m.mid}]")
        print("-" * WRAP)
        print(w(m.scenario))
        idx = ask_choice(m.options)
        out = m.evaluate(idx)
        self.apply(out)
        print("\n" + "-" * WRAP)
        print(w(out.feedback))
        print(f"\nPoints: {out.points}/5")

    def report(self) -> None:
        hr()
        pct = (self.score / self.max_score * 100) if self.max_score else 0.0
        print("TOPIC 1.5 SIMULATION REPORT")
        print("-" * WRAP)
        print(f"Score: {self.score}/{self.max_score} ({pct:.1f}%)")
        if pct >= 85:
            print("Readiness: Exam-ready for Topic 1.5")
        elif pct >= 70:
            print("Readiness: Close — review weak spots")
        else:
            print("Readiness: Needs more reps")

        if self.missed:
            print("\nConcepts to review (most missed first):")
            for tag, n in sorted(self.missed.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {tag} (missed {n}x)")
        else:
            print("\nNo major weak concepts detected.")

        tips = []
        if self.missed.get("least-privilege", 0) > 0:
            tips.append("Review: least privilege and why daily root usage is risky.")
        if self.missed.get("sudo-root", 0) > 0:
            tips.append("Review: what sudo does (authorized elevation for a command).")
        if self.missed.get("permissions", 0) > 0:
            tips.append("Review: rwx meanings for files vs directories.")
        if self.missed.get("ownership-groups", 0) > 0:
            tips.append("Review: owner vs group vs others and why groups exist.")
        if self.missed.get("security-hygiene", 0) > 0:
            tips.append("Review: updates/patching + firewall concept + avoiding world-writable settings.")
        if tips:
            print("\nTargeted next steps:")
            for t in tips:
                print(f"  • {t}")
        hr()


# --------------------------- Missions Builder --------------------------- #

def build_missions(sim: Topic15Sim) -> List[Mission]:
    sys = sim.sys

    def eval_least(choice: int) -> Outcome:
        correct = 1
        pts = 5 if choice == correct else 2
        return Outcome(
            pts, ["least-privilege"],
            (
                "Correct. Least privilege means users get only what they need—reducing damage from mistakes or compromise."
                if pts == 5 else
                "Close. Least privilege is about minimizing permissions to reduce risk."
            )
        )

    def eval_root(choice: int) -> Outcome:
        correct = 2
        pts = 5 if choice == correct else 1
        return Outcome(
            pts, ["sudo-root"],
            (
                "Correct. Using sudo for specific commands is safer than logging in as root for daily work."
                if pts == 5 else
                "Not quite. Root access increases blast radius; sudo provides controlled elevation."
            )
        )

    def eval_perm_file(choice: int) -> Outcome:
        # -rwxr-xr--
        fm = sys.files["/home/cannon/script.sh"]
        correct = 0
        pts = 5 if choice == correct else 2
        owner_trip = fm.perms[1:4]
        group_trip = fm.perms[4:7]
        other_trip = fm.perms[7:10]
        fb = (
            "Correct. Owner can read/write/execute; group can read/execute; others can read."
            f" (Owner: {explain_perm(owner_trip, False)}; Group: {explain_perm(group_trip, False)}; Others: {explain_perm(other_trip, False)})"
            if pts == 5 else
            "Close. Interpret rwx in triplets: owner/group/others."
        )
        return Outcome(pts, ["permissions"], fb)

    def eval_perm_dir(choice: int) -> Outcome:
        fm = sys.files["/home/cannon/public"]
        correct = 1
        pts = 5 if choice == correct else 2
        fb = (
            "Correct. For directories: r=list, x=enter/traverse, w=create/delete entries (with x)."
            if pts == 5 else
            "Close. Directory permissions differ: x controls traversal; r lists names; w changes entries."
        )
        return Outcome(pts, ["permissions"], fb)

    def eval_shadow(choice: int) -> Outcome:
        line = sys.ls_l("/etc/shadow")
        correct = 0
        pts = 5 if choice == correct else 1
        return Outcome(
            pts, ["security-hygiene", "ownership-groups"],
            (
                f"Correct. /etc/shadow should be tightly restricted. Example output:\n{line.strip()}\n"
                "World-readable shadow would be a serious security risk."
                if pts == 5 else
                f"Not quite. /etc/shadow should be restricted (typically readable only by root).\n{line.strip()}"
            )
        )

    def eval_world_writable(choice: int) -> Outcome:
        correct = 2
        pts = 5 if choice == correct else 2
        return Outcome(
            pts, ["security-hygiene"],
            (
                "Correct. World-writable files allow any user to modify them—risking tampering or malware injection."
                if pts == 5 else
                "Close. World-writable settings are risky because they allow tampering by any user."
            )
        )

    def eval_updates(choice: int) -> Outcome:
        correct = 1
        pts = 5 if choice == correct else 2
        return Outcome(
            pts, ["security-hygiene"],
            (
                "Correct. Updates patch known vulnerabilities and fix bugs attackers may exploit."
                if pts == 5 else
                "Close. Updates are primarily for security patches and bug fixes (not just features)."
            )
        )

    def eval_firewall(choice: int) -> Outcome:
        correct = 0
        pts = 5 if choice == correct else 2
        return Outcome(
            pts, ["security-hygiene"],
            (
                "Correct. A firewall filters network traffic using allow/deny rules."
                if pts == 5 else
                "Close. Firewalls control network traffic; they don’t manage file permissions."
            )
        )

    missions = [
        Mission(
            "1.5-A",
            "Mission 1: Least Privilege",
            "A junior admin asks what “least privilege” means. What is the BEST explanation?",
            [
                "Everyone should have admin rights to prevent delays",
                "Users should have only the permissions necessary to do their tasks",
                "All files should be world-writable so collaboration is easy",
                "Least privilege means never using updates",
            ],
            eval_least,
        ),
        Mission(
            "1.5-B",
            "Mission 2: Root vs sudo",
            "You need to edit a protected system config file. What is the BEST practice?",
            [
                "Log in as root permanently for convenience",
                "Disable permissions so anyone can edit system files",
                "Use sudo for the specific command that needs elevation (if authorized)",
                "Copy the file into /tmp and leave it there forever",
            ],
            eval_root,
        ),
        Mission(
            "1.5-C",
            "Mission 3: Interpret file permissions",
            "You see a script with permissions: -rwxr-xr--. Which is MOST accurate?",
            [
                "Owner: rwx, Group: r-x, Others: r--",
                "Owner: r--, Group: rwx, Others: r-x",
                "Everyone: rwx",
                "No one can execute it",
            ],
            eval_perm_file,
        ),
        Mission(
            "1.5-D",
            "Mission 4: Directory permissions concept",
            "Which statement is MOST accurate about directory permissions?",
            [
                "Execute (x) on a directory means you can run the directory as a program",
                "Execute (x) on a directory controls entering/traversing it (cd), not ‘running’ it",
                "Read (r) on a directory means you can always delete files in it",
                "Write (w) on a directory is meaningless",
            ],
            eval_perm_dir,
        ),
        Mission(
            "1.5-E",
            "Mission 5: Sensitive files (shadow)",
            "You check /etc/shadow. Which is the BEST expectation?",
            [
                "It should be restricted (typically only root readable)",
                "It should be world-readable so any user can troubleshoot logins",
                "It should be stored in /home for convenience",
                "It should always be executable",
            ],
            eval_shadow,
        ),
        Mission(
            "1.5-F",
            "Mission 6: World-writable risk",
            "A file is set to world-writable. What is the biggest risk?",
            [
                "It becomes hidden automatically",
                "It becomes encrypted automatically",
                "Any user can modify it, enabling tampering or malicious injection",
                "It cannot be executed anymore",
            ],
            eval_world_writable,
        ),
        Mission(
            "1.5-G",
            "Mission 7: Updates & patching",
            "Why are regular updates considered a security best practice?",
            [
                "They eliminate the need for passwords",
                "They patch known vulnerabilities and fix bugs attackers may exploit",
                "They prevent all attacks permanently",
                "They are only for cosmetic UI changes",
            ],
            eval_updates,
        ),
        Mission(
            "1.5-H",
            "Mission 8: Firewall concept",
            "Conceptually, a firewall is used to:",
            [
                "Filter network traffic based on allow/deny rules",
                "Change file ownership and permissions",
                "Install packages from repositories",
                "Create new user accounts automatically",
            ],
            eval_firewall,
        ),
    ]

    sim.rng.shuffle(missions)
    return missions


def main() -> int:
    ap = argparse.ArgumentParser(description="LPIC Essentials Topic 1.5 — Simulation App")
    ap.add_argument("--seed", type=int, default=None, help="Deterministic mission order")
    ap.add_argument("--short", action="store_true", help="Short run (fewer missions)")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    sim = Topic15Sim(rng=rng, short=args.short)

    hr()
    print("LPIC Essentials — Topic 1.5 Simulation")
    print("-" * WRAP)
    print(w(
        "You’ll complete scenario missions aligned to Topic 1.5 (Security & Permissions). "
        "Focus: least privilege, sudo/root, permissions, updates, and firewall concepts."
    ))
    hr()

    mlist = build_missions(sim)
    run_count = 4 if args.short else 6
    for m in mlist[:run_count]:
        sim.run_mission(m)

    sim.report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
