# Lab 20: Production Readiness & SLO Engineering — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. What does "production ready" actually mean?**
- A) Deployed, healthy, and monitored
- B) A service whose behaviour under foreseeable failure is *known and evidenced*: it has SLIs with SLOs, capacity headroom measured, graceful startup and shutdown tested, dependencies and failure modes enumerated, runbooks that have been exercised, alerts with owners, and a rollback path that has been drilled
- C) Passing all tests
- D) Reviewed and approved

**Answer: B** — "It works" is not readiness. Readiness is the set of claims you can make about the service and can demonstrate. The most common PRR failure is that items are checked off, not evidenced.

---

**Q2. What is the difference between an SLI, an SLO, and an error budget?**
- A) Synonyms
- B) SLI = a measured property of user-visible behaviour; SLO = a target for that SLI over a stated window; error budget = the allowed failure implied by the SLO, expressed in time or requests
- C) SLO is a metric
- D) An error budget is a budget

**Answer: B** — The chain matters because it makes reliability a currency you can spend: `allowed failure = (1 − SLO) × window`.

---

**Q3. Why is a single end-to-end "availability" SLO often the wrong model?**
- A) It is always right
- B) It hides *which* part is unreliable and prevents targeted alerts. Separate SLIs for each dimension (success rate, latency, freshness/throughput, correctness) let you tell a 500-storm from a slow degradation from a stale projection, and each maps to a different runbook
- C) It is too easy
- D) Availability cannot be measured

**Answer: B** — Google's four golden signals (latency, traffic, errors, saturation) plus correctness and freshness is the practical decomposition. A single blended number is a reporting convenience, not an operating tool.

---

**Q4. Why must the SLI denominator exclude deliberately non-counted events, explicitly?**
- A) To make the number look better
- B) Because client cancellations, probes, and allowlisted tenants must not count as failures — but the exclusion must be written down, or the SLI is ambiguous and two people will compute different numbers from the same data
- C) It is unnecessary
- D) Only for internal services

**Answer: B** — Ambiguous SLIs produce disputes during incidents. Write `good/valid` with the exclusions and the reason for each.

---

**Q5. What is the correct alerting approach, and what is wrong with threshold alerts?**
- A) Alert on CPU above 80%
- B) Burn-rate alerts on the SLO: fast burns page, slow burns ticket. Threshold alerts are simultaneously too sensitive during normal periods (noise) and too insensitive during slow burns (missed degradation) — because they alert on absolute metric levels rather than on budget consumption
- C) Alert on every error
- D) Alert on business hours only

**Answer: B** — The burn rate is `observed_bad / allowed_bad`; it is scale-free and tied to the promise rather than to an arbitrary number.

---

**Q6. What must a readiness review check about capacity?**
- A) That autoscaling is enabled
- B) That there is a measured capacity model with peak traffic, utilisation target, per-resource saturation points, and headroom that survives an N+1 failure — plus a forecast and a defined trigger for scaling up proactively
- C) That the node pool is large
- D) That CPU is under 70%

**Answer: B** — Autoscaling without a capacity model is a reactive strategy that fails exactly when it is needed. Headroom must survive failure, not just peak.

---

**Q7. What must a readiness review check about startup?**
- A) That it starts
- B) That startup is *fast and observable*: readiness passes only when the service can actually serve (caches warm, connections established, migrations confirmed), startup has a probe so liveness does not kill a warming JVM, and slow startup does not consume production capacity on rollout
- C) That the pod becomes Running
- D) That logs are printed

**Answer: B** — A pod that is `Running` but not serving will receive traffic if readiness is wrong, and it will consume CPU while JIT-warming, reducing capacity for everyone.

---

**Q8. What must a readiness review check about shutdown?**
- A) That it exits cleanly on SIGTERM
- B) That it drains: stop accepting, finish in-flight work within the grace period, flush telemetry, close connections, and exit — with the grace period derived from the request timeout budget, and verified by observing zero 502s during a rollout
- C) That it has a preStop hook
- D) That it closes the database

**Answer: B** — The verification is what counts: deploy under load and count 5xx. A shutdown that "looks clean" in a log still produces user-visible failures if the grace period is too short.

---

**Q9. What makes a runbook production-ready?**
- A) It exists and is linked from the alert
- B) Someone who was not its author has followed it, end to end, and succeeded — every command verified to work, every dashboard link accessible without a VPN, every step with an expected output
- C) It is under a page
- D) It is reviewed quarterly

**Answer: B** — "Exercised by someone else" is the standard. Runbooks rot silently and the failure surfaces during an incident.

---

**Q10. What is the DR test that actually proves recovery?**
- A) A backup exists
- B) A restore into a clean environment with the measured RTO and RPO, performed on a schedule — because an untested restore is a hypothesis, and a backup you cannot restore is not a backup
- C) Replication is enabled
- D) Snapshots are configured

**Answer: B** — Measure the actual restore time and the actual data loss (`RPO`), and compare with the stated objectives. Most organisations discover both are worse than documented.

---

**Q11. What belongs in a production readiness review, and what does not?**
- A) Architecture diagrams
- B) Evidence in eight areas: SLIs/SLOs, capacity, startup/shutdown, dependencies and failure modes, observability and alerting, runbooks and on-call, deployment and rollback, data and recovery. Diagrams and design documents are inputs, not readiness criteria
- C) Code quality metrics
- D) The team's headcount

**Answer: B** — Readiness is about *operations*, so the review is operational. Include a "what would hurt us most if this broke tomorrow, and would we notice?" question.

---

**Q12. When should the PRR happen relative to launch?**
- A) After launch, retroactively
- B) Before any production traffic, as a gate with named sign-off, and repeated for material changes (new dependency, new data store, a scaling change, a change in the failure model). A service that never has a PRR never gets one once it is critical
- C) During the beta
- D) Only for tier-1 services

**Answer: B** — Repeat for material changes. Also: a PRR is not a one-time ceremony; the checklist should become a template the platform enforces, not a document a team completes.

---

**Q13. What is the error-budget policy, and why does it matter?**
- A) A budget for infrastructure spend
- B) A written rule connecting remaining error budget to acceptable release risk — ship freely above 50%, canary-only 25–50%, freeze below 25%. Without it, the SLO has no consequence and the budget is a number nobody acts on
- C) A financial reserve
- D) A performance target

**Answer: B** — The policy is what converts SLOs from reporting into governance. It also gives teams an honest argument for slowing down.

---

**Q14. What is the most common false signal in a readiness review?**
- A) A green dashboard
- B) Evidence collected in a non-representative environment — a single pod, no load, no failure injection, no peak traffic. A service that passes every check in staging at 5% of production load is not ready
- C) Passing integration tests
- D) A signed-off checklist

**Answer: B** — Require evidence from a production-shaped environment under load, and require at least one failure-injection exercise per service before launch.

---

**Q15. The single most common reason services are not actually production ready is?**
- A) Missing documentation
- B) Nobody has asked the operational questions: what breaks, how would we know, what would we do, and can we prove it. Readiness is a set of answers, not a set of artefacts, and the artefacts are what teams produce when nobody asks the questions
- C) Insufficient testing
- D) Wrong instance types

**Answer: B** — The most effective single change most organisations can make is a short, mandatory, evidence-based readiness review with a named sign-off owner, run before production traffic, and repeated on material change.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and run a real readiness review.
- 12–10: revisit SLO design, burn-rate alerting, and evidence standards; redo EXERCISES 2–5.
- <10: re-read THEORY + `CHECKLIST` + RUNBOOKS cold and retake in 48 hours.
