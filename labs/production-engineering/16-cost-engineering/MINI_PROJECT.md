# Lab 16: Cost Engineering & Cloud Optimization — Mini Project

## Project: `CostLab` — Attribute, Rightsize, Shut Down, and Alert

**Time**: 10–14 hours | **Difficulty**: Advanced | **Stack**: Java 21, Spring Boot 3, Kubernetes (kind or a real cluster with billing access), Prometheus + Grafana, OpenCost or Kubecost or cloud billing export, k6, Loki/ELK for log volume, Python for the cost scripts

Take a real (or faithfully reproduced) Java platform, produce the numbers, and make the savings real — measuring before and after each one, and proving no SLO regressed.

---

## Part 1 — The platform

Six Spring Boot 3 services in one Kubernetes cluster, deliberately shaped like a real estate:

| Service | Replicas | Requests | p95 actual | Notes |
|---|---|---|---|---|
| `catalog-api` | 8 | 1 vCPU / 3 Gi | 210 m / 1.1 Gi | 1,200 rps peak |
| `checkout-api` | 12 | 2 vCPU / 4 Gi | 480 m / 1.6 Gi | 900 rps peak, latency-critical |
| `search-api` | 4 | 1 vCPU / 2 Gi | 340 m / 900 Mi | read-heavy |
| `notification-worker` | 3 | 500 m / 1 Gi | 220 m / 700 Mi | queue consumer |
| `reporting-batch` | 2 | 1 vCPU / 2 Gi | 300 m / 800 Mi | runs 00:00–04:00 only |
| `legacy-admin` | 2 | 1 vCPU / 2 Gi | 20 m / 300 Mi | "nobody uses it" |

Plus: one dev namespace (6 pods, always on), one staging namespace (10 pods, always on), a Redis with 64 Gi provisioned, a managed Postgres with 32 Gi, and INFO-level logging on every request in `catalog-api`.

Instance cost for the exercise: `8 vCPU / 32 Gi` node = **$420/month**; vCPU-hour = **$0.031**; egress = **$0.09/GB**; storage = **$0.115/GB-month**.

---

## Part 2 — Attribute the cost (do this before touching anything)

### 2.1 Billing export → per-service

With a cost tool or a billing CSV:

```bash
# OpenCost exposes allocation by namespace and by pod labels
curl -s "http://opencost/api/v1/allocation?window=7d&aggregate=node,namespace,pod" | jq '.data[0] |
  group_by(.properties.labels["app.kubernetes.io/name"]) |
  map({ service: .[0].properties.labels["app.kubernetes.io/name"],
        cpuCost: (map(.cpuCost) | add),
        ramCost: (map(.ramCost) | add),
        cpuCoreHours: (map(.cpuCoreHours) | add),
        ramCoreHours: (map(.ramGiByteHours) | add) })'
```

Produce the attribution table:

| Service | CPU $/mo | RAM $/mo | Total $/mo | % of fleet | $/1k requests |
|---|---|---|---|---|---|
| | | | | | |

### 2.2 Shared-cost allocation rule

State it explicitly, because it is a policy decision:

```
shared costs allocated as:
  ingress/LB   -> by request count
  NAT gateway  -> by egress bytes
  log storage  -> by ingested bytes
  control plane-> by pod count
```

**Deliverable**: `COST_BREAKDOWN.md` — the attribution table, the shared-cost allocation rule, the per-environment split (prod/staging/dev), and the "waste candidates" column: services where the ratio of allocation to usage is worse than 3×.

---

## Part 3 — The waste dashboard

```promql
# actual / requested per service — the only chart that matters for rightsizing
avg by (app) (
  rate(container_cpu_usage_seconds_total{container!=""}[5m])
) / avg by (app) (
  kube_pod_container_resource_requests{resource="cpu"}
)
```

```promql
# memory utilisation ratio
1 - (
  sum by (app) (container_memory_working_set_bytes{container!=""})
  / sum by (app) (kube_pod_container_resource_requests{resource="memory"} * 1024 * 1024)
)
```

For each service compute:

```
p95_actual, request, ratio, headroom_needed = p95 × 1.3, proposed_request, saving
```

**Deliverable**: `WASTE.md` — the utilisation-distribution table, the computed waste in vCPU-hours and GiB-months, the dollar figure under *both* billing models (requests and usage), and the ranked rightsizing list with the `legacy-admin` and `reporting-batch` outliers called out.

---

## Part 4 — Rightsize one service properly

Pick `checkout-api` (latency-critical, so it must be done rigorously).

### 4.1 Measure the live set, do not guess the heap

```bash
kubectl exec deploy/checkout-api -- jcmd 1 GC.class_histogram | head -30
kubectl exec deploy/checkout-api -- jcmd 1 VM.native_memory summary
# Live set after a full GC, measured across a peak window:
kubectl exec deploy/checkout-api -- jcmd 1 GC.run
kubectl exec deploy/checkout-api -- jstat -gcutil 1 1000 5
```

Observed: live set 620 Mi peak, metaspace 210 Mi, code cache 180 Mi, thread stacks 160 Mi (320 threads × 512 Ki), direct buffers 180 Mi, JVM overhead 200 Mi.

```
native_total = 210 + 180 + 160 + 180 + 200 = 930 Mi
heap_needed  = 620 Mi × 1.3 = 806 Mi → set -Xms/-Xmx = 850m
pod_memory   = 850 + 930 = 1,780 Mi → round to 2 Gi request
```

CPU: `p95 = 480 m` → `480 × 1.3 = 624 m` → request `650m`. Keep `limits.cpu = limits.cpu = request` (latency-critical, so no throttling — Lab 07).

```yaml
env:
- name: JAVA_OPTS
  value: >-
    -Xms850m -Xmx850m -Xss512k
    -XX:MaxRAMPercentage=42
    -XX:MaxMetaspaceSize=256m -XX:MaxDirectMemorySize=192m
    -XX:+UseContainerSupport -XX:+ExitOnOutOfMemoryError
resources:
  requests: { cpu: "650m", memory: "2Gi", ephemeral-storage: "2Gi" }
  limits:   { cpu: "650m", memory: "2Gi", ephemeral-storage: "3Gi" }
```

### 4.2 Verify the SLO is unchanged

```bash
k6 run -e RATE=900 -e DURATION=15m checkout.js    # before
# apply the new manifest, warm, then:
k6 run -e RATE=900 -e DURATION=15m checkout.js    # after
```

Compare p50/p99/p99.9 and error rate across three runs each. If p99 regressed, the heap is too small — go back and look at the allocation profile rather than reverting the request.

### 4.3 Recompute the node count

```markdown
Before: 12 pods × 4 Gi = 48 Gi requests; pods/node = floor(51.9/4) = 12 → 1 node-equivalent
After:  12 pods × 2 Gi = 24 Gi requests; pods/node = floor(51.9/2) = 25 → 0.5 node-equivalent
Saving: memory allocation halved; 10 pods/node freed across the fleet
```

**Deliverable**: `RIGHTSIZING.md` — the live-set measurement, the native breakdown, the before/after manifest, the three-run load test comparison, and the node/dollar delta. Explicitly state what headroom you kept and why.

---

## Part 5 — Shut down the environments that should not be on

### 5.1 Scheduled shutdown

```yaml
# kube-scheduler / CronJob that scales namespaces at the boundary.
# Simpler for the lab: a `CronJob` calling the API.
apiVersion: batch/v1
kind: CronJob
metadata: { name: env-shutdown }
spec:
  schedule: "0 19 * * 1-5"     # 19:00 Mon-Fri
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
          - name: scaler
            image: bitnami/kubectl
            command: ["sh","-c",
              "for ns in dev staging; do kubectl scale --all -n $ns --replicas=0; done"]
---
apiVersion: batch/v1
kind: CronJob
metadata: { name: env-startup }
spec:
  schedule: "0 8 * * 1-5"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
          - name: scaler
            image: bitnami/kubectl
            command: ["sh","-c",
              "for ns in dev staging; do kubectl scale --all -n $ns --replicas=2; done"]
```

### 5.2 The developer's cost of this change

Be honest and measure it: how many times a developer needs the environment outside hours, how long the startup takes, and whether a "wake" script removes the friction.

```bash
./scripts/wake-dev.sh          # scales dev back up and waits for ready
```

Then compute:

```
weekly_saving = idle_pods × cost_per_pod_equivalent × hours_off/168 × 4.33
```

**Deliverable**: `ENV_SHUTDOWN.md` — the saving, the friction, the wake mechanism, and the policy (who can wake it, and how it interacts with on-call).

---

## Part 6 — Classify every workload for spot

Build the decision table:

| Workload | Interruption cost | Spot safe? | Reasoning |
|---|---|---|---|
| `reporting-batch` | recompute $2 | **yes** | idempotent, restartable, no deadline |
| `notification-worker` | duplicate notification, $40 | **yes, with idempotency + DLQ** | verify dedupe key exists |
| CI runners | $3 | **yes** | ephemeral by nature |
| `search-api` | 400 rps customer search, 1 replica | **no at 1 replica** | yes at 4 replicas across a pool |
| `checkout-api` | $12,000 | **no** | latency-critical, expected interruption cost ≫ discount |
| Postgres primary | data loss | **absolutely not** | |

Compute the interruption arithmetic per row (Lab MATH §9) rather than asserting "yes/no".

Diversify the spot pool:

```yaml
# node pool across families/sizes/AZs so capacity loss is not correlated
- { instanceTypes: [m6a.large, m6a.xlarge, m6i.large], availabilityZones: [a, b, c] }
```

**Deliverable**: `SPOT_PLAN.md` — the classification table with arithmetic, the node pool design, and the interruption-handling requirement (graceful shutdown, checkpointed offsets, idempotency) for each spot workload.

---

## Part 7 — Fix the volume-driven costs

### 7.1 Logging

```xml
<!-- Per-request INFO logging: 6.5 TB/month. Sample successes, keep the rest. -->
<appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
  <encoder class="net.logstash.logback.encoder.LogstashEncoder"/>
  <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
    <level>INFO</level>
  </filter>
</appender>
```

```java
@Component
class RequestLogger {
    private static final double SAMPLE_RATE = 0.01;
    private final ThreadLocalRandom rnd = ThreadLocalRandom.current();

    void logRequest(HttpServletRequest req, long statusMs, long durationMs) {
        if (statusMs >= 500 || durationMs > 1000) {          // always: errors and slow requests
            log.info("request completed status={} ms={} path={}", statusMs, durationMs, templated(req));
            return;
        }
        if (rnd.nextDouble() < SAMPLE_RATE) {
            log.info("request completed status={} ms={} path={}", statusMs, durationMs, templated(req));
        }
    }
    private String templated(HttpServletRequest req) {
        return (String) req.getAttribute("org.springframework.web.servlet.HandlerMapping.bestMatchingPattern");
    }
}
```

Compute the saving from the measured log volume before and after. Add retention tiers and a lifecycle policy.

### 7.2 Egress

Measure actual egress bytes per service from the flow logs, then:
- Enable gzip for responses above 1 KB (`server.compression.mime-types`, `min-response-size`).
- Add conditional GET (`ETag`) for the 40% of read traffic that is cacheable.
- Check whether any cross-AZ traffic is unnecessary (client region vs pod region).

**Deliverable**: `VOLUME_COSTS.md` — measured log and egress volume per service, the fix, and the before/after dollar figure for each.

---

## Part 8 — Cost anomaly alerts and budgets

```yaml
groups:
- name: cost-anomalies
  rules:
  - alert: ServiceSpendAnomaly
    expr: |
      (
        sum by (app) (increase(container_cpu_cores_allocated_total{...}[1d]) * 31.536)
        /
        avg_over_time(sum by (app) (container_cpu_cores_allocated_total{...})[30d:1d])
      ) > 1.5
    for: 10m
    labels: { severity: warn, team: platform }
    annotations:
      summary: "{{ $labels.app }} CPU allocation is >50% above its 30-day baseline"
      runbook_url: "https://runbooks.example.com/cost-anomaly"

  - alert: LogVolumeExplosion
    expr: increase(loki_lines_bytes_total[1h]) > (3 * avg_over_time(loki_lines_bytes_total[30d:1h]))
    for: 15m

  - alert: ServiceDailyBudgetBurned
    expr: increase(container_cpu_cores_allocated_total[1d] * 31.536) > on(app) group_left team_label budget_usd
    labels: { severity: page }
```

Then verify them by injecting failures:

| Injection | Alert expected |
|---|---|
| Scale `legacy-admin` 2 → 40 replicas | ServiceSpendAnomaly for `legacy-admin` |
| Turn on DEBUG logging in `catalog-api` | LogVolumeExplosion |
| Add a loop that retries a failing call 50× | ServiceSpendAnomaly + retry alert |
| Create an untagged namespace running 10 pods | "untagged spend" alert (build one) |

**Acceptance**: each injection fires the correct alert within its window, with a runbook link and a team label.

---

## Part 9 — Unit economics

```markdown
| Month | Total spend | Orders | $/1k orders | $/order | Margin impact |
|---|---|---|---|---|---|
```

Do not stop at the ratio: state the contribution margin per order before and after, and the total annual effect.

**Deliverable**: `UNIT_ECONOMICS.md` — the trend, the margin arithmetic, and the recommendation (where to invest the saved money: capacity for the next peak, or reduction).

---

## Acceptance Criteria

- [ ] `COST_BREAKDOWN.md`: per-service and per-environment attribution with a stated shared-cost allocation rule, and a per-unit column.
- [ ] `WASTE.md`: utilisation distribution per service, waste quantified in vCPU-hours and GiB-months, and dollars under both billing models.
- [ ] `RIGHTSIZING.md`: live-set and NMT measurement, before/after manifest, three-run load test proving the SLO is unchanged, node and dollar delta.
- [ ] `ENV_SHUTDOWN.md`: scheduled shutdown working, saving computed, developer friction measured with a wake mechanism.
- [ ] `SPOT_PLAN.md`: classification table with interruption-cost arithmetic per workload, diversified node pool, and interruption-handling requirements.
- [ ] `VOLUME_COSTS.md`: measured log and egress volume per service with before/after dollar figures.
- [ ] Cost anomaly alerts and per-service budgets firing on all four injected failures.
- [ ] `UNIT_ECONOMICS.md`: three-month trend with margin arithmetic and a recommendation.

---

## Stretch

- Build a cost dashboard that ranks services by waste (allocation minus measured usage), and have it in a weekly digest email.
- Compute the cost of each architectural choice you made in earlier labs — cache hit ratio, retry budget, log sampling — and present it as a portfolio.
- Implement an autoscaler that scales to zero for dev namespaces and measure how many "environment unavailable" support questions it creates before you add the wake script.
- Model the effect of a Reserved/committed-use purchase against your actual baseline usage, with the utilisation risk if you commit too much.
