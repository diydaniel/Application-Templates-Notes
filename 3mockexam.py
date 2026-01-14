#!/usr/bin/env python3
"""
LPIC Essentials — 40 Question Mock Exam (v3 HARD)

Features:
- Exactly 40 questions (harder, scenario-based)
- Shuffle questions + options (grade-safe)
- Topic breakdown (1.1–1.5)
- Review mode: missed | all | none
- Deterministic shuffling with --seed

Run:
  python3 lpic_essentials_mock_exam_v3_hard.py

Options:
  --seed 123
  --no-shuffle
  --pass 75
  --review missed|all|none
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple


LETTERS = ("A", "B", "C", "D")


@dataclass(frozen=True)
class Question:
    qid: int
    topic: str          # 1.1..1.5
    prompt: str
    options: Tuple[str, str, str, str]
    correct: int        # 0..3
    explanation: str


def bank() -> List[Question]:
    # Exactly 40 harder questions, aligned to LPIC Essentials topics 1.1–1.5.
    # Topic distribution: 1.1 (7), 1.2 (8), 1.3 (9), 1.4 (10), 1.5 (6) = 40
    return [
        # ===================== Topic 1.1 (7) =====================
        Question(
            1, "1.1",
            "A company uses Linux internally but never shares modifications to the Linux kernel outside the company. "
            "Which statement is MOST accurate (high-level, Essentials)?",
            (
                "This is always illegal because Linux must be used only for public projects",
                "This can be allowed; obligations depend on how the software is distributed and its license terms",
                "This is allowed only if the company pays a fee to the Linux community",
                "This is allowed only if the company never updates the system",
            ),
            1,
            "Licenses define obligations; many obligations trigger on redistribution, not private internal use."
        ),
        Question(
            2, "1.1",
            "Which BEST describes why open-source communities can improve software quality over time?",
            (
                "Because open-source code never contains bugs",
                "Because many reviewers and contributors can find bugs and propose fixes transparently",
                "Because open-source software cannot be used commercially",
                "Because only one vendor controls changes",
            ),
            1,
            "Broad peer review and transparent contributions can improve quality and security."
        ),
        Question(
            3, "1.1",
            "You’re planning a Linux learning path for infrastructure work. Which sequence is MOST sensible?",
            (
                "LPIC-2 → LPIC-1 → LPIC Essentials",
                "LPIC Essentials → LPIC-1 → LPIC-2",
                "LPIC Essentials → LPIC-3 only",
                "Skip fundamentals and start directly with kernel development",
            ),
            1,
            "Essentials builds foundations; LPIC-1 covers admin tasks; LPIC-2 goes deeper."
        ),
        Question(
            4, "1.1",
            "A key reason Linux is dominant in cloud/server environments is:",
            (
                "Linux requires expensive per-server licensing",
                "Linux is stable, automation-friendly, and widely supported on server hardware and cloud platforms",
                "Linux cannot be customized, which prevents configuration errors",
                "Linux is only used for desktop gaming",
            ),
            1,
            "Linux is efficient, stable, scriptable, and deeply integrated into cloud ecosystems."
        ),
        Question(
            5, "1.1",
            "Which is the BEST description of a Linux distribution (distro) in practice?",
            (
                "The Linux kernel by itself",
                "The kernel plus user-space tools, libraries, package manager, and default configuration",
                "Only the graphical desktop interface",
                "A special type of Linux license",
            ),
            1,
            "A distro is a complete OS package built around the Linux kernel."
        ),
        Question(
            6, "1.1",
            "An LTS release is MOST useful when you need:",
            (
                "The newest features as fast as possible, even if they break compatibility",
                "A stable platform with long-term security fixes and fewer disruptive changes",
                "A system that never receives any updates",
                "A system that only runs containers",
            ),
            1,
            "LTS is about stability and extended support."
        ),
        Question(
            7, "1.1",
            "Which job task most strongly suggests Linux competency is required?",
            (
                "Building scalable CI/CD pipelines and managing containers in production",
                "Editing photos for marketing brochures",
                "Designing a restaurant menu",
                "Coaching a youth sports team",
            ),
            0,
            "CI/CD, containers, and production infrastructure typically rely on Linux."
        ),

        # ===================== Topic 1.2 (8) =====================
        Question(
            8, "1.2",
            "A user says: “I’m in /home/cannon/projects and I ran `cd ..` twice.” Where are they now?",
            (
                "/home/cannon",
                "/home",
                "/",
                "/home/cannon/projects/..",
            ),
            1,
            "From /home/cannon/projects → /home/cannon → /home."
        ),
        Question(
            9, "1.2",
            "Which directory is MOST associated with system logs and variable runtime data?",
            (
                "/etc",
                "/var",
                "/bin",
                "/home",
            ),
            1,
            "/var contains variable data like logs, cache, spool (e.g., /var/log)."
        ),
        Question(
            10, "1.2",
            "A path like `./scripts/run.sh` is an example of:",
            (
                "An absolute path",
                "A relative path",
                "A kernel path",
                "A device file path",
            ),
            1,
            "Relative paths depend on the current directory; ./ means “current directory”."
        ),
        Question(
            11, "1.2",
            "You need system-wide configuration for a service. Which location is MOST likely correct?",
            (
                "/etc",
                "/home",
                "/tmp",
                "/bin",
            ),
            0,
            "/etc is the standard location for system-wide configuration."
        ),
        Question(
            12, "1.2",
            "Which statement BEST matches the idea “everything is a file”?",
            (
                "Linux stores every file as plain text",
                "Many devices and system info appear as files (e.g., /dev, /proc)",
                "Only the root user can create files",
                "Files cannot be executed in Linux",
            ),
            1,
            "Linux represents many resources through file-like interfaces."
        ),
        Question(
            13, "1.2",
            "Hidden files are typically hidden because:",
            (
                "They are always malicious",
                "They start with a dot (.) and are often configuration files",
                "They are stored only in /var",
                "They require sudo to view",
            ),
            1,
            "Dotfiles are commonly per-user configuration files (e.g., .bashrc)."
        ),
        Question(
            14, "1.2",
            "Which path is absolute?",
            (
                "../notes.txt",
                "notes.txt",
                "/etc/hosts",
                "./notes.txt",
            ),
            2,
            "Absolute paths start with '/'."
        ),
        Question(
            15, "1.2",
            "Which directory is MOST likely to contain binaries (essential commands) used during boot or recovery?",
            (
                "/bin",
                "/home",
                "/var/log",
                "/etc",
            ),
            0,
            "/bin commonly holds essential user commands (varies by distro, but concept stands)."
        ),

        # ===================== Topic 1.3 (9) =====================
        Question(
            16, "1.3",
            "You want to save the output of a command to a file, overwriting the file if it exists. Which operator do you use?",
            (
                "|",
                ">",
                ">>",
                "<",
            ),
            1,
            "> redirects stdout to a file and overwrites/creates it."
        ),
        Question(
            17, "1.3",
            "You ran `echo hello | wc -c`. What is the pipe doing?",
            (
                "Sending wc output into echo",
                "Sending echo output into wc input",
                "Saving output to a file",
                "Running both commands as root",
            ),
            1,
            "The pipe passes stdout of the first command to stdin of the second."
        ),
        Question(
            18, "1.3",
            "Which is the BEST reason CLI is preferred for many server tasks?",
            (
                "CLI uses more resources than GUI, so it is preferred",
                "CLI is scriptable and works well over remote connections (SSH)",
                "CLI is only available on Windows servers",
                "CLI prevents all user mistakes automatically",
            ),
            1,
            "CLI is automation-friendly and efficient for remote admin."
        ),
        Question(
            19, "1.3",
            "You want to VIEW a long text file without editing it, one screen at a time. Best tool:",
            (
                "less",
                "rm",
                "mv",
                "mkdir",
            ),
            0,
            "less is a pager for viewing long output."
        ),
        Question(
            20, "1.3",
            "Which command combination BEST matches: “Copy file a.txt to b.txt”?",
            (
                "mv a.txt b.txt",
                "cp a.txt b.txt",
                "rm a.txt b.txt",
                "mkdir a.txt b.txt",
            ),
            1,
            "cp copies; mv moves/renames."
        ),
        Question(
            21, "1.3",
            "You typed a command earlier and want to quickly reuse it without retyping. Which feature helps most?",
            (
                "Tab completion",
                "Command history",
                "Filesystem hierarchy",
                "Package repository",
            ),
            1,
            "History allows recalling previous commands (often with arrow keys or history search)."
        ),
        Question(
            22, "1.3",
            "What is the difference between a terminal and a shell?",
            (
                "They are the same thing",
                "Terminal is the interface; shell interprets commands",
                "Shell is hardware; terminal is software",
                "Terminal manages packages; shell manages users",
            ),
            1,
            "Terminal provides the window; shell runs and interprets commands."
        ),
        Question(
            23, "1.3",
            "Which command creates an empty file named report.txt (typical usage)?",
            (
                "touch report.txt",
                "mkdir report.txt",
                "cd report.txt",
                "ps report.txt",
            ),
            0,
            "touch creates an empty file (or updates timestamps)."
        ),
        Question(
            24, "1.3",
            "You want to APPEND command output to a file without overwriting. Which operator?",
            (
                ">",
                ">>",
                "|",
                "&&",
            ),
            1,
            ">> appends stdout to the end of a file."
        ),

        # ===================== Topic 1.4 (10) =====================
        Question(
            25, "1.4",
            "A user says: “The kernel is just another app.” Which is the BEST correction?",
            (
                "The kernel is the core component that manages hardware and system resources",
                "The kernel is a text editor included with Linux",
                "The kernel only provides the GUI",
                "The kernel is a package repository",
            ),
            0,
            "Kernel manages CPU/memory/devices/process scheduling; apps run in user space."
        ),
        Question(
            26, "1.4",
            "Which statement best describes user space vs kernel space?",
            (
                "User space runs core hardware drivers; kernel space runs web browsers",
                "User space is where apps run; kernel space is where core OS functions execute",
                "Kernel space is where files live; user space is where directories live",
                "There is no difference on Linux",
            ),
            1,
            "Apps run in user space; kernel handles privileged operations."
        ),
        Question(
            27, "1.4",
            "A “process” is:",
            (
                "A program stored on disk",
                "A running instance of a program with a PID",
                "A Linux distribution",
                "A software license",
            ),
            1,
            "Process = running program instance (has PID)."
        ),
        Question(
            28, "1.4",
            "Which is MOST accurate about package managers (Essentials level)?",
            (
                "They install software and handle dependencies from repositories",
                "They only work for GUI applications",
                "They are only used on Windows",
                "They replace the need for security updates",
            ),
            0,
            "Package managers install/update/remove software and manage deps from repos."
        ),
        Question(
            29, "1.4",
            "A dependency is best described as:",
            (
                "A user group that owns a file",
                "A required library/component another program needs to run",
                "A directory inside /home",
                "A network cable type",
            ),
            1,
            "Dependencies are required components (e.g., shared libraries)."
        ),
        Question(
            30, "1.4",
            "Which statement about RAM vs swap is MOST accurate?",
            (
                "Swap is faster than RAM",
                "Swap is disk-backed memory used when RAM is under pressure, usually slower than RAM",
                "RAM is stored on disk permanently",
                "Swap is only used for networking",
            ),
            1,
            "Swap extends memory using disk; it’s typically slower than RAM."
        ),
        Question(
            31, "1.4",
            "Which is the BEST conceptual difference between containers and virtual machines?",
            (
                "Containers include full guest OS kernels; VMs share the host kernel",
                "Containers share the host kernel; VMs typically run full guest OS stacks",
                "Containers can’t be used in cloud platforms",
                "VMs cannot isolate processes",
            ),
            1,
            "Containers share host kernel; VMs run full guest OS."
        ),
        Question(
            32, "1.4",
            "You run `ps` and `top`. Which statement is MOST accurate?",
            (
                "`ps` is real-time; `top` is a one-time snapshot",
                "`top` provides a real-time-ish view; `ps` provides a snapshot at the moment it runs",
                "Both commands only show disk usage",
                "Both commands only show installed packages",
            ),
            1,
            "top updates continuously; ps prints a snapshot."
        ),
        Question(
            33, "1.4",
            "Linux is often called “multi-user.” In practical terms this implies:",
            (
                "Only one user can log in",
                "Multiple accounts can exist with separate permissions and concurrent sessions",
                "Users cannot share a system",
                "Linux does not support permissions",
            ),
            1,
            "Multi-user systems support multiple accounts and permission boundaries."
        ),
        Question(
            34, "1.4",
            "Why do cloud providers often favor Linux images?",
            (
                "Linux is heavier and requires more overhead",
                "Linux is efficient, automation-friendly, and has broad ecosystem support",
                "Linux cannot be customized, which is good for cloud",
                "Linux requires per-core licensing costs",
            ),
            1,
            "Linux is light, scriptable, stable, and widely supported in cloud environments."
        ),

        # ===================== Topic 1.5 (6) =====================
        Question(
            35, "1.5",
            "Principle of least privilege means:",
            (
                "Everyone should be admin to avoid permission problems",
                "Users should have only the permissions necessary to perform their tasks",
                "All files should be world-writable",
                "Root should be used for daily work",
            ),
            1,
            "Least privilege reduces damage from mistakes and compromise."
        ),
        Question(
            36, "1.5",
            "Which statement is MOST accurate about `sudo`?",
            (
                "`sudo` permanently makes a user root",
                "`sudo` lets authorized users run specific commands with elevated privileges",
                "`sudo` is a firewall tool",
                "`sudo` disables permissions checking",
            ),
            1,
            "sudo provides controlled privilege escalation for authorized users."
        ),
        Question(
            37, "1.5",
            "Permission string: `-rwxr-xr--` means:",
            (
                "Owner can read/write/execute; group can read/execute; others can read",
                "Owner can read only; group can write only; others can execute only",
                "Owner can execute only; group can read only; others can write only",
                "Everyone can read/write/execute",
            ),
            0,
            "Triplets are owner/group/others: rwx / r-x / r--."
        ),
        Question(
            38, "1.5",
            "You set a file to be world-writable (others have write permission). The biggest risk is:",
            (
                "The file becomes hidden automatically",
                "Any user can modify it, potentially injecting malicious content or breaking behavior",
                "The file becomes read-only",
                "The file is encrypted",
            ),
            1,
            "Overly open permissions increase tampering and security risks."
        ),
        Question(
            39, "1.5",
            "Updates are a security best practice primarily because:",
            (
                "They always add new features first",
                "They patch known vulnerabilities and fix bugs",
                "They remove the need for permissions",
                "They stop all attacks permanently",
            ),
            1,
            "Patching reduces exposure to known vulnerabilities."
        ),
        Question(
            40, "1.5",
            "Conceptually, a firewall is used to:",
            (
                "Manage file ownership",
                "Filter network traffic based on allow/deny rules",
                "Install packages from repositories",
                "Convert GUI apps into CLI apps",
            ),
            1,
            "Firewalls control inbound/outbound network traffic according to rules."
        ),
    ]


def shuffle_options(q: Question, rng: random.Random) -> Question:
    idx = list(range(4))
    rng.shuffle(idx)
    new_opts = tuple(q.options[i] for i in idx)
    new_correct = idx.index(q.correct)
    return Question(q.qid, q.topic, q.prompt, new_opts, new_correct, q.explanation)


def read_answer() -> str:
    while True:
        ans = input("Your answer (A/B/C/D) or Q to quit: ").strip().upper()
        if ans in ("Q", "QUIT", "EXIT"):
            return "Q"
        if ans in LETTERS:
            return ans
        print("Please enter A, B, C, D, or Q.")


def main() -> int:
    ap = argparse.ArgumentParser(description="LPIC Essentials — 40Q Mock Exam (v3 HARD)")
    ap.add_argument("--seed", type=int, default=None, help="Deterministic shuffle seed")
    ap.add_argument("--no-shuffle", action="store_true", help="Disable shuffling")
    ap.add_argument("--pass", dest="pass_mark", type=int, default=75, help="Pass mark percent (default 75 for HARD)")
    ap.add_argument("--review", choices=["missed", "all", "none"], default="missed", help="Review mode")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    qs = bank()

    if len(qs) != 40:
        print(f"ERROR: Question bank must be exactly 40 questions, found {len(qs)}.")
        return 2

    if not args.no_shuffle:
        rng.shuffle(qs)
        qs = [shuffle_options(q, rng) for q in qs]

    print("\nLPIC Essentials — 40 Question Mock Exam (v3 HARD)\n")
    print("Harder exam-style questions. Answer A–D. Type Q to quit.\n")

    results: List[Dict] = []
    for i, q in enumerate(qs, start=1):
        print("=" * 76)
        print(f"Q{i}/40  |  Topic {q.topic}  |  ID {q.qid}")
        print(q.prompt)
        print("-" * 76)
        for j, opt in enumerate(q.options):
            print(f"  {LETTERS[j]}. {opt}")

        ans = read_answer()
        if ans == "Q":
            print("\nExiting early. Scoring completed questions...\n")
            break

        chosen = LETTERS.index(ans)
        is_correct = chosen == q.correct
        results.append({
            "qid": q.qid,
            "topic": q.topic,
            "prompt": q.prompt,
            "options": q.options,
            "chosen": chosen,
            "correct": q.correct,
            "is_correct": is_correct,
            "explanation": q.explanation,
        })

    answered = len(results)
    correct_count = sum(1 for r in results if r["is_correct"])
    pct = (correct_count / answered * 100) if answered else 0.0
    status = "PASS" if pct >= args.pass_mark else "FAIL"

    print("=" * 76)
    print("RESULTS")
    print("=" * 76)
    print(f"Answered: {answered}/40")
    print(f"Correct : {correct_count}")
    print(f"Score   : {pct:.1f}%")
    print(f"Status  : {status} (Pass mark: {args.pass_mark}%)")

    # Topic breakdown
    topic_totals: Dict[str, int] = {}
    topic_correct: Dict[str, int] = {}
    for r in results:
        t = r["topic"]
        topic_totals[t] = topic_totals.get(t, 0) + 1
        topic_correct[t] = topic_correct.get(t, 0) + (1 if r["is_correct"] else 0)

    print("\nBy Topic:")
    for t in sorted(topic_totals.keys()):
        tt = topic_totals[t]
        cc = topic_correct[t]
        tp = (cc / tt * 100) if tt else 0.0
        print(f"  Topic {t}: {cc}/{tt} ({tp:.1f}%)")

    # Review
    if args.review != "none" and results:
        if args.review == "missed":
            review_items = [r for r in results if not r["is_correct"]]
            title = "REVIEW (MISSED)"
        else:
            review_items = results
            title = "REVIEW (ALL)"

        print("\n" + "=" * 76)
        print(title)
        print("=" * 76)

        if not review_items:
            print("No missed questions. Nice.")
        else:
            for r in review_items:
                print("\n" + "-" * 76)
                print(f"Topic {r['topic']} | ID {r['qid']}")
                print(r["prompt"])
                for j, opt in enumerate(r["options"]):
                    tag = ""
                    if j == r["correct"]:
                        tag += " [CORRECT]"
                    if j == r["chosen"]:
                        tag += " [YOU]"
                    print(f"  {LETTERS[j]}. {opt}{tag}")
                print(f"Explanation: {r['explanation']}")

    print("\nDone.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
