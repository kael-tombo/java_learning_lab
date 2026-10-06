# Time Series Analysis - Code Deep Dive

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

## 1. Module Map

```text
src/
  TimeSeriesAnalysis.java   driver: decompose, model, forecast, evaluate
  Series.java               timestamps plus values, order enforced
  Decomposition.java        trend, seasonal and residual components
  Smoothing.java            SMA and EMA with explicit parameters
  Autocorrelation.java      ACF up to a maximum lag, seasonal lag identification
  Forecaster.java           seasonal naive, smoothed, and residual forecasts
  RollingOriginEval.java    time-aware evaluation producing error by horizon
  ChangePoints.java         structural break detection on the level
```

RollingOriginEval is the only evaluation path the driver uses. There is no random-split method available, which removes the most common way to flatter a time-series model.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `Series` | timestamps plus values, with gaps and ordering validated |
| `Decomposition` | trend, seasonal indices and residual component |
| `Autocorrelation` | ACF up to a maximum lag with seasonal lag identification |
| `RollingOriginEval` | errors by horizon from time-aware folds only |

---

## 3.1 Exponential smoothing with the parameter as an explicit choice

Alpha is a statement about responsiveness, so it is a named argument rather than a constant buried in the loop.

```java
public double[] smooth(double[] y, double alpha) {
    if (alpha <= 0 || alpha > 1) throw new IllegalArgumentException("alpha must be in (0,1]");
    double[] out = new double[y.length];
    double level = y[0];
    out[0] = level;
    for (int t = 1; t < y.length; t++) {
        double observation = y[t];
        level = alpha * observation + (1 - alpha) * level;   // alpha is responsiveness
        out[t] = level;                                      // not smoothing the value itself
    }
    return out;
}

// effective memory ~ 1/alpha observations; document it next to any tuned alpha
static String describeAlpha(double alpha) {
    return "alpha=" + alpha + " gives effective memory of about " + Math.round(1 / alpha)
            + " observations; too slow lags a turning point, too fast chases noise";
}
```


---

## 3.2 Rolling-origin evaluation with no random split available

Every fold trains only on the past and reports error by horizon, which is the only protocol that matches deployment.

```java
public ErrorByHorizon evaluate(Series s, Forecaster f, int horizon, int origins) {
    double[] errByH = new double[horizon];
    int[] counts = new int[horizon];
    int stride = Math.max(1, (s.size() - horizon * 2) / origins);
    for (int origin = horizon; origin < s.size() - horizon; origin += stride) {
        Series train = s.head(origin);                  // strictly the past, never the future
        double[] forecast = f.forecast(train, horizon);
        for (int h = 0; h < horizon; h++) {
            double actual = s.at(origin + h);
            errByH[h] += Math.abs(actual - forecast[h]); // MAE, robust to outliers
            counts[h]++;
        }
    }
    return ErrorByHorizon.from(errByH, counts);         // error growth with horizon is the result
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Moving average or EMA | `O(n)` | single pass |
| ACF up to lag k | `O(n log n)` | sort lagged pairs; avoids O(n²) recomputation |
| Seasonal decomposition | `O(n)` | one pass per component |
| Rolling-origin evaluation | `O(origins × n)` | the honest cost of validating a forecaster |

## 5. Correctness and Numerics

- Centre the series before computing ACF, or the trend dominates the correlation.
- Use a ring buffer for sliding windows instead of copying subarrays.
- Accumulate MAE rather than MAPE when y can be near zero.
- Report error by horizon, not as a single aggregate.
- Seed nothing in a deterministic time series; validate ordering and gaps instead.

## 6. Test Strategy

- SMA of a constant series equals the constant.
- EMA converges to a constant series and reacts to a level shift within about 1/alpha observations.
- ACF of white noise is within confidence bounds of zero at all lags.
- ACF of a seasonal series peaks at the seasonal lag.
- Rolling-origin evaluation never trains on an observation at or after its test point.
- A seasonal naive forecaster reproduces the value from one season earlier exactly.

## 7. Extension Points

- Add autoregressive modelling with differencing for stationarity.
- Add seasonal strength and trend strength diagnostics.
- Add Prophet-style changepoint handling for holidays and interventions.

## 8. Review Checklist

- [ ] Series validated for ordering and gaps
- [ ] Naive and seasonal naive baselines computed
- [ ] Rolling-origin evaluation is the only evaluation path
- [ ] Error reported by horizon with an interval
- [ ] Change points detected and modelled
- [ ] Smoothing parameters tuned on validation folds, never the test period
