# Lab 10: AI Deployment & CI/CD — Mini Project

## Project: Progressive Delivery Control Plane for an LLM Service

Build a Java 21 control plane that owns release manifests, artifact promotion, cohort
assignment, canary gating, rollback, routing with breakers, queue-depth autoscaling,
feature flags, and environment parity — with a simulated production traffic load so the
ladder, gates, and rollback are exercised end to end.

## Goal

A runnable `Main` that takes a candidate manifest from 0% to 100% (or rolls it back at
the failing step), writes a release report with the numbers, and demonstrates that
rollback is a single alias write measured in milliseconds.

## Requirements

### Phase 1: Manifest and Artifact Store
- [ ] `ReleaseManifest` record with all seven components and a `canonical()` form.
- [ ] SHA-256 hash over the canonical form; hash printed in every simulated response.
- [ ] Content-addressed store: write-once, dedupe on repeat put, provenance sidecar.
- [ ] Aliases as pointers; `point(alias, hash)` is the only mutation path.
- [ ] Retention: last 5 artifacts per alias; eviction refuses if it would break rollback.

### Phase 2: Simulated Workload
- [ ] Deterministic generator seeded by a fixed seed: request stream with per-request
      prompt length, output length, and a tenant id.
- [ ] Deterministic per-user quality outcome driven by the manifest hash, so the
      candidate can be made to pass or fail at a chosen ladder step.
- [ ] Latency model: `service_time = base + tokens/rate`, with tail noise from a fixed
      distribution.
- [ ] Replayable: same seed + same manifests = byte-identical report.

### Phase 3: Cohorts
- [ ] Hash-based assignment on `userId + salt`; identical across replicas.
- [ ] Weights in permille; sum validated at startup.
- [ ] Cache bounded; eviction counted.
- [ ] Test: no user changes variant within a session; assignment stable across two
      router instances.

### Phase 4: Canary Controller and Gates
- [ ] Ladder `1 -> 5 -> 25 -> 100` permille with per-step minimum samples and max wait.
- [ ] Gates: task success, safety violation rate (zero tolerance), p95 latency, cost per
      successful request, refusal rate delta, tool-call error rate.
- [ ] Four distinct outcomes: `WAIT` / `ADVANCED` / `HOLD` / `ROLLBACK`.
- [ ] Missing metric returns BREACH, not PASS. Prove with a deliberately unnamed metric.
- [ ] Report the sample count and margin at each step decision.

### Phase 5: Rollback
- [ ] Promotion history as a stack; rollback pops.
- [ ] Measure rollback duration; objective 5 minutes, report in ms.
- [ ] In-flight requests keep their resolved manifest hash; count them.
- [ ] Prove no rebuild: rollback must not touch the filesystem except the alias write.

### Phase 6: Routing and Breakers
- [ ] Logical name -> ordered version list with per-version capacity.
- [ ] Circuit breaker per version; 4xx never trips it and never triggers a retry.
- [ ] Fallback chain skips the failed version; `NEVER_RETRIES_4XX` proven by test.
- [ ] Drain before decommission.

### Phase 7: Capacity
- [ ] Queue-depth driven autoscaler with a boot-time lookahead and a warm pool.
- [ ] Simulation of a step-change traffic spike; report shed requests before scale-up.
- [ ] Admission controller returning 429 rather than queueing unbounded; queue cap tested.

### Phase 8: Feature Flags
- [ ] Scoped flags (`model:x`, `tool:y`, `tenant:z`) with owner, expiry, and scope.
- [ ] Guardrail-disabling flags require an approval record and page without one.
- [ ] Stale flag detection: a test proving an expired flag reports and self-disables.

### Phase 9: Parity
- [ ] `ParityChecker` comparing staging and production manifests.
- [ ] Hard-fail set `{model, prompt, index}`; weighted score for the rest.
- [ ] Six parity scenarios, three of which must block.

### Phase 10: Report
- [ ] Ladder trace: step, samples, per-gate value, decision.
- [ ] Exposure computed for both a passing and a failing candidate.
- [ ] Rollback duration, cold vs warm.
- [ ] Cost per successful request for every gate.
- [ ] `REPORT.md`.

## Directory Layout

```
lab10/
  src/com/aiengineering/lab10/
    manifest/{ReleaseManifest,ManifestHasher,ArtifactStore,Provenance}.java
    delivery/{CohortAssigner,CanaryController,GateEvaluator,RollbackController}.java
    routing/{ModelRouter,CircuitBreaker}.java
    capacity/{Autoscaler,AdmissionController,LatencyModel}.java
    flags/FlagStore.java
    parity/ParityChecker.java
    workload/TrafficGenerator.java
    Main.java
  out/release_report.json
  out/ladder_trace.txt
  REPORT.md
```

## Milestones

1. **M1** — manifest, canonical hash, artifact store; write-once verified.
2. **M2** — deterministic workload; replay produces identical output.
3. **M3** — cohorts; cross-replica stability test green.
4. **M4** — canary ladder with four outcomes; missing-metric breach proven.
5. **M5** — rollback as an alias write; duration measured in ms.
6. **M6** — routing and breakers; 4xx no-retry test green.
7. **M7** — autoscaler and admission control; spike simulation report.
8. **M8** — flags with expiry and approval enforcement.
9. **M9** — parity checker; three blocking scenarios.
10. **M10** — passing candidate to 100%; then a failing candidate rolled back at 5%.
11. **M11** — exposure and cost-per-success comparison between the two runs.
12. **M12** — `REPORT.md` written.

## Acceptance Criteria

- [ ] Manifest hash is stable across JVM restarts (canonical, not map order).
- [ ] Re-running with the same seed produces a byte-identical report.
- [ ] Rollback completes in under 5 seconds of simulated time with no artifact rebuild.
- [ ] A missing gate metric causes ROLLBACK, not ADVANCE.
- [ ] `HOLD` is reachable: a candidate that is neither passing nor failing does not promote.
- [ ] No user sees two variants within a session.
- [ ] A 400 response never increments breaker failures.
- [ ] Queue depth at the admission cap returns 429 instead of growing.
- [ ] An expired flag self-disables and increments the staleness counter.
- [ ] A staging/prod prompt mismatch blocks parity.
- [ ] Exposure for the failing candidate is strictly smaller than for a direct release.
- [ ] Cost-per-successful-request reported for every gate, not cost-per-request.
- [ ] Reverting a gate to `pass()` on missing data makes the suite fail.

## Stretch Goals

- [ ] Shadow mode comparator: automatic side-effect-free live-vs-candidate diffing.
- [ ] Blue-green with instant flip for a config-only release, timed.
- [ ] A/B test with a stated decision rule and a written conclusion.
- [ ] Sequential-testing boundaries so peeking at each ladder step stays valid.
- [ ] Drift monitoring with a CUSUM over quality metrics across the run.
- [ ] Multi-version fleet with deprecation ladder and auto-pin at the deadline.
- [ ] Expand/contract schema migration proven backward-compatible under rollback.
- [ ] A game-day script: kill a canary replica mid-ladder and observe the ladder.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Hash changes between runs | Hashing a map or a non-canonical encoding |
| Rollback takes minutes | Rebuilding, or reloading a cold model |
| Canary promoted on 40 requests | Gate with no minimum sample size |
| Missing telemetry silently passes | `value()` defaulting instead of `present()` |
| User sees two versions in a session | Cohort assigned per request |
| Breaker opens on client errors | 4xx counted as failures |
| Latency fine, p95 bad | Target utilization too high |
| Shed load during a spike | Scaling on utilization instead of queue depth |
| Stale flag keeps a feature off | Flag with no expiry |
| Staging green, prod red | Parity soft-scored instead of hard-failed |
| Shadow path caused a duplicate email | Comparator with side effects |
| Report differs on re-run | Unseeded randomness in the workload |

## Definition of Done

`REPORT.md` contains: the release manifest and its canonical hash, the artifact store
invariants (write-once, alias-pointer rollback), the cohort assignment method, the full
ladder trace with per-gate values and sample counts for a passing candidate, the same for
a candidate that rolls back at 5% with the failing gate named, computed exposure for both
runs versus a direct 100% release, rollback duration in milliseconds with in-flight
counts, breaker and routing decisions including the 4xx exclusion proof, the autoscaling
trace through a traffic spike with shed counts, flag inventory with stale-flag counts,
parity results for all six scenarios, cost per successful request at every gate, and a
list of residual risks accepted with reasons.
