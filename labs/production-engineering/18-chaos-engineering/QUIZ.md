# Lab 18: Chaos Engineering & Fault Injection — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. What is the actual goal of a chaos experiment?**
- A) To break production and observe the breakage
- B) To *verify a specific hypothesis* about how the system behaves under a specific fault. An experiment without a hypothesis is a stress test; a hypothesis without a steady-state comparison is an anecdote
- C) To find as many bugs as possible
- D) To prove the team is resilient

**Answer: B** — Chaos Monkey's original framing was to expose weaknesses that would otherwise be found in production. The discipline is: hypothesis → steady state → inject → observe → (restore) → decide. A chaos run with no hypothesis produces a story, not evidence.

---

**Q2. What is the "steady state" requirement, and what happens without it?**
- A) It is optional
- B) The system must be healthy *before* injection — defined by SLI metrics, not by "it looks fine". Without it you cannot attribute the observed degradation to the injection, and you will either panic at a pre-existing problem or conclude a real fault is harmless
- C) It means the load test is running
- D) It means no alerts are firing

**Answer: B** — The check should be automated: a precondition assertion that refuses to inject unless key SLIs are inside their objective for the last N minutes.

---

**Q3. What is blast radius, and how do you bound it?**
- A) The number of affected services
- B) The maximum fraction of requests/users/instances the experiment may affect at once. Bound it by scope selector (`namespace`, `app`, `label`, `az`), by percentage, by time, and by a hard abort — and always start at the smallest radius you can learn from
- C) The duration
- D) The severity

**Answer: B** — Production experiments are legitimate and often necessary, but the radius must be a parameter you set explicitly, with an automatic abort, and the first runs belong in production only after staging has validated the experiment mechanics.

---

**Q4. What is the abort condition, and why must it be automated?**
- A) A human watching the dashboard
- B) A machine-evaluated threshold on user-visible SLIs (error rate, latency, availability) that halts the experiment and triggers cleanup automatically. A human cannot evaluate a metric reliably at 30-second intervals for an hour, and hesitation during a real degradation is the worst possible behaviour
- C) A time limit only
- D) A Slack command

**Answer: B** — The abort must be independent of the experimenter, and it must be tested: inject a controlled regression and verify the abort fires and cleans up.

---

**Q5. Why must an experiment restore the steady state automatically?**
- A) To keep the graph pretty
- B) Because if it does not, the experiment *becomes* the incident. Every injection needs a guaranteed rollback path (the inverse operation plus a verification step), on a timer, not on human action
- C) Because chaos tools cannot undo
- D) It is not required if the blast radius is small

**Answer: B** — Undo-by-default is the design requirement. If you cannot state the inverse operation and verify the return to steady state, you are not ready to run it.

---

**Q6. What does `network latency` injection reveal that `network loss` does not?**
- A) Nothing
- B) Latency inflates queue occupancy via Little's Law (`L = λ × W`) and exposes concurrency-limit and timeout-budget bugs, while *requests still succeed*. Packet loss breaks correctness paths. Most real incidents are latency, not loss, so latency is the higher-value injection
- C) Loss is higher value
- D) They are equivalent

**Answer: B** — Latency is the incident shape you will actually see: pools exhaust, thread pools saturate, deadlines are missed, and the failure is "slow", not "down".

---

**Q7. What does a "DNS failure" injection actually simulate, and why is it a favourite?**
- A) Only DNS
- B) Everything that resolves by name fails at once — a stale-JVM DNS cache masks it until TTL expiry, then every pod resolves simultaneously. This reproduces a specific, common, and often-mitigated-in-theory-only failure
- C) A network partition
- D) Nothing

**Answer: B** — The JVM's DNS cache (`networkaddress.cache.ttl`) is the key detail: the mitigation is caching, and the risk is a synchronised expiry, which is a Lab 12 problem resurfacing in a new place.

---

**Q8. What does a "CPU saturation" injection reveal?**
- A) Nothing, since you can just measure CPU
- B) Behaviour under *insufficient* CPU: CFS throttling, p99 inflation invisible in the mean (Lab 07/15), queue growth, GC starvation, and whether the service sheds or collapses. It also reveals whether your `requests == limits` decision was correct
- C) Only GC behaviour
- D) Only network behaviour

**Answer: B** — And it is one of the cheapest injections to run (a CPU burner in the pod) with a precise inverse (kill the burner).

---

**Q9. What does a "disk full" injection reveal, and why is it under-tested?**
- A) Nothing interesting
- B) A large class of silent failures: logs stop being written (so you lose the evidence of the very incident you are diagnosing), heap dumps fail, temp files fail, and metrics may stop. Systems often fail *observably safe* rather than loudly, and you discover your diagnostics depend on the disk
- C) Only performance
- D) Only data loss

**Answer: B** — It is also a security-relevant test: full-disk conditions can cause writes to fail silently, which is how data-integrity incidents happen.

---

**Q10. What is the difference between a fault at the network boundary and a fault injected inside the application?**
- A) No difference
- B) Boundary injection (sidecar/proxy, e.g. Toxiproxy) exercises the real client stack — retries, timeouts, pools, TLS — and is the default choice. In-code injection (`@InjectableFault`) reaches paths a network fault cannot (a specific business rule, a specific exception type) but *bypasses the client behaviour you actually want to test*
- C) In-code is always better
- D) Boundary injection cannot simulate latency

**Answer: B** — Prefer boundary injection for infrastructure faults; use in-code injection for business-logic faults, and label which is which so nobody mistakes one for the other.

---

**Q11. What does "verify the hypothesis, not the chaos" mean?**
- A) Run fewer experiments
- B) Every experiment has a pass condition stated *before* injection, derived from an SLO or a documented expectation, and the result is pass/fail. Without it, chaos produces anecdotes that get remembered selectively
- C) Ignore the results
- D) Chaos is not rigorous

**Answer: B** — The pass condition might be "p99 stays under 400 ms" or "no duplicate orders created" or "the circuit breaker opens within 30 s". If you cannot state it before you start, you cannot learn.

---

**Q12. What is a GameDay, and how does it differ from a chaos experiment?**
- A) Synonyms
- B) A chaos experiment tests one hypothesis about one fault. A GameDay is a coordinated, human-in-the-loop exercise that tests the *human system*: incident command, runbooks, escalation, communication, decision-making under uncertainty, with several injections coordinated in time
- C) GameDays are only for training
- D) GameDays need no injections

**Answer: B** — Chaos finds technical gaps; GameDays find organisational ones (the runbook command that no longer exists, the dashboard behind a VPN, the escalation to someone who left).

---

**Q13. Why is a production experiment sometimes the only way to test something?**
- A) It is always required
- B) Because some failure modes only exist in production: real traffic shape, real data skew, real multi-AZ networking, the real managed-service behaviour, real certificate expiry. But it requires the strongest controls: tiny radius, verified abort, observed-in-production metrics, and business sign-off
- C) Because staging is unreliable
- D) Never

**Answer: B** — The staging result is evidence about staging. Production experiments are justified when the hypothesis concerns a property only production has, and they are run with the same discipline plus a human watching.

---

**Q14. What should you do when a chaos experiment reveals a failure?**
- A) Immediately write it up as a bug
- B) Treat the *discovery* as the result: stop the experiment, restore the steady state, record the timeline, and let the incident response run as it would in production. Then the postmortem, and then the fix. Chaos that skips the incident process teaches nobody anything about the organisation
- C) Fix it in the experiment branch
- D) Re-run to confirm

**Answer: B** — The most valuable part of a chaos finding is often the *time to detection and diagnosis*, which you should measure rather than shortcut.

---

**Q15. The single most common reason chaos programmes fail is?**
- A) The tooling is immature
- B) Experiments are run without hypotheses, pass conditions, or abort conditions, so they produce anecdotes and no change; and when something breaks, the programme gets cancelled because there is no trust that abort works. Trust is earned by starting small and always restoring
- C) Engineers do not want to break things
- D) Production is too busy

**Answer: B** — The discipline (hypothesis → steady state → abort → verify → undo) is what makes chaos safe. Without it, chaos is just outage generation.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and run experiments with full instrumentation.
- 12–10: revisit hypotheses, abort conditions, and blast-radius control; redo EXERCISES 2–5.
- <10: re-read THEORY + RUNBOOKS cold and retake in 48 hours.
