# Lab 18: Chaos Engineering & Fault Injection — Mini Project

## Project: `ChaosLab` — A Hypothesis-Driven Experiment Harness With Tested Aborts

**Time**: 12–16 hours | **Difficulty**: Advanced | **Stack**: Java 21, Spring Boot 3, Toxiproxy, Spring Boot Chaos Monkey / CM4SB (optional), Docker Compose, Prometheus + Grafana, resilience4j, JUnit + Testcontainers, a chaos runner script

Build the harness that makes chaos *safe and legible*: preconditions, an automated abort, guaranteed restore, and a registry of hypotheses with pass conditions. Then run ten experiments and one GameDay.

---

## Part 1 — The system

```
[k6] → [gateway] → [orders-api] → [inventory-api] → [postgres]
                      └──────────→ [payments-api] ──→ [psp-stub (WireMock)]
                            └──→ [cache (Redis)]
```

Deliberate design choices that chaos will find:
- `orders-api` uses a WebClient with `maxInFlight 20` and a 2 s timeout.
- `inventory-api` uses HikariCP with `maximumPoolSize: 5` and holds a connection for the duration of the call.
- Resilience4j circuit breakers are configured on `payments-api` → `psp-stub` with a 60 s window / 50% threshold.
- `orders-api` has no retry on `inventory-api` (good) and a 2-attempt retry on `payments-api` (questionable).
- Redis cache has no negative caching and a 60 s TTL with **no jitter**.

---

## Part 2 — The experiment harness

### 2.1 Experiment definition

```java
public record Experiment(
    String id,                       // "latency-inventory-3s"
    String hypothesis,               // falsifiable, with a metric and a threshold
    String passCondition,            // the measurable pass condition
    String steadyStateMetric,        // guarded SLI + query
    Duration steadyStateWindow,      // 15 min
    String target,                   // "inventory-api"
    ToxiproxyToxics toxic,           // latency, reset, bandwidth
    Duration duration,
    int radiusPercent,
    String abortQuery,               // query that must not be exceeded
    double abortThreshold,
    String undoCommand               // the guaranteed inverse operation
) {}

var EXPERIMENTS = List.of(
    new Experiment(
        "latency-inventory-3s",
        "H: with inventory-api at 3 s latency, orders-api p99 stays under 1.2 s and the error rate stays under 0.5%",
        "p99(orders_error_rate) < 0.005 AND p99(http_server_duration_seconds) < 1.2",
        "sum(rate(http_server_requests_seconds_count{service=\"orders-api\",status=~\"5..\"}[5m]))",
        Duration.ofMinutes(15),
        "inventory-api",
        new ToxiproxyToxics().latency(Duration.ofMillis(3000), Duration.ofMillis(500)),
        Duration.ofMinutes(10),
        100,
        "sum(rate(http_server_requests_seconds_count{service=\"orders-api\",status=~\"5..\"}[1m])) / sum(rate(http_server_requests_seconds_count{service=\"orders-api\"}[1m]))",
        0.02,
        "toxiproxy-cli toxic remove inventory-api upstream_latency"),
    ...
);
```

### 2.2 Preconditions — refuse to inject into a broken system

```bash
#!/usr/bin/env bash
# check-steady-state.sh <metric_query> <threshold> <window>
Q=$1; T=$2; W=${3:-15m}
for i in $(seq 1 $W_STEPS); do
  V=$(promtool query instant "http://prometheus:9090" "$Q")
  if awk "BEGIN{exit !($V > $T)}"; then
    echo "PRECONDITION FAILED: $Q = $V > $T — not injecting"
    exit 1
  fi
  sleep 60
done
echo "steady state confirmed over ${W}"
```

This must be **automated and non-overridable**. If the precondition fails, wait; do not proceed.

### 2.3 The abort loop

```bash
#!/usr/bin/env bash
# abort-watch.sh <abort_query> <threshold> <duration_s> <undo_command>
Q=$1; T=$2; DUR=$3; UNDO=$4
END=$(( $(date +%s) + DUR ))
VIOLATIONS=0

while [ "$(date +%s)" -lt "$END" ]; do
  V=$(promtool query instant "http://prometheus:9090" "$Q")
  if awk "BEGIN{exit !($V > $T)}"; then
    echo "$(date -Is) ABORT: $Q = $V > $T"
    VIOLATIONS=$((VIOLATIONS+1))
    if [ "$VIOLATIONS" -ge 2 ]; then          # two consecutive breaches -> abort
      echo "ABORTING and restoring"
      eval "$UNDO"
      exit 2
    fi
  else
    VIOLATIONS=0
  fi
  sleep 15
done
echo "experiment window completed without abort"
```

Use a **short aggregation window** in the abort query (`[1m]`, ideally `[30s]`) so the abort is not governed by a five-minute rate.

### 2.4 Guaranteed restore

```bash
trap 'echo "restoring"; eval "$UNDO"; sleep 10; verify_steady_state' EXIT INT TERM
```

The restore runs on normal completion, on abort, and on any signal. Then assert the steady state returns:

```bash
verify_steady_state() {
  for i in $(seq 1 6); do
    V=$(promtool query instant "http://prometheus:9090" "$GUARDED_SLI")
    if awk "BEGIN{exit !($V <= $STEADY_THRESHOLD)}"; then
      echo "steady state restored after ${i} min"; return 0
    fi
    sleep 60
  done
  echo "STEADY STATE NOT RESTORED — escalating"; exit 3
}
```

**Acceptance**: `kill -TERM` the runner mid-experiment and verify the trap fires, the undo runs, and the steady state is confirmed.

### 2.5 Prove the fault was actually applied

Every experiment must emit:

```java
@Component
class FaultEvidence {
    private final MeterRegistry registry;

    void recordApplied(String type, String location) {
        registry.counter("fault_injected_total", "type", type, "location", location).increment();
        log.warn("FAULT APPLIED type={} location={}", type, location);
    }
}
```

A null result with no `fault_injected_total` increment means the fault never applied — the experiment proved nothing.

**Deliverable**: `HARNESS.md` — the harness design, the precondition, the abort loop with its aggregation window, the trap-based restore, the fault-evidence metric, and the demonstrated behaviour of `kill -TERM` mid-experiment.

---

## Part 3 — The ten experiments

| # | Injection | Hypothesis | Pass condition |
|---|---|---|---|
| E1 | `inventory-api` 3 s latency | orders p99 stays < 1.2 s, errors < 0.5% | measured |
| E2 | `inventory-api` latency 8 s | the client times out and the bulkhead sheds; p99 < 2.5 s | measured |
| E3 | `psp-stub` unavailable | circuit breaker opens within 30 s; orders still complete with a fallback | measured |
| E4 | `psp-stub` 500 ms latency | retries stay within the 10% budget; p99 < 1.5 s | measured |
| E5 | Postgres connection limit reduced to 8 | inventory degrades gracefully; orders error rate < 2% | measured |
| E6 | Redis unavailable | cache-miss path holds p99 < 900 ms; no cascade | measured |
| E7 | `orders-api` pod killed under load | no in-flight order lost; in-flight requests retried or failed cleanly | measured |
| E8 | `inventory-api` CPU limited to 100m | p99 degrades proportionally; shed before collapse | measured |
| E9 | `orders-api` disk filled to 98% | logs stop but the service degrades visibly and recovers after cleanup | measured |
| E10 | DNS failure for `psp-stub` | stale DNS cache masks it; after TTL expiry all pods fail simultaneously — measure the synchronised failure | measured |

For each, record: hypothesis, steady-state window, injected values, `fault_injected_total`, the metric series before/during/after, abort behaviour, drain/undo time, pass/fail, and — if it failed — the finding and the tracked action.

**Deliverable**: `EXPERIMENTS.md` — the table of ten with results, and `REGISTRY.md` — the searchable experiment catalogue.

---

## Part 4 — The two experiments that always find something

### 4.1 E9 — disk full

```bash
# fill the pod's ephemeral storage
kubectl exec deploy/orders-api -- sh -c 'dd if=/dev/zero of=/app/fill bs=1M count=1200 status=none'
kubectl get events --field-selector reason=Evicted -w
```

Observe: logback starts failing to write (evidence of the incident disappears), `/tmp` writes fail, the heap dump path fails, and — critically — whether the service reports degraded state or silently continues with stale logs. Then clean up and verify recovery.

**Finding to expect**: your observability depends on writable disk, and the failure mode is "diagnostics go dark exactly when you need them".

### 4.2 E10 — DNS failure

```java
// Deliberately NO DNS caching for this experiment
System.setProperty("networkaddress.cache.ttl", "0");
System.setProperty("networkaddress.cache.negative.ttl", "0");
```

Inject by pointing the JVM at a dead resolver (or by blocking UDP 53 in the container's namespace). Measure the time from injection to failure, and the shape of the failure: every pod resolving at the same instant is a stampede, not a gradual degradation.

Then fix it properly (set `networkaddress.cache.ttl` to a sane value, use connection-pooled clients, and add a circuit breaker) and re-run.

**Deliverable**: the two experiment reports, each with the finding, the tracked action, and the re-run result after the fix.

---

## Part 5 — Retry amplification experiment

```java
// E11: measure retry amplification under latency
@Retryable(retryFor = {WebClientRequestException.class}, maxAttempts = 3,
           backoff = @Backoff(delay = 200, multiplier = 2))
```

Instrument: `retry_attempts_total` and `http_client_requests_total`. During the 3 s latency injection, plot retries per original request.

```
β = retry_attempts / original_requests
sustainable iff healthy_load × (1 + β) ≤ capacity_remaining
```

Then reduce `maxAttempts` to 2 and re-run, comparing β and the order-completion rate. **If β > 0.1, the retry policy is wrong** and this experiment has proven it.

**Deliverable**: `RETRY_EXPERIMENT.md` with β before/after, the effect on p99 and on downstream load, and the recommended policy.

---

## Part 6 — GameDay

A coordinated scenario in the staging environment with three participants (IC, ops, comms+scribe) and four injections on a schedule:

| Time | Event | What it tests |
|---|---|---|
| 09:00 | Inject: `inventory-api` 3 s latency | detection, initial diagnosis |
| 09:20 | Real change: deploy a version with a deliberate bug (a 5% error rate on one endpoint) | whether responders attribute the new symptom to the chaos injection or hunt independently |
| 09:35 | Inject: Postgres connection limit reduced | multi-fault discrimination |
| 09:50 | Inject: revoke the responder's `kubectl` access to the staging namespace | access/permission reality |
| 10:10 | All faults cleared | recovery verification |

Measure: time to detect each, time to declare, time to first correct hypothesis (per fault), runbook usability (which steps failed), and every point a human was blocked.

**Deliverable**: `GAMEDAY.md` — the timeline, the four hypotheses the team actually formed and when they were corrected, the runbook defects found, and the tracked actions.

---

## Part 7 — Findings to actions

```markdown
| # | Finding | Class | Action | Owner | By | Definition of done | Re-run |
|---|---|---|---|---|---|---|---|
| 1 | Hikari pool of 5 in inventory-api saturates at 3 s latency | resource | Resize pool to 45 + alert on pending | | | Alert fires in re-run E1 | E1 |
| 2 | DNS cache TTL is 0 in orders-api | resilience | Set TTL 30 s, add breaker | | | E10 shows a bounded failure | E10 |
| 3 | psp-stub breaker threshold 50% over 60 s opens too slowly for a 30 s target | resilience | Sliding window 10 s, threshold 25% | | | Breaker opens < 30 s in E3 | E3 |
```

**Acceptance**: every finding has an action with an owner, a date, and a re-run scheduled to verify the fix.

---

## Acceptance Criteria

- [ ] `HARNESS.md` documents the design, and `kill -TERM` mid-experiment demonstrably triggers restore with steady-state verification.
- [ ] Preconditions are automated and refuse to inject into a non-steady system (demonstrated by injecting while the system is already degraded).
- [ ] Abort is automated, machine-evaluated, uses a short aggregation window, and is itself tested with a controlled regression.
- [ ] `EXPERIMENTS.md` covers ten experiments, each with hypothesis, pass condition, fault-evidence metric, before/during/after metrics, abort behaviour, and pass/fail.
- [ ] `REGISTRY.md` is searchable and includes the null results with what they prove.
- [ ] `RETRY_EXPERIMENT.md` measures β and recommends a policy, with a before/after comparison.
- [ ] `GAMEDAY.md` with four coordinated injections, the human-system timings, and the runbook defects found.
- [ ] Every finding has an action with an owner, a date, and a verification re-run.

---

## Stretch

- Run one experiment in production at 1% radius with a business sign-off document, and record the approval path and the result.
- Build an experiment scheduler that refuses to run if the previous experiment's finding is unresolved — so findings force behaviour.
- Add a "chaos coverage" metric: distinct failure modes with a *passing* experiment divided by declared failure modes, tracked as a sprint metric.
- Write a postmortem for the deliberately-buggy deployment in the GameDay, using the Lab 14 structure, and compare the measured detection time with the machine-detected time.
