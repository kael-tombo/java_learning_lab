# PRODUCTION_SCENARIOS — 5 AWS-Java incidents that actually happen

All five use this lab's stack: catalog API on EKS + ALB → Aurora PostgreSQL Multi-AZ + ElastiCache Redis + MSK (or SQS), IRSA identity, Flyway pre-deploy Job, HPA on p99 + CPU, Graviton nodes. Each scenario follows the same shape: symptom → timeline → root cause → fix → prevention (what to add to the repo/runbook this week).

---

## 1. ALB drains live pods during deploy — liveness used as the target-group health check

**Symptom:** Every deploy causes a 2–4 minute 5xx spike (ALB `TargetConnectionError` / `HTTPCode_Target_5XX_Count` jumps), even though `kubectl rollout status` reports success. Between deploys the service is healthy.

**Timeline (typical 14:00 deploy):**

| Time | Event |
|---|---|
| T+0:00 | `kubectl apply` new image tag; ReplicaSet scales up 1 surge pod |
| T+0:45 | Surge pod passes **liveness** (`/actuator/health/liveness` = UP within seconds — JVM is alive, Hikari pool still warming) |
| T+0:50 | ALB target group marks surge pod **healthy**, starts routing; simultaneously old pod receives SIGTERM (maxSurge 1 / maxUnavailable 0 churns one at a time) |
| T+0:55 | Surge pod gets production traffic but its DB pool has 2/20 connections and Redis AUTH token mount hasn't refreshed → slow queries, `HikariPool - Connection is not available` timeouts → 500s |
| T+1:10 | Old (warm, healthy) pod deregisters (deregistration delay elapsed) → capacity drops while surge pod is still cold |
| T+1:10–4:00 | Cycle repeats per batch: cold pod serves, old pod dies, p99 climbs 150 ms → 2–4 s, HPA (CPU-only in this broken config) sees 40% CPU and does nothing |
| T+4:00 | Pools finally warm; error rate decays; team declares "deploy jitters, normal" |

**Root cause:** The ALB target-group health check (and the pod `readinessProbe`) pointed at **liveness instead of readiness**. Liveness answers "is the JVM alive?" — true seconds after startup. Readiness answers "can this pod serve?" — DB pool filled, Flyway-validated schema version matched, Redis reachable, warmup complete. Gating routing on liveness means every new pod receives traffic before it can handle it, and every old pod is killed while it is still the only warm capacity. Two compounding errors made it worse: `terminationGracePeriodSeconds: 30` shorter than the ALB deregistration delay, so in-flight requests were SIGKILLed; and HPA on CPU alone, which is blind to pool-starved saturation (threads parked → CPU low, latency exploding).

**Fix (during the incident):**

1. Halt the rollout: `kubectl rollout pause deploy/catalog-api`.
2. Re-point the ALB target-group health check to `GET /actuator/health/readiness`, healthy threshold 2 × 15 s, unhealthy 2 × 5 s (matches this lab's standard).
3. Verify pod spec: `readinessProbe` hits readiness with `initialDelaySeconds` covering pool warmup + `preStop` hook sleeping for the deregistration delay (`preStop: sleep 30` with deregistration delay 30 s, grace period 60 s).
4. Resume rollout one batch at a time; watch `HealthyHostCount` per AZ before allowing the next batch.

**Prevention:**

- Manifest policy (checked in CI): target-group health path must equal the pod readiness path; `maxUnavailable: 0, maxSurge: 1`; `minAvailable: 2` PodDisruptionBudget; readiness must include custom `ReadinessIndicator`s for DB pool (`HikariPoolMXBean`) and Redis ping — not just framework defaults.
- Exercise 2 in EXERCISES.md is exactly this drill: black-hole the DB, roll, and prove ALB keeps old pods while new pods sit `OutOfService`. Run it before every pipeline change.
- HPA on p99 latency AND CPU (CODE_DEEP_DIVE §3) so cold-pod saturation scales instead of festering.

---

## 2. Aurora failover at 03:12 — then a DNS-cache storm doubles the outage

**Symptom:** Aurora Multi-AZ writer fails over (AZ event). Expected RTO ~30–60 s. Actual: 8 minutes of `PSQLException: connection refused / connection timed out` plus a secondary wave of `Too many connections` on the freshly promoted writer.

**Timeline:**

| Time | Event |
|---|---|
| 03:12:00 | Writer AZ impairment; Aurora begins failover; cluster endpoint DNS flips to the promoted reader (~15–30 s for DNS propagation) |
| 03:12:30 | App pods keep dialing the **old writer IP**: JVM caches DNS (default `networkaddress.cache.ttl` effectively infinite in many container images / `InetAddress` cache), Hikari pools hold stale sockets, half-open connections sit in `ESTABLISHED` until TCP timeout |
| 03:13–03:16 | Each pod's pool exhausts its stale connections one by one; retries pile up; p99 → timeout; ALB marks pods sick — but readiness still returns UP (DB check uses a cached connection), so sick pods keep receiving traffic |
| 03:16 | Caches finally expire / pools cycle; **all ~40 pods reconnect simultaneously** with full pool size (20 each = 800 connections) against a cold promoted writer whose `max_connections` is 500 → connection storm, new failures |
| 03:20 | On-call kills half the pods (forced pool reset + staggered reconnect), raises `max_connections` via parameter group, restores service |

**Root cause:** Three layers, all classic: (a) JVM DNS caching defeated Aurora's DNS-based failover — the cluster endpoint changed but the JVM didn't re-resolve; (b) HikariCP `maxLifetime` longer than failover time plus no `connectionTimeout`/`validationTimeout` tuning, so stale sockets lingered; (c) no reconnect jitter — every pod re-established its full pool at once (thundering herd on a cold buffer cache).

**Fix:**

1. Set JVM DNS TTL low for RDS endpoints: `-Dnetworkaddress.cache.ttl=5 -Dnetworkaddress.cache.negative.ttl=5` (or `security.properties`), so re-resolution happens within seconds.
2. HikariCP hardening: `maxLifetime` ≤ 5 min, `connectionTimeout` 3 s, `validationTimeout` 2 s, `connectionTestQuery` or JDBC4 validation, `keepaliveTime` 30 s. Readiness indicator must open a **fresh** validation query, not reuse a pooled idle connection.
3. Stagger recovery: restart deployment in batches (or rolling restart with `maxUnavailable: 1`) so pools refill gradually; enable Aurora reader-endpoint reads for read-only traffic so only writes need the new writer.

**Prevention:**

- Failover game-day quarterly: trigger `aws rds failover-db-cluster`, measure true RTO (endpoint flip → p99 recovered) and record it; assert ≤ 60 s or fix TTL/pool settings until it is.
- CloudWatch alarms on `DatabaseConnections` (warn at 70% of max) + `FailoverState` events → SNS → runbook, so the storm is caught at the connection-count ramp, not at user-facing 500s.
- PITR drill (EXERCISES §3) covers data loss (RPO); this drill covers **connectivity loss** (RTO). Both go in the runbook — passing one does not prove the other.

---

## 3. MSK consumer-lag death spiral — one slow deploy, then rebalances finish the job

**Symptom:** Catalog price-update events lag grows from seconds to 40+ minutes after a routine deploy. Consumer group rebalances every few minutes. Throughput never recovers even after traffic drops — classic death spiral.

**Timeline:**

| Time | Event |
|---|---|
| D-1 | New catalog-api version adds a synchronous enrichment call (Redis + DB) per event, raising per-record processing from ~8 ms to ~45 ms. Load test covered HTTP p99, not consumer throughput. Nobody recomputes consumer capacity. |
| D-day 10:00 | Deploy rolls; consumers restart; partitions rebalance (cooperative-sticky, but 60 s `max.poll.interval.ms` exceeded during startup warmup → members judged dead → second rebalance). |
| 10:15 | Lag builds: produce rate 1,200 msg/s × 45 ms ≈ 54 consumer-threads needed; group has 24 threads → utilization > 100%, lag grows linearly. |
| 10:20 | HPA (HTTP-latency driven) sees normal HTTP p99 and doesn't scale consumers (separate Deployment, no lag-based scaling). |
| 10:30 | `max.poll.records` still 500 → each poll takes 22 s, fetch heartbeats starve, more `LeaveGroup` / rebalance storms; lag 25 min. |
| 11:00 | On-call adds partitions' worth of consumers manually — but new members trigger *another* full rebalance, pausing all consumption for minutes. Lag 40 min. |

**Root cause:** Consumer capacity is a separate scaling dimension from HTTP capacity, and it was scaled by vibes. The deploy raised per-record cost ~5×; the poll loop (`max.poll.records: 500`, `max.poll.interval.ms: 60 s`) couldn't sustain it; rebalances (triggered by slow polls being mistaken for dead members) stopped the world repeatedly. Manual scale-out during a rebalance storm made it worse.

**Fix (in order):**

1. Stop the rebalance storm first: raise `max.poll.interval.ms` (e.g., 300 s), lower `max.poll.records` (e.g., 50–100) so no poll exceeds the interval, confirm `session.timeout.ms` < interval. Rolling-restart consumers one at a time.
2. Scale consumers to the math: `threads ≥ produce_rate × per_record_s / target_util` → 1,200 × 0.045 / 0.7 ≈ 78 threads across ≤ partition-count members. Temporarily raise replicas (partition count is the ceiling — you can't out-scale partitions).
3. Revert or async the enrichment call (the 8 ms → 45 ms regression) or move it off the poll thread (hand to a worker pool so polling/heartbeating continues).

**Prevention:**

- Consumer autoscaling on **lag**, not HTTP: KEDA `kafka` scaler (or CloudWatch `KafkaConsumerLag` → Application Auto Scaling) targeting lag-per-partition; alert on `ConsumerLag > 10k for 10 min` and rebalance rate.
- Deploy guardrail: any change touching the consumer path must report per-record processing time (JFR / Micrometer `kafka.consumer.process` timer) in the PR, and the capacity formula is recomputed — same discipline as HPA arithmetic in MATH_FOUNDATION §4.
- Decision checkpoint from ARCHITECTURE.md: if the workload is task distribution without replay needs, SQS (with per-queue visibility-timeout + DLQ + lag-native scaling) avoids partition-ceiling and rebalance failure modes entirely. MSK earns its broker ops only when replay/compaction justify them.

---

## 4. IRSA outage after the EKS cluster upgrade — every AWS call 403s at once

**Symptom:** Morning after EKS 1.29 → 1.30 upgrade (managed via CDK): catalog API pods start, readiness flaps, all AWS SDK calls fail — Secrets Manager (`AccessDenied`), SQS (`AccessDenied`), ECR pull on new nodes fails. `aws sts get-caller-identity` from a debug pod returns the **node role**, not `catalog-api`. No application code changed.

**Timeline:**

| Time | Event |
|---|---|
| Day before 17:00 | Cluster upgrade applied by pipeline; nodes replaced; OIDC provider thumbprint/issuer URL rotates as part of the upgrade (new OIDC issuer endpoint). |
| Night | New nodes join; old pods keep running on cached credentials — no visible impact. |
| 06:30 | Natural pod churn (HPA scale-in + deploy) creates fresh pods; fresh pods fetch web-identity tokens from the **new** issuer. |
| 06:35 | IAM role trust policy still pins the **old** OIDC issuer URL (`oidc.eks.<region>.amazonaws.com/id/OLD...:sub`). `AssumeRoleWithWebIdentity` → 403. SDKs fall back to node-role credentials (IMDS) → Secrets/SQS denied (node role has no such grants, by design). Readiness (DB password from Secrets) fails → ALB drains pods → cascading 5xx. |
| 07:10 | On-call reads the trust-policy condition, spots the stale issuer ID, updates CDK OIDC provider + role trust, redeploys stack; pods recover as tokens validate again. |

**Root cause:** IRSA trust is a three-way binding — EKS OIDC provider ↔ IAM role trust policy (`StringEquals` on issuer + `sub` = serviceaccount name) ↔ pod ServiceAccount annotation. The upgrade rotated one leg (issuer) while IaC pinned the old value; the trust policy silently stopped matching. Because failure mode is "valid token, untrusted issuer," the error surfaces as a generic 403 deep in SDK calls, not as a clear "IRSA broken" signal — and the node-role fallback masks it further.

**Fix:**

1. `aws eks describe-cluster` → current `identity.oidc.issuer`; compare byte-for-byte with the IAM role trust policy (`aws iam get-role --role-name catalog-api`). Update the CDK stack's OIDC provider + trust condition; `cdk deploy`.
2. Restart affected pods (new projected tokens validate immediately once trust matches).
3. Verify the lab's IRSA proof (EXERCISES §1): debug pod `sts get-caller-identity` must show the `catalog-api` role ARN, not the node role.

**Prevention:**

- Manage the OIDC provider **in the same CDK stack as the cluster** (never a hand-created provider), so upgrades rotate issuer and trust atomically. CI check after any cluster-version bump: `issuer(cluster) == issuer(trust policy)` for every IRSA role.
- Alarm on the proxy signal: CloudTrail `AssumeRoleWithWebIdentity` failures + app-level `AccessDenied` rate; readiness must fail fast on secret-fetch errors so ALB stops routing instead of serving 500s.
- Pre-upgrade runbook step (REAL_WORLD_PROJECT ops list): snapshot issuer URL + all IRSA role trust policies, upgrade in staging, re-run the IRSA proof before promoting. Static keys would have "survived" the upgrade — and that is exactly why they are dangerous: they'd also survive an employee's laptop theft. IRSA's explicit binding is the feature.

---

## 5. Graviton migration reveals a crypto-path regression — 20% cheaper nodes, 3× slower TLS handshakes

**Symptom:** EKS node group migrated m7i (x86) → m7g (Graviton) for the advertised ~20% saving. Bill drops. Then p99 climbs 180 ms → 450 ms at peak, ALB target response time confirms server-side, CPU utilization *lower* than before. Rolling back to x86 "fixes" latency. Team concludes "Graviton is slower for Java" — wrong conclusion.

**Timeline:**

| Time | Event |
|---|---|
| Week 1 | m7g node group added, pods scheduled on ARM; throughput test at low concurrency looks equal-or-better (matches the "JVM-neutral" expectation in MATH_FOUNDATION §1). Migration approved. |
| Week 2 (peak) | At 5× baseline with mTLS-heavy service-mesh sidecars + Redis TLS + Aurora TLS, p99 degrades. Profiles (JFR, async-profiler) show 35% of request time in `sun.security` ECDSA/RSA + AES-GCM paths. |
| Investigation | JDK version pinned to an older 17.0.x without the ARM crypto intrinsics backports; the x86 path used AES-NI / PCLMULQDQ intrinsics, the ARM path fell back to pure-Java xxtea/GCM loops. Same bytecode, wildly different intrinsic coverage. One dependency (old Netty tcnative / BouncyCastle version) also lacked `arm64` native bindings and loaded the portable fallback. |
| Proof | Upgrade to latest JDK 17.0.latest (or 21) + update tcnative/BouncyCastle to arm64-capable versions; rerun the lab-53 benchmark matrix (throughput + p99 + $/M-req) on m7g vs m7i at equal pod specs. Result: m7g p99 back to ~170 ms, cost-per-M-requests ~18% lower. |

**Root cause:** "Arch-neutral JVM" is true for allocation/GC/interpreter — it is **not** automatically true for crypto intrinsics and JNI native bindings. x86 AES-NI/SHA-NI fast paths have ARM equivalents (NEON/crypto extensions), but only recent JDKs emit them reliably, and native libraries must ship `arm64` artifacts. The migration benchmarked steady-state throughput (JIT-warmed, low-TLS) instead of the production mix (TLS everywhere), so the regression hid until peak.

**Fix:**

1. Pin current JDK micro version + set `-XX:+UseAES -XX:+UseAESIntrinsics -XX:+UseSHA` explicitly (defaults on, but explicit survives flag audits), verify with `-XX:+PrintIntrinsics` / JFR `jdk.JVMInformation` that AES/SHA intrinsics fire on the m7g nodes.
2. Upgrade native crypto providers (tcnative, BouncyCastle, Conscrypt if used) to versions with `linux-aarch64` classifiers; fail the Docker build if the fallback classifier loads (log-grep in CI).
3. Keep mixed-arch node groups during validation (taints/tolerations per arch) so rollback is a reschedule, not a rebuild.

**Prevention:**

- The Graviton verdict exercise (EXERCISES §5) *requires* the crypto-heavy benchmark before committing — throughput + p99 + $/M-req at peak TLS mix, not a hello-world load test. That exercise exists because of incidents exactly like this one.
- Image pipeline builds multi-arch (`linux/amd64,linux/arm64`) from day one; CI runs the benchmark matrix on both; node recommendation is data (the table), not a slogan.
- JVM flags at scale (see BIG_TECH_FEEDBACK.md): standardize flags per arch in the Helm/CDK values file and diff them in PRs — a JDK minor bump changing intrinsic behavior should be as visible as a code change.

---

## Common threads (read once, apply five times)

1. **Gate on readiness, scale on saturation, migrate on proof** — every incident above is a violation of one of those three. The lab's defaults (readiness-gated ALB, p99+CPU HPA, benchmark-before-Graviton) are the scar tissue.
2. **Failover, rollback, and restore are three different drills.** PITR proves RPO; DNS/pool tuning proves RTO; previous-tag rollback proves deploy recovery. Schedule all three; passing one proves nothing about the others.
3. **Identity and capacity are load-bearing config.** IRSA trust bindings and consumer-thread math deserve the same PR review rigor as Java code — they page you at 06:30 either way.
