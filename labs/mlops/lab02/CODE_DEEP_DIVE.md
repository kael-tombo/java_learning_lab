# Experiment Tracking with MLflow - Code Deep Dive

**Track:** mlops  |  **Lab:** lab02  |  **Level:** Intermediate

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
  ExperimentTrackingLab.java     driver: runs experiments, compares to champion
  TrackingClient.java            REST client for runs/params/metrics/artifacts
  RunContext.java                AutoCloseable run lifecycle (start, log, end)
  MetricLogger.java              cadence-controlled scalar logging with units
  RunNamer.java                  convention: date-owner-purpose, collision-safe
  ComparisonReport.java          candidate vs champion delta, printed
```

RunContext is AutoCloseable so the run always ends, even on exception. A tracking client that leaks open runs on crashes produces exactly the 'stuck running' rows nobody cleans up.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `TrackingClient` | createExperiment, createRun, logParam, logMetric, logArtifact, setTag |
| `RunContext` | scoped run handle that logs params on open and closes the run |
| `MetricLogger` | cadence control and unit tagging for scalar time series |
| `ComparisonReport` | delta versus champion on a matched data version |

---

## 3.1 Run lifecycle as a scoped resource

Params and tags are logged at construction so a crashed run is still diagnosable, and the run is always closed.

```java
try (RunContext run = tracking.startRun(experiment, runNamer.next())) {
    run.param("learningRate", lr);          // logged before anything can fail
    run.param("maxDepth", depth);
    run.tag("owner", "jratombo");
    run.tag("dataVersion", "v42");         // without this, comparisons are meaningless
    run.tag("branch", git.branch());
    MetricLogger loss = run.metric("train_loss", 0.0, 50);   // every 50 iterations
    for (int i = 0; i < maxIter; i++) {
        trainStep(i);
        loss.at(i, currentLoss());           // cadence enforced inside the logger
        if (i % 1000 == 0) System.out.printf("iter %d loss %.4f%n", i, currentLoss());
    }
    run.metricOnce("val_auc", evaluate(heldOut()));
    run.logArtifact("model.bin", modelPath);   // once, not per iteration
}   // run closed here even if the body threw
```


---

## 3.2 Metric logger with cadence and units

Cadence is part of the metric definition, so every logger for a metric behaves the same way. Units go in the tag so a chart can label itself.

```java
final class MetricLogger {
    private final long runId; private final String name; private final int cadence;
    private long lastLoggedAt = Long.MIN_VALUE;

    MetricLogger(TrackingClient client, long runId, String name, double initial, int cadence) {
        this.runId = runId; this.name = name; this.cadence = cadence;
        client.logMetric(runId, name, initial);        // value 0 is the honest starting point
    }
    void at(long step, double value) {
        if (step - lastLoggedAt < cadence) return;      // drop the rest, keep the series
        lastLoggedAt = step;
        client.logMetric(runId, name, value);
    }
    void tagUnits(String unit) { client.setTag(runId, name + ".unit", unit); }
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| One metric log call | `O(1) HTTP` | cadence control dominates, not the call |
| Full run with 20 metrics at cadence 50 | `O(metrics x steps/cadence)` | tens of thousands of small writes |
| Artifact log | `O(artifact size)` | the real storage cost |
| Comparison query | `O(indexed rows)` | needs the right tags to be indexed |

## 5. Correctness and Numerics

- Use an AutoCloseable run so runs are never left open on exceptions.
- Log params before the first training step, not after.
- Choose cadence by run length, not by habit.
- Attach units and step indices as tags so a chart is self-describing.
- Set retention and a storage budget before scaling to thousands of runs.

## 6. Test Strategy

- A run that throws still appears as FINISHED with its params intact.
- Metric cadence drops intermediate values but keeps first and last.
- Two runs with the same config get different run ids but the same reproducibility key.
- Filtering by a data version tag returns only those runs.
- The delta report refuses to compare runs with different data version tags.

## 7. Extension Points

- Add a registry client so promotion writes back to the model registry.
- Implement a parent/child run hierarchy for hyperparameter sweeps.
- Build a regression alert that pages when a nightly run's metric drops beyond tolerance.

## 8. Review Checklist

- [ ] Params and tags logged at run start
- [ ] Runs closed reliably via try-with-resources
- [ ] Metrics logged as a time series with cadence and units
- [ ] Artifacts logged once, with a size and retention policy
- [ ] Comparisons refuse to mix data versions
- [ ] Run naming follows a convention that avoids collisions
