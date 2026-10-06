# Lab 08: AI Observability — Quiz

**Q1.** Traces and metrics differ because traces explain...
- a) Trends over time
- b) A single request end to end
- c) Costs
- d) Quality

**Q2.** Metrics answer trends; traces answer a single request. A latency alert tells you...
- a) Quality dropped
- b) Nothing about correctness
- c) Cost rose
- d) Users are unhappy

**Q3.** Long prompts and completions should be stored as...
- a) Inline text
- b) Hashes with a pointer to a controlled store
- c) Truncated text
- d) Base64

**Q4.** Inline prompt text in logs is a problem primarily because...
- a) It bloats storage
- b) Logs may contain PII and are broadly accessible
- c) It cannot be searched
- d) It is slow

**Q5.** Every trace must record version information because...
- a) Providers require it
- b) A quality regression must be attributable to a component
- c) It helps caching
- d) It is needed for billing

**Q6.** The most useful first question for a quality-drop alert is...
- a) "Is the model down?"
- b) "Did any versioned component change?"
- c) "Did traffic spike?"
- d) "Who is on call?"

**Q7.** A metric labelled with a request id is wrong because...
- a) Request ids are strings
- b) Unbounded cardinality destroys the metrics backend
- c) It duplicates traces
- d) Metrics cannot have string labels

**Q8.** High-cardinality detail belongs in...
- a) Metric labels
- b) Traces
- c) Logs only
- d) Dashboards

**Q9.** The random stratified sample is the unbiased estimate of quality because...
- a) It is cheapest
- b) It is sampled without regard to outcome
- c) It covers all errors
- d) It uses the strongest judge

**Q10.** Targeted strata (errors, escalations) must not be averaged with the random
sample because...
- a) They are too noisy
- b) The mix is deliberately biased and describes nothing
- c) They are more expensive
- d) They are duplicated

**Q11.** `cost_per_successful_outcome` exists because...
- a) Cost per request is easy to game
- b) A quality drop changes what a request is worth
- c) Providers report it
- d) It is required for billing

**Q12.** A 5-point quality drop at constant cost changes cost per outcome by...
- a) 5%
- b) about 6%
- c) about 20%
- d) nothing

**Q13.** PSI above 0.25 means...
- a) Stable
- b) A major distribution shift worth investigating
- c) Perfect calibration
- d) No data

**Q14.** A drift alert should trigger...
- a) Automatic rollback
- b) Investigation and eval-set review
- c) A page
- d) Nothing

**Q15.** Quality regression should trigger rollback because it is...
- a) Cheaper to detect
- b) The signal users actually feel
- c) Easier to measure
- d) Required by audits

**Q16.** Conflating drift and quality alerts causes...
- a) Better coverage
- b) Alert fatigue
- c) Higher cost
- d) Slower queries

**Q17.** Retry amplification is best detected by...
- a) The monthly invoice
- b) attempts/request from traces
- c) CPU usage
- d) Error codes alone

**Q18.** Cache hit rate collapse is a useful deploy signal because...
- a) It means the index is broken
- b) It usually means volatile content entered the cached prefix
- c) It improves recall
- d) It reduces cost

**Q19.** Guardrail stage attribution tells you...
- a) Which user caused the violation
- b) Which layer is doing the work and where the gaps are
- c) The total violation count
- d) The policy version

**Q20.** Every alert must have an owner, a first question, and a tested containment
action because...
- a) Audits require it
- b) Unowned alerts do not get fixed and untested runbooks are fiction
- c) It reduces metric count
- d) Providers need it

---

## Answers

1. **b** — aggregates are metrics; per-request reconstruction is a trace.
2. **b** — orthogonal signals.
3. **b** — content on demand, never by default.
4. **b** — retention and access make logs a compliance surface.
5. **b** — attribution is the whole value.
6. **b** — most quality incidents are a prompt or index change.
7. **b** — cardinality is the classic way to take a metrics system down.
8. **b** — traces are designed for high cardinality.
9. **b** — independent of the outcome.
10. **b** — reporting the mix as one number is meaningless.
11. **b** — a request that fails is not worth its cost.
12. **b** — `1/0.95 / (1/1.0) = 1.053`.
13. **b** — investigate and freeze releases.
14. **b** — rollback belongs to quality, not to input mix changes.
15. **b** — quality is the user-visible outcome.
16. **b** — unactionable alerts train people to ignore them.
17. **b** — the ratio is a leading indicator; the invoice is a lagging one.
18. **b** — a template edit that moves a timestamp into the prefix.
19. **b** — it shows which layer to invest in next.
20. **b** — both conditions mean nobody acts.

## Score Guide

18-20: ready for lab 10 (deployment) and lab 09 (security).
14-17: redo Exercises 2, 7, 9.
0-13: reread THEORY sections 2-8.