# Lab 06: Microservices at Scale — Mini Project

## Project: `FleetLab` — Scale-Out Harness, Connection Budget Calculator, and Bottleneck Finder

**Time**: 10–14 hours | **Difficulty**: Advanced | **Stack**: Java 21, Docker, Linux networking tools (`ss`, `ss -s`, `/proc`, cgroup v2), WireMock for dependencies

Build a small multi-service system you can scale locally, plus the tooling that makes scaling arithmetic explicit. Reproduce the three scaling failures that account for most "we scaled and it got worse" incidents.

---

## Part 1 — The system

Three services, each a Spring Boot app with a configurable HTTP client (connection pool, timeouts) and a stub dependency:

```
[loadgen] → [service-a:8080] → [service-b:8081] → [stub-db:8082]
                    └──────────→ [stub-cache:8083]     (WireMock with configurable latency)
```

`service-a` config surface (all overridable by env var so you can scale experiments without rebuilding):

```yaml
server:
  tomcat:
    threads:
      max: ${TOMCAT_MAX:200}
      min-spare: ${TOMCAT_SPARE:20}
    accept-count: ${TOMCAT_ACCEPT:100}
    max-connections: ${TOMCAT_MAXCONN:8192}

spring:
  datasource:
    hikari:
      maximum-pool-size: ${POOL_MAX:20}
      minimum-idle: ${POOL_IDLE:2}
      max-lifetime: ${POOL_MAX_LIFETIME_MS:1800000}
      connection-timeout: ${POOL_ACQUIRE_MS:3000}
      leak-detection-threshold: ${POOL_LEAK_MS:5000}

resilience4j:
  retry:
    instances:
      downstream:
        max-attempts: ${RETRY_ATTEMPTS:3}
        enable-randomized-wait: true
```

---

## Part 2 — Connection budget calculator

A CLI that takes a deployment description and emits the budgets:

```java
public record ServiceSpec(String name, int replicas, int poolMax, int httpClients,
                          int heapMb, int threads, int maxConns) {}

public record BudgetReport(Map<String, Integer> perDependencyConnections,
                           Map<String, Double> fdRequired, double kernelMemMb,
                           List<String> violations) {}

public final class BudgetCalculator {

    /** Total outbound connections this service fleet imposes on each dependency. */
    public static Map<String, Integer> connectionBudget(List<ServiceSpec> fleet, int depCapacity) {
        Map<String, Integer> out = new LinkedHashMap<>();
        for (ServiceSpec s : fleet) {
            out.merge(s.name(), s.replicas() * s.poolMax() * s.httpClients(), Integer::sum);
        }
        out.forEach((dep, conns) -> {
            if (conns > 0.7 * depCapacity) {
                // flagged by the caller as a violation
            }
        });
        return out;
    }

    /** FDs ≈ 2-3x concurrent connections (connect/accept churn) + static overhead. */
    public static long requiredFds(ServiceSpec s) {
        long concurrent = (long) s.replicas() * Math.max(s.poolMax(), s.maxConns() / 2);
        return 3 * concurrent + 50;
    }

    /** Kernel memory for sockets, at the kernel's per-connection cost. */
    public static double kernelSocketMemoryMb(int connections, int kbPerConn) {
        return connections * (double) kbPerConn / 1024.0;
    }

    /** Container memory composition for a JVM service. */
    public static String memoryBudget(ServiceSpec s, double heapShare) {
        int heap = (int) (s.heapMb() * heapShare / 100);
        int metaspace = 256, codeCache = 250, nativeOverhead = 400;
        int stacks = (int) (s.threads() * 0.5);                       // 512 KB stacks
        int direct = 512;
        int total = heap + metaspace + codeCache + nativeOverhead + stacks + direct;
        return String.format(
            "heap=%dMB metaspace=%dMB codeCache=%dMB stacks=%dMB direct=%dMB native=%dMB "
          + "=> set memory limit %dMB (headroom %dMB), MaxRAMPercentage=%d",
            heap, metaspace, codeCache, stacks, direct, nativeOverhead,
            total + 1024, 1024, (int) (100.0 * heap / (total + 1024)));
    }
}
```

**Deliverable**: `FLEET_BUDGET.md` for three fleet shapes (6 services × 20 replicas; 6 × 60; 3 × 12), showing connection totals, FD requirements, kernel memory, and the violations each shape triggers. The 60-replica case should be impossible without a pooler — prove it.

---

## Part 3 — Connection storm reproduction

### Experiment 1: un-jittered `maxLifetime`

```bash
# Run with POOL_MAX_LIFETIME_MS=60000 (1 min, un-jittered) and watch the stub's accept rate
POOL_MAX_LIFETIME_MS=60000 docker compose up -d
watch -n 0.5 'ss -tan | grep stub-db | awk "{print \$1}" | sort | uniq -c'
```

Then enable jittered lifetime (HikariCP doesn't jitter by default — implement a wrapper or use a custom `HikariConfig` + your own eviction scheduler) and re-run.

**Measure**: peak new-connection rate at the stub, `SYN-RECV` counts, and any connection refusals.

### Experiment 2: ephemeral port exhaustion

```yaml
# make the client open-per-request (no pooling)
POOL_MAX: 1
POOL_IDLE: 0
```
Drive 2,000 rps and watch for `cannot assign requested address`. Then widen the range and re-run:

```bash
sudo sysctl -w net.ipv4.ip_local_port_range="10000 65535"
sudo sysctl -w net.ipv4.tcp_tw_reuse=1
```

**Deliverable**: a table showing, per configuration, peak connections, `TIME_WAIT` count, error rate, and whether the failure reproduced. Explain why the port-range widening delays rather than fixes the problem.

### Experiment 3: FD exhaustion

```bash
docker exec svc-a sh -c 'ulimit -n'                    # observe the default
docker exec svc-a sh -c 'ls /proc/1/fd | wc -l'        # count open FDs
docker exec svc-a sh -c 'cat /proc/1/limits | grep -i "open files"'
```

Drive load until `Too many open files` appears; then set `ulimits: nofile: soft/hard` in compose and in the JVM container config, and re-run.

**Deliverable**: the exact FDs consumed per in-flight connection (measured as ΔFDs / Δconnections), your `nofile` recommendation, and the verification that it resolved the error.

---

## Part 4 — CPU throttling reproduction

Run with a tight CPU limit and observe throttling:

```yaml
services:
  svc-a:
    deploy:
      resources:
        limits: { cpus: "0.5" }
```

```bash
# cgroup v2
docker exec svc-a cat /sys/fs/cgroup/cpu.stat        # nr_throttled, throttled_usec
# or Prometheus
container_cpu_cfs_throttled_seconds_total
```

Correlate throttle events with p99 latency from your load generator. Compute the predicted amplification `ΔL = λ × ΔW_throttle` and compare to observed concurrency.

**Deliverable**: a plot-equivalent table of (throttle events/sec, p99, in-flight) and your explanation of why average CPU hid this.

---

## Part 5 — Shared bottleneck finder

Scale `service-a` from 1 → 8 replicas against a single `stub-db` with a fixed capacity, and watch throughput plateau:

```bash
for r in 1 2 4 8 16; do
  docker compose up -d --scale svc-a=$r
  run-load-test 2000 60        # 2000 rps for 60s
  record completed_rps, p99, per_replica_cpu, stub_cpu, pool_wait_ms
done
```

**Deliverable**: `SCALING_CURVE.md` with the measured curve and the identified ceiling. Then break the ceiling (add a cache in front of the stub) and show the curve extends. State the diagnostic rule you would use in production to find the ceiling in under 10 minutes (per-service CPU vs per-dependency saturation vs per-instance queue depth).

---

## Part 6 — Deploy safety checks

Write a `check-manifest.sh` that fails CI on the configuration mistakes this lab covers:

```bash
#!/usr/bin/env bash
# usage: ./check-manifest.sh docker-compose.yml replicas_max
set -euo pipefail
fail=0
YML=$1; R=${2:-1}

# 1. heap must leave room for native memory
PCTL=$(grep -oP 'MaxRAMPercentage=\K[0-9]+' "$YML" || echo 100)
if [ "$PCTL" -gt 75 ]; then echo "FAIL: MaxRAMPercentage=$PCTL leaves no native headroom"; fail=1; fi

# 2. pool size x replicas must stay under dependency capacity
POOL=$(grep -oP 'maximum-pool-size: \$\{POOL_MAX:\K[0-9]+' "$YML" || echo 20)
CAP=$(grep -oP 'STUB_MAX_CONN:\K[0-9]+' "$YML" || echo 400)
if [ $(( POOL * R )) -gt $(( CAP * 7 / 10 )) ]; then
  echo "FAIL: replicas($R) x pool($POOL) = $(( POOL * R )) exceeds 70% of $CAP"; fail=1
fi

# 3. nofile must be raised from the image default
NFILE=$(grep -oP 'nofile:\s*\K[0-9]+' "$YML" | head -1 || echo 1024)
if [ "$NFILE" -lt 8192 ]; then echo "FAIL: nofile=$NFILE too low for high connection counts"; fail=1; fi

# 4. liveness must not depend on downstream health
if grep -qA3 'livenessProbe' "$YML" && grep -qA6 'livenessProbe' "$YML" | grep -qi 'downstream\|dependency\|/health/ready'; then
  echo "FAIL: livenessProbe appears to depend on downstream health"; fail=1
fi

exit $fail
```

**Acceptance**: this script fails on a deliberately broken manifest and passes on the hardened one, with each failure message naming the incident it prevents.

---

## Part 7 — Diagnosis drills

For each of these, produce the *first three commands* and the interpretation, then verify against your own lab:

| Symptom | Interpretation |
|---|---|
| Rising `CLOSE_WAIT` on the stub | Your app is not closing response bodies/connections |
| `TIME_WAIT` > 20k | Connections not being reused; check pool config |
| `OutOfMemoryError: Direct buffer memory` | Unbounded direct buffers; set `MaxDirectMemorySize` |
| Rising `FIN_WAIT_2` | Peer closed, you didn't; check close paths |
| High `SYN-RECV` | Accept backlog too small, or listener overloaded |
| `cannot assign requested address` | Ephemeral port exhaustion |
| `Too many open files` | FD limit |
| p99 spikes with 40% avg CPU | CFS throttling |
| One replica slow, others fine | Node-level issue or bad traffic shard |

**Deliverable**: `DRILL_ANSWERS.md` with commands, expected output, and your actual output.

---

## Acceptance Criteria

- [ ] `FLEET_BUDGET.md` covers three fleet shapes and correctly flags the 60-replica case as infeasible without a pooler.
- [ ] Measured FDs per in-flight connection is stated, with a `nofile` recommendation that resolves the reproduced failure.
- [ ] Ephemeral port exhaustion reproduced, and the report explains why widening the range is a mitigation not a fix.
- [ ] Connection storm reproduced with un-jittered `maxLifetime` and eliminated with jitter.
- [ ] CFS throttling reproduced, with the `ΔL` amplification matching observation.
- [ ] Scaling curve measured with the ceiling identified, and shown to extend after the ceiling is broken.
- [ ] `check-manifest.sh` fails on broken config and passes on hardened config.
- [ ] Diagnosis drills answered with real captured output.

---

## Stretch

- Implement a jittered connection-lifetime scheduler and measure the difference in stub accept-queue pressure at scale-out.
- Add a shared-egress-IP experiment showing why `TIME_WAIT` limits are per-destination, not global.
- Build a Grafana dashboard that would let an on-call spot each drill's symptom in under 60 seconds.
