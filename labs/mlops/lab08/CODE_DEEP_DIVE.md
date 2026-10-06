# Model Monitoring & Observability - Code Deep Dive

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

## 1. Module Map

```text
src/
  ModelMonitoringLab.java     driver: reference vs current windows, alert decisions
  DriftDetector.java         PSI, KL and JS on identically bucketed windows
  PerformanceMonitor.java    sliding-window quality joined by prediction id
  PredictionLog.java         append-only score records with the join key
  AlertPolicy.java           sustained-slope detection with reviewed thresholds
  RetrainTrigger.java        evidence + minimum interval decision logic
```

AlertPolicy takes its thresholds from a configuration object whose values were derived from history, with a comment recording where they came from. Copied-in 0.25 values with no provenance are how monitoring loses credibility.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `DriftDetector` | psi(reference, current), kl(...), js(...) on fixed buckets |
| `PerformanceMonitor` | sliding-window metric over matured labels, joined by prediction id |
| `PredictionLog` | append-only records carrying the join key and model version |
| `RetrainTrigger` | decide(driftSeries, qualitySeries, sinceLastTrain) |

---

## 3.1 Drift on identically bucketed windows

Bucket edges are computed once from the reference and reused for every current window. Without this, PSI values are not comparable.

```java
public double psi(double[] reference, double[] current, double[] edges) {
    // edges computed ONCE from the reference and reused for every window,
    // otherwise PSI values across windows are not comparable
    int[] refCounts = bucket(reference, edges);
    int[] curCounts = bucket(current, edges);
    double psi = 0;
    for (int i = 0; i < refCounts.length; i++) {
        double b = Math.max(refCounts[i] / (double) reference.length, EPS);
        double a = Math.max(curCounts[i] / (double) current.length, EPS);
        psi += (a - b) * Math.log(a / b);          // buckets with zero mass need EPS
    }
    return psi;
}

public boolean shouldAlert(double[] psiSeries, double slopeThreshold, int consecutive) {
    int run = 0;
    for (int i = 1; i < psiSeries.length; i++) {
        double slope = psiSeries[i] - psiSeries[i - 1];
        if (slope > slopeThreshold) run++; else run = 0;
        if (run >= consecutive) return true;      // sustained trend, not one crossing
    }
    return false;
}
```


---

## 3.2 Delayed-label evaluation joined by prediction id

Quality is only computed for predictions whose labels have actually arrived, and the maturity fraction is reported alongside the number.

```java
public QualityWindow evaluate(PredictionLog log, Instant from, Instant to, OutcomeStore outcomes) {
    int scored = 0, labelled = 0, correct = 0;
    for (ScoreEvent e : log.range(from, to)) {          // join key is the prediction id
        scored++;
        Outcome o = outcomes.find(e.predictionId());     // may be absent: label lag
        if (o == null) continue;                        // do NOT count as wrong
        labelled++;
        if (o.matches(e)) correct++;
    }
    if (labelled == 0)
        return QualityWindow.empty(scored, 0);          // no mature labels: report nothing
    return new QualityWindow(scored, labelled, (double) correct / labelled,
            (double) labelled / scored);                // maturity fraction reported
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| PSI computation per feature per window | `O(n + buckets)` | streaming-friendly with running histograms |
| KL or JS per feature | `O(buckets)` | bottleneck is bucketing, not the divergence |
| Performance evaluation on matured labels | `O(n window)` | join by id, indexed |
| Servicing metrics | `O(1) per request` | counters and timers, no storage |

## 5. Correctness and Numerics

- Compute bucket edges once from the reference and reuse them.
- Clamp bucket probabilities with an epsilon to avoid infinities.
- Report the label maturity fraction next to every quality number.
- Store the threshold's provenance in a comment or config field.
- Use double for ratios and Welford for running means on the score distribution.

## 6. Test Strategy

- PSI is 0 for identical distributions and grows as they diverge.
- PSI computed with different bucket edges is not silently comparable — assert the edges match.
- JS is bounded by ln 2 and symmetric in its arguments.
- A single PSI crossing does not alert; a sustained positive slope does.
- Evaluation excludes unmatured predictions rather than counting them wrong.
- A retrain trigger does not fire when drift is high but quality is stable and the interval is short.

## 7. Extension Points

- Add covariate-shift-aware alerting that compares against a seasonal reference window.
- Add per-segment drift so a global healthy PSI hides one broken segment.
- Implement champion/challenger drift comparison to attribute a shift to a model change.

## 8. Review Checklist

- [ ] Reference distributions stored with the model version
- [ ] Bucket edges computed once and reused
- [ ] Score records carry a join key and the model version
- [ ] Unmatured labels excluded, maturity fraction reported
- [ ] Thresholds carry provenance and use sustained-slope logic
- [ ] Servicing metrics on the same dashboard as model quality
