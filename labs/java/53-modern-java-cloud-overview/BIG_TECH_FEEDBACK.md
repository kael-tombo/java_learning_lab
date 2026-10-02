# BIG_TECH_FEEDBACK — What Running JVMs at Scale Taught Netflix, Amazon, Google, Uber, and LinkedIn

Synthesized, not quoted: public engineering-blog consensus from these shops, reframed as principles for the catalog API in this lab series. Each principle states the *rule*, then the *reasoning* (why scale forced it). Where shops disagree, the disagreement is the lesson.

---

## 1. Netflix — "Size the container from measured non-heap, not from hope."

**Principle:** Derive `MaxRAMPercentage` from production N (metaspace + direct + stacks + code cache + agent overhead), re-derive it every JDK/framework/agent change, and enforce it in CI with a fit-proof.

**Reasoning:** Netflix runs thousands of JVM containers and learned that heap is the * negotiable* part — everything else is close to fixed per build. APM/JFR/profiling agents alone can add tens of MB of N; a Spring upgrade moves metaspace. Copying one service's f to another (or one limit to a smaller one) is how MATH_FOUNDATION's inequality bites at 3 AM. Their answer was paved-road base images with known N budgets plus automated rightsizing — the same discipline as EXERCISES.md #1, industrialized. Takeaway for this lab: the `f ≤ 1 − N/L` computation is a living artifact, checked into the repo next to the Dockerfile, not a wiki number.

## 2. Amazon — "Boring portability pays; sharp edges earn their lock-in one service at a time."

**Principle:** Keep 80% of the service cloud-agnostic (standard runtimes, OTel, health endpoints) and let each team consciously buy into managed primitives (DynamoDB, Aurora, SQS) only where the operational math wins — with an export path tested before adoption.

**Reasoning:** Amazon's own teams run on AWS primitives *and* maintain portable cores, because the cost of accidental lock-in shows up years later as migration paralysis, while the cost of refusing managed services shows up immediately as undifferentiated ops load. This is VISION.md's "boring core, isolated sharp edges" at org scale: the decision is per service, written down, with the exit drill priced (REAL_WORLD_PROJECT.md acceptance). For the catalog API: Postgres-behind-a-port locally, Aurora/RDS in lab 54 only behind the repository interface, with a timed export rehearsal.

## 3. Google — "Latency is a GC problem before it is a code problem; pick the collector for your p99, then cap its threads."

**Principle:** G1 is the default workhorse; ZGC (sub-millisecond pauses, generational since JDK 21) earns its place on latency-critical paths — but *either* collector must have thread counts (`ConcGCThreads`, `ParallelGCThreads`, `ActiveProcessorCount`) derived from the CPU you actually get under cgroup limits, and tail-latency SLOs must be measured under CPU contention, not on idle nodes.

**Reasoning:** Google's Java shops (and the G1/ZGC authors' production feedback they absorb) found the same shape as PRODUCTION_SCENARIOS.md #4: pauses stretch under throttle, and throughput collectors on shared tenants trade p99 for averages. ZGC's concurrent compaction removes most stop-the-world time but costs more CPU headroom — a trade worth making for checkout/catalog reads at p99 < 300 ms, not for nightly batch. Lesson: collector choice is a workload decision with a latency budget attached, and the load test must include the noisy neighbor.

## 4. Uber — "Standardize the image, the flags, and the signals — then let teams move fast inside the guardrails."

**Principle:** One paved-road Dockerfile (layered, non-root, cgroup-aware flags), one observability bundle (JSON logs, RED metrics, OTel traces, JVM/JFR signals), one set of required dashboards/alerts — mandatory; everything else (framework, libraries) is team choice.

**Reasoning:** Uber's scale forced the realization that JVM fleet problems are *fleet* problems: a thousand bespoke Dockerfiles means a thousand wrong `MaxRAMPercentage`s and a thousand missing readiness probes. Standardizing the container contract (THEORY.md §1) and the observability API (THEORY.md §4) converts incidents into platform fixes: patch the base image once, every service inherits it. Their Go/Java polyglot experience adds the corollary — the standard must be runtime-aware (JVM flags ≠ Go flags), not a single lowest-common-denominator template. For this lab: the CODE_DEEP_DIVE skeleton *is* the paved road; labs 54–56 differ only in where the signals land (CloudWatch / Cloud Monitoring / App Insights).

## 5. LinkedIn — "Virtual threads for the many, reactive discipline for the few — and measure pinning before you preach about it."

**Principle:** Default to blocking code on virtual threads for I/O-bound services (CRUD, catalog reads, `JdbcTemplate`/`RestClient`); reserve reactive/backpressure machinery for genuine stream-shaping (ingest pipelines, rate-limited fan-out). Audit `synchronized` hot paths with JFR (jdk.VirtualThreadPinned events) and replace with `ReentrantLock` only where pinning actually shows up.

**Reasoning:** LinkedIn's high-throughput Java services validated the THEORY.md §3 bet at scale: virtual threads collapse the old "reactive for throughput" mandate, and simpler blocking code is cheaper to hire for, review, and debug. But they also learned the pinning caveat is empirical, not dogmatic — most `synchronized` blocks are short and harmless; the fix belongs where the flight recorder says carriers actually stall. Lesson: adopt virtual threads as the default, keep reactive skills for the edges, and let JFR settle arguments.

## 6. Consensus — "Observability is a deploy gate, not a dashboard afterthought."

**Principle (all five, unanimously):** No service is production without end-to-end traces, RED metrics per endpoint, structured logs correlated by trace ID, and profiler/JFR access — wired before the first real deploy, with alerts on *user-facing* signals (p99, error budget burn) rather than machine signals (CPU %).

**Reasoning:** Every shop burned by "metrics looked fine, users were down" converged here: CPU/memory dashboards miss throttling (scenario #4), retry storms (scenario #3), and poison paths that are fast on average and catastrophic at p99. The VISION.md production bar (traced requests, signal autoscaling, cost attribution) is the distilled version. Practical form for the catalog API: OTel + Micrometer from day one, readiness/liveness gating every rollout, and an error-budget alert that pages before the bill or the timeline in PRODUCTION_SCENARIOS.md does.

## 7. Consensus — "Build the platform, buy the undifferentiated heavy lifting."

**Principle:** Build internal platforms (base images, flag standards, deploy pipelines, cost dashboards); buy managed data, CDN, and observability backends unless you are in the business of running them.

**Reasoning:** Netflix/Amazon/Google/Uber/LinkedIn all run large internal platforms *on top of* managed or specialized infrastructure — none hand-rolls databases for CRUD services anymore. The build-vs-buy line sits exactly at VISION.md's managed-service gravity: buy the database/CDN/trace backend (their economies of scale crush yours), build the thin adapter + portability seam so the purchase stays reversible. The COST_REALITY.md models assume this split: compute is yours to optimize (JVM/native/CRaC, ARM, rightsizing); data durability and global bytes are bought.
