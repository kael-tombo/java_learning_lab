# VISION — Lab 20: Production Readiness & SLO Engineering

> From "the service is deployed" to "here is the evidence that it behaves, and here is what we decided to accept."

---

## The Arc

1. **What readiness means** — evidence, not artefacts; operational claims rather than design quality.
2. **SLI/SLO design** — user-visible properties, explicit `valid` exclusions, per-dimension decomposition, minimum event floors.
3. **Error budgets** — the arithmetic, and choosing an SLO your organisation's incident size can survive.
4. **Burn-rate alerting** — fast pages, slow tickets, two-window confirmation, and the window/lead-time relationship.
5. **Capacity readiness** — a measured model, utilisation target, and headroom that survives N+1.
6. **Startup and shutdown readiness** — readiness gated on servability, warm-up as a capacity cost, drain and grace arithmetic, verified by counting 5xx under load.
7. **Dependencies and failure modes** — an inventory, at least one injection per service before launch.
8. **Observability readiness** — the minimum dashboard set, correlated logs, and alert/runbook pairing.
9. **Runbooks and on-call** — exercised by someone else, alerts that lead to actions, a page budget.
10. **Deployment, rollback, data, recovery** — drilled rollback, measured RTO/RPO, retention and erasure.
11. **The PRR process** — before traffic, repeated on material change, evidence-based, with a named sign-off.

---

## Why this lab exists

Readiness is usually a checklist that gets filled in by the team shipping the thing, in the environment closest to production, without load, without failure injection, and without anyone asking the operational questions. It passes, and then the service runs for four years with no SLO, no tested rollback, and a restore nobody has verified.

The specific goal here: **you can run a readiness review that produces evidence rather than checkmarks, and you can say exactly which risks you are accepting and until when.**

---

## Milestones (checkable)

- [ ] M1: Define SLIs and SLOs for a real service across four dimensions, with explicit exclusions, event floors, and computed error budgets.
- [ ] M2: Implement burn-rate alerts and measure the detection lead time against a historical incident replay.
- [ ] M3: Build a capacity model with a saturation point, a utilisation target, and an N+1 headroom requirement.
- [ ] M4: Verify startup and shutdown readiness under load: count 5xx during a rollout, and prove readiness gates traffic until servable.
- [ ] M5: Enumerate 15+ failure modes and run at least three injections per service with pass conditions.
- [ ] M6: Perform a timed restore and measure the actual RTO and RPO against stated objectives.
- [ ] M7: Run a full PRR with evidence in all eight areas, produce an accepted-risk register, and re-review after 6 months to measure drift.

---

## Anti-Goals

- Checkmarks without evidence.
- A single blended availability SLO.
- An SLI with undocumented exclusions.
- Threshold alerts instead of burn-rate alerts.
- Capacity sized for average rather than peak plus failure.
- A runbook written but never exercised by a second person.
- A rollback assumed rather than drilled.
- A backup assumed to be restorable.
- An accepted risk with no owner and no expiry.
- A PRR run in a non-representative environment.

---

## Interview Lens

- "How do you know a service is production ready?"
- "How do you define an SLO for a service like this?"
- "What would you check on a service launched tomorrow?"
- "Tell me about a time a service was not ready and what gave it away."
- "How do you decide what risk to accept?"

---

## 30-Day Plan

- **Week 1** — THEORY + `CHECKLIST`: SLO design, burn rates, capacity, startup/shutdown; hands-on with the checklist against a real service. M1–M2.
- **Week 2** — EXERCISES: budget math, headroom math, drain math, RTO math, drift; QUIZ to 13/15; FLASHCARDS daily. M3–M4.
- **Week 3** — MINI_PROJECT: run the full readiness review with evidence, injections, and a restore test. M5–M6.
- **Week 4** — REAL_WORLD_PROJECT war story; produce a readiness gate for a real platform; teach-back: "what we accept, and until when" in 10 minutes.

---

## Artifacts you should be able to show

1. An SLO specification with SLI definitions, exclusions, budgets, and the release policy.
2. Burn-rate alerts with a measured detection lead time.
3. A capacity model with the saturation point and N+1 headroom.
4. A rollout under load with a 5xx count of zero and the drain arithmetic.
5. A failure-mode inventory with three completed injections per service.
6. A measured restore test with real RTO/RPO.
7. A PRR record with evidence links, plus an accepted-risk register with owners and expiries.

---

## Done = You Can

- State what a service does under foreseeable failure and prove it.
- Choose an SLO that your organisation's incident size can survive.
- Tell whether an alert would have caught a specific historical incident, and how early.
- Say what you are accepting, why, and when you will revisit it.
