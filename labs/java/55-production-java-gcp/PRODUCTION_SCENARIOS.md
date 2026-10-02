# PRODUCTION_SCENARIOS — 5 real GCP incidents (Java)

Each scenario follows the same shape: symptom → timeline → root cause →
fix → prevention. All five are reproducible as drills using EXERCISES.md
patterns against the lab-53 service running on the ARCHITECTURE.md topology.

---

## 1. GKE Autopilot OOMKill from burstable mis-sizing

**Service:** catalog-api on GKE Autopilot, Java 21 + virtual threads,
`-XX:MaxRAMPercentage=75.0`, pod requests `cpu: 500m, memory: 1Gi`,
no memory limit set (Autopilot enforces request = limit behavior class
"burstable" confusion carried over from Standard habits).

**Symptom:** Rolling deploy Monday 10:04 — new ReplicaSet pods flap
`OOMKilled (exit 137)`, Gateway readiness gate holds rollout at 50%,
p99 spikes 180 ms → 2.1 s, HPA scales 4 → 12 pods and they die too.

**Timeline:**

| Time | Event |
|---|---|
| 09:58 | Cloud Deploy promotes canary 25% → 50%. New pods request 1 Gi. |
| 10:04 | First `OOMKilled` on `catalog-api-7d9f`. `kubectl describe` shows Last State Terminated Reason OOMKilled. |
| 10:06 | HPA (CPU 82%) adds replicas; new pods die within ~90 s of warmup. |
| 10:09 | On-call checks Cloud Monitoring: container memory working set climbs 0.9 → 1.05 Gi during Caffeine cache warmup + first Full GC deferred by ZGC generational pacing. |
| 10:14 | Old ReplicaSet (requests 2 Gi) still serving; Gateway holds traffic split — no full outage, but 50% slice degraded. |
| 10:21 | Rollback to previous revision; fleet stable by 10:26. |
| 10:40 | Post-mortem: heap dump from pre-prod replay shows peak 1.35 Gi during warmup, steady-state 0.75 Gi. |

**Root cause:** Request sized for steady state (0.75 Gi + headroom
looked safe) but not for warmup peak. On Standard the old manifest had
`requests: 1Gi / limits: 2Gi` (burstable) so peaks survived; on
Autopilot the class effectively pins usage to request, and the JVM
(`MaxRAMPercentage=75%` of 1 Gi = 768 MB heap) plus Metaspace/threads/
direct buffers blew past the cgroup during cache fill. HPA on CPU made
it worse: more cold pods = more concurrent warmup peaks.

**Fix (that day):**

```yaml
resources:
  requests:
    cpu: "1000m"
    memory: "2Gi"
  # Autopilot: keep requests == real peak need; JVM follows cgroup
env:
- name: JAVA_OPTS
  value: "-XX:MaxRAMPercentage=60.0 -XX:+UseZGC -XX:+ZGenerational"
```

Rollback first, then re-promote with corrected requests. Set HPA on a
custom p99/latency metric in addition to CPU so warmup latency gates
scale-in.

**Prevention:**

- Size Autopilot requests from the **warmup peak**, not steady state —
  record both in the ops report (MINI_PROJECT step 4).
- Add a startup memory soak test: replay 10 min of prod traffic in
  staging, assert `container/memory/working_set < 0.8 × request`.
- Alert: `container_memory_working_set / request > 0.85 for 5m` →
  page; do not wait for OOMKill counters.
- Consider CRaC/native snapshot (lab 53) to shrink the warmup hump
  instead of paying 2 Gi forever — price both, cf. COST_REALITY.md §1.

---

## 2. Pub/Sub ordering-key hotspot throttles checkout

**Service:** checkout worker (pull subscription `orders-events-sub`,
ordering enabled, ack deadline 30 s, Java subscriber with
`setParallelPullCount(4)`), key = `merchant-id`.

**Symptom:** Black Friday rehearsal: one enterprise merchant produces
60% of volume. End-to-end checkout p99 400 ms → 9 s for that merchant
only; others fine. Subscription backlog (`oldest_unacked_message_age`)
grows monotonically; DLQ starts filling with deadline-exceeded
redeliveries — healthy messages look poison.

**Timeline:**

| Time | Event |
|---|---|
| 14:00 | Load test ramps to 8K msgs/s; merchant `acme` = 5K/s on one key. |
| 14:07 | `acme` partition latency climbs; per-key throughput plateaus ~1.5–2K/s. |
| 14:12 | Ack deadlines expire → redelivery storm doubles effective load. |
| 14:18 | DLQ (`maxDeliveryAttempts: 5`) quarantines in-order-but-slow messages; operators mistake throttling for poison. |
| 14:30 | Mitigation: split key to `merchant#shard` (16 shards), drain, replay DLQ. Backlog clears by 14:55. |

**Root cause:** Ordering keys serialize delivery **per key through a
single sequencer** — one hot key has a hard throughput ceiling
regardless of subscriber parallelism. Java-side `parallelPullCount`
cannot parallelize within a key. Redeliveries amplified the jam.

**Fix:**

```java
// Producer: shard the hot key; consumer restores order per shard window
String key = merchantId + "#" + (orderId.hashCode() & 0xF); // 16 shards
PubsubMessage msg = PubsubMessage.newBuilder()
    .setOrderingKey(key).setData(payload).build();
```

Plus: raise `maxDeliveryAttempts` during the incident to stop
quarantining slow-but-healthy messages, extend ack deadline to 60 s for
the checkout handler's real processing time, and add per-key backlog
dashboards.

**Prevention:**

- Design question first (EXERCISES.md §5): global order / per-user
  order / no order? Checkout needs per-user (or per-cart) order, never
  per-merchant-global.
- Load-test with production key distribution, not uniform synthetic
  keys — uniform tests hide hotspots by construction.
- Alert on `oldest_unacked_message_age by ordering_key` (top-K), not
  just total backlog.
- Document the shard count and the replay procedure in the runbook;
  DLQ replay must preserve shard affinity.

---

## 3. Cloud SQL failover + HikariCP stampede

**Service:** catalog-api → Cloud SQL PostgreSQL HA (regional, automatic
failover), HikariCP `maximumPoolSize: 20 × 12 pods = 240 connections`,
`connectionTimeout: 5s`, no retry backoff on startup.

**Symptom:** 03:12 regional maintenance triggers failover (60–90 s
writer downtime). API 5xx rate 2% → 78% for 6 minutes — far longer than
the DB outage. After the DB recovers, pods stay broken: all Hikari
threads blocked, readiness probes fail, Gateway drains the fleet.

**Timeline:**

| Time | Event |
|---|---|
| 03:12 | Failover begins; writes return `connection refused / SSL SYSCALL EOF`. |
| 03:13 | Every pod's pool threads block in `getConnection()`; queued HTTP
  requests pile onto virtual threads (cheap, so thousands queue). |
| 03:14 | DB writer back; but 240 simultaneous reconnects + validation queries
  slam it (stampede); `pg_stat_activity` shows connection storm, CPU 100%. |
| 03:15 | Hikari `connectionTimeout` fires fleet-wide → exceptions → 5xx;
  readiness failures remove pods → restarts re-stampede. |
| 03:20 | On-call halves fleet via HPA override, staggers restarts 30 s apart,
  raises Cloud SQL `max_connections` headroom already present. Fleet
  recovers 03:24. |

**Root cause:** Two compounding errors: (a) pool sized for peak
throughput with no failover arithmetic — 240 concurrent reconnects
exceed what a just-failed-over writer absorbs; (b) no backoff/jitter on
reconnect and no circuit breaker, so the fleet synchronized into a
thundering herd, and virtual threads (which never block expensively)
let the queue grow unbounded instead of shedding load.

**Fix (code + config):**

```yaml
# application-gcp.yml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10          # 10 × 12 = 120, under writer budget
      minimum-idle: 2
      connection-timeout: 3000
      validation-timeout: 2000
      max-lifetime: 300000
      initialization-fail-timeout: 30000
resilience4j.circuitbreaker:
  instances.db:
    failure-rate-threshold: 50
    wait-duration-in-open-state: 15s
```

Java: wrap DB calls in a bulkhead (`maxConcurrentCalls`) + timeout so
the HTTP layer returns 503 fast instead of queueing. Restart with
stagger (RollingUpdate `maxUnavailable: 1`, or manual 30 s stagger).

**Prevention:**

- Quarterly failover game-day (REAL_WORLD_PROJECT.md): force failover
  in staging, measure time-to-healthy, assert RTO ≤ 30 min claim.
- Size pools by writer budget: `pods × pool ≤ 0.5 × max_connections`,
  remainder for migrations/admin/replay.
- Alert on `pg_stat_activity count` slope + Hikari `pendingThreads`,
  not just 5xx — pending-thread growth predicts the stampede minutes
  early.
- Flyway/admin connections on a separate user with reserved slots.

---

## 4. Workload Identity breakage after project migration

**Service:** `catalog-api` KSA → GSA federation
(`iam.gke.io/gcp-service-account` annotation), Secret Manager + AlloyDB
connector calls; project moved from `acme-dev` to `acme-prod` org folder
over the weekend by platform team.

**Symptom:** Monday deploy succeeds (images, manifests all green) but
every pod logs `403: Permission 'secretmanager.versions.access' denied`
and `401: Invalid authentication` to AlloyDB. Debug-pod GCP calls fail
with no `GOOGLE_APPLICATION_CREDENTIALS` — the exact success signal from
CODE_DEEP_DIVE.md §1 inverted.

**Timeline:**

| Time | Event |
|---|---|
| Sat | Project migrated; GSA `catalog-api@acme-dev...` recreated as
  `catalog-api@acme-prod...`; KSA annotation updated in Terraform. |
| Mon 09:00 | Deploy applies; pods start; all GCP API calls 403/401. |
| 09:15 | On-call suspects code; rolls back — same errors on old revision.
  (Rollback cannot fix IAM.) |
| 09:30 | `gcloud iam service-accounts get-iam-policy` shows the
  `roles/iam.workloadIdentityUser` binding still references the **old
  project number** (`serviceAccount:acme-dev.svc.id.goog[ns/ksa]`). |
| 09:45 | Re-applied binding with new project number + re-granted
  `roles/secretmanager.secretAccessor` and `roles/alloydb.client`
  (org-policy reset dropped them). Pods recover without rebuild. |

**Root cause:** KSA→GSA trust is a two-sided binding keyed by exact
project number + namespace + name. Migration changed one side; Terraform
updated the annotation but the `workloadIdentityUser` IAM binding (and
org-policy-inherited data-plane roles) still pointed at the old
identity. Symptom mimics an app bug but is pure IAM drift — the classic
GCP breach-classic in reverse (instead of leaked keys, missing trust).

**Fix:**

```bash
gcloud iam service-accounts add-iam-policy-binding \
  catalog-api@acme-prod.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:acme-prod.svc.id.goog[ catalog-ns/catalog-api]"
# then re-grant data-plane roles dropped by org policy
gcloud projects add-iam-policy-binding acme-prod \
  --member "serviceAccount:catalog-api@acme-prod.iam.gserviceaccount.com" \
  --role roles/secretmanager.secretAccessor
```

**Prevention:**

- EXERCISES.md §1 as a CI check: post-deploy job unsets
  `GOOGLE_APPLICATION_CREDENTIALS` in a debug pod and calls one API per
  dependency; fail the pipeline on 403 with the exact missing role.
- Manage **both sides** of the binding in one Terraform module (KSA
  annotation + IAM binding + role grants) — never by hand, never split.
- After any project/org move: run the keyless-proof + secret-read +
  DB-connect trio before promoting traffic (Gateway gate).
- Never "fix" by exporting a JSON key — that restores function while
  reintroducing the breach vector THEORY.md §3 exists to kill.

---

## 5. Cloud Run cold-start cascade on flash sale

**Service:** Spiky webhook slice on Cloud Run (`minScale: 0`,
`containerConcurrency: 80`, vanilla JIT JVM image ~900 MB, startup
~6 s), Gateway → Cloud Run; steady API stays on GKE.

**Symptom:** Flash sale 12:00: RPS 50 → 4,000 in 90 s. p99 250 ms →
14 s; Cloud Run spins 5 → 50 (max) instances but most requests queue
behind cold containers; autoscaler saturates at maxScale; retries from
the merchant double load; GKE steady slice unaffected.

**Timeline:**

| Time | Event |
|---|---|
| 12:00 | Sale push notification; RPS vertical step. |
| 12:01 | Cold starts serialize: each new instance needs ~6 s JVM boot +
  3 s Caffeine/Secret load before serving 80 concurrent. |
| 12:02 | `container_instance_count` pinned at 50 (max); `request_queue`
  depth grows; p99 dominated by queueing, not handler time. |
| 12:04 | Client retries (no backoff) add ~1.8× amplification. |
| 12:08 | Mitigation: raise maxScale 50 → 150, set `minScale: 8` warm,
  flip to prebuilt CRaC-restored image (startup ~400 ms), enable
  retry budgets client-side. p99 < 600 ms by 12:15. |

**Root cause:** `minScale: 0` + slow-start image + hard maxScale +
retry amplification = textbook cold-start cascade. Per-instance
concurrency math (MATH_FOUNDATION.md §2: instances ≈ RPS × latency /
concurrency) assumed warm latency 250 ms; cold latency 6–9 s raised the
required instance count ~30× instantaneously, past the cap.

**Fix:**

```yaml
# service.yaml — post-incident
autoscaling.knative.dev/minScale: "8"     # warm floor for sale hours
autoscaling.knative.dev/maxScale: "150"
containerConcurrency: 80
# image: .../api:TAG-crac  (CRaC restore, cf. lab 53 native/CRaC artifacts)
```

Plus Cloud Scheduler warmer hitting `/actuator/health` every 60 s
outside sale hours, and client retry policy: capped exponential backoff
+ jitter, no retry on 429/503 without `Retry-After`.

**Prevention:**

- Concurrency sweep (EXERCISES.md §2) must include a **cold-start
  column**: measure 0→N latency at each concurrency, not just warm.
- Keep two artifacts: JIT (debug) + CRaC/native (cold path); deploy
  the cold-path artifact to every scale-to-zero service by default.
- Alert on `cold_start_count rate` and `pending_requests / serving
  instances` — scale the floor before the queue, not after.
- Schedule `minScale: 8` (or higher) around known events; price the
  warm floor explicitly (COST_REALITY.md §1) — 8 idle instances for
  6 hours is cheaper than 7 minutes of failed checkouts.

---

## Drill mapping

| # | Incident | Reproduce via | Proves |
|---|---|---|---|
| 1 | Autopilot OOMKill | Halve memory request, replay warmup load | Request sizing + burn alert |
| 2 | Ordering hotspot | EXERCISES.md §5 single-key flood | Key-shard design |
| 3 | Pool stampede | Force Cloud SQL failover in staging | RTO + pool math |
| 4 | Identity break | Delete IAM binding, run keyless proof | CI keyless gate |
| 5 | Cold cascade | Scale Run to 0, step-load 50→4K RPS | Warm floor + CRaC image |
