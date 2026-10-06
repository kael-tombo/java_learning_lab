# VISION — Lab 18: Chaos Engineering & Fault Injection

> From "let us break production and see" to "here is the hypothesis, here is the abort, here is what we learned."

---

## The Arc

1. **The method** — hypothesis, steady-state assertion, injection, measurement, abort, undo, verify. Why experiments without hypotheses produce anecdotes.
2. **Blast radius and abort** — exposure arithmetic, automated aborts, mandatory automatic restore, tested controls.
3. **Choosing the fault** — latency first (and why), then packet loss, resource exhaustion, disk, DNS, clocks, certificates.
4. **Injection technique** — boundary (sidecar/proxy/mesh) versus in-code, and what each can and cannot reach.
5. **Kubernetes-specific faults** — pod kill, node eviction, cgroup CPU throttle, token/config deletion.
6. **Dependency failures** — unavailability, throttling, slow, corrupted response.
7. **Resource failures** — CPU, memory, disk, file descriptors, connections.
8. **GameDays** — testing the human system: command, runbooks, escalation, communication.
9. **Findings into action** — treating a discovery as an incident, tracking every finding, measuring detection time.
10. **Programme design** — frequency, radius escalation, registry, coverage metric, and when production is justified.

---

## Why this lab exists

Untested resilience is assumed resilience, and the assumption is discovered at the worst possible moment. Most teams have a resilience architecture on paper and no evidence that it works, because the failure modes were never exercised under controlled conditions.

The specific goal here: **you can design an experiment with a falsifiable hypothesis, a bounded radius, a tested abort, and a pass condition — and you can say what you learned even when nothing broke.**

---

## Milestones (checkable)

- [ ] M1: Write a failure-mode inventory for a real service (20+ modes), and choose the highest-value three by the arithmetic.
- [ ] M2: Run a latency-injection experiment and quantify the concurrency amplification `ΔL = λ × ΔW` with measurements, not estimates.
- [ ] M3: Build and *test* an automated abort: inject a controlled regression, verify the abort fires and cleanup restores the steady state.
- [ ] M4: Run ten experiments in staging with hypotheses, pass conditions, and pass/fail results recorded in a registry.
- [ ] M5: Run one GameDay with coordinated injections and measure time-to-detect, time-to-first-correct-hypothesis, and every point a human was blocked.
- [ ] M6: Run one production experiment (tiny radius) and record the business sign-off path, the abort test, and the result.
- [ ] M7: Convert at least three findings into tracked actions and measure the recurrence rate of the corresponding incident classes.

---

## Anti-Goals

- Experiments with no hypothesis and no pass condition.
- Chaos as a substitute for observability (if you cannot see it, you cannot learn).
- Human-judged aborts.
- Radius escalation without a successful prior result.
- Production chaos with an untested abort.
- Fixing a discovered failure in the experiment branch instead of running the incident process.
- Untracked findings.
- Tool-driven chaos with no one writing down what was learned.

---

## Interview Lens

- "How do you decide what to break?"
- "How do you know an experiment was safe?"
- "What did chaos find that testing did not?"
- "How do you justify running chaos in production?"
- "What is the abort condition, and who decides?"

---

## 30-Day Plan

- **Week 1** — THEORY + RUNBOOKS: method, fault taxonomy, injection techniques; hands-on with Toxiproxy and a Spring Boot service. M1–M3.
- **Week 2** — EXERCISES: exposure arithmetic, retry amplification, detection probability; QUIZ to 13/15; FLASHCARDS daily. M4.
- **Week 3** — MINI_PROJECT: build the experiment harness with preconditions and aborts, run ten experiments, write the registry. M5–M6.
- **Week 4** — REAL_WORLD_PROJECT war story; produce a chaos programme plan; teach-back: "our untested assumptions, found" in 10 minutes.

---

## Artifacts you should be able to show

1. A failure-mode inventory for a real service, ranked by expected blast radius.
2. A latency-injection result with the concurrency amplification measured.
3. A tested abort with the verification evidence.
4. An experiment registry with hypotheses, pass conditions, and results (including null results).
5. A GameDay report with the injection schedule, the human-system timings, and the defects found.
6. A chaos coverage metric and the findings-to-actions tracker.

---

## Done = You Can

- State a hypothesis and a pass condition before injecting anything.
- Compute the exposure of an experiment and justify the radius.
- Explain why latency is the highest-value injection.
- Say what a null result proves.
- Run a GameDay that tests the humans as rigorously as the system.
