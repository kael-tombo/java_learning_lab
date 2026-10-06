# VISION — Lab 19: Java Architect Decision Framework

> From "we chose Kafka" to "here is why, here is what we gave up, and here is the condition that would change our mind."

---

## The Arc

1. **The ADR itself** — structure, immutability, statuses, and the decision the record must contain.
2. **Context and forces** — what the future reader needs to know to judge whether the decision still applies.
3. **Alternatives and consequences** — including the negative ones, which are the most useful part.
4. **Revisit triggers** — turning a decree into a conditional decision.
5. **Evaluating options** — TCO, expected loss, opportunity cost, and why people time dominates.
6. **Uncertainty and reversibility** — two-way vs one-way doors, value of information, deciding interfaces early.
7. **Novelty budget** — where to spend it, and the quantified cost of being wrong.
8. **Process and governance** — the named decider, decided-or-deferred, and decision debt.
9. **Explaining decisions upward** — options, costs, expected values, and an explicit ask.
10. **Scale decisions** — boundaries, platform triggers, when a monolith is right.

---

## Why this lab exists

Architecture is a sequence of decisions, most of which are made implicitly: by whichever system existed, by whichever vendor recommended itself, by whoever was loudest. Years later, nobody can reconstruct the reasoning, so the decision cannot be revisited — only inherited.

The specific goal here: **you can write a decision record that a future team can use to decide whether the decision still holds, and you can evaluate options with the arithmetic that survives a budget conversation.**

---

## Milestones (checkable)

- [ ] M1: Write five ADRs for real pending decisions in your team, each with alternatives, negative consequences, and an observable revisit trigger.
- [ ] M2: Build a TCO comparison for one real technology choice, with people time, exit cost, and opportunity cost included.
- [ ] M3: Classify your platform's pending decisions as two-way or one-way doors, and produce a diligence plan proportionate to the door type.
- [ ] M4: Compute the expected annual loss and the TCO for two real options, and present the difference in *variance*, not just mean.
- [ ] M5: Write a business-facing decision memo for one real decision, with options, the "do nothing" option priced, an explicit ask, and an expected-value range.
- [ ] M6: Identify five decision debts in your system — decisions made implicitly — and convert three into ADRs.
- [ ] M7: Establish ADR governance (a numbered index, a required template, a trigger-check at each planning cycle) and get it adopted.

---

## Anti-Goals

- ADRs with only benefits.
- ADRs with no alternatives, or with alternatives and no reasons.
- Editing an accepted ADR instead of superseding it.
- "We should revisit this if it doesn't work out" as a trigger.
- Technology preferences presented as engineering recommendations.
- Deciding one-way doors in a week and two-way doors in a quarter.
- Building a platform for one team.
- "Build vs buy" argued on technical merit alone.

---

## Interview Lens

- "Tell me about an architecture decision you got wrong. How did you find out it was wrong?"
- "How do you evaluate a technology choice?"
- "What does a good ADR look like?"
- "How do you know when to revisit a decision?"
- "How do you explain an architecture decision to a non-technical executive?"

---

## 30-Day Plan

- **Week 1** — THEORY + `ARCHITECTURAL_FITNESS_METRICS`: ADR structure, TCO, expected loss, reversibility; hands-on writing ADRs for a real repo. M1–M2.
- **Week 2** — EXERCISES: TCO, opportunity cost, EVPI, debt interest, platform break-even; QUIZ to 13/15; FLASHCARDS daily. M3–M4.
- **Week 3** — MINI_PROJECT: run the full decision process on one real decision, from options to ADR to business memo. M5–M6.
- **Week 4** — REAL_WORLD_PROJECT war story; establish ADR governance for a real team; teach-back: "our decisions and their triggers, defended" in 10 minutes.

---

## Artifacts you should be able to show

1. Five ADRs, each with negative consequences and an observable revisit trigger.
2. A TCO comparison for a real choice, with the people-time and exit-cost terms explicit.
3. A two-way/one-way door classification of pending decisions with a diligence plan.
4. A business decision memo with an explicit ask and an expected-value range.
5. An ADR index and a governance proposal that a team actually adopted.

---

## Done = You Can

- Write a decision record a stranger can use to judge whether the decision still applies.
- Compare two options with TCO and expected loss rather than preference.
- Classify a decision by reversibility and size the diligence accordingly.
- Present a decision upward in terms of money and risk, with a specific ask.
