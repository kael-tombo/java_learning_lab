# Model Serving with Docker - Vision & Where This Is Going

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

## 1. The Future State

Serving converges on inference-optimised runtimes, GPU batching services, and autoscaling driven by queue depth rather than CPU. The packaging discipline stays the same: small reproducible images, honest resource requests, and warm-up that is a requirement rather than a hope.

The test of that future state is boring: a new engineer ships a change to model serving with docker on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Runtime images are multi-stage, pinned by digest and under 150 MB.
- JVM sizing is container-aware and RSS is monitored, not just heap.
- Readiness gates on warm-up; liveness never does work.
- Batch window is derived from the documented latency budget.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Serve | Serve single predictions with health endpoints. |
| L2 | Package well | Multi-stage build, container-aware JVM, small image. |
| L3 | Perform | Batching, warm-up, and requests sized from a load test. |
| L4 | Operate | Hot reload, autotuned batching, and a documented cold-start budget. |

## 4. Behaviours to Build

Treat packaging as part of the deliverable. Derive every timing from a measurement. Keep health checks trivial so a load spike never becomes a restart storm.

## 5. Anti-Vision (the failure mode we are avoiding)

- A fat JDK runtime image with Gradle inside.
- -Xmx equal to the container limit.
- Health checks that call the model.
- Resource limits set equal to requests, causing permanent throttling.

## 6. Technology Shifts That Change the Work

1. Dedicated inference runtimes with continuous batching and KV-cache reuse.
1. Autoscaling on queue depth and inference latency rather than CPU alone.
1. GPU serving with tensor and quantisation optimisations for sub-10 ms budgets.
1. Reproducible, minimal, distroless runtime images as a security baseline.

## 7. Your 30/60/90 Commitment

- **30 days.** Ship a multi-stage image under 150 MB with a container-aware JVM.
- **60 days.** Add batching, warm-up and readiness gating, and measure each contribution.
- **90 days.** Load test, size requests and limits from measurement, and add graceful hot reload.

## 8. How To Tell You Are Actually Getting Better

- I can state my image size and cold-start decomposition.
- My container survives a 3x burst without being OOMKilled.
- My first request after deploy is not an outlier.
- Requests and limits come from a load test.

## 9. Principles That Should Not Change

- **Write a multi-stage Dockerfile that keeps the runtime image small** Write a multi-stage Dockerfile that keeps the runtime image small
- **Choose JVM flags appropriate for a container memory limit** Choose JVM flags appropriate for a container memory limit
- **Design a prediction API with batch, single** Design a prediction API with batch, single and health endpoints

> Packaging is the difference between a model that scores well and a model that serves.
