#!/usr/bin/env python3
"""
LPIC Essentials — Topic 1.3 Simulation (Command Line Power)

What this is:
- A scenario + lab style simulator (not just Q&A)
- Focus areas (Topic 1.3):
  * shell vs terminal
  * basic commands: pwd, cd, ls, mkdir, touch, cp, mv, rm, cat, less (concept)
  * pipes and redirection: |, >, >>
  * command history + tab completion (concept)
  * why CLI matters (automation/SSH/efficiency)

Gameplay:
- You interact with a SIMULATED shell (safe: no real filesystem changes)
- Type commands like: pwd, ls, cd, mkdir, touch, cp, mv, rm, cat, echo, wc
- Missions require you to accomplish tasks in the simulated environment
- Includes "concept checkpoints" (exam-style) inside the sim
- Score + weak-spot report

Run:
  python3 lpic_essentials_topic_1_3_sim.py

Options:
  --seed 123       Deterministic mission order
  --short          Short run (fewer missions)
  --no-hints       Hide hints during missions
"""

from __future__ import annotations

import argparse
import random
import shlex
import textwrap
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


WRAP = 78


def w(text: str) -> str:
    return "\n".join(textwrap.wrap(text, width=WRAP))


def hr() -> None:
    print("\n" + "=" * WRAP)


def warn(msg: str) -> None:
    print(f"\n⚠️  {msg}")


def ok(msg: str) -> None:
    print(f"\n✅ {msg}")


def fail(msg: str) -> None:
    print(f"\n❌ {msg}")


# ----------------------------- Simulated FS ----------------------------- #

class SimFS:
    """
    A small in-memory filesystem with files + dirs.
    Supports minimal commands needed for Topic 1.3.
    """

    def __init__(self):
        self.dirs: Dict[str, List[str]] = {
            "/": ["home", "etc", "var", "tmp"],
            "/home": ["cannon"],
            "/home/cannon": ["notes", "labs"],
            "/home/cannon/notes": [],
            "/home/cannon/labs": [],
            "/etc": [],
            "/var": ["log"],
            "/var/log": [],
            "/tmp": [],
        }
        # file content map
        self.files: Dict[str, str] = {
            "/home/cannon/notes/readme.txt": "Welcome to LPIC Essentials Topic 1.3\n",
        }
        self.cwd = "/home/cannon"

    def _norm(self, path: str) -> str:
        # resolve relative to cwd, handle ., ..
        if not path.startswith("/"):
            if path == ".":
                path = self.cwd
            elif path.startswith("./"):
                path = self.cwd.rstrip("/") + "/" + path[2:]
            else:
                path = self.cwd.rstrip("/") + "/" + path

        parts: List[str] = []
        for p in path.split("/"):
            if p == "" or p == ".":
                continue
            if p == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(p)
        return "/" + "/".join(parts) if parts else "/"

    def pwd(self) -> str:
        return self.cwd

    def ls(self, path: Optional[str] = None) -> Tuple[bool, str]:
        p = self._norm(path) if path else self.cwd
        if p in self.dirs:
            kids = self.dirs[p]
            # include files in that directory
            prefix = p.rstrip("/") + "/"
            local_files = sorted([
                fp[len(prefix):] for fp in self.files.keys()
                if fp.startswith(prefix) and "/" not in fp[len(prefix):]
            ])
            items = sorted(kids + local_files)
            return True, "  ".join(items) if items else ""
        return False, f"ls: cannot access '{path}': No such directory"

    def cd(self, path: str) -> Tuple[bool, str]:
        p = self._norm(path)
        if p in self.dirs:
            self.cwd = p
            return True, ""
        return False, f"cd: no such file or directory: {path}"

    def mkdir(self, name: str) -> Tuple[bool, str]:
        p = self._norm(name)
        if p in self.dirs or p in self.files:
            return False, f"mkdir: cannot create directory '{name}': File exists"
        # parent dir must exist
        parent = "/" + "/".join(p.strip("/").split("/")[:-1]) if "/" in p.strip("/") else "/"
        if parent not in self.dirs:
            return False, f"mkdir: cannot create directory '{name}': No such file or directory"
        base = p.split("/")[-1]
        self.dirs[parent].append(base)
        self.dirs[p] = []
        return True, ""

    def touch(self, name: str) -> Tuple[bool, str]:
        p = self._norm(name)
        # parent must exist
        parent = "/" + "/".join(p.strip("/").split("/")[:-1]) if "/" in p.strip("/") else "/"
        if parent not in self.dirs:
            return False, f"touch: cannot touch '{name}': No such directory"
        if p not in self.files:
            self.files[p] = ""
        return True, ""

    def cat(self, name: str) -> Tuple[bool, str]:
        p = self._norm(name)
        if p in self.files:
            return True, self.files[p]
        return False, f"cat: {name}: No such file"

    def rm(self, name: str) -> Tuple[bool, str]:
        p = self._norm(name)
        if p in self.files:
            del self.files[p]
            return True, ""
        if p in self.dirs:
            # only allow empty dirs with rm -r? Not implemented; keep simple
            return False, f"rm: cannot remove '{name}': Is a directory"
        return False, f"rm: cannot remove '{name}': No such file"

    def cp(self, src: str, dst: str) -> Tuple[bool, str]:
        s = self._norm(src)
        d = self._norm(dst)
        if s not in self.files:
            return False, f"cp: cannot stat '{src}': No such file"
        parent = "/" + "/".join(d.strip("/").split("/")[:-1]) if "/" in d.strip("/") else "/"
        if parent not in self.dirs:
            return False, f"cp: cannot create regular file '{dst}': No such directory"
        self.files[d] = self.files[s]
        return True, ""

    def mv(self, src: str, dst: str) -> Tuple[bool, str]:
        s = self._norm(src)
        d = self._norm(dst)
        if s not in self.files:
            return False, f"mv: cannot stat '{src}': No such file"
        parent = "/" + "/".join(d.strip("/").split("/")[:-1]) if "/" in d.strip("/") else "/"
        if parent not in self.dirs:
            return False, f"mv: cannot move to '{dst}': No such directory"
        self.files[d] = self.files[s]
        del self.files[s]
        return True, ""

    def write_file(self, path: str, content: str, append: bool) -> Tuple[bool, str]:
        p = self._norm(path)
        parent = "/" + "/".join(p.strip("/").split("/")[:-1]) if "/" in p.strip("/") else "/"
        if parent not in self.dirs:
            return False, f"redirect: cannot write '{path}': No such directory"
        if append:
            self.files[p] = self.files.get(p, "") + content
        else:
            self.files[p] = content
        return True, ""


# ----------------------------- Command Engine ----------------------------- #

def wc_count(text: str, mode: str) -> str:
    if mode == "-w":
        return str(len(text.split()))
    if mode == "-c":
        return str(len(text.encode("utf-8")))
    # default lines
    return str(len(text.splitlines()))


class ShellSim:
    """
    Parses a limited subset of shell syntax:
    - commands: pwd, ls, cd, mkdir, touch, cp, mv, rm, cat, echo, wc
    - redirection: > and >> (stdout only)
    - pipe: | (one pipe segment)
    """

    def __init__(self, fs: SimFS):
        self.fs = fs

    def run(self, line: str) -> Tuple[bool, str]:
        line = line.strip()
        if not line:
            return True, ""

        # handle a single pipe
        if "|" in line:
            left, right = [p.strip() for p in line.split("|", 1)]
            ok1, out1 = self._run_simple(left, piped_in=None)
            if not ok1:
                return False, out1
            ok2, out2 = self._run_simple(right, piped_in=out1)
            return ok2, out2

        return self._run_simple(line, piped_in=None)

    def _run_simple(self, line: str, piped_in: Optional[str]) -> Tuple[bool, str]:
        # handle redirection: > or >>
        redirect_path = None
        append = False
        if ">>" in line:
            parts = line.split(">>", 1)
            line = parts[0].strip()
            redirect_path = parts[1].strip()
            append = True
        elif ">" in line:
            parts = line.split(">", 1)
            line = parts[0].strip()
            redirect_path = parts[1].strip()
            append = False

        try:
            argv = shlex.split(line)
        except ValueError:
            return False, "Parse error: unmatched quotes"

        if not argv:
            return True, ""

        cmd, args = argv[0], argv[1:]
        out = ""

        # built-ins / supported commands
        if cmd == "pwd":
            out = self.fs.pwd() + "\n"

        elif cmd == "ls":
            path = args[0] if args else None
            ok_, out_ = self.fs.ls(path)
            return self._finalize(ok_, out_ + ("\n" if out_ and ok_ else ""), redirect_path, append)

        elif cmd == "cd":
            if not args:
                return False, "cd: missing operand\n"
            ok_, out_ = self.fs.cd(args[0])
            return ok_, out_ + ("\n" if out_ else "")

        elif cmd == "mkdir":
            if not args:
                return False, "mkdir: missing operand\n"
            ok_, out_ = self.fs.mkdir(args[0])
            return ok_, out_ + ("\n" if out_ else "")

        elif cmd == "touch":
            if not args:
                return False, "touch: missing file operand\n"
            ok_, out_ = self.fs.touch(args[0])
            return ok_, out_ + ("\n" if out_ else "")

        elif cmd == "cat":
            if not args:
                return False, "cat: missing file operand\n"
            ok_, out_ = self.fs.cat(args[0])
            return self._finalize(ok_, out_ + ("" if out_.endswith("\n") or not ok_ else "\n"), redirect_path, append)

        elif cmd == "rm":
            if not args:
                return False, "rm: missing operand\n"
            ok_, out_ = self.fs.rm(args[0])
            return ok_, out_ + ("\n" if out_ else "")

        elif cmd == "cp":
            if len(args) != 2:
                return False, "cp: usage: cp SRC DST\n"
            ok_, out_ = self.fs.cp(args[0], args[1])
            return ok_, out_ + ("\n" if out_ else "")

        elif cmd == "mv":
            if len(args) != 2:
                return False, "mv: usage: mv SRC DST\n"
            ok_, out_ = self.fs.mv(args[0], args[1])
            return ok_, out_ + ("\n" if out_ else "")

        elif cmd == "echo":
            # echo prints args joined by spaces; if piped_in exists, we ignore it (simple)
            out = " ".join(args) + "\n"

        elif cmd == "wc":
            # only handle: wc -w / wc -c, reading from piped input or file
            mode = args[0] if args and args[0].startswith("-") else ""
            if piped_in is not None:
                out = wc_count(piped_in, mode) + "\n"
            elif len(args) >= 2:
                ok_, data = self.fs.cat(args[1])
                if not ok_:
                    return False, data + ("\n" if not data.endswith("\n") else "")
                out = wc_count(data, mode) + "\n"
            else:
                return False, "wc: expected piped input or file\n"
        else:
            return False, f"{cmd}: command not found\n"

        return self._finalize(True, out, redirect_path, append)

    def _finalize(self, ok_: bool, out: str, redirect_path: Optional[str], append: bool) -> Tuple[bool, str]:
        if not ok_:
            return False, out
        if redirect_path:
            ok2, msg = self.fs.write_file(redirect_path, out, append=append)
            if not ok2:
                return False, msg + ("\n" if not msg.endswith("\n") else "")
            return True, ""  # redirected output doesn't print
        return True, out


# ----------------------------- Missions ----------------------------- #

@dataclass
class Mission:
    mid: str
    title: str
    scenario: str
    objective: str
    success_checks: List[str]  # simple patterns we check in state
    hint: str
    tags: List[str]


class Topic13Sim:
    def __init__(self, rng: random.Random, short: bool, hints: bool):
        self.rng = rng
        self.short = short
        self.hints = hints
        self.fs = SimFS()
        self.shell = ShellSim(self.fs)
        self.score = 0
        self.max_score = 0
        self.missed: Dict[str, int] = {}
        self.covered: Dict[str, int] = {}

    def hit(self, tag: str) -> None:
        self.covered[tag] = self.covered.get(tag, 0) + 1

    def miss(self, tag: str) -> None:
        self.missed[tag] = self.missed.get(tag, 0) + 1

    def _check_objective(self, checks: List[str]) -> bool:
        # Checks are small assertions, evaluated against current simulated state.
        # Supported checks:
        #   cwd==/path
        #   file_exists:/path
        #   file_contains:/path:substring
        for c in checks:
            if c.startswith("cwd=="):
                want = c.split("==", 1)[1]
                if self.fs.pwd() != want:
                    return False
            elif c.startswith("file_exists:"):
                p = c.split(":", 1)[1]
                p = self.fs._norm(p)
                if p not in self.fs.files:
                    return False
            elif c.startswith("file_contains:"):
                rest = c.split(":", 1)[1]
                path, substr = rest.split(":", 1)
                p = self.fs._norm(path)
                if p not in self.fs.files:
                    return False
                if substr not in self.fs.files[p]:
                    return False
            else:
                # unknown check
                return False
        return True

    def run_mission(self, m: Mission) -> None:
        hr()
        print(f"{m.title} [{m.mid}]")
        print("-" * WRAP)
        print(w(m.scenario))
        print("\nObjective:")
        print(w(f"- {m.objective}"))
        if self.hints:
            print("\nHint:")
            print(w(m.hint))

        # Each mission: up to 6 attempts for full points.
        attempts_left = 6
        self.max_score += 5
        while attempts_left > 0:
            print(f"\n[{self.fs.pwd()}]$ ", end="")
            line = input().strip()
            if line.lower() in ("q", "quit", "exit"):
                raise SystemExit(0)

            ok_run, output = self.shell.run(line)
            if output:
                print(output, end="")

            # allow user to type "check"
            if line.strip().lower() == "check":
                # "check" isn't a real command; ignore output
                pass

            if self._check_objective(m.success_checks):
                # points scale with attempts used
                used = 6 - attempts_left
                pts = 5 if used <= 1 else 4 if used <= 2 else 3 if used <= 3 else 2 if used <= 4 else 1
                self.score += pts
                ok(f"Objective complete! (+{pts}/5)")
                for t in m.tags:
                    if pts >= 4:
                        self.hit(t)
                    elif pts <= 2:
                        self.miss(t)
                return

            attempts_left -= 1
            if attempts_left > 0:
                warn(f"Objective not complete yet. Attempts left: {attempts_left}")

        # failed
        fail("Mission failed (0/5). Review the hint and try again next run.")
        for t in m.tags:
            self.miss(t)

    def concept_checkpoint(self) -> None:
        hr()
        print("Concept Checkpoint (Exam Style)")
        print("-" * WRAP)
        q = [
            ("A terminal is best described as:", [
                "The program that interprets commands (shell)",
                "The interface/app that provides access to a shell session",
                "A package manager",
                "A Linux distribution",
            ], 1, ["terminal-vs-shell"]),
            ("What does the pipe '|' do?", [
                "Sends output of one command as input to another",
                "Overwrites a file with output",
                "Appends output to a file",
                "Changes directory",
            ], 0, ["pipes-redirection"]),
            ("What does '>>' do?", [
                "Overwrites a file",
                "Appends output to a file",
                "Sends output to another command",
                "Deletes a file",
            ], 1, ["pipes-redirection"]),
        ]
        prompt, opts, correct, tags = self.rng.choice(q)

        print(w(prompt))
        for i, opt in enumerate(opts, start=1):
            print(f"  {i}) {opt}")
        ans = input("\nChoose 1-4: ").strip()
        self.max_score += 5
        if ans.isdigit() and 1 <= int(ans) <= 4 and (int(ans) - 1) == correct:
            self.score += 5
            ok("Correct! (+5/5)")
            for t in tags:
                self.hit(t)
        else:
            self.score += 2
            warn("Not quite. (+2/5) Review this concept before the exam.")
            for t in tags:
                self.miss(t)

    def report(self) -> None:
        hr()
        pct = (self.score / self.max_score * 100) if self.max_score else 0.0
        print("TOPIC 1.3 SIMULATION REPORT")
        print("-" * WRAP)
        print(f"Score: {self.score}/{self.max_score} ({pct:.1f}%)")

        if pct >= 85:
            print("Readiness: Exam-ready for Topic 1.3")
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
        if self.missed.get("pipes-redirection", 0) > 0:
            tips.append("Practice: | vs > vs >> (pipe vs overwrite vs append).")
        if self.missed.get("terminal-vs-shell", 0) > 0:
            tips.append("Review: terminal (interface) vs shell (command interpreter).")
        if self.missed.get("basic-commands", 0) > 0:
            tips.append("Practice: pwd, cd, ls, mkdir, touch, cp, mv, rm, cat, less (concept).")
        if self.missed.get("automation-why", 0) > 0:
            tips.append("Explain: why CLI is valuable (remote admin, automation, scripts).")
        if tips:
            print("\nTargeted next steps:")
            for t in tips:
                print(f"  • {t}")
        hr()


def build_missions(rng: random.Random) -> List[Mission]:
    ms = [
        Mission(
            mid="1.3-A",
            title="Mission 1: Navigate and confirm location",
            scenario="You just opened a terminal. You need to confirm where you are in the filesystem.",
            objective="Print the current working directory.",
            success_checks=["file_contains:/tmp/.dummy:__never__"],  # placeholder; we check via command history alternative
            hint="Use: pwd",
            tags=["basic-commands"],
        ),
        Mission(
            mid="1.3-B",
            title="Mission 2: Create a lab directory",
            scenario="You want to start a new lab. Create a directory named practice inside your home directory.",
            objective="Create /home/cannon/practice (from wherever you are).",
            success_checks=["cwd==/home/cannon", "file_contains:/tmp/.dummy:__never__"],  # placeholder
            hint="You can cd to /home/cannon then run: mkdir practice",
            tags=["basic-commands"],
        ),
        Mission(
            mid="1.3-C",
            title="Mission 3: Create and write to a file using redirection",
            scenario="Create a file and write text into it using output redirection.",
            objective="Create /home/cannon/practice/out.txt containing the word hello.",
            success_checks=["file_exists:/home/cannon/practice/out.txt", "file_contains:/home/cannon/practice/out.txt:hello"],
            hint="Try: echo hello > /home/cannon/practice/out.txt",
            tags=["pipes-redirection"],
        ),
        Mission(
            mid="1.3-D",
            title="Mission 4: Append output to a file",
            scenario="Now add another line without overwriting the existing content.",
            objective="Append the word again into /home/cannon/practice/out.txt",
            success_checks=["file_contains:/home/cannon/practice/out.txt:again"],
            hint="Use append redirection: echo again >> /home/cannon/practice/out.txt",
            tags=["pipes-redirection"],
        ),
        Mission(
            mid="1.3-E",
            title="Mission 5: Copy and rename",
            scenario="You want a backup copy of your file with a new name.",
            objective="Copy out.txt to out.bak in the same directory.",
            success_checks=["file_exists:/home/cannon/practice/out.bak"],
            hint="Use: cp /home/cannon/practice/out.txt /home/cannon/practice/out.bak",
            tags=["basic-commands"],
        ),
        Mission(
            mid="1.3-F",
            title="Mission 6: Pipe output into another command",
            scenario="You want to count how many words are in out.txt using a pipe.",
            objective="Run a command that pipes file contents into wc -w (this simulator supports cat | wc -w).",
            success_checks=["file_contains:/tmp/pipeproof:wc_done"],
            hint="Use: cat /home/cannon/practice/out.txt | wc -w",
            tags=["pipes-redirection"],
        ),
        Mission(
            mid="1.3-G",
            title="Mission 7: Clean up",
            scenario="Remove the backup file you created (out.bak).",
            objective="Delete /home/cannon/practice/out.bak",
            success_checks=["file_contains:/tmp/.dummy:__never__"],  # placeholder
            hint="Use: rm /home/cannon/practice/out.bak",
            tags=["basic-commands"],
        ),
        Mission(
            mid="1.3-H",
            title="Mission 8: Why CLI matters (concept)",
            scenario="A teammate asks why admins use CLI on servers instead of a GUI.",
            objective="Answer with the BEST choice (exam style).",
            success_checks=[],
            hint="Think: automation + remote (SSH) + efficiency",
            tags=["automation-why"],
        ),
    ]

    # Replace placeholder checks with mission-specific validators by injecting side-effects
    # We'll implement by adjusting simulator behavior: for some missions, success is detected
    # by checking filesystem state; for others, we mark a proof file when correct command run.
    return ms


# ----------------------------- Enhanced Validation ----------------------------- #

class Topic13Runner(Topic13Sim):
    """
    Extends Topic13Sim with mission-specific proof hooks:
    - For Mission 1: user must run pwd at least once
    - For Mission 2: directory must exist
    - For Mission 6: user must run cat ... | wc -w (we detect it and mark proof)
    - For Mission 7: backup must be deleted
    - For Mission 8: concept MCQ
    """

    def __init__(self, rng: random.Random, short: bool, hints: bool):
        super().__init__(rng, short, hints)
        self.ran_pwd = False

        # create proof directory in /tmp for internal checks
        self.fs.dirs["/tmp"] = self.fs.dirs.get("/tmp", [])
        self.fs.dirs["/tmp"].append("proof")
        self.fs.dirs["/tmp/proof"] = []
        self.fs.files["/tmp/pipeproof"] = ""
        self.fs.files["/tmp/cmdproof"] = ""

        # wrap shell to intercept commands
        self._orig_run = self.shell.run
        self.shell.run = self._run_with_hooks  # type: ignore

    def _run_with_hooks(self, line: str) -> Tuple[bool, str]:
        raw = line.strip()

        # record "pwd" usage
        if raw == "pwd":
            self.ran_pwd = True

        # detect the pipe pattern for mission 6
        # (simple string check; accurate enough for this simulator)
        if "| wc -w" in raw and raw.startswith("cat "):
            self.fs.files["/tmp/pipeproof"] = "wc_done"

        return self._orig_run(line)

    def run_mission(self, m: Mission) -> None:
        # Mission-specific objective checks:
        if m.mid == "1.3-A":
            # override checks: must run pwd
            m = Mission(m.mid, m.title, m.scenario, m.objective,
                        success_checks=["file_contains:/tmp/cmdproof:pwd_done"], hint=m.hint, tags=m.tags)
        super().run_mission(m)

    def _check_objective(self, checks: List[str]) -> bool:
        # Extend checks for directories
        for c in checks:
            if c.startswith("dir_exists:"):
                p = self.fs._norm(c.split(":", 1)[1])
                if p not in self.fs.dirs:
                    return False
        # use base checks
        ok_base = super()._check_objective([c for c in checks if not c.startswith("dir_exists:")])

        # Special: Mission 1 uses a proof string
        # If they ran pwd, mark cmdproof.
        if self.ran_pwd:
            self.fs.files["/tmp/cmdproof"] = "pwd_done"

        return ok_base or self._check_extra_state(checks)

    def _check_extra_state(self, checks: List[str]) -> bool:
        # Implement specific checks not covered by base:
        for c in checks:
            if c == "ran_pwd":
                if not self.ran_pwd:
                    return False
        return True

    def concept_mission_cli_reason(self) -> int:
        hr()
        print("Mission 8 (Exam Style): Why CLI matters")
        print("-" * WRAP)
        print(w("Which BEST explains why administrators often prefer CLI on servers?"))
        opts = [
            "CLI uses more memory than GUI so it must be better",
            "CLI is scriptable, efficient, and works well over remote connections like SSH",
            "CLI prevents all mistakes automatically",
            "CLI is required because GUIs cannot run on Linux",
        ]
        for i, o in enumerate(opts, start=1):
            print(f"  {i}) {o}")
        ans = input("\nChoose 1-4: ").strip()
        if ans.isdigit() and 1 <= int(ans) <= 4 and (int(ans) - 1) == 1:
            return 5
        return 2


def missions_for_runner(sim: Topic13Runner) -> List[Mission]:
    ms = build_missions(sim.rng)

    # Update mission 1 check to use special state (pwd done)
    ms2: List[Mission] = []
    for m in ms:
        if m.mid == "1.3-A":
            ms2.append(Mission(
                mid=m.mid, title=m.title, scenario=m.scenario, objective=m.objective,
                success_checks=["file_contains:/tmp/cmdproof:pwd_done"],
                hint=m.hint, tags=m.tags
            ))
        elif m.mid == "1.3-B":
            ms2.append(Mission(
                mid=m.mid, title=m.title, scenario=m.scenario, objective=m.objective,
                success_checks=["dir_exists:/home/cannon/practice"],
                hint=m.hint, tags=m.tags
            ))
        elif m.mid == "1.3-G":
            # mission 7: ensure file no longer exists
            # We'll detect by checking it does NOT exist via custom negative check (implemented here):
            ms2.append(Mission(
                mid=m.mid, title=m.title, scenario=m.scenario, objective=m.objective,
                success_checks=["file_contains:/tmp/cmdproof:rm_done"],  # proof set when file absent
                hint=m.hint, tags=m.tags
            ))
        else:
            ms2.append(m)

    # Shuffle missions but keep their order stable-ish for learning
    sim.rng.shuffle(ms2)
    return ms2


def main() -> int:
    ap = argparse.ArgumentParser(description="LPIC Essentials Topic 1.3 — Simulation App")
    ap.add_argument("--seed", type=int, default=None, help="Deterministic mission order")
    ap.add_argument("--short", action="store_true", help="Short run (fewer missions)")
    ap.add_argument("--no-hints", action="store_true", help="Disable hints")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    sim = Topic13Runner(rng=rng, short=args.short, hints=(not args.no_hints))

    hr()
    print("LPIC Essentials — Topic 1.3 Simulation")
    print("-" * WRAP)
    print(w(
        "You’ll complete lab-style missions aligned to Topic 1.3 (Command Line Power). "
        "This is a SAFE simulated shell. Practice commands, pipes, and redirection."
    ))
    print("\nSupported commands: pwd, ls, cd, mkdir, touch, cp, mv, rm, cat, echo, wc")
    print("Supported syntax: |   >   >>")
    hr()

    mlist = missions_for_runner(sim)

    # We'll run 5 missions short, 7 missions full + a checkpoint
    run_count = 5 if args.short else 7
    completed = 0

    for m in mlist:
        if completed >= run_count:
            break

        # Special handling for mission 7 delete proof:
        if m.mid == "1.3-G":
            # Before starting, set success check proof to empty
            sim.fs.files["/tmp/cmdproof"] = sim.fs.files.get("/tmp/cmdproof", "")
            # Run mission normally; after each command we can mark proof if file is gone
            # We'll do this by patching the objective checker behavior: after each prompt,
            # if file doesn't exist, write "rm_done" into cmdproof.
            # Simple approach: we mark it just before checking objective:
            # (hooked inside _check_objective)
            pass

        # Special: Mission 8 is concept MCQ, not shell lab
        if m.mid == "1.3-H":
            hr()
            print(f"{m.title} [{m.mid}]")
            print("-" * WRAP)
            print(w(m.scenario))
            pts = sim.concept_mission_cli_reason()
            sim.score += pts
            sim.max_score += 5
            if pts == 5:
                ok("Correct. (+5/5)")
                sim.hit("automation-why")
            else:
                warn("Not quite. (+2/5)")
                sim.miss("automation-why")
            completed += 1
            continue

        # Patch objective checker for delete proof (Mission 7)
        if m.mid == "1.3-G":
            # Wrap the original check temporarily
            orig_check = sim._check_objective

            def check_with_delete_proof(checks: List[str]) -> bool:
                # If out.bak is absent, mark proof string
                if "/home/cannon/practice/out.bak" not in sim.fs.files:
                    sim.fs.files["/tmp/cmdproof"] = "rm_done"
                return orig_check(checks)

            sim._check_objective = check_with_delete_proof  # type: ignore
            sim.run_mission(m)
            sim._check_objective = orig_check  # restore
        else:
            sim.run_mission(m)

        completed += 1

        # Add a checkpoint mid-way in full mode
        if (not args.short) and completed == 4:
            sim.concept_checkpoint()

    sim.report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
