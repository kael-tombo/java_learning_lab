# REAL_WORLD_PROJECT — Production Monitoring for a Fraud Platform

**Track:** mlops  |  **Lab:** lab08  |  **Level:** Advanced

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. Scenario

A fraud platform serves 2M transactions a day with chargeback labels arriving 60 to 120 days later. The last silent degradation ran for five weeks before the chargeback rate alert fired, and nobody could say when it started.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Volume | ~2M decisions/day, peak 900/s |
| Label lag | 60-120 days for chargebacks; 7 days for internal declines |
| Alert history | one silent degradation lasting 5 weeks |
| Current signals | service health only; no feature or score drift monitoring |
| Cost of a miss | fraud losses plus regulatory exposure on missed SARs |

## 3. Target Architecture

```text
 decisions --> prediction log (score, features, model version, id)
     |                     |
     |                  drift detector
     |                (PSI/KL/JS per feature,
     |                 fixed buckets, per segment)
     |                     |
     |                  alert policy (sustained slope)
     |                     |
 outcomes (60-120d) ---------+
     |
 quality monitor (joined by id, maturity reported)
     |
 retrain trigger: drift AND matured quality drop AND interval
     |
 dashboards: serving health | model health | segment health
 runbook: alert -> owner -> first action -> verify
```

## 4. Component Responsibilities

### 4.1 Prediction log and join discipline

- Every decision logged with prediction id, score, feature values, model version and latency
- Outcomes attach by prediction id; internal declines at 7 days give an early signal
- Log completeness and drop rate monitored as a metric in their own right
- Retention aligned to the longest label horizon plus a margin

### 4.2 Drift detection

- Reference distributions captured at model publish time and stored with the version
- PSI, KL and JS per important feature, on bucket edges computed once and reused
- Per-segment windows (merchant category, channel, geography) so a global healthy PSI cannot hide a broken segment
- Alerts on sustained slope across consecutive windows, with seasonality-aware baselines

### 4.3 Quality monitoring with delayed labels

- Two-tier view: fast proxy from internal decline outcomes at 7 days, authoritative chargebacks at 60+ days
- Every quality number published with its label maturity fraction
- Calibration by score band and by segment, not only aggregate accuracy
- Chargeback-matured quality published weekly as the ground truth

### 4.4 Retrain triggers and operations

- Trigger requires sustained drift plus a matured quality drop plus a minimum interval
- Post-retrain comparison recorded so trigger quality is itself measured
- Alert runbook with severity, owner and first action; each alert drilled quarterly
- Compliance reporting exports of decision quality for regulatory review

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Instrument the prediction log; verify completeness and the outcome join with a sample audit |
| Week 3 | Drift detection on important features with seasonality-aware baselines and slope alerts |
| Week 4 | Per-segment drift dashboards so a broken segment cannot hide in the aggregate |
| Week 5-6 | Two-tier quality monitoring: 7-day proxy and 60-day authoritative chargebacks |
| Week 8 | Retrain trigger wired to the orchestrator; drill every alert and publish timings |

## 6. Runbook (copy-paste)

```bash
# Model health: drift, quality with maturity, and serving health
curl -s localhost:8080/monitoring/health | jq '{driftAlert,qualityMaturity,proxyQuality,chargebackQuality}'

# Per-feature PSI trend with slope for the top features
curl -s 'localhost:8080/monitoring/drift?top=10' | jq '.[] | {feature,psi,slope,segment}'

# Segment health for the last 24 hours
curl -s 'localhost:8080/monitoring/segments?window=24h' | jq '.[] | {segment,psi,proxyQuality,n}'

# Why is a retrain firing (or not)?
curl -s 'localhost:8080/monitoring/retrain-decision' | jq '{driftBreach,qualityDrop,maturity,intervalOk,decision}'

# Verify the outcome join is not silently dropping
curl -s 'localhost:8080/monitoring/join-health?window=24h' | jq '{decisions,matched,matchRate}'
```

## 7. Observability and SLOs

- Coverage: join match rate between decisions and outcomes (target > 99%).
- Detection: time-to-detect a deliberate degradation (target < 24 h for drift, < 14 days for the proxy).
- Quality: chargeback-matured quality by segment and score band, published weekly.
- Alert trust: alert precision measured as the fraction of alerts that led to a real finding.
- Operations: mean time from alert to mitigation, measured per alert type.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A five-week degradation went undetected | No feature or score drift monitoring, only service health | Deploy drift detection on important features with slope alerting before the next campaign |
| Join match rate drops to 60% | Outcome pipeline lag or schema change | Alert on match rate; fall back to the 7-day proxy and page the outcome owner |
| Drift alerts fire every campaign weekend | Seasonality not modelled | Seasonal reference windows per segment; alert on slope across windows |
| A retrain fires but quality does not improve | Drift is benign or labels have not matured | Require matured quality drop and a minimum interval; record post-retrain comparison |
| Global PSI healthy while one merchant category breaks | Aggregate window hides segment effects | Per-segment monitoring with minimum sample sizes |

## 9. Prevention Backlog

- Automated seasonal baselines per feature and segment.
- Post-retrain comparison published so trigger quality is measurable.
- Quarterly alert drill with recorded detection and mitigation times.
- Calibration monitoring by score band feeding a recalibration trigger.
- Compliance export of decision quality by segment for regulatory review.

## 10. Postmortem Outline (skeleton)

1. **Impact** - who was hurt, for how long, in which numbers.
2. **Timeline** - detection, diagnosis, mitigation, resolution (UTC).
3. **Detection gap** - which signal should have fired first?
4. **Root cause** - the mechanism, not the person.
5. **What went well** - the thing that shortened the incident.
6. **Action items** - owner, date, and the alert or test that proves each one.

## 11. Sourced field notes (fetched Oct 2026 — verify before citing)

- **MLflow — Tracking and Model Registry documentation**: https://mlflow.org/docs/latest/ml/tracking/
  Reference model for experiment/run/metric lineage and the registry lifecycle (the vocabulary this lab re-implements in Java).
- **Kubernetes — ConfigMaps and Secrets**: https://kubernetes.io/docs/concepts/configuration/configmap/
  How configuration is injected into scheduled workloads — the practical lineage story for a DAG run that must be reproducible months later.
- **DVC — data and model versioning**: https://dvc.org/doc/user-guide
  Content-addressed versioning of datasets and model binaries; the standard way to make a data snapshot referenceable in a run record.

> The deliverable is a platform where the next silent degradation is caught by drift within a day rather than by chargebacks five weeks later, with every alert drilled and every number honest about its label maturity.
