#!/usr/bin/env python3
"""
LPIC Essentials — Topic 1.1 Simulation (Linux Community & Careers)

What this is:
- A scenario-based simulation (not just multiple choice).
- You play through "mini-missions" that reflect Topic 1.1 objectives:
  * Open source vs proprietary thinking
  * Licensing awareness (high-level)
  * Distributions & release models (LTS vs rolling)
  * Community roles and contribution flow
  * Career mapping (sysadmin/devops/cloud/security/dev)

Scoring:
- You earn points per decision.
- End report shows:
  * Readiness score
  * Missed concepts
  * Suggested review targets

Run:
  python3 lpic_essentials_topic_1_1_sim.py

Options:
  --seed 123         Deterministic scenario randomization
  --short            Short run (fewer missions)
"""

from __future__ import annotations

import argparse
import random
import textwrap
from dataclasses import dataclass
from typing import List, Dict, Callable, Tuple


WRAP = 78


def w(text: str) -> str:
    return "\n".join(textwrap.wrap(text, width=WRAP))


def hr() -> None:
    print("\n" + "=" * WRAP)


def prompt_choice(options: List[str]) -> int:
    """Return index 0..n-1"""
    while True:
        print()
        for i, opt in enumerate(options, start=1):
            print(f"  {i}) {opt}")
        raw = input("\nChoose an option (number), or Q to quit: ").strip().lower()
        if raw in ("q", "quit", "exit"):
            raise SystemExit(0)
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return idx
        print("Invalid choice. Enter a valid number.")


@dataclass
class Outcome:
    points: int
    concept_tags: List[str]
    feedback: str


@dataclass
class Mission:
    id: str
    title: str
    scenario: str
    options: List[str]
    evaluate: Callable[[int], Outcome]


class Topic11Simulator:
    def __init__(self, rng: random.Random, short: bool = False):
        self.rng = rng
        self.short = short
        self.score = 0
        self.max_score = 0
        self.missed: Dict[str, int] = {}          # concept -> misses
        self.covered: Dict[str, int] = {}         # concept -> hits
        self.history: List[Tuple[str, int, Outcome]] = []

    def tag_hit(self, tag: str) -> None:
        self.covered[tag] = self.covered.get(tag, 0) + 1

    def tag_miss(self, tag: str) -> None:
        self.missed[tag] = self.missed.get(tag, 0) + 1

    def run_mission(self, m: Mission) -> None:
        hr()
        print(f"{m.title}  [{m.id}]")
        print("-" * WRAP)
        print(w(m.scenario))

        idx = prompt_choice(m.options)
        outcome = m.evaluate(idx)

        # bookkeeping
        self.score += outcome.points
        self.max_score += 5  # normalize: each mission is out of 5 points

        # tag tracking: treat points>=4 as "hit", <=2 as "miss", else neutral
        for t in outcome.concept_tags:
            if outcome.points >= 4:
                self.tag_hit(t)
            elif outcome.points <= 2:
                self.tag_miss(t)

        self.history.append((m.id, idx, outcome))

        print("\n" + "-" * WRAP)
        print(w(outcome.feedback))
        print(f"\nPoints earned: {outcome.points}/5")

    def report(self) -> None:
        hr()
        pct = (self.score / self.max_score * 100) if self.max_score else 0.0
        print("TOPIC 1.1 SIMULATION REPORT")
        print("-" * WRAP)
        print(f"Score: {self.score}/{self.max_score}  ({pct:.1f}%)")

        if pct >= 85:
            level = "Exam-ready for Topic 1.1"
        elif pct >= 70:
            level = "Close — review weak spots"
        else:
            level = "Needs more Topic 1.1 reps"

        print(f"Readiness: {level}")

        # missed concept summary
        if self.missed:
            print("\nConcepts to review (most missed first):")
            for tag, n in sorted(self.missed.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {tag} (missed {n}x)")
        else:
            print("\nNo major weak concepts detected in this run.")

        # suggestions
        suggestions = self._suggestions()
        if suggestions:
            print("\nTargeted next steps:")
            for s in suggestions:
                print(f"  • {s}")

        print("\nTip: rerun with --seed N to benchmark improvement consistently.")
        hr()

    def _suggestions(self) -> List[str]:
        s: List[str] = []
        if self.missed.get("license-obligations", 0) > 0:
            s.append("Review: high-level license obligations (especially redistribution vs internal use).")
        if self.missed.get("distro-vs-kernel", 0) > 0:
            s.append("Review: Linux kernel vs distribution (kernel + userland + package ecosystem).")
        if self.missed.get("lts-vs-rolling", 0) > 0:
            s.append("Review: LTS vs rolling release tradeoffs (stability vs newest features).")
        if self.missed.get("community-roles", 0) > 0:
            s.append("Review: how communities contribute (code, packaging, docs, triage, governance).")
        if self.missed.get("career-mapping", 0) > 0:
            s.append("Review: which Linux skills map to sysadmin/devops/cloud/security roles.")
        return s


# ------------------------ Missions (Topic 1.1) ------------------------ #

def missions_pool() -> List[Mission]:
    # Each mission is scored 0..5 (internally normalized by report)
    return [
        Mission(
            id="1.1-A",
            title="Mission 1: Open Source vs Proprietary Decision",
            scenario=(
                "You’re advising a small startup. They need a web server stack fast. "
                "The CEO asks: “Why would we choose open-source software instead of proprietary?” "
                "Pick the BEST answer."
            ),
            options=[
                "Because open-source is always free and never needs updates",
                "Because open-source allows transparency, customization, and avoids vendor lock-in (license-dependent)",
                "Because open-source cannot be used commercially",
                "Because proprietary software is illegal on servers",
            ],
            evaluate=lambda c: Outcome(
                points=[0, 5, 0, 0][c],
                concept_tags=["open-source-benefits"],
                feedback=[
                    "Not quite. Open-source still needs updates and isn’t always ‘free of cost’.",
                    "Correct. Open-source commonly offers transparency, flexibility, and can reduce lock-in (license terms matter).",
                    "Incorrect. Open-source is commonly used commercially.",
                    "Incorrect. Proprietary software is legal; it’s just different licensing and tradeoffs.",
                ][c],
            ),
        ),
        Mission(
            id="1.1-B",
            title="Mission 2: License Obligations (High-Level)",
            scenario=(
                "A company modifies an open-source component and uses it only internally. "
                "They do NOT distribute it outside the company. The team asks: “Do we have to publish our changes?” "
                "Choose the MOST accurate Essentials-level answer."
            ),
            options=[
                "Yes—open-source always requires publishing any modification immediately",
                "It depends on the license and whether you distribute; many obligations are triggered by redistribution",
                "No—licenses never have obligations",
                "Yes—but only if you used Linux",
            ],
            evaluate=lambda c: Outcome(
                points=[1, 5, 0, 0][c],
                concept_tags=["license-obligations"],
                feedback=[
                    "Too absolute. Some licenses do require sharing under conditions, but not always for internal-only use.",
                    "Correct. At Essentials level: obligations depend on the license and distribution/redistribution conditions.",
                    "Incorrect. Licenses define obligations; they absolutely can require conditions.",
                    "Incorrect. This is about licensing terms, not simply ‘using Linux’.",
                ][c],
            ),
        ),
        Mission(
            id="1.1-C",
            title="Mission 3: Kernel vs Distribution",
            scenario=(
                "A teammate says: “We installed Linux—so we installed the kernel and nothing else.” "
                "Pick the BEST correction."
            ),
            options=[
                "Correct—Linux means only the kernel; everything else is unrelated",
                "Not quite—a usable system is usually a distribution: kernel + user-space tools/libraries/apps",
                "Linux means Windows Subsystem for Linux",
                "Linux means a desktop environment like GNOME",
            ],
            evaluate=lambda c: Outcome(
                points=[0, 5, 0, 0][c],
                concept_tags=["distro-vs-kernel"],
                feedback=[
                    "Incorrect. Most real installs are full distributions, not just a kernel.",
                    "Correct. Distros bundle the kernel with user-space components to create a usable OS.",
                    "Incorrect. WSL is a Windows feature; not the definition of Linux.",
                    "Incorrect. A desktop environment is only one part of a distro.",
                ][c],
            ),
        ),
        Mission(
            id="1.1-D",
            title="Mission 4: Release Model Choice (LTS vs Rolling)",
            scenario=(
                "You’re choosing a distro for a small business file server. "
                "The business values stability, predictable updates, and long support windows. Best choice?"
            ),
            options=[
                "Rolling release (latest versions constantly)",
                "LTS/stable release model",
                "Any distro with the newest desktop UI",
                "A distro with no updates",
            ],
            evaluate=lambda c: Outcome(
                points=[1, 5, 0, 0][c],
                concept_tags=["lts-vs-rolling"],
                feedback=[
                    "Rolling can be great, but it’s not usually the best fit for stability-first business servers.",
                    "Correct. LTS/stable releases emphasize predictability and long support—great for servers.",
                    "UI choice isn’t the priority here; stability and support are.",
                    "No updates is unsafe; security patches matter.",
                ][c],
            ),
        ),
        Mission(
            id="1.1-E",
            title="Mission 5: Community Roles & Contribution Flow",
            scenario=(
                "You want to contribute to an open-source Linux tool but you’re not ready to write code. "
                "Which contribution is MOST valuable and realistic?"
            ),
            options=[
                "Testing and reporting bugs clearly with reproducible steps",
                "Refusing to file issues until paid",
                "Keeping fixes private forever",
                "Only posting complaints without details",
            ],
            evaluate=lambda c: Outcome(
                points=[5, 0, 0, 0][c],
                concept_tags=["community-roles"],
                feedback=[
                    "Correct. High-quality bug reports and testing help projects a lot and are very common contributions.",
                    "Not helpful. Open-source contribution is usually volunteer/community-driven, though companies may sponsor work.",
                    "Not ideal. Keeping fixes private doesn’t help the community maintain and improve the tool.",
                    "Low value. Issues without detail are hard to act on.",
                ][c],
            ),
        ),
        Mission(
            id="1.1-F",
            title="Mission 6: Career Mapping",
            scenario=(
                "You enjoy automation, pipelines, infrastructure-as-code, and deploying services reliably. "
                "Which role BEST matches that focus?"
            ),
            options=[
                "DevOps / Cloud Engineer",
                "Graphic Designer",
                "Data Entry Specialist",
                "Retail Cashier",
            ],
            evaluate=lambda c: Outcome(
                points=[5, 0, 1, 0][c],
                concept_tags=["career-mapping"],
                feedback=[
                    "Correct. DevOps/Cloud roles heavily involve automation, pipelines, and infrastructure reliability.",
                    "Not the best match for the described interests.",
                    "Not the best match; this role is typically not infrastructure-focused.",
                    "Not the best match for the described responsibilities.",
                ][c],
            ),
        ),
        Mission(
            id="1.1-G",
            title="Mission 7: Why Linux Dominates Servers/Cloud",
            scenario=(
                "Pick the BEST explanation for why Linux is so common in servers and cloud environments."
            ),
            options=[
                "Linux is the only OS that can run on servers",
                "Linux is stable, efficient, scriptable, and supported broadly across cloud + server ecosystems",
                "Linux requires no security updates",
                "Linux is mostly used for gaming desktops",
            ],
            evaluate=lambda c: Outcome(
                points=[0, 5, 0, 0][c],
                concept_tags=["linux-in-infrastructure"],
                feedback=[
                    "Incorrect. Other OSes can run servers; Linux is common due to its strengths and ecosystem.",
                    "Correct. Those strengths + tooling ecosystem make Linux a default in cloud/server operations.",
                    "Incorrect. Linux absolutely needs security updates.",
                    "Incorrect. Gaming isn’t the main driver for Linux’s server/cloud dominance.",
                ][c],
            ),
        ),
        Mission(
            id="1.1-H",
            title="Mission 8: Vendor Lock-in Thinking",
            scenario=(
                "Your team is worried about vendor lock-in. Which choice BEST reduces lock-in risk?"
            ),
            options=[
                "Use a single vendor’s proprietary tooling everywhere with no export options",
                "Choose open standards and portable tooling; document builds and deployments",
                "Avoid documentation to stay flexible",
                "Never update systems so nothing changes",
            ],
            evaluate=lambda c: Outcome(
                points=[0, 5, 0, 0][c],
                concept_tags=["open-standards"],
                feedback=[
                    "That usually increases lock-in risk.",
                    "Correct. Open standards + portable tooling + documentation are the practical anti-lock-in play.",
                    "No—lack of documentation creates internal lock-in and risk.",
                    "No—freezing updates is a security and reliability risk.",
                ][c],
            ),
        ),
    ]


def build_run_list(rng: random.Random, short: bool) -> List[Mission]:
    pool = missions_pool()
    rng.shuffle(pool)
    if short:
        # Short run = 5 missions
        return pool[:5]
    # Full run = 8 missions (fits Topic 1.1 well)
    return pool[:8]


# ------------------------------- main ------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser(description="LPIC Essentials Topic 1.1 — Simulation App")
    ap.add_argument("--seed", type=int, default=None, help="Deterministic scenario order")
    ap.add_argument("--short", action="store_true", help="Short run (fewer missions)")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    sim = Topic11Simulator(rng=rng, short=args.short)

    hr()
    print("LPIC Essentials — Topic 1.1 Simulation")
    print("-" * WRAP)
    print(w(
        "You’ll play through scenario missions aligned to Topic 1.1 (Linux Community & Careers). "
        "Choose the BEST answer like the real exam. After each mission you’ll get feedback."
    ))
    hr()

    run_list = build_run_list(rng, args.short)
    for m in run_list:
        sim.run_mission(m)

    sim.report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
