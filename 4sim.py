#!/usr/bin/env python3
"""
LPIC Essentials — Topic 1.4 Simulation (The Linux Operating System)

What this is:
- A scenario + lab style simulator (not just Q&A)
- Focus areas (Topic 1.4):
  * Kernel vs user space
  * Program vs process, PID
  * Multi-user & multitasking concepts
  * RAM vs swap (pressure scenarios)
  * Package managers, repositories, dependencies (concept + simulated installs)
  * Containers vs VMs (concept)
  * Basic monitoring: ps vs top (concept + simulated outputs)

Gameplay:
- You interact with a SIMULATED Linux system (safe: no real system changes)
- "mini-labs" where you inspect fake outputs (ps/top/free/df/pkg install logs)
- scenario decisions like an Essentials exam: choose BEST explanation/action
- Score + weak-spot report

Run:
  python3 lpic_essentials_topic_1_4_sim.py

Options:
  --seed 123       Deterministic scenario order
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


# --------------------------- Simulated OS Model --------------------------- #

@dataclass
class Proc:
    pid: int
    user: str
    cmd: str
    cpu: float
    mem: float


class SimOS:
    """
    A tiny, fake OS model for Topic 1.4 learning:
    - process table
    - memory model (RAM + swap)
    - package manager model (repos + dependencies)
    """
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.users = ["root", "cannon", "www-data", "postgres"]
        self.procs: List[Proc] = [
            Proc(1, "root", "systemd", 0.3, 0.8),
            Proc(222, "root", "sshd", 0.2, 0.4),
            Proc(410, "www-data", "nginx", 1.2, 1.3),
            Proc(511, "postgres", "postgres", 2.1, 4.8),
            Proc(900, "cannon", "python3 app.py", 12.5, 6.2),
        ]
        # Memory in "GiB"
        self.ram_total = 8.0
        self.ram_used = 6.6
        self.swap_total = 2.0
        self.swap_used = 0.2

        # Packages: name -> dependencies
        self.repo = {
            "curl": [],
            "git": ["curl"],
            "python3": [],
            "pip": ["python3"],
            "nginx": ["libssl", "libpcre"],
            "libssl": [],
            "libpcre": [],
            "htop": ["libncurses"],
            "libncurses": [],
            "docker": ["containerd"],
            "containerd": [],
        }
        self.installed: Dict[str, bool] = {"python3": True, "curl": True}

    def ps_snapshot(self) -> str:
        header = "  PID USER      %CPU  %MEM  CMD\n"
        lines = []
        for p in sorted(self.procs, key=lambda x: x.pid):
            lines.append(f"{p.pid:5d} {p.user:<9} {p.cpu:>4.1f}  {p.mem:>4.1f}  {p.cmd}")
        return header + "\n".join(lines) + "\n"

    def top_view(self) -> str:
        # Simulate a top-like output (not exact)
        top_procs = sorted(self.procs, key=lambda x: x.cpu, reverse=True)[:5]
        lines = [
            "top - 14:04:33 up  3:12,  2 users,  load average: 0.42, 0.58, 0.61",
            f"Tasks: {len(self.procs)} total,   1 running, {len(self.procs)-1} sleeping,   0 stopped,   0 zombie",
            f"%Cpu(s):  6.5 us,  2.0 sy,  0.0 ni, 91.0 id,  0.3 wa,  0.0 hi,  0.2 si,  0.0 st",
            f"MiB Mem :  {self.ram_total*1024:7.0f} total,  {(self.ram_total-self.ram_used)*1024:7.0f} free,  {self.ram_used*1024:7.0f} used",
            f"MiB Swap:  {self.swap_total*1024:7.0f} total,  {(self.swap_total-self.swap_used)*1024:7.0f} free,  {self.swap_used*1024:7.0f} used",
            "",
            "  PID USER      %CPU  %MEM  CMD",
        ]
        for p in top_procs:
            lines.append(f"{p.pid:5d} {p.user:<9} {p.cpu:>4.1f}  {p.mem:>4.1f}  {p.cmd}")
        return "\n".join(lines) + "\n"

    def free_view(self) -> str:
        # simplified 'free -h' style
        mem_free = max(self.ram_total - self.ram_used, 0.0)
        swap_free = max(self.swap_total - self.swap_used, 0.0)
        return (
            "              total   used   free\n"
            f"Mem:           {self.ram_total:>5.1f}G  {self.ram_used:>4.1f}G  {mem_free:>4.1f}G\n"
            f"Swap:          {self.swap_total:>5.1f}G  {self.swap_used:>4.1f}G  {swap_free:>4.1f}G\n"
        )

    def start_process(self, user: str, cmd: str, cpu: float, mem: float) -> None:
        new_pid = max(p.pid for p in self.procs) + self.rng.randint(1, 50)
        self.procs.append(Proc(new_pid, user, cmd, cpu, mem))
        # memory pressure increases RAM used; overflow uses swap
        self.ram_used += mem
        if self.ram_used > self.ram_total:
            overflow = self.ram_used - self.ram_total
            self.ram_used = self.ram_total
            self.swap_used = min(self.swap_total, self.swap_used + overflow)

    def install_pkg(self, name: str) -> Tuple[bool, str]:
        if name not in self.repo:
            return False, f"Package '{name}' not found in repositories."
        to_install = self._resolve_deps(name)
        newly = [p for p in to_install if not self.installed.get(p, False)]
        for p in newly:
            self.installed[p] = True
        if not newly:
            return True, f"'{name}' is already installed."
        return True, "Installed: " + ", ".join(newly)

    def _resolve_deps(self, name: str) -> List[str]:
        seen = set()
        order: List[str] = []

        def dfs(pkg: str) -> None:
            if pkg in seen:
                return
            seen.add(pkg)
            for dep in self.repo.get(pkg, []):
                dfs(dep)
            order.append(pkg)

        dfs(name)
        return order


# ------------------------------ Simulator ------------------------------ #

class Topic14Sim:
    def __init__(self, rng: random.Random, short: bool):
        self.rng = rng
        self.short = short
        self.os = SimOS(rng)
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
        print("TOPIC 1.4 SIMULATION REPORT")
        print("-" * WRAP)
        print(f"Score: {self.score}/{self.max_score} ({pct:.1f}%)")
        if pct >= 85:
            print("Readiness: Exam-ready for Topic 1.4")
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
        if self.missed.get("kernel-vs-userspace", 0) > 0:
            tips.append("Review: kernel responsibilities vs user space (apps).")
        if self.missed.get("process-pid", 0) > 0:
            tips.append("Review: program vs process vs PID; process lifecycle basics.")
        if self.missed.get("packages-deps", 0) > 0:
            tips.append("Review: package manager, repositories, dependencies (why they exist).")
        if self.missed.get("ram-swap", 0) > 0:
            tips.append("Review: RAM vs swap (what swap is, why it’s slower).")
        if self.missed.get("vm-vs-containers", 0) > 0:
            tips.append("Review: VMs vs containers (full OS vs shared kernel).")
        if self.missed.get("monitoring", 0) > 0:
            tips.append("Review: ps (snapshot) vs top (live-ish), what they show.")
        if tips:
            print("\nTargeted next steps:")
            for t in tips:
                print(f"  • {t}")
        hr()


# --------------------------- Missions Builder --------------------------- #

def build_missions(sim: Topic14Sim) -> List[Mission]:
    osys = sim.os

    # Mission: kernel vs user space
    def eval_kernel(choice: int) -> Outcome:
        correct = 1
        pts = 5 if choice == correct else 2
        return Outcome(
            pts,
            ["kernel-vs-userspace"],
            (
                "Correct. The kernel manages hardware resources, memory, scheduling, and privileged operations."
                if pts == 5 else
                "Not quite. The kernel manages hardware/resources; applications run in user space."
            )
        )

    # Mission: process vs program
    def eval_process(choice: int) -> Outcome:
        correct = 0
        pts = 5 if choice == correct else 1
        return Outcome(
            pts,
            ["process-pid"],
            (
                "Correct. A process is a running instance of a program with a PID."
                if pts == 5 else
                "Not quite. Program (on disk) vs process (running instance)."
            )
        )

    # Mission: ps vs top using simulated outputs
    ps_text = osys.ps_snapshot()
    top_text = osys.top_view()

    def eval_monitor(choice: int) -> Outcome:
        correct = 2
        pts = 5 if choice == correct else 2
        return Outcome(
            pts,
            ["monitoring"],
            (
                "Correct. top updates continuously (live-ish); ps shows a snapshot at execution time."
                if pts == 5 else
                "Close. Remember: ps is a snapshot; top is live-ish and updates repeatedly."
            )
        )

    # Mission: RAM vs swap scenario
    def eval_mem(choice: int) -> Outcome:
        correct = 1
        pts = 5 if choice == correct else 2
        return Outcome(
            pts,
            ["ram-swap"],
            (
                "Correct. Swap extends memory using disk; it helps under pressure but is slower than RAM."
                if pts == 5 else
                "Not quite. Swap is disk-backed memory used when RAM is pressured; it’s slower than RAM."
            )
        )

    # Mission: package manager + dependencies (simulate install)
    def eval_pkg(choice: int) -> Outcome:
        # best action: install git and let package manager pull curl dependency
        correct = 0
        pts = 5 if choice == correct else 2
        if choice == 0:
            ok_, msg = osys.install_pkg("git")
            fb = f"Correct. {msg} (Package managers resolve dependencies from repos.)"
        elif choice == 1:
            fb = "Not ideal. Manually downloading bypasses repo trust/updates; package managers are preferred."
        elif choice == 2:
            fb = "Incorrect. Dependencies are common; package managers handle them."
        else:
            fb = "Not correct. Repositories are standard sources for packages."
        return Outcome(pts, ["packages-deps"], fb)

    # Mission: container vs VM
    def eval_vm(choice: int) -> Outcome:
        correct = 0
        pts = 5 if choice == correct else 2
        return Outcome(
            pts,
            ["vm-vs-containers"],
            (
                "Correct. Containers share the host kernel; VMs typically run a full guest OS stack."
                if pts == 5 else
                "Close. Containers share host kernel; VMs generally include a full guest OS."
            )
        )

    # Mission: multi-user concept
    def eval_multi(choice: int) -> Outcome:
        correct = 1
        pts = 5 if choice == correct else 1
        return Outcome(
            pts,
            ["multi-user"],
            (
                "Correct. Multi-user means multiple accounts with separated permissions and possible concurrent sessions."
                if pts == 5 else
                "Not quite. Multi-user supports multiple accounts and permission boundaries."
            )
        )

    missions = [
        Mission(
            "1.4-A",
            "Mission 1: Kernel vs User Space",
            "A teammate says: “The kernel is basically just another app.” What is the BEST correction?",
            [
                "True—kernel and apps are the same thing",
                "No—the kernel is the core component managing hardware/resources; apps run in user space",
                "Kernel only provides the desktop GUI",
                "Kernel is a package repository",
            ],
            eval_kernel,
        ),
        Mission(
            "1.4-B",
            "Mission 2: Program vs Process",
            "Which statement is MOST accurate?",
            [
                "A process is a running instance of a program (has a PID)",
                "A process is a file on disk",
                "A process is a Linux distribution",
                "A process is a package repository",
            ],
            eval_process,
        ),
        Mission(
            "1.4-C",
            "Mission 3: ps vs top (reading outputs)",
            "You ran two tools:\n\n"
            + ps_text + "\n"
            + top_text + "\n"
            + "Which statement is MOST accurate about these tools?",
            [
                "ps is live-updating; top is a one-time snapshot",
                "Both are identical and always show the same view",
                "top updates continuously; ps shows a snapshot at the moment it runs",
                "Neither can show processes",
            ],
            eval_monitor,
        ),
        Mission(
            "1.4-D",
            "Mission 4: Memory Pressure (RAM vs Swap)",
            "A system starts using swap heavily. Which explanation is MOST accurate?",
            [
                "Swap is faster than RAM so it’s used first",
                "Swap is disk-backed memory used when RAM is under pressure; it’s usually slower than RAM",
                "Swap is a type of CPU cache",
                "Swap is where logs are stored",
            ],
            eval_mem,
        ),
        Mission(
            "1.4-E",
            "Mission 5: Package Managers & Dependencies (simulated)",
            "You need to install git. The system says curl is a dependency. What is the BEST approach?",
            [
                "Use the package manager to install git and allow it to resolve dependencies automatically",
                "Download random binaries from the internet and copy them into /bin",
                "Cancel because dependencies mean the software is broken",
                "Disable repositories so installs are faster",
            ],
            eval_pkg,
        ),
        Mission(
            "1.4-F",
            "Mission 6: Containers vs Virtual Machines",
            "Which statement BEST distinguishes containers from virtual machines?",
            [
                "Containers share the host kernel; VMs typically run full guest OS stacks",
                "Containers always include a full guest OS kernel; VMs share the host kernel",
                "Containers cannot be used on servers",
                "VMs cannot isolate workloads",
            ],
            eval_vm,
        ),
        Mission(
            "1.4-G",
            "Mission 7: Multi-user concept",
            "Linux is called “multi-user.” What does that mean in practice?",
            [
                "Only one user can exist at a time",
                "Multiple accounts can exist with separate permissions and concurrent sessions",
                "Every user has root access automatically",
                "Users cannot share the same machine",
            ],
            eval_multi,
        ),
    ]

    sim.rng.shuffle(missions)
    return missions


def main() -> int:
    ap = argparse.ArgumentParser(description="LPIC Essentials Topic 1.4 — Simulation App")
    ap.add_argument("--seed", type=int, default=None, help="Deterministic mission order")
    ap.add_argument("--short", action="store_true", help="Short run (fewer missions)")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    sim = Topic14Sim(rng=rng, short=args.short)

    hr()
    print("LPIC Essentials — Topic 1.4 Simulation")
    print("-" * WRAP)
    print(w(
        "You’ll complete scenario missions aligned to Topic 1.4 (The Linux Operating System). "
        "You’ll interpret simulated outputs (ps/top/free) and make exam-style decisions."
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
