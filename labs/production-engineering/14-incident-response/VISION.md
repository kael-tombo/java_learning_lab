# VISION — Lab 14: Production Incident Response & RCA

> From "we fixed it" to "here is the class of failure, why the system allowed it, and what is now different."

---

## The Arc

1. **Declaration and command** — when to declare, who declares, roles, and the first five minutes.
2. **The timeline as the primary artefact** — timestamped facts, hypotheses with confidence, single clock.
3. **Diagnosis discipline** — recent changes, saturation, scope; one change at a time; hypothesis refutation.
4. **Mitigation before root cause** — reversible actions, load shedding, degrade over fail, fix-forward vs rollback.
5. **Communication** — scheduled cadence, "no change" updates, external vs internal register.
6. **Time decomposition** — MTTD/MTTA/MTTM/MTTR and which investment moves which.
7. **Blast radius arithmetic** — what an incident actually costs, computed so detection work can be funded.
8. **Blameless postmortems** — contributing factors over root cause, actions with owners and definition of done.
9. **Recurrence** — incident classes, completion rates, and the statistics of small samples.
10. **On-call and game days** — sustainable rotation, escalation ladders, and testing the system rather than understanding it.

---

## Why this lab exists

Incidents are the only events in a system's life that reliably produce organisational learning — and most of that learning is lost, because the timeline was never written, the review is skipped, and the actions are unowned.

The specific goal here: **you can run an incident from declaration to blameless postmortem with a timeline, roles, and a measured outcome — and you can prove, numerically, whether the actions actually reduced risk.**

---

## Milestones (checkable)

- [ ] M1: Run a full incident exercise (real, staged, or game day) with declared roles, a live timeline doc, and scheduled stakeholder updates.
- [ ] M2: Decompose one real incident's MTTR into phases and identify the dominant phase with the cheapest fix.
- [ ] M3: Write a blameless postmortem for a real or simulated incident with contributing factors, owned actions with definition-of-done, and a recurrence check.
- [ ] M4: Compute the expected-damage arithmetic for a bad release with and without a canary, and use it to fund progressive delivery.
- [ ] M5: Measure alert quality for a real estate (actionable fraction, pages per shift) and delete or downgrade the offenders.
- [ ] M6: Design an escalation ladder with acknowledgement probabilities, including the point where a human is called.
- [ ] M7: Run a game day that finds real defects in runbooks, dashboards, and escalation — and record them as tracked actions.

---

## Anti-Goals

- Diagnosing while customers are still being hurt and no mitigation has been attempted.
- Two people making production changes without coordination.
- A timeline reconstructed from memory after the fact.
- "No change" stakeholder updates skipped because nothing changed.
- A postmortem with a single root cause and no contributing factors.
- Actions phrased as intentions ("be more careful", "improve monitoring").
- Actions with no owner, no date, and no observable definition of done.
- Declaring a fix "done" because zero incidents occurred in a month.
- A game day designed only to prove the system works.

---

## Interview Lens

- "Tell me about an incident you handled. What did you do in the first five minutes?"
- "How do you decide whether to roll back or fix forward?"
- "What makes a postmortem actually change things?"
- "How do you know your alerting is working?"
- "What would you do differently in your last incident?"

---

## 30-Day Plan

- **Week 1** — THEORY + RUNBOOKS: declaration criteria, roles, timeline, diagnosis and mitigation order. M1–M2.
- **Week 2** — EXERCISES: time decomposition, blast-radius math, alert-quality measurement, escalation probabilities; QUIZ to 13/15; FLASHCARDS daily. M3–M4.
- **Week 3** — MINI_PROJECT: run a staged incident with a full timeline, write the postmortem, and track the actions to completion. M5–M6.
- **Week 4** — REAL_WORLD_PROJECT war story; produce an incident-response standard for a real team; teach-back: "our incident class trends, defended" in 10 minutes.

---

## Artifacts you should be able to show

1. A live timeline document from a real or staged incident, with phases and confidence levels.
2. A time decomposition showing which phase dominates and the cheapest intervention for it.
3. A blameless postmortem with contributing factors and owned, time-boxed actions with definition-of-done.
4. An alert-quality report (actionable fraction, pages per shift) with the deletions made.
5. An escalation ladder with acknowledgement probabilities.
6. A game-day report listing real defects found and their tracked fixes.

---

## Done = You Can

- Run an incident with clear command, a timeline, and a measured outcome.
- Decide rollback vs fix-forward with stated preconditions.
- Write a postmortem that names causes and produces owned actions.
- Say whether your incident response is improving, with numbers.
