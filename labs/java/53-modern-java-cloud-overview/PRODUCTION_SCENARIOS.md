# PRODUCTION_SCENARIOS — 5 Incidents That Teach Cloud Java

Each scenario follows the same shape: **timeline → root cause → fix → prevention checklist**. All five are set on the lab-05 catalog API running the CODE_DEEP_DIVE skeleton (layered non-root image, `MaxRAMPercentage`, actuator probes, env-only config).

---

## 1. OOMKilled at 3 AM — the copied `MaxRAMPercentage`

**Setup:** Catalog API ran clean for months at a 2 GiB limit with `MaxRAMPercentage=75.0` (heap ≈ 1.5 GiB, non-heap N ≈ 300 MiB, headroom ≈ 200 MiB). To "save money," the team halved the limit to 1 GiB — same image, same flag.

**Timeline:**

| Time | Event |
|------|-------|
| 14:00 | Limit lowered 2 GiB → 1 GiB in the Helm values; no flag change. |
| 22:00 | Evening batch raises heap demand; GC time climbs 2% → 15%. |
| 02:47 | First `OOMKilled` (exit 137) on pod-3 during a promotion import. |
| 03:05 | All 4 pods crash-looping; readiness gates traffic, catalog reads 503. |
| 03:40 | On-call bumps limit back to 2 GiB; service recovers. |

**Root cause:** The MATH_FOUNDATION inequality was violated. Heap = 0.75 × 1 GiB = 768 MiB, but N (metaspace + direct buffers from the JDBC driver + thread stacks on virtual threads + code cache) still ≈ 300 MiB — and the import spiked direct memory past it. 768 + 350 > 1024. Smaller L needs *smaller* f because N does not shrink proportionally; copying f=75% into a 1 GiB (or 512 MiB) limit is the #1 OOMKilled cause in this lab series.

**Fix:**

```yaml
# values for L=1Gi: drop f to ~55-60%, cap metaspace/direct explicitly
env:
- name: JAVA_OPTS
  value: "-XX:MaxRAMPercentage=55.0 -XX:MaxMetaspaceSize=160m -XX:MaxDirectMemorySize=128m -XX:+UseG1GC -XshowSettings:system"
```

Plus: verified with `java -XshowSettings:system` inside the image and a soak test at the real import size.

**Prevention checklist:**

- [ ] Every limit change recomputes `f ≤ 1 − N/L` from a *measured* N (JFR / `NativeMemoryTracking`), never a copied flag.
- [ ] Container-fit proof (EXERCISES.md #1) is a deploy gate: OOM-free soak at the new limit before merge.
- [ ] Alert on `container_memory_working_set / limit > 0.85` AND on GC-time ratio, not just restarts.
- [ ] Keep the 2 GiB load-test profile in CI so a limit edit fails the build if it OOMs.

---

## 2. The $40k egress surprise — thumbnails served from the wrong region

**Setup:** Catalog API served product images via presigned URLs — but the fallback path streamed thumbnails *through* the Java pods (blocking I/O on virtual threads, so throughput looked fine). Mobile clients were global.

**Timeline:**

| Time | Event |
|------|-------|
| Week 1 | Launch in `us-east-1`; image CDN ticket deferred as "optimization." |
| Week 3 | Marketing campaign in EU/APAC; thumbnail traffic 10×. |
| Week 5 | Finance flags a $38k line item: cross-region + internet egress at ~$0.09/GB on ~400 TB of thumbnail bytes proxied through the pods. |
| Week 6 | Fix ships: signed CloudFront/S3 (or Cloud CDN/GCS, Azure CDN/Blob) URLs; pods return redirects, bytes never touch the JVM. Bill drops to ~$3k CDN. |

**Root cause:** The cost model in MATH_FOUNDATION §4 was computed on compute only; nobody priced `data × transfer`. Proxied binary bytes are the worst of both worlds: you pay egress *and* container CPU/memory to pump them. Virtual threads hid the throughput symptom (no thread starvation) while the meter ran.

**Fix:** Origin bucket + CDN; API returns 302 signed URLs with short TTLs; cache `Cache-Control: public, max-age=86400, immutable` on thumbnails; delete the streaming endpoint or restrict it to admin preview.

**Prevention checklist:**

- [ ] Cost attribution per service *including* transfer (VISION.md production bar) — dashboarded from day one, with an anomaly alert at 2× weekly burn.
- [ ] Architecture rule: JVMs serve JSON/redirects, never bulk bytes. Any endpoint returning `image/*` or `application/octet-stream` needs a written egress justification.
- [ ] CDN in front of every public read path before any marketing event; load test measures GB out, not just RPS.
- [ ] Multi-AZ transfer reviewed too: chatty cross-AZ DB/cache calls bill at ~$0.01/GB each way and add up silently.

---

## 3. Cold-start cascade on Black Friday — scale-from-zero meets JVM startup

**Setup:** "Deals" webhook handler on scale-to-zero serverless (Knative/Cloud Run/ACA Jobs style): classic Spring JVM, cold start 4–8 s, concurrency-per-instance 80, min-replicas 0 to save money. Traffic 20 RPS steady, 3,000 RPS spikes on deal drops.

**Timeline:**

| Minute | Event |
|--------|-------|
| 0 | Deal drop; 3,000 RPS arrives in 10 s. |
| 0–1 | Autoscaler requests 40 instances; each takes ~6 s to first readiness-OK. |
| 1–3 | Queue depth explodes; readiness-gated instances join too late; latency p99 12 s; retries double the load (λ effectively 2×). |
| 3–6 | Partial recovery as warm pool forms; then the next drop repeats the cascade. |
| +1 day | Postmortem: expected waste ≈ λ·S·mem·p was computed for *average* λ, not spike λ. |

**Root cause:** Steady-state math applied to a bursty workload. With S_j ≈ 6 s and min-scale 0, every spike pays the full startup penalty *serially before serving*. Retries amplified λ. Readiness probes behaved correctly (refused traffic until warm) — but there was nothing warm to route to.

**Fix (pick per path, matching THEORY.md §2):** GraalVM native image (~100 ms start) for the webhook handler *or* CRaC snapshot restore (~200 ms) to keep full JVM dynamism, **plus** `min-replicas ≥ ceil(baseline λ × W / per-pod C)` (a warm floor), concurrency tuned down so more instances start in parallel, and retry budgets with backoff+jitter + idempotency keys so retries don't 2× the spike.

**Prevention checklist:**

- [ ] Classify every workload steady vs bursty *before* choosing runtime (EXERCISES.md #2 table is the artifact).
- [ ] Scale-to-zero only with native/CRaC *and* a warm floor sized from Little's law (C = λ·W), never min-0 JVM on a spike path.
- [ ] Load test the spike shape (0 → 100× in 10 s), not just steady RPS; assert p99 < budget *during* scale-up.
- [ ] Provisioned-concurrency / min-instances budgeted as insurance; alerts on cold-start count and queue depth, not just CPU.

---

## 4. Noisy-neighbor throttling — CPU limits that lie about latency

**Setup:** Catalog API on shared nodes with `requests.cpu=250m, limits.cpu=500m` and G1GC. p99 < 300 ms in staging. In production, every ~15 minutes p99 spiked to 1.5–3 s with no traffic change and no OOMs.

**Timeline:**

| Time | Event |
|------|-------|
| 09:00 | Deploy with tight CPU limits to "pack more pods per node." |
| 09:15+ | Periodic p99 spikes; traces show GC pauses + throttled carrier threads, not DB. |
| 11:30 | `container_cpu_cfs_throttled_seconds_total` confirms: pods throttled 20–40% of periods during G1 mixed collections on shared nodes. |
| 13:00 | Fix: raise CPU limit (or remove it, keep requests for scheduling), pin G1 threads (`-XX:ConcGCThreads`, `-XX:ParallelGCThreads`) to the request value, move to dedicated node pool. Spikes vanish. |

**Root cause:** CPU *limits* throttle via CFS quota; the JVM (GC threads, JIT, virtual-thread carriers) assumes it can burst. When throttled mid-collection, GC pauses stretch, carriers stall, and Little's-law queues build — latency explodes while RPS looks normal. The orchestrator saw "low CPU usage" (throttled processes can't use more) and refused to scale.

**Fix:** Size CPU requests from measured steady usage, set limits ≥ 2–4× requests (or unset limits with proper requests + node isolation), tune `-XX:ActiveProcessorCount` / GC thread counts to the request, and autoscale on latency/queue signals (VISION.md: "autoscaling on a real signal") rather than CPU alone.

**Prevention checklist:**

- [ ] Never ship tight CPU limits on latency-sensitive JVMs without a throttling dashboard (`cfs_throttled_seconds`, GC pause p99, carrier-blocked time).
- [ ] Autoscale on p99/queue-depth/custom RED metric, not CPU utilization.
- [ ] G1 (or ZGC, see BIG_TECH_FEEDBACK.md) thread counts derived from CPU *request*, verified under throttle simulation (`stress-ng` sidecar test).
- [ ] Node isolation for the hot path: dedicated pool / guaranteed QoS for catalog reads; burstable QoS only for batch.

---

## 5. Failed rollback — the incompatible migration

**Setup:** Release v2.14 added `price_cents NOT NULL` + a backfill + code reading the new column. Deploy went out with Flyway `migrate-on-start`; 10 minutes in, checkout errors spiked (rounding bug in the new pricing code). Team hit "rollback" — redeployed v2.13.

**Timeline:**

| Minute | Event |
|--------|-------|
| 0 | v2.14 rolls out, health-gated, probes green. Migration V37 applied (column added, backfilled). |
| 10 | Pricing bug found: totals off by 1¢ on discounted items. Rollback ordered. |
| 12 | v2.13 pods start — crash-loop: old code's entities/queries break against the new non-null column + altered constraint. Readiness never goes green; orchestrator halts the rollback mid-flip. |
| 12–40 | Catalog half on v2.14 (buggy prices), half on failed v2.13 (unready). Manual forward-fix v2.15 ships instead. |
| +1 day | Postmortem: "written rollback" (VISION.md) existed as a runbook step but was never *compatible* with the migration. |

**Root cause:** Expand and contract were fused into one release. The migration was not backward-compatible, so the old artifact could not run against the new schema. Health gating correctly refused to route to v2.13 — which turned a bad deploy into a stuck deploy.

**Fix:** Expand-migrate-contract discipline: (a) V37a *expand* — add nullable column, backfill, old code ignores it (deployable both ways); (b) v2.14 code writes both, reads new with fallback; (c) V37b *contract* — add NOT NULL weeks later once no old code remains. Immediate fix here was forward (v2.15) since rollback was impossible by construction.

**Prevention checklist:**

- [ ] Every migration labeled expand vs contract; contract migrations ship in a *later* release than the code that stops needing the old shape.
- [ ] Rollback drill per release (REAL_WORLD_PROJECT.md exit-drill spirit): actually redeploy N−1 against the migrated schema in staging and watch readiness.
- [ ] `migrate-on-start` ownership clear (one migrator job, not every pod racing); PITR-tested restore before risky migrations; RPO ≤ 5 min / RTO ≤ 30 min as acceptance, not aspiration.
- [ ] Kill-switch / feature flag on new pricing logic so the code path can be disabled without a schema rollback.
