# Model Serving with Docker - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | Why multi-stage Docker builds? | Compile with a JDK, ship only a JRE plus the artefact; the runtime image drops from ~450 MB to ~90 MB. |
| 2 | Why MaxRAMPercentage instead of -Xmx? | The JVM must size itself to the cgroup limit, so the same image works under any limit without rebuilding. |
| 3 | What lives outside the Java heap? | Metaspace, thread stacks, direct and mapped buffers, and native libraries, all of which count toward the container limit. |
| 4 | What should readiness include? | Warm-up completion. Otherwise the rollout sends real traffic to an uncompiled JVM. |
| 5 | What is the main throughput lever when serving? | Batching several examples into one inference, amortising the per-request overhead. |
| 6 | How do you choose the batch window? | From the latency budget: window plus inference must fit p99, so the window is pure added latency. |
| 7 | What should /healthz do? | Return quickly and cheaply. Never do model work or dependency calls in a liveness check. |
| 8 | How do you make image builds reproducible? | Pin the base image by digest and lock dependency versions. |
| 9 | What is Multi-stage builds? | Compile in a JDK stage, copy only the artefact into a JRE stage. |
| 10 | What is JVM flags in a container? | The JVM does not know the cgroup limit by default. |
| 11 | What is Warm-up is a latency requirement? | JIT compilation, class loading and lazy model initialisation make early requests slower. |
| 12 | What is The API is the product boundary? | POST /predict (single), POST /predict/batch (amortised), GET /healthz (liveness, cheap), GET /readyz (readiness, includes warm-up). |
| 13 | What is Batching is the main throughput lever? | Serving one example per request wastes the hardware. |
| 14 | What is Reproducible images? | Pin the base image by digest, pin the dependency lockfile, and record the image digest with every deployment. |
| 15 | In this lab, what does `RSS = heap + metaspace + threads x stack + direct` mean? | Memory model: all of it must fit the limit |
| 16 | In this lab, what does `heap_max = 0.70 x container_limit` mean? | Heap sizing: leaves headroom for the rest |
| 17 | In this lab, what does `throughput = batch / (latency + window)` mean? | Batching: amortised cost per example |
| 18 | In this lab, what does `cold_start = jvm + load + warmup` mean? | Startup budget: must fit the rollout window |
| 19 | In this lab, what does `p99_batch = p99_infer / batch + window` mean? | Latency with batching: the window is pure added latency |
| 20 | In this lab, what does `image_size = base + jre + app` mean? | Image budget: push time scales with size |
| 21 | You see 'Container OOMKilled with plenty of free heap' in production. What is the cause and the fix? | heap set too large relative to the limit, or native memory Fix: MaxRAMPercentage around 0.70 and monitor RSS, not just heap |
| 22 | You see 'First request after deploy takes 2 seconds' in production. What is the cause and the fix? | no warm-up behind the readiness probe Fix: warm with representative traffic before readyz passes |
| 23 | You see 'Images take 4 minutes to pull' in production. What is the cause and the fix? | JRE plus build tools in the runtime stage Fix: multi-stage build and a slim JRE base |
| 24 | You see 'p99 is 10x p50 under load' in production. What is the cause and the fix? | no batching, one inference per request Fix: batch with a window sized to the latency budget |
| 25 | You see 'Deploy works locally, fails in CI' in production. What is the cause and the fix? | unpinned base image or dependency Fix: pin by digest and lock the build |
| 26 | You see 'Heap dumps missing when the container dies' in production. What is the cause and the fix? | OOMKilled is external to the JVM Fix: enable heap dumps on error and capture container events, not just JVM flags |
| 27 | Which Java API is the backbone of: let the JVM size itself to the cgroup limit | `MaxRAMPercentage / UseContainerSupport` |
| 28 | Which Java API is the backbone of: a dependency-free serving surface for labs | `com.sun.net.httpserver.HttpServer` |
| 29 | Which Java API is the backbone of: bounded accumulation with a flush policy | `java.util.concurrent.ArrayBlockingQueue as a batch buffer` |
| 30 | Which Java API is the backbone of: capture evidence before the container is killed | `-XX:+HeapDumpOnOutOfMemoryError` |
| 31 | Which Java API is the backbone of: warm-up completion gates the readiness endpoint | `CountDownLatch / AtomicBoolean for readiness` |
| 32 | Why does Multi-stage builds matter operationally? | Compile in a JDK stage, copy only the artefact into a JRE stage. |
| 33 | Why does JVM flags in a container matter operationally? | The JVM does not know the cgroup limit by default. |
| 34 | Why does Warm-up is a latency requirement matter operationally? | JIT compilation, class loading and lazy model initialisation make early requests slower. |
| 35 | Why does The API is the product boundary matter operationally? | POST /predict (single), POST /predict/batch (amortised), GET /healthz (liveness, cheap), GET /readyz (readiness, includes warm-up). |
| 36 | Why does Batching is the main throughput lever matter operationally? | Serving one example per request wastes the hardware. |
| 37 | Why does Reproducible images matter operationally? | Pin the base image by digest, pin the dependency lockfile, and record the image digest with every deployment. |
| 38 | In the Model Serving with Docker pipeline, what happens next? Build a fat or thin artefact with a pinned dependency lockfi... | Build a fat or thin artefact with a pinned dependency lockfile. |
| 39 | In the Model Serving with Docker pipeline, what happens next? Multi-stage Dockerfile: compile with a JDK, run on a JRE wit... | Multi-stage Dockerfile: compile with a JDK, run on a JRE with MaxRAMPercentage. |
| 40 | In the Model Serving with Docker pipeline, what happens next? Implement /healthz and /readyz; readiness only passes after ... | Implement /healthz and /readyz; readiness only passes after warm-up. |
| 41 | In the Model Serving with Docker pipeline, what happens next? Add /predict and /predict/batch; batch with a short accumula... | Add /predict and /predict/batch; batch with a short accumulation window. |
| 42 | In the Model Serving with Docker pipeline, what happens next? Set requests from measured p99 and limits above measured pea... | Set requests from measured p99 and limits above measured peak plus headroom. |
| 43 | In the Model Serving with Docker pipeline, what happens next? Verify: reproducibility from a clean build, image size, cold... | Verify: reproducibility from a clean build, image size, cold-start time and load-test p99. |
| 44 | Exercise focus: Multi-stage Dockerfile | Cut the runtime image and keep the build reproducible. |
| 45 | Exercise focus: Container-aware JVM sizing | Stop being OOMKilled with a healthy heap. |
| 46 | Exercise focus: Health endpoints and readiness | Do not send traffic to a cold JVM. |
| 47 | Exercise focus: Batch inference | Throughput without breaking the latency budget. |
| 48 | Exercise focus: Warm-up and cold start | Know where your 5 seconds go. |
| 49 | Exercise focus: Requests and limits from a load test | Set them from evidence. |
| 50 | State the Container memory budget result for Model Serving with Docker. | Limit 1 GiB: heap at 0.70 = 717 MB, leaving 307 MB for metaspace (~80 MB), 200 threads x 1 MB stacks (200 MB), and buffers. Tight; use 0.65 or fewer threads. |
| 51 | State the Batching latency and throughput result for Model Serving with Docker. | Budget 50 ms, single-inference p99 12 ms. Window 10 ms gives p99 22 ms at b=1; window 25 ms with b=8 gives p99 37 ms and roughly 6x the throughput. Window 40 ms would breach the budget. |
| 52 | State the Cold start budget result for Model Serving with Docker. | JVM 0.6 s, model load 1.2 s, warm-up 3.0 s = 4.8 s. With a 5 s readiness period the rollout is marginal; trimming warm-up to 1.5 s gives 3.3 s and comfortable headroom. |
| 53 | State the Sizing requests from measurement result for Model Serving with Docker. | p99 CPU 0.4 cores at 500 QPS, p99 RSS 700 MB. Requests 0.4 CPU / 700 MB, limits 1 CPU / 950 MB: throttling only during bursts, and 250 MB of memory headroom for spikes. |
| 54 | Why does a container get OOMKilled with free heap? | Native memory (metaspace, thread stacks, direct buffers) exceeded the limit, so headroom must be left above the heap. |
| 55 | How do you find the cold-start budget? | Measure JVM start, model load and warm-up separately; the sum must fit the rollout window. |
| 56 | Should health checks call the model? | No: a liveness probe that does work creates cascading restarts under load. |
| 57 | What is a slim JRE image for? | Removing build tools and unneeded modules reduces pull time and attack surface. |
| 58 | Assumption / invariant to defend: The JVM is told the container limit, so MaxRAMPercentage is used rathe... | The JVM is told the container limit, so MaxRAMPercentage is used rather than -Xmx |
| 59 | Assumption / invariant to defend: Readiness covers warm-up, so the rollout does not shift startup cost t... | Readiness covers warm-up, so the rollout does not shift startup cost to users |
| 60 | Assumption / invariant to defend: Base images are pinned by digest for reproducibility... | Base images are pinned by digest for reproducibility |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
