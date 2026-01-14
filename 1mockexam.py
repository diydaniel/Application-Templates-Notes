#!/usr/bin/env python3
"""
LPIC Essentials — 40 Question Mock Exam (CLI)

Features:
- 40 multiple-choice questions (A–D)
- Shuffle questions and answer choices (grading remains correct)
- Score report + pass/fail
- Review mode with explanations
- Optional JSON export

Run:
  python3 lpic_essentials_mock_exam.py
Options:
  --no-shuffle           Do not shuffle questions
  --seed 123             Deterministic shuffle
  --pass 70              Pass mark percentage (default 70)
  --no-review            Skip end review
  --export results.json  Export results to JSON
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Tuple


@dataclass
class MCQ:
    id: str
    topic: str  # 1.1 - 1.5
    question: str
    choices: List[str]          # exactly 4
    correct_index: int          # 0..3
    explanation: str


def build_exam_bank() -> List[MCQ]:
    # 40 questions spanning Topics 1.1–1.5 (balanced-ish)
    return [
        # --- Topic 1.1 (Community & Careers) ---
        MCQ(
            id="1",
            topic="1.1",
            question="Which best describes open-source software?",
            choices=[
                "Software whose source code is publicly available under a license allowing use, modification, and redistribution",
                "Software that is free of charge but cannot be modified",
                "Software owned by a single vendor with no user access to code",
                "Software that only runs on Linux",
            ],
            correct_index=0,
            explanation="Open-source means the source code is available and rights are granted via a license to use/modify/redistribute."
        ),
        MCQ(
            id="2",
            topic="1.1",
            question="A major benefit of community-driven development is:",
            choices=[
                "Only one company decides the roadmap",
                "Faster innovation through many contributors and transparent review",
                "Software never needs security updates",
                "Users cannot report bugs directly",
            ],
            correct_index=1,
            explanation="Community contribution and transparent review often increases pace and quality."
        ),
        MCQ(
            id="3",
            topic="1.1",
            question="What is a Linux distribution (distro)?",
            choices=[
                "Only the Linux kernel",
                "A packaged OS: Linux kernel + tools, libraries, and applications",
                "A GUI desktop environment only",
                "A proprietary operating system based on UNIX",
            ],
            correct_index=1,
            explanation="A distro bundles the kernel with user-space components to form a usable OS."
        ),
        MCQ(
            id="4",
            topic="1.1",
            question="Which role most commonly requires Linux skills?",
            choices=[
                "Linux/Cloud/DevOps engineer",
                "Graphic designer",
                "Cashier",
                "Architectural drafter",
            ],
            correct_index=0,
            explanation="Linux is central in infrastructure roles (sysadmin, DevOps, cloud, security)."
        ),
        MCQ(
            id="5",
            topic="1.1",
            question="What does an LTS release prioritize?",
            choices=[
                "Frequent breaking changes",
                "Long-term stability and extended security updates",
                "Only gaming performance",
                "Disabling updates entirely",
            ],
            correct_index=1,
            explanation="LTS = long support window, stable platform, extended patches."
        ),
        MCQ(
            id="6",
            topic="1.1",
            question="How does LPIC Essentials differ from LPIC-1?",
            choices=[
                "Essentials is more advanced than LPIC-1",
                "Essentials focuses on foundational concepts; LPIC-1 is more operational/task-focused",
                "Essentials is only about programming",
                "LPIC-1 has no command line content",
            ],
            correct_index=1,
            explanation="Essentials = intro literacy; LPIC-1 = hands-on admin skills."
        ),

        # --- Topic 1.2 (Finding Your Way) ---
        MCQ(
            id="7",
            topic="1.2",
            question="What is the root directory in Linux?",
            choices=[
                "/root",
                "/home",
                "/",
                "/etc",
            ],
            correct_index=2,
            explanation="The filesystem root is '/'. Do not confuse with '/root' (root user’s home)."
        ),
        MCQ(
            id="8",
            topic="1.2",
            question="Which directory typically contains system configuration files?",
            choices=[
                "/etc",
                "/var",
                "/tmp",
                "/home",
            ],
            correct_index=0,
            explanation="/etc holds system-wide configuration."
        ),
        MCQ(
            id="9",
            topic="1.2",
            question="Which directory commonly contains log files?",
            choices=[
                "/bin",
                "/var/log",
                "/etc",
                "/home",
            ],
            correct_index=1,
            explanation="Logs are usually stored under /var/log."
        ),
        MCQ(
            id="10",
            topic="1.2",
            question="What is the difference between an absolute and relative path?",
            choices=[
                "Absolute starts with '/', relative depends on the current directory",
                "Absolute depends on the current directory, relative always starts with '/'",
                "Relative paths can only be used by root",
                "Absolute paths cannot reference files",
            ],
            correct_index=0,
            explanation="Absolute paths start from '/', relative paths start from the current working directory."
        ),
        MCQ(
            id="11",
            topic="1.2",
            question="In Linux, files starting with a dot (.) are usually:",
            choices=[
                "Executable-only",
                "Hidden files",
                "System logs",
                "Invalid filenames",
            ],
            correct_index=1,
            explanation="Dotfiles are hidden by default in many directory listings."
        ),
        MCQ(
            id="12",
            topic="1.2",
            question="What does '..' represent in paths?",
            choices=[
                "Current directory",
                "Home directory",
                "Parent directory",
                "Root directory",
            ],
            correct_index=2,
            explanation=".. means “one level up” (the parent directory)."
        ),
        MCQ(
            id="13",
            topic="1.2",
            question="The phrase 'everything is a file' in Linux means:",
            choices=[
                "Linux only supports text files",
                "Devices and system resources are often represented as files (e.g., in /dev, /proc)",
                "Files cannot be deleted",
                "Only root can create files",
            ],
            correct_index=1,
            explanation="Linux exposes many resources via file-like interfaces."
        ),

        # --- Topic 1.3 (Command Line Power) ---
        MCQ(
            id="14",
            topic="1.3",
            question="What is a shell?",
            choices=[
                "A spreadsheet program",
                "A program that interprets and executes commands",
                "A file compression format",
                "A hardware component",
            ],
            correct_index=1,
            explanation="The shell is the command interpreter (e.g., bash, zsh)."
        ),
        MCQ(
            id="15",
            topic="1.3",
            question="What does the pipe '|' do?",
            choices=[
                "Sends output of one command as input to another",
                "Writes output to a file",
                "Deletes files permanently",
                "Changes directory",
            ],
            correct_index=0,
            explanation="Pipes chain commands by passing stdout to stdin."
        ),
        MCQ(
            id="16",
            topic="1.3",
            question="What does redirection with '>' do?",
            choices=[
                "Appends output to a file",
                "Overwrites a file with command output (or creates it)",
                "Pipes output to another command",
                "Makes a file executable",
            ],
            correct_index=1,
            explanation="> redirects stdout to a file, replacing contents."
        ),
        MCQ(
            id="17",
            topic="1.3",
            question="Which command shows your current directory?",
            choices=[
                "pwd",
                "whoami",
                "ps",
                "cat",
            ],
            correct_index=0,
            explanation="pwd prints the working directory."
        ),
        MCQ(
            id="18",
            topic="1.3",
            question="What does 'mv' commonly do?",
            choices=[
                "Copy files",
                "Move or rename files/directories",
                "Show system logs",
                "List processes",
            ],
            correct_index=1,
            explanation="mv moves and renames."
        ),
        MCQ(
            id="19",
            topic="1.3",
            question="Why is tab completion useful?",
            choices=[
                "It encrypts files",
                "It speeds typing and reduces command/path typos",
                "It installs packages automatically",
                "It restarts services",
            ],
            correct_index=1,
            explanation="Tab completion helps you avoid errors and work faster."
        ),
        MCQ(
            id="20",
            topic="1.3",
            question="What does 'less' do?",
            choices=[
                "Edits a file",
                "Views text one screen/page at a time",
                "Deletes files",
                "Lists hardware devices",
            ],
            correct_index=1,
            explanation="less is a pager to view long text."
        ),
        MCQ(
            id="21",
            topic="1.3",
            question="Why do administrators often prefer CLI over GUI on servers?",
            choices=[
                "CLI cannot be used remotely",
                "CLI is typically faster, scriptable, and works well over SSH",
                "GUI is always more secure",
                "CLI uses more memory than GUI",
            ],
            correct_index=1,
            explanation="CLI supports automation and remote admin with low overhead."
        ),

        # --- Topic 1.4 (Linux Operating System) ---
        MCQ(
            id="22",
            topic="1.4",
            question="What is the Linux kernel responsible for?",
            choices=[
                "Only user documents",
                "Managing hardware resources like CPU, memory, devices, and process scheduling",
                "Providing a web browser",
                "Writing source code for applications",
            ],
            correct_index=1,
            explanation="Kernel = core resource manager and hardware abstraction."
        ),
        MCQ(
            id="23",
            topic="1.4",
            question="What is a process?",
            choices=[
                "A compressed archive",
                "A running instance of a program",
                "A Linux distribution",
                "A file permission",
            ],
            correct_index=1,
            explanation="Program on disk becomes a process when running."
        ),
        MCQ(
            id="24",
            topic="1.4",
            question="What is a PID?",
            choices=[
                "A package install directory",
                "A process identifier",
                "A permission indicator",
                "A network protocol",
            ],
            correct_index=1,
            explanation="PID uniquely identifies a running process."
        ),
        MCQ(
            id="25",
            topic="1.4",
            question="What does it mean that Linux is multi-user?",
            choices=[
                "Only one user can log in at a time",
                "Multiple user accounts can exist and use the system with separate permissions",
                "Only root can create users",
                "Users cannot share files",
            ],
            correct_index=1,
            explanation="Multi-user means multiple accounts with permission separation."
        ),
        MCQ(
            id="26",
            topic="1.4",
            question="What is a package manager?",
            choices=[
                "A tool to install, remove, and update software packages",
                "A GUI theme manager",
                "A hardware driver",
                "A firewall",
            ],
            correct_index=0,
            explanation="Package managers handle software installation and dependencies."
        ),
        MCQ(
            id="27",
            topic="1.4",
            question="What is a software repository?",
            choices=[
                "A temporary folder for downloads",
                "A central collection of packages that a package manager can install from",
                "A kernel module",
                "A text editor",
            ],
            correct_index=1,
            explanation="Repos host packages and metadata for installation."
        ),
        MCQ(
            id="28",
            topic="1.4",
            question="What is a dependency in software packaging?",
            choices=[
                "A user account",
                "A required component/library that another package needs to run",
                "A filesystem permission",
                "A CPU feature",
            ],
            correct_index=1,
            explanation="Dependencies are required libraries/components."
        ),
        MCQ(
            id="29",
            topic="1.4",
            question="What is RAM used for?",
            choices=[
                "Storing long-term backups",
                "Temporary storage for running programs and active data",
                "Encrypting network traffic",
                "Only storing the kernel source code",
            ],
            correct_index=1,
            explanation="RAM holds active data and running processes."
        ),
        MCQ(
            id="30",
            topic="1.4",
            question="What is swap space?",
            choices=[
                "A separate CPU",
                "Disk space used to extend memory when RAM is under pressure",
                "A user directory",
                "A kernel module",
            ],
            correct_index=1,
            explanation="Swap is disk-backed memory used when RAM is insufficient."
        ),
        MCQ(
            id="31",
            topic="1.4",
            question="What is virtualization?",
            choices=[
                "Running multiple virtual machines on one physical host",
                "Disabling system updates",
                "Converting GUI apps to CLI apps",
                "A type of file permission",
            ],
            correct_index=0,
            explanation="Virtualization allows multiple OS instances to run on one machine."
        ),
        MCQ(
            id="32",
            topic="1.4",
            question="Which best distinguishes containers from virtual machines?",
            choices=[
                "Containers always run Windows",
                "VMs share one kernel; containers include full OS kernels",
                "Containers share the host kernel; VMs typically include a full guest OS",
                "Containers cannot be used in cloud environments",
            ],
            correct_index=2,
            explanation="Containers share the host kernel; VMs run full guest OS stacks."
        ),
        MCQ(
            id="33",
            topic="1.4",
            question="Why does Linux dominate many cloud platforms?",
            choices=[
                "Because Linux cannot be customized",
                "Because Linux is efficient, stable, widely supported, and licensing-friendly",
                "Because Linux requires paid activation keys",
                "Because Linux cannot run on servers",
            ],
            correct_index=1,
            explanation="Linux aligns well with cloud scale, cost, and automation."
        ),
        MCQ(
            id="34",
            topic="1.4",
            question="What does 'ps' generally show?",
            choices=[
                "Disk usage",
                "A snapshot list of running processes",
                "Network routes",
                "Kernel version only",
            ],
            correct_index=1,
            explanation="ps lists processes (snapshot, not live like top)."
        ),
        MCQ(
            id="35",
            topic="1.4",
            question="What does 'top' generally show?",
            choices=[
                "Real-time view of processes and resource usage",
                "Only directory contents",
                "Only kernel configuration",
                "Only installed packages",
            ],
            correct_index=0,
            explanation="top shows CPU/memory usage by processes in near real time."
        ),
        MCQ(
            id="36",
            topic="1.4",
            question="What does it mean for a system to be stable?",
            choices=[
                "It never updates",
                "It operates reliably and predictably over time",
                "It can only run one application",
                "It does not use permissions",
            ],
            correct_index=1,
            explanation="Stability = reliable, predictable operation."
        ),
        MCQ(
            id="37",
            topic="1.4",
            question="What is scalability (in a Linux context)?",
            choices=[
                "The ability to grow and handle more workload by adding resources or nodes",
                "The ability to avoid updates",
                "The ability to run only on laptops",
                "The ability to remove user accounts quickly",
            ],
            correct_index=0,
            explanation="Scalability means growing capacity as demand increases."
        ),
        MCQ(
            id="38",
            topic="1.4",
            question="Why is Linux common in embedded systems?",
            choices=[
                "Linux is always larger than other OSes",
                "Linux can be lightweight and customized for specific hardware",
                "Linux requires a GUI",
                "Linux only runs on desktops",
            ],
            correct_index=1,
            explanation="Linux is configurable, efficient, and works well on many devices."
        ),

        # --- Topic 1.5 (Security & Permissions) ---
        MCQ(
            id="39",
            topic="1.5",
            question="What is the principle of least privilege?",
            choices=[
                "Users should have the highest access possible",
                "Users should have only the permissions necessary to do their tasks",
                "Only root should log in",
                "Files should always be world-writable",
            ],
            correct_index=1,
            explanation="Least privilege limits damage from mistakes and compromise."
        ),
        MCQ(
            id="40",
            topic="1.5",
            question="Who is the root user?",
            choices=[
                "A normal user with limited permissions",
                "The superuser with full administrative privileges",
                "A user that can only read files",
                "A guest account",
            ],
            correct_index=1,
            explanation="Root has unrestricted control over the system."
        ),
        MCQ(
            id="41",
            topic="1.5",
            question="Why should root usage be limited?",
            choices=[
                "Root cannot run commands",
                "Root can cause major damage if misused, accidentally or maliciously",
                "Root passwords are optional",
                "Root cannot access system files",
            ],
            correct_index=1,
            explanation="Root can change anything; limit use and use sudo where possible."
        ),
        MCQ(
            id="42",
            topic="1.5",
            question="What does sudo do?",
            choices=[
                "Deletes a user",
                "Allows a permitted user to run a command with elevated privileges",
                "Encrypts files automatically",
                "Disables the firewall",
            ],
            correct_index=1,
            explanation="sudo performs controlled privilege escalation."
        ),
        MCQ(
            id="43",
            topic="1.5",
            question="In permissions like -rwxr-xr--, what do the first three bits after the dash refer to?",
            choices=[
                "Group permissions",
                "Owner (user) permissions",
                "Other (world) permissions",
                "File size permissions",
            ],
            correct_index=1,
            explanation="Permission triplets are: owner, group, others."
        ),
        MCQ(
            id="44",
            topic="1.5",
            question="What does read (r) permission on a file allow?",
            choices=[
                "Running the file as a program",
                "Viewing the file contents",
                "Deleting the file always",
                "Changing ownership",
            ],
            correct_index=1,
            explanation="Read permission allows reading file content."
        ),
        MCQ(
            id="45",
            topic="1.5",
            question="What does write (w) permission on a file allow?",
            choices=[
                "Viewing file contents only",
                "Modifying the file contents",
                "Executing the file",
                "Changing the kernel",
            ],
            correct_index=1,
            explanation="Write permission allows editing/overwriting the file."
        ),
        MCQ(
            id="46",
            topic="1.5",
            question="What does execute (x) permission on a file allow?",
            choices=[
                "Editing the file",
                "Running the file as a program (or script if valid)",
                "Changing the file name only",
                "Reading system logs",
            ],
            correct_index=1,
            explanation="Execute allows running the file (as a program/script)."
        ),
        MCQ(
            id="47",
            topic="1.5",
            question="Why are updates part of security?",
            choices=[
                "Updates always remove security features",
                "Updates patch known vulnerabilities and bugs",
                "Updates disable permissions",
                "Updates prevent all attacks permanently",
            ],
            correct_index=1,
            explanation="Patching fixes known issues; it’s a key security practice."
        ),
        MCQ(
            id="48",
            topic="1.5",
            question="Conceptually, what does a firewall do?",
            choices=[
                "Stores user passwords",
                "Filters network traffic based on rules",
                "Overclocks the CPU",
                "Creates backups automatically",
            ],
            correct_index=1,
            explanation="Firewalls control allowed/blocked network connections."
        ),

        # --- Mixed “exam style” comprehension questions (still tied to topics) ---
        MCQ(
            id="49",
            topic="1.2",
            question="Which path is an absolute path?",
            choices=[
                "Documents/report.txt",
                "../report.txt",
                "/home/user/report.txt",
                "./report.txt",
            ],
            correct_index=2,
            explanation="Absolute paths start with '/'."
        ),
        MCQ(
            id="50",
            topic="1.2",
            question="Which directory most likely contains user-specific personal files?",
            choices=[
                "/etc",
                "/var",
                "/home",
                "/bin",
            ],
            correct_index=2,
            explanation="/home contains user home directories."
        ),
        MCQ(
            id="51",
            topic="1.3",
            question="Which command would you use to create a directory named 'labs'?",
            choices=[
                "touch labs",
                "mkdir labs",
                "rm labs",
                "cat labs",
            ],
            correct_index=1,
            explanation="mkdir creates directories."
        ),
        MCQ(
            id="52",
            topic="1.3",
            question="What is standard output (stdout)?",
            choices=[
                "The default stream where most command output is sent (usually the terminal)",
                "A special file inside /etc",
                "A user account",
                "The network interface name",
            ],
            correct_index=0,
            explanation="stdout is the default output stream."
        ),
        MCQ(
            id="53",
            topic="1.4",
            question="When you start a program, it becomes:",
            choices=[
                "A directory",
                "A process",
                "A package manager",
                "A repository",
            ],
            correct_index=1,
            explanation="A running program instance is a process."
        ),
        MCQ(
            id="54",
            topic="1.5",
            question="Which is the best reason to use groups for permissions?",
            choices=[
                "Groups make files smaller",
                "Groups simplify managing access for multiple users",
                "Groups disable sudo",
                "Groups replace the kernel",
            ],
            correct_index=1,
            explanation="Groups let you manage permissions for sets of users efficiently."
        ),

        # Add 40 exactly: We currently have 54 MCQs. Need exactly 40 for mock exam.
        # The app will use the first 40 by default (or user can set count).
    ]


def normalize_bank_to_40(bank: List[MCQ]) -> List[MCQ]:
    # Keep exactly 40 questions for the mock exam.
    if len(bank) < 40:
        raise ValueError(f"Question bank has only {len(bank)} questions; needs at least 40.")
    return bank[:40]


def shuffle_choices(mcq: MCQ, rng: random.Random) -> Tuple[List[str], int]:
    indexed = list(enumerate(mcq.choices))
    rng.shuffle(indexed)
    new_choices = [c for _, c in indexed]
    new_correct = [i for i, (old_idx, _) in enumerate(indexed) if old_idx == mcq.correct_index][0]
    return new_choices, new_correct


def ask_question(
    qnum: int,
    total: int,
    mcq: MCQ,
    rng: random.Random,
    shuffle_ans: bool = True
) -> Dict[str, Any]:
    choices, correct_index = (mcq.choices, mcq.correct_index)
    if shuffle_ans:
        choices, correct_index = shuffle_choices(mcq, rng)

    letters = ["A", "B", "C", "D"]
    print("\n" + "=" * 72)
    print(f"Question {qnum}/{total}  |  Topic {mcq.topic}  |  ID {mcq.id}")
    print(mcq.question.strip())
    print("-" * 72)
    for i, ch in enumerate(choices):
        print(f"  {letters[i]}. {ch}")

    while True:
        ans = input("\nYour answer (A/B/C/D or Q to quit): ").strip().upper()
        if ans in ("Q", "QUIT", "EXIT"):
            return {"quit": True}
        if ans in letters:
            chosen_index = letters.index(ans)
            correct_letter = letters[correct_index]
            chosen_letter = letters[chosen_index]
            is_correct = chosen_index == correct_index
            return {
                "quit": False,
                "topic": mcq.topic,
                "id": mcq.id,
                "question": mcq.question,
                "choices": choices,
                "correct_index": correct_index,
                "correct_letter": correct_letter,
                "chosen_index": chosen_index,
                "chosen_letter": chosen_letter,
                "is_correct": is_correct,
                "explanation": mcq.explanation,
            }
        print("Please enter A, B, C, D — or Q to quit.")


def print_summary(results: List[Dict[str, Any]], pass_mark: int) -> None:
    answered = [r for r in results if not r.get("quit")]
    correct = sum(1 for r in answered if r["is_correct"])
    total = len(answered)
    pct = (correct / total * 100) if total else 0.0
    status = "PASS" if pct >= pass_mark else "FAIL"

    print("\n" + "=" * 72)
    print("RESULTS")
    print("=" * 72)
    print(f"Answered: {total}/40")
    print(f"Correct : {correct}")
    print(f"Score   : {pct:.1f}%")
    print(f"Status  : {status} (Pass mark: {pass_mark}%)")

    # Topic breakdown
    topic_totals: Dict[str, int] = {}
    topic_correct: Dict[str, int] = {}
    for r in answered:
        t = r["topic"]
        topic_totals[t] = topic_totals.get(t, 0) + 1
        topic_correct[t] = topic_correct.get(t, 0) + (1 if r["is_correct"] else 0)

    print("\nBy Topic:")
    for t in sorted(topic_totals.keys()):
        ct = topic_correct[t]
        tt = topic_totals[t]
        tp = (ct / tt * 100) if tt else 0.0
        print(f"  Topic {t}: {ct}/{tt} ({tp:.1f}%)")
    print("=" * 72)


def print_review(results: List[Dict[str, Any]]) -> None:
    answered = [r for r in results if not r.get("quit")]
    missed = [r for r in answered if not r["is_correct"]]

    print("\n" + "=" * 72)
    print("REVIEW")
    print("=" * 72)
    if not missed:
        print("You got everything correct. Nice.")
        return

    letters = ["A", "B", "C", "D"]
    for r in missed:
        print("\n" + "-" * 72)
        print(f"Topic {r['topic']} | ID {r['id']}")
        print(r["question"])
        print("Choices:")
        for i, ch in enumerate(r["choices"]):
            marker = ""
            if i == r["correct_index"]:
                marker = "  <-- correct"
            if i == r["chosen_index"]:
                marker = (marker + "  <-- your choice").strip()
                marker = "  <-- your choice" if marker == "" else marker
            print(f"  {letters[i]}. {ch}{marker}")
        print(f"Explanation: {r['explanation']}")
    print("\n" + "=" * 72)


def export_json(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="LPIC Essentials — 40 Question Mock Exam (CLI)")
    parser.add_argument("--no-shuffle", action="store_true", help="Do not shuffle questions")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for deterministic shuffling")
    parser.add_argument("--pass", dest="pass_mark", type=int, default=70, help="Pass mark percentage (default 70)")
    parser.add_argument("--no-review", action="store_true", help="Skip end-of-exam review")
    parser.add_argument("--export", type=str, default=None, help="Export results to JSON file")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    bank = normalize_bank_to_40(build_exam_bank())

    if not args.no_shuffle:
        rng.shuffle(bank)

    results: List[Dict[str, Any]] = []
    print("\nLPIC Essentials — 40 Question Mock Exam")
    print("Enter A/B/C/D for each question. Enter Q to quit.\n")

    for i, mcq in enumerate(bank, start=1):
        r = ask_question(i, 40, mcq, rng, shuffle_ans=not args.no_shuffle)
        if r.get("quit"):
            print("\nYou quit the exam early. Scoring what you've completed...")
            break
        results.append(r)

    # If user quit on a question, it returns quit=True without adding an answered record.
    # That's fine: we score answered ones.
    print_summary(results, args.pass_mark)

    if not args.no_review:
        print_review(results)

    if args.export:
        answered = [r for r in results if not r.get("quit")]
        correct = sum(1 for r in answered if r["is_correct"])
        payload = {
            "exam": "LPIC Essentials Mock Exam",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "pass_mark": args.pass_mark,
            "answered": len(answered),
            "correct": correct,
            "score_percent": round((correct / len(answered) * 100), 1) if answered else 0.0,
            "results": answered,
        }
        export_json(args.export, payload)
        print(f"\nExported results to: {args.export}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
