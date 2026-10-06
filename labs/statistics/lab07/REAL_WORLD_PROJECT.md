# REAL_WORLD_PROJECT — Weekly Demand Forecast for a Retail Network

**Track:** statistics  |  **Lab:** lab07  |  **Level:** Advanced

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

A grocery chain forecasts weekly store-level demand to place orders. The current forecast is a spreadsheet moving average tuned by eye, has no interval, and was never evaluated against a baseline on a time-aware split.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Stores | 1,100 stores, 4,800 SKUs, weekly demand |
| Horizon | 4-week order placement, refreshed weekly |
| Current method | spreadsheet moving average, hand-tuned, no intervals |
| Known problem | holiday weeks and a store opening wave break the series |
| Business impact | waste and stockout cost estimated at $14M/year |

## 3. Target Architecture

```text
 order + promotion + holiday calendars
     |
 weekly demand series per store x SKU category
     |
 diagnostics: plot | ACF | seasonal strength | change points
     |
 decomposition (multiplicative where amplitude scales)
     |
 model candidates: seasonal naive | smoothed seasonal | AR with holiday regressors
     |
 rolling-origin evaluation per store tier --> errors by horizon
     |
 reconciliation across store/SKU totals (coherence check)
     |
 publish: forecast + calibrated intervals + recommended horizon
     |
 monitoring: weekly WAPE vs baseline, interval coverage, break alerts
```

## 4. Component Responsibilities

### 4.1 Data and calendar

- Weekly demand with promotion, holiday and closure flags joined before modelling
- Store openings and format changes recorded as known interventions
- Zero-demand weeks flagged explicitly rather than treated as zero demand
- Category-level series used for low-volume SKUs where store-level series are too sparse

### 4.2 Diagnostics and baselines

- ACF and seasonal strength per store tier to confirm a 52-period cycle
- Change-point detection capturing openings, format changes and the pandemic period
- Seasonal naive computed as the production baseline on identical folds
- Coherence check: store forecasts must sum to the network total within a tolerance

### 4.3 Modelling and evaluation

- Model set: seasonal naive, smoothed seasonal, and autoregressive with holiday regressors
- Rolling-origin evaluation per tier, reporting error by horizon
- Promotion effects modelled so promotions are not mistaken for trend
- Selected per tier from the evaluation, not from a single global choice

### 4.4 Publishing and monitoring

- Forecast published with calibrated intervals per store and SKU category
- A recommended horizon stated explicitly, beyond which error is not acceptable
- Weekly monitoring of WAPE against the baseline and of interval coverage
- Break alerts when a store's series changes structure mid-season

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Build the weekly series with calendar features; ACF and seasonal strength by tier |
| Week 3 | Seasonal naive baseline and coherence check across store and network totals |
| Week 4-5 | Rolling-origin evaluation of three model families per tier, error by horizon |
| Week 6 | Change-point handling for openings, format changes and the pandemic period |
| Week 7-8 | Calibrated intervals, published forecast with a recommended horizon, monitoring live |

## 6. Runbook (copy-paste)

```bash
# Forecast for a store with interval and model version
curl -s 'localhost:8086/forecast/store=0417' | jq '{model,week,point,low,high,version}'

# Rolling-origin error by horizon for a tier
curl -s 'localhost:8086/forecast/eval?tier=metro&horizons=4' | jq '.[] | {h,wape,mase}'

# Baseline comparison for the same folds
curl -s 'localhost:8086/forecast/baseline?tier=metro' | jq '{seasonalNaiveWape,selectedModelWape}'

# Coherence check: store forecasts versus network total
curl -s localhost:8086/forecast/coherence | jq '{sumStores,networkTotal,relDiff,tolerance,ok}'

# Interval coverage and structural-break alerts for the week
curl -s 'localhost:8086/forecast/monitoring?window=8w' | jq '{coverage,breaks}'
```

## 7. Observability and SLOs

- Accuracy: WAPE and MASE against the seasonal naive baseline, per tier and by horizon.
- Uncertainty: empirical interval coverage, targeted near the nominal level.
- Coherence: store forecasts summing to the network total within tolerance.
- Operations: weekly forecast published before the ordering cut-off with the horizon stated.
- Business: waste and stockout cost tracked against the spreadsheet period.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Accuracy collapses in holiday weeks | No calendar regressors; holidays look like outliers | Model holiday and promotion flags explicitly; report holiday-week error separately |
| A new store's forecast is wild | No history; structure undefined | Fall back to a category-level or peer-store forecast with a wider interval |
| Store forecasts do not sum to the network total | Independent fitting per store | Reconciliation step enforcing coherence, with a tolerance check in CI |
| Intervals cover about 60% of outcomes | Intervals derived from residual spread, not realised errors | Calibrate from rolling-origin errors by tier and horizon |
| Accuracy looks better than the spreadsheet but is worse in reality | No time-aware evaluation; the spreadsheet was compared on a random split | Require rolling-origin comparison against the existing method before any cutover |

## 9. Prevention Backlog

- Hierarchical reconciliation between store, category and network levels.
- Promotion-aware causal features with a holdout-based promotion lift estimate.
- Quantile forecasts with distributional calibration checks.
- Automated change-point handling for openings and format changes.
- Tier-specific model selection revisited monthly with the same evaluation protocol.

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

> The deliverable is a weekly forecast with calibrated intervals, a stated horizon, coherence across the network, and a beating seasonal-naive baseline measured on time-aware folds.
