# Model Serving with Docker

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

## 1. The Problem This Solves

A model that trains well and cannot be loaded, warmed and served reliably under load is not a model. Packaging is part of the deliverable.

Containers are the unit of deployment everywhere. Getting image size, JVM flags, warm-up behaviour and health endpoints right is the difference between a 300 MB artefact and a 90 MB one, and between a cold start that pages you and one that does not.

## 2. Learning Objectives

- Write a multi-stage Dockerfile that keeps the runtime image small
- Choose JVM flags appropriate for a container memory limit
- Design a prediction API with batch, single and health endpoints
- Implement warm-up so the first request is not an outlier
- Set resource requests and limits that match measured behaviour
- Containerise with cache-aware layering and verify reproducibility

## 3. Core Concepts

### 3.1 Multi-stage builds

Compile in a JDK stage, copy only the artefact into a JRE stage. The runtime image drops from ~450 MB to ~90 MB, which shortens pull time, reduces patch surface and makes cold starts predictable.

### 3.2 JVM flags in a container

The JVM does not know the cgroup limit by default. Set MaxRAMPercentage rather than -Xmx in absolute bytes, so the same image behaves correctly under any limit. Metaspace, thread stacks and direct buffers live outside the heap and must fit inside the limit.

### 3.3 Warm-up is a latency requirement

JIT compilation, class loading and lazy model initialisation make early requests slower. A readiness probe that fires before warm-up ends converts startup cost into user-visible latency. Warm up with representative synthetic traffic, not a single request.

### 3.4 The API is the product boundary

POST /predict (single), POST /predict/batch (amortised), GET /healthz (liveness, cheap), GET /readyz (readiness, includes warm-up). Keep health checks cheap and never do model work in them.

### 3.5 Batching is the main throughput lever

Serving one example per request wastes the hardware. Accumulate a small batch over a few milliseconds and score it together. The latency budget and the batch window are a single design decision.

### 3.6 Reproducible images

Pin the base image by digest, pin the dependency lockfile, and record the image digest with every deployment. 'It works on the build machine' is a packaging defect, not a mystery.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `RSS = heap + metaspace + threads x stack + direct` | Memory model | all of it must fit the limit |
| `heap_max = 0.70 x container_limit` | Heap sizing | leaves headroom for the rest |
| `throughput = batch / (latency + window)` | Batching | amortised cost per example |
| `cold_start = jvm + load + warmup` | Startup budget | must fit the rollout window |
| `p99_batch = p99_infer / batch + window` | Latency with batching | the window is pure added latency |
| `image_size = base + jre + app` | Image budget | push time scales with size |

## 5. How the Pieces Fit Together

1. Build a fat or thin artefact with a pinned dependency lockfile.

2. Multi-stage Dockerfile: compile with a JDK, run on a JRE with MaxRAMPercentage.

3. Implement /healthz and /readyz; readiness only passes after warm-up.

4. Add /predict and /predict/batch; batch with a short accumulation window.

5. Set requests from measured p99 and limits above measured peak plus headroom.

6. Verify: reproducibility from a clean build, image size, cold-start time and load-test p99.

## 6. Assumptions and Invariants

- The JVM is told the container limit, so MaxRAMPercentage is used rather than -Xmx
- Readiness covers warm-up, so the rollout does not shift startup cost to users
- Base images are pinned by digest for reproducibility
- Health endpoints are cheap and do no model work
- Batching window is chosen from the latency budget, not by feel
- Resource requests reflect measured behaviour, limits include headroom

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Container OOMKilled with plenty of free heap | heap set too large relative to the limit, or native memory | MaxRAMPercentage around 0.70 and monitor RSS, not just heap |
| First request after deploy takes 2 seconds | no warm-up behind the readiness probe | warm with representative traffic before readyz passes |
| Images take 4 minutes to pull | JRE plus build tools in the runtime stage | multi-stage build and a slim JRE base |
| p99 is 10x p50 under load | no batching, one inference per request | batch with a window sized to the latency budget |
| Deploy works locally, fails in CI | unpinned base image or dependency | pin by digest and lock the build |
| Heap dumps missing when the container dies | OOMKilled is external to the JVM | enable heap dumps on error and capture container events, not just JVM flags |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `MaxRAMPercentage / UseContainerSupport` | let the JVM size itself to the cgroup limit |
| `com.sun.net.httpserver.HttpServer` | a dependency-free serving surface for labs |
| `java.util.concurrent.ArrayBlockingQueue as a batch buffer` | bounded accumulation with a flush policy |
| `-XX:+HeapDumpOnOutOfMemoryError` | capture evidence before the container is killed |
| `CountDownLatch / AtomicBoolean for readiness` | warm-up completion gates the readiness endpoint |

## 9. Where This Sits in the Larger System

- **mlops/lab06** takes this image into Kubernetes and scales it.
- **mlops/lab03** decides which image version serves.
- **mlops/lab08** instruments the endpoints this lab serves.
- **labs/ml/lab10** is the evaluation contract a served model must keep.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Write a multi-stage Dockerfile that keeps the runtime image small
- [ ] 0 — cannot yet — Choose JVM flags appropriate for a container memory limit
- [ ] 0 — cannot yet — Design a prediction API with batch, single and health endpoints
- [ ] 0 — cannot yet — Implement warm-up so the first request is not an outlier
- [ ] 0 — cannot yet — Set resource requests and limits that match measured behaviour
- [ ] 0 — cannot yet — Containerise with cache-aware layering and verify reproducibility

## 11. Summary Checklist

- [ ] My runtime image is multi-stage and under 150 MB.
- [ ] The JVM knows the container limit and RSS stays inside it.
- [ ] Readiness passes only after warm-up.
- [ ] Batching is sized from the latency budget.
- [ ] Base image and dependencies are pinned.
- [ ] Resource requests come from measured behaviour.
