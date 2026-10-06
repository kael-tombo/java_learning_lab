# Lab 14: LLMOps (LLM Operations) — Mini Project

## Project: LLMOps Control Plane Simulator

Build the operational control plane in Java 21 — release manifests, traces, metrics,
canary control, drift detection, incident runbook automation, and safe mode — then
run scripted incidents through it and measure whether the runbooks actually work.

## Goal

A simulator that can stage releases, inject incidents, walk the automated runbooks,
and produce a measured report: time-to-diagnose, rollback time, blast radius, and
whether each alert fired with the right first question.

## Requirements

### Phase 1: Release Manifest
- [ ] `ReleaseManifest` covering model, prompt, index, tools, policy, generation,
      evaluator; canonical hash.
- [ ] `ConfigRegistry` with promote/rollback/pin.
- [ ] `ComponentDiff` with a ranked first hypothesis per alert type.
- [ ] Tests: field reorder does not change the hash; each single change does.

### Phase 2: Trace and Metrics
- [ ] Full trace span structure; JSONL writer with hashed payloads.
- [ ] `Percentiles` (reservoir) for TTFT/TPOT; verified against exact on a known set.
- [ ] `MetricRegistry` counters, gauges, histograms with cost attribution.
- [ ] Cost per request / feature / tenant / model version / cache status.

### Phase 3: Simulated Workload
- [ ] 5,000 synthetic requests across traffic tiers (interactive/standard/batch)
      with latency and error distributions.
- [ ] Poisson arrivals; configurable quality by intent.
- [ ] Deterministic from a seed.

### Phase 4: Deployment Strategies
- [ ] Shadow runner: mirror 100% of traffic, score both versions, paired CI.
- [ ] Canary controller with the 1/10/50/100 ladder, gates, min sample, auto rollback.
- [ ] Stable user bucketing.
- [ ] Verify a degraded candidate is rolled back at the first step.

### Phase 5: Drift
- [ ] PSI with quantile bins and a rolling comparator.
- [ ] Drift injected into intent mix, prompt length, and language.
- [ ] Verdict thresholds; verify major shift detection.

### Phase 6: Quality Monitoring
- [ ] Tier 1: cheap signals on 100%.
- [ ] Tier 2: judged sample with random + targeted subsets kept separate.
- [ ] Review queue with priority weighting; export to eval-suite format.

### Phase 7: Incidents
- [ ] Four scripted incidents: latency spike, quality drop (index change), cost
      spike (retry storm), refusal spike (policy change).
- [ ] Automated runbook execution per alert type.
- [ ] Measure time-to-alert, time-to-diagnose, time-to-contain, rollback time.
- [ ] Safe mode engaged in one incident; verify graceful degradation.

### Phase 8: Load Shedding and Retry Detection
- [ ] Tier-ordered shedding; verify protected fraction.
- [ ] Retry storm detector with the three-condition rule.

### Phase 9: Runbook Quality
- [ ] `RunbookQuality` mechanical scoring; find and fix the gaps in your own runbooks.

## Directory Layout

```
lab14/
  src/com/genai/lab14/{release,trace,metrics,cost,deploy,drift,quality,incident,ops}/
  config/runbooks.yaml
  out/incidents/
  out/metrics.json
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — manifest + hash + registry + diff; hash tests pass.
2. **M2** — traces round-trip; percentiles match exact on a known distribution.
3. **M3** — workload simulator; baseline metrics produced.
4. **M4** — shadow runner produces paired CIs on identical items.
5. **M5** — canary ladder; degraded candidate rolled back at 1%.
6. **M6** — PSI drift detection; injected shifts detected.
7. **M7** — quality monitor tiers; random and targeted samples separate.
8. **M8** — four incidents staged; runbooks executed; times measured.
9. **M9** — safe mode verified; retry storm detected.
10. **M10** — runbook scoring; gaps fixed; report written.

## Acceptance Criteria

- [ ] Manifest hash is order-independent and change-sensitive.
- [ ] Percentiles within 1% of exact on a known distribution.
- [ ] Canary blocks and rolls back a degraded candidate automatically.
- [ ] Missing gate metric counts as a breach.
- [ ] Major drift (PSI > 0.25) detected within one window.
- [ ] Random judged sample is unbiased and reported separately.
- [ ] Time-to-diagnose under 5 minutes in the scripted quality-drop drill.
- [ ] Rollback completes as a config flip (measured, not asserted).
- [ ] Retry storm detected before cost crosses the budget line.
- [ ] Every runbook entry passes the mechanical quality score.

## Stretch Goals

- [ ] Continuous rollback drill: deploy known-bad configs and verify rollback.
- [ ] Multi-model fleet scheduling with deprecation of an old version.
- [ ] Eval set drift detection (does the suite still represent traffic?).
- [ ] Toil analysis classifying operational work by automation level.
- [ ] Error budget with burn-rate freeze on quality/safety regressions.
- [ ] Alert deduplication and grouping for a cascading incident.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Canary promotes a bad version | Gate not measured, or NaN treated as pass |
| Cross-user version flicker | Assignment by request instead of user |
| Prometheus-style metric gaps | Missing gate metric counted as pass |
| Drift alert every window | Equal-width bins on skewed data |
| Drift never alerts | Empty bins producing log(0) |
| Cost spike undetected | No retry ratio metric |
| Rollback takes minutes | Rebuild instead of config flip |
| Quality metric jumps randomly | Mixing random and targeted samples |
| Runbook unused | No owner, no tested action |
| Shedding drops interactive | Wrong tier order |

## Definition of Done

`REPORT.md` contains: the release bundle diagram, baseline metrics, canary and
shadow results with CIs, drift detection results for three injected shifts, the
quality monitoring design, four incident reports with measured times, the safe-mode
drill, the retry storm drill, the load shedding table, the runbook quality score with
fixes, and a "what would we automate next" section derived from toil analysis.