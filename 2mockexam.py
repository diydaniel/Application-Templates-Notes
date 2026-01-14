#!/usr/bin/env python3
"""
LPIC Essentials — 40 Question Mock Exam (v2)

Run:
  python3 lpic_essentials_mock_exam_v2.py

Options:
  --seed 123          Deterministic shuffle
  --no-shuffle        No shuffling (questions + choices stay fixed)
  --pass 70           Pass mark percent (default 70)
  --review all        Review: all | missed | none (default missed)
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass(frozen=True)
class Question:
    qid: int
    topic: str  # 1.1..1.5
    prompt: str
    options: Tuple[str, str, str, str]  # A,B,C,D
    correct: int  # 0..3
    explanation: str


LETTERS = ("A", "B", "C", "D")


def bank() -> List[Question]:
    # Exactly 40 questions total, spanning topics 1.1–1.5
    return [
        # ---------------- Topic 1.1 (8) ----------------
        Question(1, "1.1",
                 "Open-source software is best described as:",
                 (
                     "Software that is free of charge but cannot be modified",
                     "Software whose source code is available and licensed for use, modification, and redistribution",
                     "Software that only runs on Linux",
                     "Software that is always developed by a single company",
                 ),
                 1,
                 "Open-source means source is available and rights are granted via license to use/modify/redistribute."),
        Question(2, "1.1",
                 "Which statement best describes a Linux distribution?",
                 (
                     "The Linux kernel only",
                     "A desktop environment like GNOME or KDE",
                     "Linux kernel plus user-space tools, libraries, and applications packaged together",
                     "A proprietary Unix operating system",
                 ),
                 2,
                 "A distro bundles the kernel + user-space to create a complete usable OS."),
        Question(3, "1.1",
                 "A common advantage of community-driven open-source development is:",
                 (
                     "No need for updates because code is perfect",
                     "Faster improvements through broad collaboration and peer review",
                     "Only paid users can report bugs",
                     "Roadmap is secret and closed",
                 ),
                 1,
                 "Many contributors and transparent review often improves quality and pace."),
        Question(4, "1.1",
                 "Which environment most commonly uses Linux heavily?",
                 (
                     "Cloud and server infrastructure",
                     "Arcade machines only",
                     "Only home printers",
                     "Only smartphones that are not Android",
                 ),
                 0,
                 "Linux dominates servers/cloud due to stability, automation, licensing, and ecosystem support."),
        Question(5, "1.1",
                 "What does LTS (Long-Term Support) primarily provide?",
                 (
                     "Rolling releases with frequent breaking changes",
                     "Extended security updates and stability over a longer support window",
                     "A guarantee of newest features first",
                     "No updates allowed",
                 ),
                 1,
                 "LTS prioritizes stability and long support for production use."),
        Question(6, "1.1",
                 "LPIC Essentials is best described as:",
                 (
                     "An advanced Linux admin certification beyond LPIC-2",
                     "A foundational Linux literacy and concepts certification",
                     "A certification only about programming in C",
                     "A vendor-specific exam for one Linux distro",
                 ),
                 1,
                 "Essentials is introductory and concept-heavy; LPIC-1 is more operational."),
        Question(7, "1.1",
                 "A key benefit of Linux certifications is:",
                 (
                     "They replace real experience entirely",
                     "They validate baseline knowledge in a structured way for employers",
                     "They guarantee a job offer",
                     "They are only useful for Windows admins",
                 ),
                 1,
                 "Certs help signal and standardize skills; they don’t replace experience."),
        Question(8, "1.1",
                 "Which role is MOST likely to use Linux daily?",
                 (
                     "DevOps / Cloud Engineer",
                     "Fashion stylist",
                     "Restaurant waiter",
                     "Gym trainer",
                 ),
                 0,
                 "Infrastructure and automation roles commonly rely on Linux."),

        # ---------------- Topic 1.2 (8) ----------------
        Question(9, "1.2",
                 "Which directory is the top of the Linux filesystem hierarchy?",
                 ("/etc", "/root", "/", "/home"),
                 2,
                 "The filesystem root is '/'. /root is root user’s home directory."),
        Question(10, "1.2",
                 "System-wide configuration files are primarily found in:",
                 ("/etc", "/bin", "/home", "/tmp"),
                 0,
                 "/etc stores system configuration."),
        Question(11, "1.2",
                 "Log files are commonly stored under:",
                 ("/var/log", "/etc/log", "/bin/log", "/home/log"),
                 0,
                 "Logs usually live in /var/log."),
        Question(12, "1.2",
                 "A path that starts with '/' is:",
                 ("Relative", "Absolute", "Hidden", "Executable-only"),
                 1,
                 "Absolute paths start at '/' (filesystem root)."),
        Question(13, "1.2",
                 "In Linux, a filename beginning with a dot (.) is typically:",
                 ("A hidden file", "A directory only", "A broken file", "A system-only executable"),
                 0,
                 "Dotfiles are hidden by default in many listings."),
        Question(14, "1.2",
                 "What does '..' refer to?",
                 ("Current directory", "Parent directory", "Home directory", "Root directory"),
                 1,
                 ".. means the parent directory."),
        Question(15, "1.2",
                 "Which directory typically contains user home folders?",
                 ("/usr", "/var", "/home", "/lib"),
                 2,
                 "/home contains user directories like /home/alex."),
        Question(16, "1.2",
                 "The phrase 'everything is a file' mainly means:",
                 (
                     "Linux only supports text files",
                     "Many devices and system resources are exposed via file-like interfaces",
                     "Files cannot be deleted in Linux",
                     "Only root can create files",
                 ),
                 1,
                 "Examples: /dev for devices, /proc for process/system info."),

        # ---------------- Topic 1.3 (8) ----------------
        Question(17, "1.3",
                 "A shell is:",
                 (
                     "A hardware part that stores files",
                     "A command interpreter that runs your commands",
                     "A GUI theme manager",
                     "A firewall component",
                 ),
                 1,
                 "Shells include bash, zsh, etc."),
        Question(18, "1.3",
                 "A terminal is best described as:",
                 (
                     "The Linux kernel",
                     "A program/interface used to access a shell",
                     "A file permissions system",
                     "A package repository",
                 ),
                 1,
                 "Terminal emulators provide an interface to interact with the shell."),
        Question(19, "1.3",
                 "What does the pipe symbol '|' do?",
                 (
                     "Sends output of one command to a file",
                     "Sends output of one command as input to another",
                     "Changes permissions",
                     "Stops a running program",
                 ),
                 1,
                 "Pipes connect stdout of one command to stdin of another."),
        Question(20, "1.3",
                 "What does output redirection with '>' typically do?",
                 (
                     "Appends output to the end of a file",
                     "Overwrites (or creates) a file with command output",
                     "Deletes the file",
                     "Runs the command as root",
                 ),
                 1,
                 "> overwrites/creates the target file with stdout."),
        Question(21, "1.3",
                 "Which command prints the current working directory?",
                 ("pwd", "cd", "ls", "whoami"),
                 0,
                 "pwd prints working directory."),
        Question(22, "1.3",
                 "Which command is used to create a directory?",
                 ("mkdir", "touch", "cat", "grep"),
                 0,
                 "mkdir creates directories."),
        Question(23, "1.3",
                 "What does 'mv' commonly do?",
                 (
                     "Move or rename files/directories",
                     "Copy files only",
                     "List processes",
                     "Show system logs",
                 ),
                 0,
                 "mv moves/renames."),
        Question(24, "1.3",
                 "Why is tab completion useful?",
                 (
                     "It encrypts files",
                     "It reduces typing and prevents command/path typos",
                     "It makes your CPU faster",
                     "It deletes history automatically",
                 ),
                 1,
                 "Tab completion speeds navigation and reduces mistakes."),

        # ---------------- Topic 1.4 (10) ----------------
        Question(25, "1.4",
                 "The Linux kernel is responsible for:",
                 (
                     "Managing hardware resources and scheduling processes",
                     "Only providing a GUI desktop",
                     "Only managing user documents",
                     "Running only web servers",
                 ),
                 0,
                 "Kernel manages CPU, memory, devices, processes, scheduling."),
        Question(26, "1.4",
                 "A process is:",
                 ("A file on disk", "A running instance of a program", "A repository", "A user account"),
                 1,
                 "When a program runs, it becomes a process."),
        Question(27, "1.4",
                 "PID stands for:",
                 ("Package Install Directory", "Process Identifier", "Permission ID", "Program Internal Data"),
                 1,
                 "PID uniquely identifies a process."),
        Question(28, "1.4",
                 "Linux being multi-user means:",
                 (
                     "Only one person can use Linux",
                     "Multiple users can exist with separate permissions and sessions",
                     "Users cannot share resources",
                     "Only root can log in",
                 ),
                 1,
                 "Multi-user: many accounts, separation via permissions."),
        Question(29, "1.4",
                 "A package manager is used to:",
                 (
                     "Install, update, and remove software packages",
                     "Format disks only",
                     "Create user accounts only",
                     "Configure network routes only",
                 ),
                 0,
                 "Package managers handle software lifecycle and dependencies."),
        Question(30, "1.4",
                 "A software repository is:",
                 (
                     "A folder for your personal files",
                     "A collection of packages + metadata for installation",
                     "A CPU feature",
                     "A kernel driver",
                 ),
                 1,
                 "Repos are sources package managers pull from."),
        Question(31, "1.4",
                 "A dependency is:",
                 (
                     "A library/component another program needs to run",
                     "A user group",
                     "A disk partition",
                     "A network interface",
                 ),
                 0,
                 "Dependencies are required supporting components."),
        Question(32, "1.4",
                 "RAM is primarily used for:",
                 (
                     "Long-term storage after shutdown",
                     "Temporary working memory for running programs",
                     "Storing only system logs",
                     "Holding the BIOS",
                 ),
                 1,
                 "RAM holds active data and running processes."),
        Question(33, "1.4",
                 "Swap space is:",
                 (
                     "Extra disk-backed memory used when RAM is pressured",
                     "A second CPU",
                     "A type of file permission",
                     "A place to store user passwords",
                 ),
                 0,
                 "Swap extends memory using disk (slower than RAM)."),
        Question(34, "1.4",
                 "Containers differ from VMs because containers:",
                 (
                     "Include a full separate kernel for each container",
                     "Share the host kernel and isolate user space",
                     "Can only run on Windows",
                     "Cannot run in the cloud",
                 ),
                 1,
                 "Containers share host kernel; VMs include full guest OS stacks."),

        # ---------------- Topic 1.5 (6) ----------------
        Question(35, "1.5",
                 "The principle of least privilege means:",
                 (
                     "Users should have admin access by default",
                     "Users should have only the access required to do their job",
                     "All files should be world-writable",
                     "Only root should exist",
                 ),
                 1,
                 "Least privilege reduces damage from mistakes/compromise."),
        Question(36, "1.5",
                 "The root user is:",
                 (
                     "A normal user with limited rights",
                     "The superuser with full administrative control",
                     "A guest account",
                     "A group for admins only",
                 ),
                 1,
                 "Root can do anything on the system."),
        Question(37, "1.5",
                 "sudo is used to:",
                 (
                     "Delete system logs",
                     "Run a command with elevated privileges (if permitted)",
                     "Encrypt the filesystem automatically",
                     "Disable networking",
                 ),
                 1,
                 "sudo grants controlled privilege escalation."),
        Question(38, "1.5",
                 "In -rwxr-xr--, the first 'rwx' set applies to:",
                 ("The file owner", "The group", "Everyone", "Only root"),
                 0,
                 "Permission triplets are owner, group, others."),
        Question(39, "1.5",
                 "Read (r) permission on a file allows:",
                 ("Viewing the file contents", "Executing the file", "Deleting the file", "Changing owner"),
                 0,
                 "Read permission allows reading contents."),
        Question(40, "1.5",
                 "Conceptually, a firewall is used to:",
                 (
                     "Filter network traffic according to rules",
                     "Store passwords securely",
                     "Speed up the CPU",
                     "Install software packages",
                 ),
                 0,
                 "Firewalls allow/deny traffic based on rules."),
    ]


def shuffle_question(q: Question, rng: random.Random) -> Question:
    # Shuffle answer options while keeping correct index accurate
    idx = list(range(4))
    rng.shuffle(idx)
    new_opts = tuple(q.options[i] for i in idx)
    new_correct = idx.index(q.correct)
    return Question(q.qid, q.topic, q.prompt, new_opts, new_correct, q.explanation)


def get_answer() -> str:
    while True:
        a = input("Your answer (A/B/C/D) or Q to quit: ").strip().upper()
        if a in ("Q", "QUIT", "EXIT"):
            return "Q"
        if a in LETTERS:
            return a
        print("Please enter A, B, C, D, or Q.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=None, help="Deterministic shuffle seed")
    ap.add_argument("--no-shuffle", action="store_true", help="Disable shuffling")
    ap.add_argument("--pass", dest="pass_mark", type=int, default=70, help="Pass mark percent (default 70)")
    ap.add_argument("--review", choices=["all", "missed", "none"], default="missed", help="Review mode")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    qs = bank()

    if len(qs) != 40:
        print(f"ERROR: Bank must be exactly 40 questions, found {len(qs)}.")
        return 2

    # Shuffle questions and choices unless disabled
    if not args.no_shuffle:
        rng.shuffle(qs)
        qs = [shuffle_question(q, rng) for q in qs]

    print("\nLPIC Essentials — 40 Question Mock Exam (v2)\n")
    print("Answer each question A–D. Type Q to quit.\n")

    results: List[Dict] = []
    for i, q in enumerate(qs, start=1):
        print("=" * 72)
        print(f"Q{i}/40  |  Topic {q.topic}  |  ID {q.qid}")
        print(q.prompt)
        print("-" * 72)
        for j, opt in enumerate(q.options):
            print(f"  {LETTERS[j]}. {opt}")

        ans = get_answer()
        if ans == "Q":
            print("\nExiting early. Scoring completed questions...\n")
            break

        chosen = LETTERS.index(ans)
        correct = q.correct
        is_correct = chosen == correct

        results.append({
            "qid": q.qid,
            "topic": q.topic,
            "prompt": q.prompt,
            "options": q.options,
            "chosen": chosen,
            "correct": correct,
            "is_correct": is_correct,
            "explanation": q.explanation,
        })

    # Score
    answered = len(results)
    correct_count = sum(1 for r in results if r["is_correct"])
    pct = (correct_count / answered * 100) if answered else 0.0
    status = "PASS" if pct >= args.pass_mark else "FAIL"

    print("=" * 72)
    print("RESULTS")
    print("=" * 72)
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

        print("\n" + "=" * 72)
        print(title)
        print("=" * 72)

        if not review_items:
            print("No missed questions. Nice.")
        else:
            for r in review_items:
                print("\n" + "-" * 72)
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
