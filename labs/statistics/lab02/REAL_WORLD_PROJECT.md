# REAL_WORLD_PROJECT — Arrival and Latency Modelling for Capacity

**Track:** statistics  |  **Lab:** lab02  |  **Level:** Foundational

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

A payments platform sizes its infrastructure on request arrivals and authorisation latency. Capacity was set from a Poisson assumption while traffic clearly varies by time of day, and last Black Friday peak latency was four times the predicted p99.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Traffic | steady 2,100/s, peak 11,000/s during Black Friday |
| Latency target | p99 under 250 ms; actual peak p99 was 980 ms |
| Model today | homogeneous Poisson for arrivals, normal for latency |
| Failure | peak capacity underestimated because arrivals cluster |
| Requirement | a distributional model that matches observed shape and drives capacity |

## 3. Target Architecture

```text
 edge + gateway telemetry (timestamp, region, endpoint, outcome)
    |
 [1] arrivals per second --> dispersion ratio, rate variation by time of day
    |                             |
 Poisson adequate?         overdispersed --> negative binomial / rate model
    |
 [2] latency distribution --> skewness, tail percentiles, mixture check
    |                             |
 normal adequate?             skewed --> lognormal / mixture / tail model
    |
 [3] capacity model: queue depth vs service rate at observed arrival shapes
    |
 peak forecast with intervals, not point estimates
    |
 alerts on shape change (dispersion, skewness) as well as rate
```

## 4. Component Responsibilities

### 4.1 Arrival modelling

- Per-second and per-minute arrival counts by region and endpoint, with the raw series retained
- Dispersion ratio computed per window; overdispersion routed to a negative binomial or a rate model
- Rate modelled by time of day and day of week rather than as a single constant lambda
- Peak quantiles estimated from the fitted model with intervals, plus a direct empirical quantile for comparison

### 4.2 Latency modelling

- Full latency distribution retained per endpoint, not just aggregates
- Skewness and tail percentiles computed; a lognormal or mixture compared against the normal
- Mixture detection across success and timeout paths, which have different shapes
- Service rate and its variability estimated to drive queueing-based capacity

### 4.3 Capacity model and forecasting

- Queueing relationship between arrival shape, service rate and queue depth, using measured inputs
- Peak forecast produced with intervals from the fitted arrival model
- Scenario comparison: homogeneous Poisson versus time-varying negative binomial
- The chosen model published with its assumptions and its known limits

### 4.4 Operational integration

- Capacity thresholds derived from the fitted quantiles rather than assumed percentiles
- Alerts on shape change (dispersion ratio, skewness) alongside rate thresholds
- Model refitted on a schedule with drift detection on the fitted parameters
- Analyst-facing summary showing empirical versus model quantiles side by side

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Retain arrival and latency series at full resolution; compute dispersion and skewness by window |
| Week 2 | Fit time-varying arrival and latency models; compare against the homogeneous Poisson baseline |
| Week 3 | Build the capacity model from measured arrival shape and service rate |
| Week 4 | Scenario forecast with intervals; compare predictions against the Black Friday outcome |
| Week 5 | Operational integration: thresholds from fitted quantiles, shape-change alerts, scheduled refits |

## 6. Runbook (copy-paste)

```bash
# Arrival shape now: dispersion ratio and rate by time of day
curl -s 'localhost:9090/traffic/arrivals?window=24h' | jq '{dispersionRatio,lambdaByHour,model}'

# Latency shape per endpoint, empirical and modelled quantiles
curl -s 'localhost:9090/traffic/latency?endpoint=auth' | jq '{skewness,empirical:.p99,modelled:.p99Model,mixture}'

# Capacity scenario comparison at the modelled peak
curl -s 'localhost:9090/traffic/capacity?scenario=black-friday' | jq '{model,peakQps,queueDepth,p99Lower,p99Upper}'

# What the homogeneous Poisson would have predicted
curl -s 'localhost:9090/traffic/capacity?scenario=poisson' | jq '{peakQps,p99}'

# Fitted parameter drift since last refit
curl -s 'localhost:9090/traffic/model/drift' | jq '{lambdaDelta,dispersionDelta,refitAgeHours}'
```

## 7. Observability and SLOs

- Model fit: empirical versus modelled peak quantiles within a stated tolerance for each scenario.
- Shape: dispersion ratio and skewness tracked per window with alerts on change.
- Capacity: predicted peak queue depth versus observed across the last four events.
- Impact: peak latency relative to target, and capacity headroom at modelled peak.
- Trust: forecast intervals wide enough to be honest, verified against outcomes.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Peak p99 four times the forecast | Homogeneous Poisson ignored rate variation | Fit a time-varying model; compare scenarios explicitly; alert on dispersion change |
| Fitted quantiles disagree with empirical quantiles | Model family mismatch or fit drift | Report both side by side; refit on a schedule; alert on parameter drift |
| A timeout path inflates latency percentiles | Success and timeout responses have different shapes | Model them separately and combine by mixture weights |
| Capacity threshold fires on normal peak variation | Thresholds assumed rather than derived | Derive thresholds from fitted quantiles with an agreed service level |
| Model fits history and fails the next event | No out-of-sample verification | Backtest on the last four events and publish the error |

## 9. Prevention Backlog

- Negative binomial arrival model with time-of-day and event covariates.
- Automated family selection between Poisson, negative binomial and mixtures.
- Simulation-based calibration for the arrival model tail.
- Service-rate variability model feeding a queueing-based capacity model.
- Per-region model comparison with a single source of truth for capacity planning.

## 10. Postmortem Outline (skeleton)

1. **Impact** - who was hurt, for how long, in which numbers.
2. **Timeline** - detection, diagnosis, mitigation, resolution (UTC).
3. **Detection gap** - which signal should have fired first?
4. **Root cause** - the mechanism, not the person.
5. **What went well** - the thing that shortened the incident.
6. **Action items** - owner, date, and the alert or test that proves each one.

## 11. Sourced field notes (fetched Oct 2026 — verify before citing)

- **NIST/SEMATECH e-Handbook of Statistical Methods**: https://www.itl.nist.gov/div898/handbook/
  Authoritative reference for estimators, measures of central tendency and dispersion, with the guidance on when each is appropriate.
- **SciPy — statistics module documentation**: https://docs.scipy.org/doc/scipy/reference/stats.html
  Reference implementations of distributions, hypothesis tests and descriptive statistics; the semantics this lab re-implements in plain Java.

> The deliverable is a capacity model that admits traffic clusters, reports its forecast with intervals, and is verified against the last four peak events rather than trusted.
