# MINI_PROJECT — Production Inference Service

**Track:** mlops  |  **Lab:** lab05  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

**Brief.** Containerise a model server with warm-up, batching, honest resource sizing and a measured latency budget.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

Every model eventually becomes an HTTP service under a latency budget. Building it once properly saves the argument later.

## 2. Requirements

- Multi-stage Dockerfile: runtime image under 150 MB, base pinned by digest.
- Container-aware JVM sizing with RSS monitoring; survive a 3x burst.
- /healthz (cheap) and /readyz (gated on warm-up) endpoints.
- Single and batched predict endpoints; assert batched equals single.
- Batch window derived from a stated latency budget; sweep and report p99 and throughput.
- Requests and limits set from a load test at 1x, 2x and 3x target QPS.
- Graceful model reload with no failed requests.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Multi-stage Dockerfile; build, measure image size and digest | A small reproducible image |
| 2 | 25m | Container-aware JVM sizing with an RSS breakdown | A memory budget with headroom |
| 3 | 30m | Health endpoints and readiness gated on warm-up | A readiness smoke test |
| 4 | 35m | Batched predict with a flush timer; parity assertion | Parity test plus a sweep table |
| 5 | 30m | Load test at 1x/2x/3x; derive requests and limits | A sizing table from measurement |
| 6 | 25m | Graceful hot reload with drain | No failed requests during a swap |
| 7 | 20m | Runbook plus a capacity note | A runbook with the cold-start budget |

## 4. Architecture Sketch

```text
 model.bin
    |
 ModelHolder (lazy load -> warm-up -> ready)
    |
 +--+----------------------+----------------------+
 |                                             |
/healthz  /readyz                     POST /predict (single)
/predict/batch (batched)             GET /capacity
    |
 BatchQueue (bounded, flush on size or window)
    |
 container: MaxRAMPercentage + RSS monitoring + heap dump on OOM
    |
 load test -> requests/limits, cold-start budget, capacity note
```

## 5. Implementation Notes

- Measure cold start as three numbers, not one; the fix depends on which dominates.
- The batch window is latency you are spending, so subtract it from the budget explicitly.
- Set limits above p99 so bursts throttle briefly instead of permanently.
- RSS, not heap, is what the container limit sees.

## 6. Deliverables

1. Dockerfile plus recorded image size and digest.
1. Load test results at 1x/2x/3x with derived requests and limits.
1. Batch sweep table and the chosen operating point.
1. Runbook with cold-start decomposition and a capacity note.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Packaging | 25% | Multi-stage, small image, pinned digest, container-aware JVM |
| Correctness | 20% | Batched equals single; readiness gates on warm-up |
| Performance | 30% | Latency budget met; batch window derived; throughput reported |
| Reliability | 15% | Survives a burst; graceful reload; health checks cheap |
| Operations | 10% | Runbook and capacity note |

## 8. Stretch Goals

- Autotune the batch window from observed latency.
- Add a GPU-style continuous batching simulation and compare queueing policies.
- Add shadow scoring of a challenger on a fraction of traffic.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Multi-stage Dockerfile: runtime image under 150 MB, base pinned by digest.
- [ ] Container-aware JVM sizing with RSS monitoring; survive a 3x burst.
- [ ] /healthz (cheap) and /readyz (gated on warm-up) endpoints.
- [ ] Single and batched predict endpoints; assert batched equals single.
- [ ] Batch window derived from a stated latency budget; sweep and report p99 and throughput.
- [ ] Requests and limits set from a load test at 1x, 2x and 3x target QPS.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
