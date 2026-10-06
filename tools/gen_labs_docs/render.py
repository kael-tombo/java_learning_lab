"""Renderer for ML / MLOps / Statistics lab companion docs.

Generates THEORY.md, EXERCISES.md, QUIZ.md, FLASHCARDS.md,
MATH_FOUNDATION.md, CODE_DEEP_DIVE.md, VISION.md, MINI_PROJECT.md and
REAL_WORLD_PROJECT.md from a per-lab spec dict.

Rule: never overwrite an existing file.
"""

import os

ROOT = r"C:\Users\jratombo-adm\Desktop\java_learning_lab\labs"

SEP = "\n---\n\n"


def write_missing(path, content):
    if os.path.exists(path):
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = content.rstrip("\n") + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return True


def banner(title, track, lab, level):
    return [
        "# " + title,
        "",
        "**Track:** " + track + "  |  **Lab:** " + lab + "  |  **Level:** " + level,
        "",
        "> Companion notes to the runnable lab. Everything here is grounded in the "
        "source under `src/`, so a claim you cannot reproduce is a claim you do not ship.",
        "",
        "| Doc | Read it when you want |",
        "|---|---|",
        "| `THEORY.md` | the mental model and the assumptions |",
        "| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |",
        "| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |",
        "| `EXERCISES.md` | deliberate practice, one deliverable at a time |",
        "| `QUIZ.md` | to find the gaps before an interview |",
        "| `FLASHCARDS.md` | spaced repetition on the day before a review |",
        "| `VISION.md` | the career-level context and the anti-patterns to avoid |",
        "| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |",
        "| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |",
    ]


# --------------------------------------------------------------------------
# THEORY.md
# --------------------------------------------------------------------------

def theory(s):
    L = list(banner(s["title"], s["track"], s["lab"], s.get("level", "Intermediate")))
    L += ["", "## 1. The Problem This Solves", "", s["problem"], "",
          s.get("why_now") or (
              "It matters because every downstream claim \u2014 a feature decision, an "
              "experiment conclusion, a capacity forecast \u2014 inherits whatever this "
              "step got wrong or got right.")]

    L += ["", "## 2. Learning Objectives", ""]
    L += ["- " + o for o in s["objectives"]]

    L += ["", "## 3. Core Concepts", ""]
    for i, (name, body) in enumerate(s["concepts"], 1):
        L += ["### 3." + str(i) + " " + name, "", body, ""]

    L += ["## 4. Key Equations at a Glance", "",
          "| Symbol | Name | Meaning |", "|---|---|---|"]
    for sym, name, meaning in s["formulas"]:
        L.append("| `" + sym + "` | " + name + " | " + meaning + " |")

    L += ["", "## 5. How the Pieces Fit Together", ""]
    for i, step in enumerate(s["flow"], 1):
        L += [str(i) + ". " + step, ""]

    L += ["## 6. Assumptions and Invariants", ""]
    L += ["- " + a for a in s["assumptions"]]

    L += ["", "## 7. Failure Modes You Will Meet in Production", "",
          "| Symptom | Root cause | Fix |", "|---|---|---|"]
    for sym, cause, fix in s["pitfalls"]:
        L.append("| " + sym + " | " + cause + " | " + fix + " |")

    L += ["", "## 8. Java Building Blocks", "",
          "| API / class | Why it earns its place here |", "|---|---|"]
    for api, why in s["java"]:
        L.append("| `" + api + "` | " + why + " |")

    L += ["", "## 9. Where This Sits in the Larger System", ""]
    L += ["- " + x for x in s["links"]]

    L += ["", "## 10. Self-Assessment Before You Ship Anything", "",
          "Score yourself 0-2 on each. Any zero below means you are not ready to "
          "operate this in production.", ""]
    for o in s["objectives"]:
        L.append("- [ ] 0 \u2014 cannot yet \u2014 " + o)
    L += ["", "## 11. Summary Checklist", ""]
    L += ["- [ ] " + c for c in s["checklist"]]
    return "\n".join(L)


# --------------------------------------------------------------------------
# EXERCISES.md
# --------------------------------------------------------------------------

def exercises(s):
    L = list(banner(s["title"] + " - Exercises", s["track"], s["lab"],
                    s.get("level", "Intermediate")))
    L += ["", "## How To Work These", "",
          "Work in order. Each exercise builds the next; do not skip ahead.",
          "Every exercise ends with a *deliverable* you can show someone - code that "
          "compiles, a number you can defend, or a table you can regenerate.",
          "",
          "Run the lab as you go:", "", "```bash",
          "cd " + s["lab"],
          "javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })",
          "java -cp out " + s["main_class"],
          "```", ""]

    for i, ex in enumerate(s["exercises"], 1):
        title, task, steps, deliverable = ex
        L += ["## Exercise " + str(i) + ": " + title, "",
              "**Task.** " + task, "", "**Steps**"]
        L += ["- " + st for st in steps]
        L += ["", "**Deliverable.** " + deliverable, ""]

    L += [SEP.rstrip("\n"), "", "## Self-Check Before You Move On", ""]
    L += ["- [ ] " + c for c in s["exercise_selfcheck"]]
    return "\n".join(L)


# --------------------------------------------------------------------------
# QUIZ.md
# --------------------------------------------------------------------------

def quiz(s):
    L = list(banner(s["title"] + " - Quiz (15 Questions)", s["track"], s["lab"],
                    s.get("level", "Intermediate")))
    L += ["", "**Instructions.** Answer all 15 questions before reading the bold "
          "answer lines. Multiple choice, one best answer. Target: 12/15 before "
          "you move on to the mini project.", ""]
    letters = "ABCDEFGHI"
    for i, q in enumerate(s["quiz"], 1):
        text, opts, ans, why = q
        L += ["### Q" + str(i) + ": " + text, ""]
        for j, o in enumerate(opts):
            L.append(letters[j] + ") " + o)
        L += ["", "**Answer: " + letters[ans] + "** - " + why, "", "---", ""]
    L += ["> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read "
          "THEORY.md sections 3 and 7, then retake."]
    return "\n".join(L)


# --------------------------------------------------------------------------
# FLASHCARDS.md
# --------------------------------------------------------------------------

def _cards_for(s):
    """Authored cards first, then derived cards until we hit the target."""
    out = []
    seen = set()

    def push(q, a):
        key = q.strip().lower()
        if key in seen:
            return
        seen.add(key)
        out.append((q, a))

    for q, a in s.get("cards", []):
        push(q, a)
    for name, body in s["concepts"]:
        push("What is " + name + "?", body.split(".")[0].strip() + ".")
    for sym, name, meaning in s["formulas"]:
        push("In this lab, what does `" + sym + "` mean?", name + ": " + meaning)
    for sym, cause, fix in s["pitfalls"]:
        push("You see '" + sym + "' in production. What is the cause and the fix?",
             cause + " Fix: " + fix)
    for api, why in s["java"]:
        push("Which Java API is the backbone of: " + why, "`" + api + "`")
    for name, body in s["concepts"]:
        first = body.split(".")[0].strip()
        push("Why does " + name + " matter operationally?", first + ".")
    for step in s["flow"][:6]:
        push("In the " + s["title"] + " pipeline, what happens next? " + step[:60] + "...",
             step)
    for ex in s["exercises"][:6]:
        push("Exercise focus: " + ex[0], ex[1])
    for head, formula, meaning, worked in s["math"]:
        push("State the " + head + " result for " + s["title"] + ".", worked)
    for extra_q, extra_a in s.get("extra_cards", []):
        push(extra_q, extra_a)
    for a in s["assumptions"]:
        push("Assumption / invariant to defend: " + a[:70] + "...", a)
    for api, why in s["java"]:
        push("Why is `" + api + "` used instead of a hand-rolled version?", why)

    target = s.get("card_target", 60)
    return out[:target]


def flashcards(s):
    cards = _cards_for(s)
    L = list(banner(s["title"] + " - Flashcards (" + str(len(cards)) + " cards)",
                    s["track"], s["lab"], s.get("level", "Intermediate")))
    L += ["", "**Format.** Question (front) -> answer (back). Use for spaced repetition: "
          "day 0, day 1, day 3, day 7, day 21. Do not read the answer first.", "",
          "| # | Front | Back |", "|---|---|---|"]
    for i, (q, a) in enumerate(cards, 1):
        q = q.replace("|", "\\|").replace("\n", " ")
        a = a.replace("|", "\\|").replace("\n", " ")
        L.append("| " + str(i) + " | " + q + " | " + a + " |")
    L += ["", "## Deck Notes", "",
          "- Rows are generated from this lab's own concepts, equations, failure modes "
          "and Java APIs - if you disagree with a card, fix the card.",
          "- The last block of cards is deliberately operational: they are the "
          "questions a staff engineer gets asked in a design review."]
    return "\n".join(L)


# --------------------------------------------------------------------------
# MATH_FOUNDATION.md
# --------------------------------------------------------------------------

def math_doc(s):
    L = list(banner(s["title"] + " - Mathematical Foundations", s["track"], s["lab"],
                    s.get("level", "Intermediate")))
    L += ["", "## Notation", "", "| Symbol | Meaning |", "|---|---|"]
    for sym, name, meaning in s["formulas"]:
        L.append("| `" + sym + "` | " + name + " - " + meaning + " |")

    L += ["", "## Why the Math Matters", "",
          s.get("math_why") or (
              "The formulas below are not decoration: each one is the place where a "
              "wrong assumption silently produces a plausible number. Knowing which "
              "formula applies, and when it stops applying, is the skill this lab "
              "builds."), ""]

    for i, (head, formula, meaning, worked) in enumerate(s["math"], 1):
        L += [SEP.rstrip("\n"), "", "## " + str(i) + ". " + head, "",
              "```text", formula, "```", "",
              meaning, "",
              "**Worked example.** " + worked, ""]

    L += [SEP.rstrip("\n"), "", "## Cheat Sheet", ""]
    for sym, name, _ in s["formulas"]:
        L.append("- `" + sym + "` - " + name)
    L += ["", "## Numerical Traps", ""]
    L += ["- " + t for t in s["math_traps"]]
    L += ["", "## Self-Check Problems", ""]
    L += [str(i) + ". " + p for i, p in enumerate(s["math_problems"], 1)]
    return "\n".join(L)


# --------------------------------------------------------------------------
# CODE_DEEP_DIVE.md
# --------------------------------------------------------------------------

def code_doc(s):
    L = list(banner(s["title"] + " - Code Deep Dive", s["track"], s["lab"],
                    s.get("level", "Intermediate")))
    L += ["", "## 1. Module Map", "", "```text", s["tree"], "```", "",
          s["tree_note"], ""]

    L += ["## 2. Core Types", "", "| Type | Responsibility |", "|---|---|"]
    for t, r in s["types"]:
        L.append("| `" + t + "` | " + r + " |")

    for i, (head, note, snippet) in enumerate(s["patterns"], 1):
        L += [SEP.rstrip("\n"), "", "## 3." + str(i) + " " + head, "", note, "",
              "```java", snippet.strip("\n"), "```", ""]

    L += [SEP.rstrip("\n"), "", "## 4. Cost Model", "",
          "| Operation | Complexity | Notes |", "|---|---|---|"]
    for op, cx, note in s["costs"]:
        L.append("| " + op + " | `" + cx + "` | " + note + " |")

    L += ["", "## 5. Correctness and Numerics", ""]
    L += ["- " + n for n in s["numerics"]]

    L += ["", "## 6. Test Strategy", ""]
    L += ["- " + t for t in s["tests"]]

    L += ["", "## 7. Extension Points", ""]
    L += ["- " + e for e in s["extensions"]]

    L += ["", "## 8. Review Checklist", ""]
    L += ["- [ ] " + c for c in s["code_checklist"]]
    return "\n".join(L)


# --------------------------------------------------------------------------
# VISION.md
# --------------------------------------------------------------------------

def vision(s):
    t = s["title"]
    v = s["vision"]
    L = list(banner(t + " - Vision & Where This Is Going", s["track"], s["lab"],
                    s.get("level", "Intermediate")))
    L += ["", "## 1. The Future State", "", v["future"], "",
          "The test of that future state is boring: a new engineer ships a change to "
          + t.lower() + " on day two without asking anyone where the magic lives.", ""]
    L += ["## 2. What \"Good\" Looks Like in Practice", ""]
    L += ["- " + g for g in v["good"]]
    L += ["", "## 3. Capability Ladder", "",
          "| Level | Capability | You can... |", "|---|---|---|"]
    for lvl, cap, can in v["ladder"]:
        L.append("| " + lvl + " | " + cap + " | " + can + " |")
    L += ["", "## 4. Behaviours to Build", "", v["behaviors"], ""]
    L += ["## 5. Anti-Vision (the failure mode we are avoiding)", ""]
    L += ["- " + a for a in v["anti"]]
    L += ["", "## 6. Technology Shifts That Change the Work", ""]
    L += ["1. " + x for x in v["trends"]]
    L += ["", "## 7. Your 30/60/90 Commitment", ""]
    L += ["- **30 days.** " + v["d30"]]
    L += ["- **60 days.** " + v["d60"]]
    L += ["- **90 days.** " + v["d90"]]
    L += ["", "## 8. How To Tell You Are Actually Getting Better", ""]
    L += ["- " + g for g in v["metrics"]]
    L += ["", "## 9. Principles That Should Not Change", ""]
    L += ["- **" + o.split(" and ")[0] + "** " + o for o in s["objectives"][:3]]
    L += ["", "> " + v["closer"]]
    return "\n".join(L)


# --------------------------------------------------------------------------
# MINI_PROJECT.md
# --------------------------------------------------------------------------

def mini(s):
    m = s["mini"]
    L = list(banner(m["name"], s["track"], s["lab"], s.get("level", "Intermediate")))
    L += ["", "**Brief.** " + m["brief"], "",
          "**Timebox.** " + m["timebox"], "", "## 1. Why This Project Exists", "",
          m["why"], "", "## 2. Requirements", ""]
    for r in m["requirements"]:
        L.append("- " + r)
    L += ["", "## 3. Build Order", "", "| Step | Time | What you do | Done when |",
          "|---|---|---|---|"]
    for st, tm, what, done in m["steps"]:
        L.append("| " + st + " | " + tm + " | " + what + " | " + done + " |")
    L += ["", "## 4. Architecture Sketch", "", "```text", m["diagram"], "```", ""]
    L += ["## 5. Implementation Notes", ""]
    L += ["- " + n for n in m["notes"]]
    L += ["", "## 6. Deliverables", ""]
    L += ["1. " + d for d in m["deliverables"]]
    L += ["", "## 7. Grading Rubric", "", "| Dimension | Weight | What earns full marks |",
          "|---|---|---|"]
    for dim, w, crit in m["grading"]:
        L.append("| " + dim + " | " + w + " | " + crit + " |")
    L += ["", "## 8. Stretch Goals", ""]
    L += ["- " + g for g in m["stretch"]]
    L += ["", "## 9. Definition of Done", "",
          "You are finished when every box below is checked, not when the code compiles.",
          ""]
    L += ["- [ ] " + r for r in m["requirements"][:6]]
    L += ["- [ ] A stranger can reproduce the reported numbers with one command",
          "- [ ] The limitations section says what this cannot do",
          "- [ ] At least one number is alerted on in production"]
    L += ["", "## 10. Retrospective Template", "",
          "- What worked:",
          "- What surprised me:",
          "- The one number I would alert on in production:",
          "- What I would delete before shipping this to real users:"]
    return "\n".join(L)


# --------------------------------------------------------------------------
# REAL_WORLD_PROJECT.md
# --------------------------------------------------------------------------

def real(s):
    r = s["real"]
    L = list(banner(r["name"], s["track"], s["lab"], s.get("level", "Intermediate")))
    L += ["", "## 1. Scenario", "", r["scenario"], "",
          "**You are the on-call engineer.** The system below is the one you inherit, "
          "not a greenfield toy - the interesting work is in the seams.", ""]
    L += ["## 2. Numbers That Matter", "", "| Quantity | Value |", "|---|---|"]
    for k, v in r["scale"]:
        L.append("| " + k + " | " + v + " |")
    L += ["", "## 3. Target Architecture", "", "```text", r["diagram"], "```", ""]
    L += ["## 4. Component Responsibilities", ""]
    for ci, (comp, desc) in enumerate(r["components"], 1):
        L += ["### 4." + str(ci) + " " + comp, ""]
        L += ["- " + d for d in desc]
        L.append("")
    L += ["## 5. Delivery Timeline", "", "| When | Milestone |", "|---|---|"]
    for when, what in r["timeline"]:
        L.append("| " + when + " | " + what + " |")
    L += ["", "## 6. Runbook (copy-paste)", "", "```bash"]
    L += r["runbook"]
    L += ["```", ""]
    L += ["## 7. Observability and SLOs", ""]
    L += ["- " + m for m in r["metrics"]]
    L += ["", "## 8. Failure Modes and the Rollback Plan", ""]
    L += ["| Failure | Detection | Response |", "|---|---|---|"]
    for f, d, resp in r["failures"]:
        L.append("| " + f + " | " + d + " | " + resp + " |")
    L += ["", "## 9. Prevention Backlog", ""]
    L += ["- " + p for p in r["backlog"]]
    L += ["", "## 10. Postmortem Outline (skeleton)", "",
          "1. **Impact** - who was hurt, for how long, in which numbers.",
          "2. **Timeline** - detection, diagnosis, mitigation, resolution (UTC).",
          "3. **Detection gap** - which signal should have fired first?",
          "4. **Root cause** - the mechanism, not the person.",
          "5. **What went well** - the thing that shortened the incident.",
          "6. **Action items** - owner, date, and the alert or test that proves each one."]
    L += ["", "## 11. Sourced field notes (fetched Oct 2026 \u2014 verify before citing)", ""]
    for label, url, note in r["urls"]:
        L += ["- **" + label + "**: " + url, "  " + note]
    L += ["", "> " + r["closer"]]
    return "\n".join(L)


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

FULL = ["THEORY.md", "EXERCISES.md", "QUIZ.md", "FLASHCARDS.md",
        "MATH_FOUNDATION.md", "CODE_DEEP_DIVE.md", "VISION.md",
        "MINI_PROJECT.md", "REAL_WORLD_PROJECT.md"]

CORE = ["THEORY.md", "MATH_FOUNDATION.md", "CODE_DEEP_DIVE.md", "VISION.md",
        "MINI_PROJECT.md", "REAL_WORLD_PROJECT.md"]

BUILDERS = {
    "THEORY.md": theory,
    "EXERCISES.md": exercises,
    "QUIZ.md": quiz,
    "FLASHCARDS.md": flashcards,
    "MATH_FOUNDATION.md": math_doc,
    "CODE_DEEP_DIVE.md": code_doc,
    "VISION.md": vision,
    "MINI_PROJECT.md": mini,
    "REAL_WORLD_PROJECT.md": real,
}


def emit(s):
    created, skipped = [], []
    folder = os.path.join(ROOT, s["track"], s["lab"])
    wanted = FULL if s.get("full_set", True) else CORE
    for name in wanted:
        path = os.path.join(folder, name)
        if write_missing(path, BUILDERS[name](s)):
            created.append(name)
        else:
            skipped.append(name)
    return created, skipped


def report(results):
    total_new = 0
    for spec, (created, skipped) in results:
        total_new += len(created)
        print("{0}/{1}: +{2} {3}".format(
            spec["track"], spec["lab"], len(created),
            ("kept " + ",".join(skipped)) if skipped else ""))
    print("TOTAL FILES CREATED: " + str(total_new))
