# Lab 06: Microservices at Scale — Real World Project

## Scenario: "We scaled to save ourselves and made it worse"

You are a platform engineer on a B2B order-processing platform: 9 Spring Boot services, Java 21, Kubernetes, 120 pods total, PostgreSQL primary + 2 replicas, Redis cluster, Kafka.

**The incident** — Tuesday 08:41, before business hours. A Kafka consumer group rebalances after a broker restart, creating a temporary 6x inbound spike to `order-ingest`.

**What happened over 25 minutes**:

1. `order-ingest` scales from 12 → 60 pods in 4 minutes (HPA working as designed).
2. Each new pod opens its own DB pool of 30 → Postgres `max_connections = 600` is exhausted in ~90 seconds. New connections rejected.
3. Meanwhile, `order-api`'s outbound HTTP pools to `pricing` are sized for 12 pods (pool 50). At 60 pods they are 5x oversized → `pricing` sees a connection storm, its `TIME_WAIT` count hits 240k, and it starts refusing connections.
4. A deploy of `order-api` at 08:50 restarts all its pods. Because pool `maxLifetime` is un-jittered at 30 minutes, `pricing` receives 3,000 simultaneous connection attempts, overrunning its accept queue.
5. Total impact: order intake unavailable 27 minutes. Estimated backlog: 190,000 orders; 6 hours of manual triage to reconcile. Direct cost: $840K, plus 4 delayed customer shipments.

**Postmortem**: "We have no capacity model. Replica counts multiply our connection footprint, nobody budgets for it, and our scale-up strategy is untested at scale."

**Your job over 4 weeks**: build a capacity and scaling model for the platform, enforce it in CI, and prove the platform survives the same event.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Reconstruct the failure (Day 1–3)

### 1.1 Build the causal chain

For each of the three amplifiers, name the resource and the number:
- Replica multiplication of DB connections (pods × pool vs `max_connections`).
- Oversized per-pod HTTP pools after scale-out (`λ/pod` shrinks as replicas grow; the pool does not).
- Un-jittered `maxLifetime` causing a connection storm at deploy.

**Deliverable 1 — Causal analysis**: the chain with the arithmetic at each step, plus a timeline table (time → resource → saturation → symptom). Include what telemetry existed vs what you had to reconstruct.

### 1.2 Establish the current state

Inventory all 9 services: replicas (min/max), pool sizes, `maxLifetime`, timeouts, retry config, heap, threads, `nofile`, CPU/memory requests and limits.

**Deliverable 2 — Fleet inventory** as a table, and the summed per-dependency connection totals. Identify every dependency already over 70% of capacity at max replicas.

---

## Phase 2 — Build the capacity model (Day 3–7)

### 2.1 Per-service capacity model

For each service, produce:

```
CPU_cores  = λ_peak × (W_cpu + W_io) / U_target
mem_pod    = heap + native + connections × kb_per_conn
conn_dep   = replicas × pool × clients
FDs        ≈ 2–3 × concurrent_connections + 50
```

Backed by a load test per service in staging.

**Deliverable 3 — Capacity model document** per service, with measured `W_cpu`/`W_io`, the resulting replica requirements at 1x/2x/3x traffic, and the headroom policy.

### 2.2 Fleet-level dependency budgets

Sum across services per dependency and compare to capacity:

| Dependency | Capacity | Current max-replica demand | % | Verdict |
|---|---|---|---|---|
| Postgres primary | 600 conns | 1,150 | 192% | BLOCKED: needs pooler |
| `pricing` HTTP | 400 conns | 3,000 | 750% | BLOCKED |
| Redis cluster | per-node | ... | | |

**Deliverable 4 — Dependency budget matrix** with the ordered list of resolutions: pooler → replicas reduction → read replicas → capacity increase, each with cost and risk.

### 2.3 Kernel and FD budgets

Per node: expected concurrent connections (aggregated across pods per node), required `nofile`, ephemeral port rate, and socket memory.

**Deliverable 5 — Kernel budget** with `net.core.somaxconn`, `tcp_max_syn_backlog`, `ip_local_port_range`, and `nofile` recommendations, plus the node type implications.

---

## Phase 3 — Fix the amplifiers (Week 2)

### 3.1 Connection management

- Introduce **pgbouncer in transaction pooling** for application traffic (with prepared-statement handling verified), keep a separate direct pool for migrations and long transactions.
- Resize every HTTP client pool to `floor(0.7 × dep_capacity / (services_calling × max_replicas))`, per dependency — not one global default.
- Enable **jittered** `maxLifetime` and `keepaliveTime` on every pool; set `keepaliveTime` below the LB idle kill.
- Add connection-pool metrics to dashboards (pending, active, idle, created, acquire latency).

### 3.2 Concurrency and timeouts

- Per-dependency bulkheads sized from the model, with priority shedding.
- Deadline propagation from the gateway, verified so no inner hop outlives the caller.
- Global retry budget ≤10%, idempotency keys on retried writes.

### 3.3 JVM and container config

Standardize per service class:

```yaml
env:
  - name: JAVA_TOOL_OPTIONS
    value: >-
      -XX:MaxRAMPercentage=60
      -XX:InitialRAMPercentage=60
      -XX:+UseZGC                      # for latency-critical paths
      -XX:MaxDirectMemorySize=512m
      -XX:MaxMetaspaceSize=256m
      -XX:+HeapDumpOnOutOfMemoryError
      -XX:HeapDumpPath=/var/dumps
      -XX:+ExitOnOutOfMemoryError
      -XX:NativeMemoryTracking=summary
      -Xlog:gc*:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=5,filesize=50m
resources:
  requests: { cpu: "2", memory: "8Gi" }
  limits:   { cpu: "2", memory: "8Gi" }   # requests == limits for latency-critical
securityContext:
  capabilities: { drop: ["ALL"] }
  runAsNonRoot: true
```

Plus `ulimits: nofile: { soft: 32768, hard: 32768 }` and a node-level `sysctl` profile for ephemeral ports and backlog sizes.

**Deliverable 6 — Standard config + diff**: the before/after manifest for all 9 services, with per-line rationale, canaried 24 h at 5%.

---

## Phase 4 — Enforce the model in CI (Week 2–3)

Build the enforcement from MINI_PROJECT Part 6 into real gates:

1. **Connection budget gate**: fail if `Σ replicas_max × pool > 0.7 × dependency capacity`, using a checked-in dependency-capacity registry.
2. **Memory budget gate**: fail if `MaxRAMPercentage > 75` or the declared limit < the computed native overhead + heap.
3. **Probe semantics gate**: fail if liveness depends on downstream health; require startup probes for JVM services with warmup > 30 s.
4. **Pool config gate**: fail if `maxLifetime` is not jittered, if `keepaliveTime` ≥ `maxLifetime`, or if pool > per-pod computed bound.
5. **Load test in CI**: run each service's micro-benchmark against a stub and fail on >10% p99 regression or connection-count regression.
6. **Break-glass process**: documented, time-boxed, with an expiry date per exception.

**Deliverable 7 — CI gates** merged with the dependency-capacity registry as a reviewed artifact.

---

## Phase 5 — Prove it (Week 3)

Run the real event in a production-shaped staging environment:

| Scenario | Injection | Success criteria |
|---|---|---|
| S1 | Baseline (normal morning peak) | p99 < 300 ms, error < 0.1% |
| S2 | 6x inbound spike to `order-ingest` | HPA scales to max; DB conns stay < 70%; `pricing` conns < 70%; no refusals |
| S3 | Spike + concurrent deploy of `order-api` | No connection storm (`TIME_WAIT` < 50k); no refusals |
| S4 | Postgres failover during spike | Reconnect < 60 s; no connection storm on the new primary; backlog drains |
| S5 | `pricing` 2 s latency during spike | Bulkhead sheds; good path p99 degrades < 10%; no cascade |
| S6 | Node drain (rolling node replacement) | PDB respected; graceful shutdown completes; no in-flight 502s |

**Deliverable 8 — Scale test report** with all six scenarios, criteria met/missed, and the fix for anything missed. Include the scaling curve for `order-ingest` (throughput vs replicas) proving linearity or naming the ceiling.

---

## Phase 6 — Operating the model (Week 3–4)

- **Runbooks**: `RUNBOOK_SATURATION.md` (which resource is saturated → how to relieve it), `RUNBOOK_CONNECTION_EXHAUSTION.md`, `RUNBOOK_SCALE_EVENT.md` (the exact sequence for a traffic event, including when *not* to scale).
- **Alerts** derived from the model:
  - `db_connections_ratio > 0.7` (10 min) → warn
  - `pool_acquire_wait > 100ms` → warn; `> 1s` → page
  - `timewait_sockets > 50k` → warn
  - `cpu_throttled_seconds` rate > 0 → warn (any sustained throttling on a latency path)
  - `tcp_syn_recv > 1000` → warn (accept backlog pressure)
  - `TIME_WAIT` growth rate + `HPA scale-up event` correlation → page (storm signature)
- **A scaling runbook that says when not to scale**: because scaling multiplied the connection footprint and made the incident worse. Include the decision rule.
- **Game day**: execute S2–S4 with on-call, business hours, kill switch, and a written exercise.

**Deliverable 9 — Operational package**: runbooks, alerts with thresholds tied to the model, game-day report.

---

## Phase 7 — Quantify and institutionalize (Week 4)

Present the before/after:

| Metric | Before | After |
|---|---|---|
| Peak DB connections | 1,150 (192% of capacity) | 380 (63%) |
| `pricing` connections at max replicas | 3,000 | 260 |
| Deploy-time connection storm | 3,000 simultaneous | < 50/s |
| `TIME_WAIT` peak | 240k | < 20k |
| Scale-event MTTR | 27 min | 4 min |
| Cost per 1M orders | X | Y (capacity + pooler) |

Then institutionalize: add the capacity model to the service template so new services are born compliant; add "capacity budget" to the service design review checklist; schedule a quarterly capacity re-review.

**Deliverable 10 — Business case + institutionalization**.

---

## Deliverables checklist

- [ ] Phase 1 causal analysis + fleet inventory.
- [ ] Phase 2 capacity model, dependency budget matrix, kernel budget.
- [ ] Phase 3 connection/timeouts/JVM fixes, canaried.
- [ ] Phase 4 CI gates + dependency registry.
- [ ] Phase 5 six-scenario scale test report + scaling curve.
- [ ] Phase 6 runbooks, alerts, "when not to scale" rule, game day.
- [ ] Phase 7 before/after business case + institutionalization.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Diagnosis | "Connections were the problem" | Three amplifiers with arithmetic, timeline, telemetry gaps |
| Model | "It should scale linearly" | Measured per-service capacity model with headroom policy and per-dependency budgets |
| Fix | Added pods/replicas | Pooler, per-dependency pools, jittered lifetimes, bulkheads, container config |
| Enforcement | Documented conventions | CI gates with a reviewed capacity registry and break-glass process |
| Proof | Load test at steady state | Replay the actual event shape, plus deploy-during-spike and failover-during-spike |
| Operations | "Watch the graphs" | Model-derived thresholds, runbooks, game day, "when not to scale" rule |
| Economics | Technical only | Before/after dollars + institutionalized template |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Linux socket/tcp(7) and `ss(8)` documentation** — https://man7.org/linux/man-pages/man7/tcp.7.html and https://man7.org/linux/man-pages/man8/ss.8.html — authoritative definitions of socket states (`CLOSE_WAIT` means the *local* application has not closed; `TIME_WAIT` is the normal closing state), `SO_KEEPALIVE`/keepalive timers, and the `ss` filter/state syntax used in the drills. Also see `tcp(7)` for `tcp_tw_reuse` semantics.
2. **HikariCP configuration documentation** — https://github.com/brettwooldridge/HikariCP — the canonical source for `maximumPoolSize`, `minimumIdle`, `maxLifetime`, `keepaliveTime`, `connectionTimeout`, and `leakDetectionThreshold` semantics (notably: `keepaliveTime` must be *less* than `maxLifetime`, and `minimumIdle` is not a warm-up target). Note HikariCP does not jitter `maxLifetime` by default — verify current behavior before claiming jitter is built in.

Additional anchors worth verifying: Kubernetes `securityContext` capability/ulimit support in your cluster version, and pgbouncer transaction-pooling caveats for your Postgres and JDBC driver versions (prepared statements, `SET LOCAL`, advisory locks).

---

## Reflection questions

1. HPA scaled up automatically and made the incident worse. What should the autoscaling policy have considered that it does not?
2. Which resource actually saturated first, and how would you have known 20 minutes earlier?
3. If you could only fix one of the three amplifiers this quarter, which one, and what does the arithmetic say?
4. What is the cost of the pooler and the read replicas you recommended, and how would you justify it against the incident cost?
5. What would tell you that your capacity model has gone stale?
