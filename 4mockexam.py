#!/usr/bin/env python3
"""
LPIC Essentials — 60 Question Mock Exam (v4 EXAM-DAY)

Goal:
- Most accurate "exam-day" style for LPIC Essentials (Topics 1.1–1.5)
- 60 questions total, more realistic distractors, "best answer" wording
- Shuffle questions + options (grade-safe)
- Topic breakdown + review (missed/all/none)
- Optional timer + JSON export

Run:
  python3 lpic_essentials_mock_exam_v4_60.py

Common options:
  --seed 123
  --no-shuffle
  --pass 75
  --review missed|all|none
  --time 45              # minutes (soft limit; warns when exceeded)
  --export results.json
"""

from __future__ import annotations

import argparse
import json
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Tuple, Any


LETTERS = ("A", "B", "C", "D")


@dataclass(frozen=True)
class Question:
    qid: int
    topic: str  # 1.1..1.5
    prompt: str
    options: Tuple[str, str, str, str]
    correct: int  # 0..3
    explanation: str


# ------------------------- Question Bank (60) ------------------------- #
def bank() -> List[Question]:
    """
    Exactly 60 questions.
    Topic distribution (balanced for exam-day coverage):
      1.1: 12
      1.2: 12
      1.3: 12
      1.4: 14
      1.5: 10
    Total = 60
    """
    return [
        # ========================= Topic 1.1 (12) =========================
        Question(1, "1.1",
                 "Which statement BEST describes open-source software?",
                 (
                     "Software that is always free of charge and cannot be sold",
                     "Software whose source code is available under a license allowing use, modification, and redistribution",
                     "Software that runs only on Linux operating systems",
                     "Software developed only by volunteers, never companies",
                 ),
                 1,
                 "Open-source is defined by source availability + license rights to use/modify/redistribute."),
        Question(2, "1.1",
                 "A key reason open-source software can be considered more trustworthy is:",
                 (
                     "It cannot contain vulnerabilities",
                     "Its code can be reviewed publicly, enabling transparency and peer review",
                     "It never requires updates",
                     "It is always written by security experts only",
                 ),
                 1,
                 "Transparency enables auditing and faster discovery of issues."),
        Question(3, "1.1",
                 "Which is the BEST description of a Linux distribution (distro)?",
                 (
                     "The Linux kernel only",
                     "A packaged operating system: kernel + tools/libraries/apps + a package manager and defaults",
                     "A graphical interface such as GNOME",
                     "A license that controls how Linux is used",
                 ),
                 1,
                 "A distro bundles kernel and user-space into a usable OS."),
        Question(4, "1.1",
                 "Which environment MOST commonly relies on Linux in production?",
                 (
                     "Cloud and server infrastructure",
                     "Only desktop gaming PCs",
                     "Only single-user personal laptops",
                     "Only proprietary embedded systems",
                 ),
                 0,
                 "Linux dominates servers/cloud due to stability, automation, cost, and ecosystem support."),
        Question(5, "1.1",
                 "What does LTS (Long-Term Support) primarily emphasize?",
                 (
                     "Newest features as fast as possible, even if compatibility breaks",
                     "Stability and extended security updates over a longer support window",
                     "No updates at all",
                     "Only running container workloads",
                 ),
                 1,
                 "LTS prioritizes stability and long support."),
        Question(6, "1.1",
                 "Which sequence is MOST sensible for a beginner moving deeper into Linux certs?",
                 (
                     "LPIC-2 → LPIC-1 → LPIC Essentials",
                     "LPIC Essentials → LPIC-1 → LPIC-2",
                     "LPIC-3 → LPIC Essentials → LPIC-1",
                     "Skip fundamentals and start directly with kernel development",
                 ),
                 1,
                 "Essentials builds foundations; LPIC-1 is operational; LPIC-2 is advanced admin."),
        Question(7, "1.1",
                 "Which statement BEST matches the role of the Linux community?",
                 (
                     "Only one company controls all Linux development",
                     "Community members contribute code, documentation, testing, packaging, and support",
                     "Linux is closed source so community cannot contribute",
                     "Community contribution is limited to reporting bugs only",
                 ),
                 1,
                 "Linux is developed by a wide ecosystem of contributors."),
        Question(8, "1.1",
                 "Why are Linux certifications often valuable to employers?",
                 (
                     "They guarantee job performance without experience",
                     "They provide a standardized signal of validated knowledge and commitment",
                     "They replace the need for interviews",
                     "They are only relevant to hobbyists",
                 ),
                 1,
                 "Certs are a signal—not a guarantee—of validated baseline skills."),
        Question(9, "1.1",
                 "A common advantage of open-source licensing for organizations is:",
                 (
                     "Mandatory per-device activation fees",
                     "Flexibility to audit, customize, and deploy widely depending on license terms",
                     "Inability to use software commercially",
                     "Prohibition of internal modifications",
                 ),
                 1,
                 "Open-source licenses often enable broad customization and deployment (with conditions)."),
        Question(10, "1.1",
                 "Which job task MOST strongly suggests Linux skills are required?",
                 (
                     "Managing CI/CD pipelines and containerized services in production",
                     "Designing a flyer in a photo editor",
                     "Planning a wedding venue layout",
                     "Editing a restaurant menu in a word processor",
                 ),
                 0,
                 "DevOps/cloud/container work commonly uses Linux."),
        Question(11, "1.1",
                 "What is the BEST high-level reason Linux is common in embedded systems?",
                 (
                     "Linux requires a full desktop GUI",
                     "Linux is lightweight, configurable, and can be tailored to specific hardware",
                     "Linux only runs on x86 desktops",
                     "Linux cannot be modified for custom devices",
                 ),
                 1,
                 "Linux can be stripped down and customized for embedded devices."),
        Question(12, "1.1",
                 "Which statement BEST describes LPIC Essentials?",
                 (
                     "A vendor-specific certification for one Linux distro",
                     "A foundational certification focused on Linux and open-source concepts and basic usage",
                     "An advanced certification covering kernel internals and driver development",
                     "A certification focused only on programming languages",
                 ),
                 1,
                 "Essentials is a fundamentals/literacy certification."),

        # ========================= Topic 1.2 (12) =========================
        Question(13, "1.2",
                 "Which directory is the top of the Linux filesystem hierarchy?",
                 ("/root", "/home", "/", "/etc"),
                 2,
                 "The filesystem root is '/'."),
        Question(14, "1.2",
                 "Which directory MOST commonly contains system-wide configuration files?",
                 ("/etc", "/var", "/bin", "/home"),
                 0,
                 "/etc holds system configuration."),
        Question(15, "1.2",
                 "Which directory MOST commonly contains log files?",
                 ("/var/log", "/etc/log", "/bin/log", "/home/log"),
                 0,
                 "Logs are typically stored in /var/log."),
        Question(16, "1.2",
                 "Which path is an absolute path?",
                 ("../notes.txt", "./notes.txt", "notes.txt", "/etc/hosts"),
                 3,
                 "Absolute paths start with '/'."),
        Question(17, "1.2",
                 "A user is in /home/cannon/projects and runs `cd ..` twice. Where are they now?",
                 ("/home/cannon", "/home", "/", "/home/cannon/projects/.."),
                 1,
                 "/home/cannon/projects → /home/cannon → /home."),
        Question(18, "1.2",
                 "What does '.' represent in a path?",
                 ("The root directory", "The current directory", "The parent directory", "The home directory"),
                 1,
                 ". refers to the current directory."),
        Question(19, "1.2",
                 "What does '..' represent in a path?",
                 ("The root directory", "The current directory", "The parent directory", "The /etc directory"),
                 2,
                 ".. refers to the parent directory."),
        Question(20, "1.2",
                 "Hidden files are typically identified by:",
                 ("A trailing dash (-) in the filename", "A leading dot (.) in the filename", "Being stored in /var", "Always being executable"),
                 1,
                 "Dotfiles (e.g., .bashrc) are hidden by default in many tools."),
        Question(21, "1.2",
                 "Which directory MOST commonly contains user home directories?",
                 ("/usr", "/home", "/var", "/bin"),
                 1,
                 "/home contains user folders like /home/alex."),
        Question(22, "1.2",
                 "Which directory is MOST associated with variable data that changes frequently (logs, cache, spool)?",
                 ("/etc", "/var", "/bin", "/lib"),
                 1,
                 "/var stores variable runtime data."),
        Question(23, "1.2",
                 "The phrase “everything is a file” MOST accurately means:",
                 (
                     "All files are plain text",
                     "Many devices and system information are exposed via file-like interfaces (e.g., /dev, /proc)",
                     "Files cannot have permissions",
                     "Only root can access files",
                 ),
                 1,
                 "Linux exposes many resources as files for consistent access patterns."),
        Question(24, "1.2",
                 "Which directory MOST commonly contains essential user commands (binaries)?",
                 ("/bin", "/home", "/var/log", "/etc"),
                 0,
                 "/bin commonly contains essential commands (layout varies by distro; concept remains)."),

        # ========================= Topic 1.3 (12) =========================
        Question(25, "1.3",
                 "Which operator redirects standard output to a file, overwriting the file if it exists?",
                 ("|", ">", ">>", "<"),
                 1,
                 "> redirects stdout to a file and overwrites/creates it."),
        Question(26, "1.3",
                 "Which operator appends standard output to a file?",
                 (">", ">>", "|", "&&"),
                 1,
                 ">> appends stdout to a file."),
        Question(27, "1.3",
                 "What does the pipe operator '|' do?",
                 (
                     "Sends output of one command as input to another",
                     "Writes command output directly to a file",
                     "Runs a command with root privileges",
                     "Changes the current directory",
                 ),
                 0,
                 "Pipes connect stdout of one command to stdin of the next."),
        Question(28, "1.3",
                 "Which command prints your current working directory?",
                 ("pwd", "cd", "ls", "whoami"),
                 0,
                 "pwd prints the current directory."),
        Question(29, "1.3",
                 "Which command is used to change directories?",
                 ("pwd", "cd", "ls", "cat"),
                 1,
                 "cd changes the current working directory."),
        Question(30, "1.3",
                 "Which command creates a directory named labs?",
                 ("touch labs", "mkdir labs", "rm labs", "cat labs"),
                 1,
                 "mkdir creates directories."),
        Question(31, "1.3",
                 "Which command is MOST appropriate to view a long text file one screen at a time?",
                 ("less", "rm", "mv", "mkdir"),
                 0,
                 "less is a pager for browsing output."),
        Question(32, "1.3",
                 "Which command copies file a.txt to b.txt?",
                 ("mv a.txt b.txt", "cp a.txt b.txt", "rm a.txt b.txt", "mkdir a.txt b.txt"),
                 1,
                 "cp copies; mv moves/renames."),
        Question(33, "1.3",
                 "Which command typically creates an empty file (or updates its timestamp)?",
                 ("touch report.txt", "mkdir report.txt", "cd report.txt", "ps report.txt"),
                 0,
                 "touch creates empty files or updates timestamps."),
        Question(34, "1.3",
                 "Which statement BEST describes the difference between a terminal and a shell?",
                 (
                     "They are the same thing",
                     "A terminal is the interface; a shell interprets and executes commands",
                     "A shell is hardware; a terminal is software",
                     "A terminal manages packages; a shell manages users",
                 ),
                 1,
                 "Terminal provides access; shell is the command interpreter."),
        Question(35, "1.3",
                 "Why is the command line especially valuable for system administration?",
                 (
                     "It prevents all mistakes",
                     "It enables automation, repeatability, and efficient remote administration (e.g., SSH)",
                     "It is required to install any software",
                     "It only works on desktops",
                 ),
                 1,
                 "CLI is scriptable and efficient, especially remotely."),
        Question(36, "1.3",
                 "What is standard output (stdout)?",
                 (
                     "The default stream where most command output is sent (usually the terminal)",
                     "A directory that stores logs",
                     "A Linux distribution component",
                     "A file permission mode",
                 ),
                 0,
                 "stdout is the default output stream for many commands."),

        # ========================= Topic 1.4 (14) =========================
        Question(37, "1.4",
                 "Which BEST describes the Linux kernel?",
                 (
                     "A desktop environment",
                     "The core component that manages hardware resources and process scheduling",
                     "A collection of office applications",
                     "A package repository",
                 ),
                 1,
                 "Kernel manages CPU/memory/devices/process scheduling."),
        Question(38, "1.4",
                 "Which statement BEST describes user space vs kernel space?",
                 (
                     "User space runs apps; kernel space runs privileged OS functions",
                     "User space is only for root; kernel space is for regular users",
                     "Kernel space is where files live; user space is where directories live",
                     "There is no difference on Linux",
                 ),
                 0,
                 "Apps run in user space; kernel space handles privileged operations."),
        Question(39, "1.4",
                 "A process is:",
                 ("A file on disk", "A running instance of a program", "A software repository", "A user group"),
                 1,
                 "A running program instance is a process."),
        Question(40, "1.4",
                 "PID stands for:",
                 ("Permission Identifier", "Process Identifier", "Package Install Directory", "Program Internal Data"),
                 1,
                 "PID uniquely identifies a process."),
        Question(41, "1.4",
                 "Linux is described as multi-user because:",
                 (
                     "Only one user can log in at a time",
                     "Multiple accounts can exist with separate permissions and concurrent sessions",
                     "Users cannot share system resources",
                     "Only root can create files",
                 ),
                 1,
                 "Multi-user systems support many accounts and permission separation."),
        Question(42, "1.4",
                 "What is the primary purpose of a package manager?",
                 (
                     "To manage user passwords",
                     "To install, update, and remove software packages while handling dependencies",
                     "To configure network routing tables",
                     "To replace the kernel",
                 ),
                 1,
                 "Package managers handle software lifecycle + dependencies."),
        Question(43, "1.4",
                 "A software repository is BEST described as:",
                 (
                     "A place where the kernel stores processes",
                     "A collection of packages and metadata that a package manager can download/install",
                     "A folder where users keep documents",
                     "A device driver type",
                 ),
                 1,
                 "Repos are sources of packages for the package manager."),
        Question(44, "1.4",
                 "A dependency is:",
                 (
                     "A group of users",
                     "A required component/library another program needs to run",
                     "A directory under /home",
                     "A network interface",
                 ),
                 1,
                 "Dependencies are required libraries/components."),
        Question(45, "1.4",
                 "Why do Linux systems receive frequent updates?",
                 (
                     "To remove security features",
                     "To patch vulnerabilities, fix bugs, and improve stability/features",
                     "To force users to reinstall the OS",
                     "Because Linux cannot run without updates every day",
                 ),
                 1,
                 "Updates patch vulnerabilities and improve reliability."),
        Question(46, "1.4",
                 "RAM is BEST described as:",
                 (
                     "Permanent storage for files and programs",
                     "Temporary working memory for running processes and active data",
                     "A network protocol",
                     "A package repository",
                 ),
                 1,
                 "RAM holds active data for running programs."),
        Question(47, "1.4",
                 "Swap space is:",
                 (
                     "Faster than RAM and used first",
                     "Disk-backed memory used when RAM is under pressure; typically slower than RAM",
                     "A directory under /etc",
                     "A user account",
                 ),
                 1,
                 "Swap extends memory using disk; slower than RAM."),
        Question(48, "1.4",
                 "Which BEST distinguishes containers from virtual machines?",
                 (
                     "Containers share the host kernel; VMs typically run full guest OS stacks",
                     "Containers require a full guest OS; VMs share the host kernel",
                     "Containers cannot isolate processes",
                     "VMs cannot be used in cloud environments",
                 ),
                 0,
                 "Containers share host kernel; VMs include full guest OS."),
        Question(49, "1.4",
                 "Which statement about `ps` vs `top` is MOST accurate?",
                 (
                     "`ps` is real-time; `top` is a one-time snapshot",
                     "`top` provides a live-ish view; `ps` shows a snapshot at execution time",
                     "Both only show disk usage",
                     "Both only show installed packages",
                 ),
                 1,
                 "top refreshes; ps is a snapshot."),
        Question(50, "1.4",
                 "Why is Linux often chosen for servers?",
                 (
                     "Because it requires a GUI to manage",
                     "Because it is stable, secure, efficient, and automation-friendly",
                     "Because it cannot be customized",
                     "Because it only supports one user",
                 ),
                 1,
                 "Linux is well suited for server workloads and automation."),

        # ========================= Topic 1.5 (10) =========================
        Question(51, "1.5",
                 "The principle of least privilege means:",
                 (
                     "Users should have admin access by default",
                     "Users should have only the permissions necessary to perform their tasks",
                     "All files should be writable by everyone",
                     "Root should be used for daily work",
                 ),
                 1,
                 "Least privilege reduces risk from mistakes and compromise."),
        Question(52, "1.5",
                 "Who is the root user?",
                 (
                     "A normal user with limited permissions",
                     "The superuser with full administrative privileges",
                     "A user who can only read system files",
                     "A guest account",
                 ),
                 1,
                 "Root can perform any action on the system."),
        Question(53, "1.5",
                 "Why is logging in as root for daily tasks discouraged?",
                 (
                     "Root cannot install software",
                     "Mistakes or malware can cause maximum damage when running with full privileges",
                     "Root cannot access /home",
                     "Root accounts cannot use the network",
                 ),
                 1,
                 "Running as root increases impact of errors or compromise."),
        Question(54, "1.5",
                 "What does `sudo` do?",
                 (
                     "Permanently converts a user into root",
                     "Allows an authorized user to run a command with elevated privileges",
                     "Encrypts a user’s home directory",
                     "Disables the firewall",
                 ),
                 1,
                 "sudo provides controlled privilege escalation for permitted users."),
        Question(55, "1.5",
                 "In `-rwxr-xr--`, the permissions are interpreted as:",
                 (
                     "Owner: rwx, Group: r-x, Others: r--",
                     "Owner: r--, Group: rwx, Others: r-x",
                     "Owner: r-x, Group: r--, Others: rwx",
                     "Everyone: rwx",
                 ),
                 0,
                 "Triplets are owner/group/others."),
        Question(56, "1.5",
                 "Read (r) permission on a file allows:",
                 ("Viewing the file contents", "Executing the file", "Changing file ownership", "Deleting any file in the directory"),
                 0,
                 "Read permission allows reading the file’s contents."),
        Question(57, "1.5",
                 "Write (w) permission on a file allows:",
                 ("Executing the file", "Modifying the file contents", "Only viewing file contents", "Changing kernel settings"),
                 1,
                 "Write permission allows changing file content."),
        Question(58, "1.5",
                 "Execute (x) permission on a file allows:",
                 ("Viewing the file contents", "Running the file as a program/script (if valid)", "Changing file ownership", "Moving the file only"),
                 1,
                 "Execute permission allows running the file as a program/script."),
        Question(59, "1.5",
                 "Why are regular updates considered part of security hygiene?",
                 (
                     "They always remove vulnerabilities permanently",
                     "They patch known vulnerabilities and fix bugs that attackers may exploit",
                     "They eliminate the need for permissions",
                     "They prevent all phishing attacks",
                 ),
                 1,
                 "Updates patch known issues; permissions still matter."),
        Question(60, "1.5",
                 "Conceptually, what does a firewall do?",
                 (
                     "Manages file ownership and permissions",
                     "Filters network traffic based on allow/deny rules",
                     "Installs packages from repositories",
                     "Creates user accounts automatically",
                 ),
                 1,
                 "Firewalls control network connections according to rules."),
    ]


# ------------------------- Helpers ------------------------- #
def shuffle_options(q: Question, rng: random.Random) -> Question:
    order = list(range(4))
    rng.shuffle(order)
    new_opts = tuple(q.options[i] for i in order)
    new_correct = order.index(q.correct)
    return Question(q.qid, q.topic, q.prompt, new_opts, new_correct, q.explanation)


def read_answer() -> str:
    while True:
        ans = input("Your answer (A/B/C/D) or Q to quit: ").strip().upper()
        if ans in ("Q", "QUIT", "EXIT"):
            return "Q"
        if ans in LETTERS:
            return ans
        print("Please enter A, B, C, D, or Q.")


def topic_breakdown(results: List[Dict[str, Any]]) -> Tuple[Dict[str, int], Dict[str, int]]:
    totals: Dict[str, int] = {}
    corrects: Dict[str, int] = {}
    for r in results:
        t = r["topic"]
        totals[t] = totals.get(t, 0) + 1
        corrects[t] = corrects.get(t, 0) + (1 if r["is_correct"] else 0)
    return totals, corrects


def export_json(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


# ------------------------- Main ------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="LPIC Essentials — 60Q Mock Exam (v4 EXAM-DAY)")
    ap.add_argument("--seed", type=int, default=None, help="Deterministic shuffle seed")
    ap.add_argument("--no-shuffle", action="store_true", help="Disable question/option shuffling")
    ap.add_argument("--pass", dest="pass_mark", type=int, default=75, help="Pass mark percent (default 75)")
    ap.add_argument("--review", choices=["missed", "all", "none"], default="missed", help="Review mode")
    ap.add_argument("--time", type=int, default=None, help="Soft time limit in minutes (warn when exceeded)")
    ap.add_argument("--export", type=str, default=None, help="Export results to JSON file")
    args = ap.parse_args()

    rng = random.Random(args.seed)

    qs = bank()
    if len(qs) != 60:
        print(f"ERROR: Bank must be exactly 60 questions, found {len(qs)}.")
        return 2

    if not args.no_shuffle:
        rng.shuffle(qs)
        qs = [shuffle_options(q, rng) for q in qs]

    print("\nLPIC Essentials — 60 Question Mock Exam (v4 EXAM-DAY)\n")
    print("Instructions: Choose the BEST answer (A–D). Type Q to quit.\n")
    if args.time:
        print(f"Time limit (soft): {args.time} minutes. You will be warned if you exceed it.\n")

    start = time.time()
    results: List[Dict[str, Any]] = []

    for i, q in enumerate(qs, start=1):
        elapsed_min = (time.time() - start) / 60.0
        if args.time and elapsed_min > args.time:
            print("\n⚠️  Time warning: You have exceeded the time limit.\n")
            # Only warn once
            args.time = None

        print("=" * 78)
        print(f"Q{i}/60  |  Topic {q.topic}  |  ID {q.qid}")
        print(q.prompt)
        print("-" * 78)
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

    print("=" * 78)
    print("RESULTS")
    print("=" * 78)
    print(f"Answered: {answered}/60")
    print(f"Correct : {correct_count}")
    print(f"Score   : {pct:.1f}%")
    print(f"Status  : {status} (Pass mark: {args.pass_mark}%)")

    totals, corrects = topic_breakdown(results)
    print("\nBy Topic:")
    for t in sorted(totals.keys()):
        tt = totals[t]
        cc = corrects[t]
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

        print("\n" + "=" * 78)
        print(title)
        print("=" * 78)

        if not review_items:
            print("No items to review. Nice.")
        else:
            for r in review_items:
                print("\n" + "-" * 78)
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

    # Export
    if args.export:
        payload = {
            "exam": "LPIC Essentials Mock Exam v4 (60Q Exam-Day)",
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "seed": args.seed,
            "shuffled": (not args.no_shuffle),
            "pass_mark": args.pass_mark,
            "answered": answered,
            "correct": correct_count,
            "score_percent": round(pct, 1),
            "status": status,
            "topic_totals": totals,
            "topic_correct": corrects,
            "results": results,
        }
        export_json(args.export, payload)
        print(f"\nExported results to: {args.export}")

    print("\nDone.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
