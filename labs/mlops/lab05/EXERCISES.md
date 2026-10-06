# Model Serving with Docker - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab05
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out ModelServingLab
```

## Exercise 1: Multi-stage Dockerfile

**Task.** Cut the runtime image and keep the build reproducible.

**Steps**
- Write a build stage with a pinned JDK.
- Copy only the artefact into a JRE runtime stage.
- Pin the base image by digest.
- Build and record the image size and digest.

**Deliverable.** A small runtime image and a recorded digest.

## Exercise 2: Container-aware JVM sizing

**Task.** Stop being OOMKilled with a healthy heap.

**Steps**
- Set MaxRAMPercentage instead of -Xmx.
- Instrument RSS, heap, metaspace and thread stacks.
- Run a burst and watch RSS against the limit.
- Adjust the percentage until there is headroom.

**Deliverable.** A memory breakdown with a safe percentage.

## Exercise 3: Health endpoints and readiness

**Task.** Do not send traffic to a cold JVM.

**Steps**
- Implement /healthz as a constant-time response.
- Gate /readyz on warm-up completion.
- Verify /healthz stays fast during model load.
- Add a deployment smoke test that waits for readyz.

**Deliverable.** A smoke test that proves readiness gating.

## Exercise 4: Batch inference

**Task.** Throughput without breaking the latency budget.

**Steps**
- Implement a bounded batch queue with a flush timer.
- Assert batched scores equal single scores.
- Sweep batch size and window; measure p99 and throughput.
- Pick the operating point from the budget.

**Deliverable.** A sweep table and a chosen operating point.

## Exercise 5: Warm-up and cold start

**Task.** Know where your 5 seconds go.

**Steps**
- Instrument JVM start, model load and warm-up separately.
- Run representative synthetic warm-up traffic.
- Verify the first user request is not an outlier.
- Write the cold-start budget into the deployment config.

**Deliverable.** A decomposed cold-start measurement.

## Exercise 6: Requests and limits from a load test

**Task.** Set them from evidence.

**Steps**
- Load test at 1x, 2x and 3x target QPS.
- Record p99 CPU, p99 RSS and p99 latency.
- Derive requests and limits.
- Verify no permanent throttling at 2x.

**Deliverable.** A sizing table derived from measurement.

## Exercise 7: Graceful reload

**Task.** Swap models without dropping requests.

**Steps**
- Load a new model in the background.
- Verify scores change only after readiness passes.
- Drain in-flight requests during the swap.
- Measure the reload's effect on p99.

**Deliverable.** A hot reload with no failed requests.

## Exercise 8: Reproducible build

**Task.** Make 'works locally' stop being acceptable.

**Steps**
- Pin base images by digest.
- Lock dependency versions.
- Build twice from clean and compare digests.
- Document the build command in the repo.

**Deliverable.** Two clean builds producing the same digest.


---

## Self-Check Before You Move On

- [ ] My runtime image is small enough to pull quickly.
- [ ] My container survives a burst without OOMKilled.
- [ ] The first request after deploy is not an outlier.
- [ ] Requests and limits come from a measurement, not a guess.
