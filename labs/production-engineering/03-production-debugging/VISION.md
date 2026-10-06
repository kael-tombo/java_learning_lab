# VISION — Lab 03: Production Debugging

> From "restart it and see" to a disciplined, evidence-driven first fifteen minutes.

---

## The Arc

1. **Signal literacy** — read thread dumps, histograms, GC logs, NMT, and container metrics correctly (and know what each cannot tell you).
2. **State taxonomy** — six thread states, native memory categories, and the specific symptom each produces.
3. **Symptom → hypothesis** — a decision tree that gets from "latency up" to a ranked hypothesis list in under five minutes.
4. **Instrumentation design** — correlation IDs, structured logs, JFR event selection, and continuous profiling chosen deliberately.
5. **Container reality** — exit codes, cgroup limits, throttling, ephemeral storage, and why JVM defaults break in Kubernetes.
6. **Debugging as design** — the argument that debuggability is an architectural property, not a skill.
7. **Postmortem literacy** — converting diagnosis difficulty into a prioritized observability backlog.

---

## Why this lab exists

Debugging is the least trained and highest-leverage engineering skill. Most teams learn it under pressure, without a hypothesis discipline, and their conclusion is usually "add more logs." That produces more logs, more cost, and no better diagnosis.

The specific goal here: **your first fifteen minutes of any incident must produce evidence, not theories.** A restart is a mitigation, not a diagnosis; a postmortem without a root cause is a diary.

---

## Milestones (checkable)

- [ ] M1: Given a thread dump, state the dominant thread state and the *specific* resource being contended or awaited — naming the owner or target.
- [ ] M2: Explain why "RUNNABLE with low CPU" means native I/O, and how you prove it from the stack.
- [ ] M3: Triage four OOM variants from the error message alone, naming the next two commands for each.
- [ ] M4: Use NMT baseline/diff to attribute native memory growth to a category.
- [ ] M5: Select the right JFR events to separate CPU / lock / park / I/O wait for a given symptom.
- [ ] M6: Diagnose a planted deadlock, a thread leak, a native-memory leak, and a cgroup-throttling latency spike in a lab harness, capturing evidence for each.
- [ ] M7: Write an instrumentation plan for a service that has only text logs and no traces — including cost estimates.

---

## Anti-Goals

- Restart-first debugging that destroys the only live evidence.
- Reading stack traces once and concluding from a single sample.
- Attributing every latency spike to GC without a correlating log line.
- Adding `System.out.println` or a remote debugger to a production process.
- Treating "we added logging" as the postmortem action item.
- Declaring a bug fixed because a short test run did not reproduce it.

---

## Interview Lens

- "Production latency doubled with no deploy. Walk me through your first ten minutes."
- "Thread dump shows 400 threads in WAITING. What are the three most likely causes?"
- "How do you tell a JVM OOM from a kernel OOM-kill?"
- "Our service is slow but CPU is 30%. Where do you look, in order?"
- "How do you prove a race condition is fixed?"

---

## 30-Day Plan

- **Week 1** — THEORY on thread states, native memory, container failure modes; hand-annotate 10 real thread dumps. M1–M3.
- **Week 2** — EXERCISES: guided triage cases, JFR event selection, NMT workflow; QUIZ to 13/15; FLASHCARDS daily. M4–M5.
- **Week 3** — MINI_PROJECT: build the evidence-capture toolkit and reproduce all four pathologies. M6.
- **Week 4** — REAL_WORLD_PROJECT war story; produce an instrumentation plan with a cost model; teach-back: "debug a planted bug using only your runbook" in 15 minutes. M7.

---

## Artifacts you should be able to show

1. An annotated thread dump showing a contention or starvation cycle.
2. An NMT `summary.diff` attributing growth to a named category.
3. A JFR recording configured for a specific symptom, plus what it revealed.
4. A triage decision tree you actually use (not a poster).
5. An instrumentation plan with GB/day cost arithmetic.

---

## Done = You Can

- Walk into an unfamiliar incident and produce ranked, evidence-backed hypotheses within five minutes.
- Know which tool answers which question, and which question a tool cannot answer.
- Choose mitigation and diagnosis deliberately and in that order, understanding their trade-off.
- Explain to a team why a restart can be the right call *and* why it must be followed by diagnosis.
