# Lab 10: AI Deployment & CI/CD — Quiz

**Q1.** The deployable artifact for an AI feature is...
- a) The model weights
- b) Model + prompt + index + tools + policy + generation config
- c) The training data
- d) The container image

**Q2.** The manifest hash must appear in every response because...
- a) For billing
- b) Any response can be attributed to the exact configuration that produced it
- c) To enable caching
- d) For rate limiting

**Q3.** Deploy and release differ because...
- a) Deploy is manual
- b) Deploy is mechanical; release is a decision with an owner
- c) Release is faster
- d) They are the same

**Q4.** Canary traffic must be assigned by user because...
- a) Users are cheaper
- b) Otherwise one user sees two versions in a session
- c) Requests are more uniform
- d) Providers require it

**Q5.** A missing canary metric must be treated as...
- a) A pass
- b) A breach, so broken telemetry cannot promote a bad release
- c) A warning
- d) A retry

**Q6.** Rollback must be a config flip because...
- a) Config flips are cheaper
- b) Slow rollback causes bad decisions under pressure
- c) Models cannot be rebuilt
- d) Config is always correct

**Q7.** Keeping the previous version warm exists to...
- a) Save storage
- b) Remove cold-start time from rollback
- c) Enable A/B tests
- d) Satisfy auditors

**Q8.** Data migrations should be expand/contract because...
- a) They are faster
- b) The old artifact must still be able to read the new schema during rollback
- c) Providers require it
- d) They use less storage

**Q9.** Rollback cannot undo an irreversible side effect, which is why...
- a) Rollback is disabled for agents
- b) Approval gates and idempotency must exist at the action level
- c) Agents are not deployed
- d) Logs are disabled

**Q10.** Target autoscaling utilization is <= 0.6 because...
- a) GPUs are expensive
- b) Tail latency degrades sharply near saturation
- c) 0.6 is a vendor maximum
- d) Batching needs it

**Q11.** Scaling on GPU utilization under-provisions because...
- a) Utilization is noisy
- b) It is a lagging signal; by the time it rises, the queue is already deep
- c) GPUs do not report it
- d) It ignores cost

**Q12.** Shadow deployment's advantage is...
- a) Faster results
- b) Measuring a candidate at zero user risk
- c) Lower cost
- d) Better accuracy

**Q13.** Logical model names decouple products from models because...
- a) They are shorter
- b) Swapping the underlying model needs no product code change
- c) They cost less
- d) They avoid rate limits

**Q14.** Fallback chains must not retry 4xx because...
- a) 4xx means overload
- b) A malformed request fails identically, so retrying burns the chain's budget
- c) Providers forbid it
- d) 4xx is slower

**Q15.** Deprecation auto-pin at the deadline exists because...
- a) Providers require it
- b) Otherwise an un-migrated caller breaks in production
- c) It reduces cost
- d) It improves quality

**Q16.** Feature flags with independent kill switches exist to...
- a) Enable experiments
- b) Bound the blast radius of a bad release
- c) Reduce cost
- d) Simplify code

**Q17.** Safety regressions should block releases with...
- a) A 5% tolerance
- b) Zero tolerance
- c) A warning
- d) An A/B test

**Q18.** Quality deltas whose CI includes zero should...
- a) Block
- b) Warn, not block, because claiming a win would be false
- c) Be ignored
- d) Trigger a rollback

**Q19.** Environment parity must include the index version because...
- a) Indexes are large
- b) A different index changes answers even with the same model
- c) Indexes change daily
- d) Providers require it

**Q20.** Production-shaped traffic in shadow mode exists to catch...
- a) Load issues
- b) Parity and quality problems that only appear with real traffic
- c) Cost overruns
- d) DNS errors

---

## Answers

1. **b** — four of the five artifacts are configuration.
2. **b** — attribution is the whole value.
3. **b** — separate mechanics from accountability.
4. **b** — session consistency is a user-visible property.
5. **b** — fail closed.
6. **b** — minutes matter under pressure.
7. **b** — rollback time is dominated by cold start.
8. **b** — rollback compatibility is the constraint.
9. **b** — release-level rollback is insufficient for actions.
10. **b** — `rho` near 1 makes mean wait explode.
11. **b** — it is a symptom, not a cause.
12. **b** — no user sees the candidate.
13. **b** — the highest-value abstraction in the platform.
14. **b** — retries would consume the whole chain's budget.
15. **b** — it is the safety net for missed migrations.
16. **b** — radius is the largest design lever on release risk.
17. **b** — a safety regression is not a trade-off.
18. **b** — inside the CI there is no effect to claim.
19. **b** — retrieval determines what the model can even see.
20. **b** — staging fixtures will not reproduce real distributions.

## Score Guide

18-20: ready for senior AI-platform and MLOps roles.
14-17: redo Exercises 5, 8, 16.
0-13: reread THEORY sections 1-8.