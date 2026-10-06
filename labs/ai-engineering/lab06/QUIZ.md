# Lab 06: AI Pipeline Orchestration — Quiz

**Q1.** A stage contract must declare...
- a) Only input and output types
- b) Inputs, outputs, error policy, timeout, retry, and limits
- c) Its author
- d) Its documentation

**Q2.** Typed stage interfaces primarily prevent...
- a) Runtime errors only
- b) Wiring the wrong stage into a chain at compile time
- c) Memory leaks
- d) Latency spikes

**Q3.** Type-driven routing replaces `if/else` chains because...
- a) It is shorter
- b) Adding a stage becomes adding a binding rather than editing a switch
- c) It is faster at runtime
- d) It supports more languages

**Q4.** Errors as typed values beat exceptions because...
- a) They are faster
- b) The pipeline can apply a declared policy per stage
- c) Exceptions are forbidden in Java
- d) They serialize better

**Q5.** Unbounded queues cause...
- a) Better throughput
- b) Unbounded memory growth and then OOM under backpressure
- c) Faster retries
- d) Lower latency

**Q6.** A stage cache key must include the config hash so that...
- a) Keys are shorter
- b) A config change invalidates downstream caches automatically
- c) Hashing is faster
- d) Providers require it

**Q7.** Retries should apply only to idempotent stages because...
- a) Idempotent stages are cheaper
- b) Retrying a side-effecting stage duplicates the effect
- c) Providers forbid it
- d) It reduces token usage

**Q8.** The most common cause of a bottleneck going unnoticed is...
- a) High load
- b) A stage without per-stage metrics looks free
- c) Slow hardware
- d) Bad prompts

**Q9.** `PipelineSpec` recorded with every result lets you...
- a) Speed up inference
- b) Attribute a quality change to a specific stage
- c) Reduce cost
- d) Skip tests

**Q10.** Backpressure in an AI pipeline means...
- a) Dropping requests silently
- b) Explicitly rejecting or blocking to protect memory
- c) Retrying faster
- d) Increasing concurrency

**Q11.** Partial failure in fan-in should be governed by...
- a) Chance
- b) A declared aggregate policy
- c) The slowest item
- d) The model

**Q12.** A stage with hidden clocks or randomness is hard to test because...
- a) Java forbids it
- b) Tests need mocks and become flaky
- c) It cannot be cached
- d) It is always slow

**Q13.** Property-based invariants (no nulls, bounded sizes) catch...
- a) Slow stages
- b) Bug classes no example-based test enumerates
- c) Cost regressions
- d) Model drift

**Q14.** Golden tests detect...
- a) New features
- b) Unintended behaviour changes in recorded cases
- c) Memory leaks
- d) Network failures

**Q15.** In a DAG, total latency follows...
- a) The sum of all stage latencies
- b) The critical path
- c) The slowest single stage
- d) The average

**Q16.** Increasing a stage's concurrency improves throughput only while it is...
- a) Always better
- b) Not the bottleneck and not queue-limited
- c) Cached
- d) Idempotent

**Q17.** A saga with compensation is required when...
- a) Stages are read-only
- b) Stages have side effects that must be undone on failure
- c) The pipeline is short
- d) Inputs are validated

**Q18.** A circuit breaker per stage exists to...
- a) Improve accuracy
- b) Stop hammering a failing dependency and enable fallback
- c) Reduce memory
- d) Speed up cold starts

**Q19.** Streaming a pipeline changes...
- a) Total latency and cost
- b) Time-to-first-result and failure visibility
- c) Accuracy
- d) Only memory

**Q20.** Deterministic replay requires recording...
- a) Only inputs
- b) Inputs, config versions, seeds, and clocks
- c) The model weights
- d) Nothing extra if stages are pure

---

## Answers

1. **b** — the declaration is what makes the chain governable.
2. **b** — compile-time wiring errors are a whole bug class removed.
3. **b** — open/closed for extension.
4. **b** — a policy per stage is only possible with classified failures.
5. **b** — a queue that cannot be bounded is an OOM with extra steps.
6. **b** — automatic invalidation instead of remembering to clear caches.
7. **b** — duplicates on the outside.
8. **b** — uninstrumented stages cost nothing in the dashboard.
9. **b** — attribution is the entire value.
10. **b** — protecting memory explicitly rather than hoping.
11. **b** — the policy must be declared, not improvised per run.
12. **b** — impure stages make tests slow and flaky.
13. **b** — nulls, unbounded growth, and leaks are classes, not examples.
14. **b** — regression detection on recorded behaviour.
15. **b** — parallel branches overlap; only the longest chain adds.
16. **b** — past that point it adds contention and queueing.
17. **b** — partial writes leave the system inconsistent without undo.
18. **b** — repeated failure calls waste budget and delay recovery.
19. **b** — the same work is done; it is surfaced earlier.
20. **b** — otherwise non-deterministic stages cannot be reproduced.

## Score Guide

18-20: ready for labs 07, 08, 10.
14-17: redo Exercises 4, 6, 9.
0-13: reread THEORY sections 1-8.