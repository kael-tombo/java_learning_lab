# INTERVIEW — 12 Senior/Staff Cloud-Java Q&A

How to use: answer aloud first, then open the `<details>`. A senior/staff candidate nails the *trade-off and the number*, not just the term.

## 1. Why `-XX:MaxRAMPercentage` instead of `-Xmx` in containers?

<details><summary>Answer</summary>Fixed <code>-Xmx</code> ignores the cgroup limit: the same image OOMs in small containers and wastes large ones. <code>MaxRAMPercentage</code> computes heap as f·L from the live limit, leaving room for non-heap (metaspace, direct, stacks, code cache, agents). The deployable artifact pairs the flag with a per-limit fit-proof (<code>heap + measured N ≤ L</code>) — see MATH_FOUNDATION §1 and scenario #1.</details>

## 2. You halve a container limit from 2 GiB to 1 GiB and pods start OOMKilling. The flag didn't change. What happened, exactly?

<details><summary>Answer</summary><code>f ≤ 1 − N/L</code>: non-heap N (~250–350 MiB) doesn't shrink with L, so the safe heap fraction falls as L falls. At 2 GiB, f=75% leaves ~200+ MiB headroom; at 1 GiB the same f leaves almost none, and any direct-buffer or metaspace spike breaches the cgroup. Fix: re-measure N (NMT/JFR), lower f (≈55–60% at 1 GiB), cap metaspace/direct explicitly, and soak-test at the new limit.</details>

## 3. Liveness vs readiness — what breaks if you only configure liveness?

<details><summary>Answer</summary>Liveness means "restart me if deadlocked"; readiness means "route to me only when I can serve (dependencies up, migrations done, warm)". With liveness alone, rolling deploys route traffic to pods whose DB/queue isn't reachable, and rollbacks of bad-config deploys can't halt — the orchestrator kills healthy old pods while new ones accept traffic they can't serve. Readiness gates both rollout and rollback; scenario #5's stuck deploy is the cautionary tale.</details>

## 4. Walk me through the JVM memory math you'd do before approving a 512 MB limit for a Spring Boot service.

<details><summary>Answer</summary>Measure N first: metaspace (~100–150 MiB Spring) + direct (JDBC/driver buffers) + thread stacks (count × size; virtual threads shift this to heap/queues) + code cache + agent overhead ≈ 250 MiB floor. Then f ≤ 1 − 250/512 ≈ 50%. So heap ≈ 256 MiB max, and I'd demand a load + import soak proving no OOMKilled and GC time < 5%, plus alerts at 85% working-set. If the service can't live in ~256 MiB heap, the limit is wrong, not the flag.</details>

## 5. When do virtual threads replace reactive code, and when do you keep reactive?

<details><summary>Answer</summary>Virtual threads (1M+ cheap, carrier-mounted) let plain blocking code (<code>JdbcTemplate</code>, <code>RestClient</code>) saturate I/O — they erase the old "go reactive for throughput" mandate for CRUD/RPC services like the catalog API. Keep reactive only where backpressure shaping, bounded-queue stream control, or an existing reactive ecosystem genuinely needs it (ingest pipelines, rate-limited fan-out). Caveat: <code>synchronized</code> pins carriers — prefer <code>ReentrantLock</code> on hot paths, verified with <code>jdk.VirtualThreadPinned</code> JFR events rather than by dogma.</details>

## 6. Compare JVM, GraalVM native, and CRaC for a staff-level runtime decision. No religion — give me the decision rule.

<details><summary>Answer</summary>JVM: 2–10 s start, zero constraints, full dynamism (agents, reflection, JFR) — default for steady services. Native: ~50–200 ms, ~½ RAM, closed-world (reflection/resource config, slower builds) — for bursty/scale-to-zero where λ·(S<sub>j</sub>−S<sub>n</sub>)·mem·p exceeds pipeline cost. CRaC: ~ms restore with full JVM semantics — when you need fast start <em>plus</em> dynamism (agents, heavy reflection). Rule: one codebase can ship two artifacts; choose per workload (steady core = JVM, spike edges = native/CRaC), and price engineering hours alongside the bill.</details>

## 7. Your p99 triples every 15 minutes with flat RPS. Metrics show low CPU. Walk me through your diagnosis.

<details><summary>Answer</summary>Classic throttling signature (scenario #4): low <em>observed</em> CPU because CFS quota caps usage. Check <code>container_cpu_cfs_throttled_seconds_total</code>, GC pause p99, and carrier-blocked time against the spike windows; confirm G1/parallel threads vs <code>ActiveProcessorCount</code> under the limit. Fix: raise/remove CPU limits (keep requests for scheduling), derive GC thread counts from the request, move the hot path to a dedicated pool, and autoscale on latency/queue signals instead of CPU%.</details>

## 8. How do you design health-gated deploys and a rollback that actually works with database migrations?

<details><summary>Answer</summary>Readiness probes (DB reachable, migrations applied, warm) gate every rollout step; liveness stays narrow (deadlock detector) so it can't flap during slow starts. For the DB: expand-migrate-contract — ship backward-compatible (expand) migrations separately from the code that uses them, keep N−1 runnable against the migrated schema, and only later ship contract (NOT NULL/drop) migrations. Prove it with a staging rollback drill per risky release, PITR-tested restore (RPO ≤ 5 min / RTO ≤ 30 min), and a feature-flag kill-switch so bad logic can be disabled without a schema rollback.</details>

## 9. Sketch the observability stack you'd mandate for every Java service, and the alert you'd page on.

<details><summary>Answer</summary>JSON logs to stdout (trace-correlated), Micrometer RED metrics per endpoint, OpenTelemetry W3C traces end-to-end, JFR/flight-recorder on demand — identical bundle on every service (the paved road), shipped to CloudWatch / Cloud Monitoring / App Insights per cloud (labs 54–56). Page on user-facing burn: p99 latency and error-budget consumption per endpoint; never on CPU% alone. Require traces visible in the cloud console as a deploy gate — untraced deploys don't ship.</details>

## 10. Your cloud bill jumps 10× in a month. The service is Java, throughput is fine, and nobody deployed a bigger fleet. Where do you look first?

<details><summary>Answer</summary>Transfer and data before compute: egress (proxied bytes? missing CDN? cross-region/AZ chatter?), then managed-service meters (IOPS, backup retention, un-sampled trace/log ingest). Throughput looking fine is consistent with virtual threads happily pumping expensive bytes (scenario #2). Process: per-service cost attribution dashboard with anomaly alerts, top-talkers by GB-out, cache-hit/CDN-offload ratios, and a rule that bulk bytes never flow through JVM pods (signed URLs + CDN).</details>

## 11. Lay out a multi-cloud strategy for this catalog API that a staff engineer would defend — and where you'd deliberately accept lock-in.

<details><summary>Answer</summary>Portable core (Jakarta/MicroProfile, 12-factor env config, OTel, standard SQL, repository ports) plus one isolated adapter module per cloud for IAM, managed Postgres, queues, and IaC — labs 54–56 own exactly one sharp edge each. Accept lock-in consciously per service where the ops math wins (e.g., Aurora/AlloyDB for the catalog store, CDN + WAF, managed trace backend), but only with an export-tested backup and a timed repoint drill. The scorecard (compute/container/serverless/data/messaging/observability/identity/IaC, weighted by requirements) is the decision artifact; "runs anywhere" is proven by the exit drill, not asserted.</details>

## 12. Size the fleet and the bill: 5k RPS average, 60 ms mean latency, 200 RPS per pod. How many pods, and what breaks first at 5× load?

<details><summary>Answer</summary>Little's law per pod: ~12 concurrent in flight — easy. Pods ≈ 5000/200 = 25 + headroom + HA ≈ 30 average; at 5× (25k RPS) ≈ 150 pods. What breaks first is rarely the JVM threads (virtual threads absorb concurrency) — it's the downstream: DB connections/pool saturation, then CPU-throttle-induced GC pauses, then egress/DB-IOPS cost. So the answer pairs the count with: PgBouncer/pool sizing, read replicas, latency-signal autoscaling, and the cost re-derivation (COST_REALITY.md method) before the load arrives.</details>
