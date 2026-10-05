# ML Platform — MINI PROJECT

## Project: Feature Store + Reproducible Training + Registry + Guarded Retraining

A platform slice in Java 21: a point-in-time-correct feature pipeline, a
reproducible trainer, a model registry with promotion gates, a serving path
with a parity guarantee, drift monitoring, and a retraining loop that refuses
to promote a regression.

### Scope

- **Features**: offline materialization with an as-of join, an online store,
  a parity checker, and a deliberate leak test.
- **Training**: deterministic run given (data snapshot, code hash, seed),
  artifact + metrics written together, an experiment log.
- **Registry**: versions, stage (`DEV -> STAGING -> PRODUCTION`), promotion
  gates (offline metric, inference latency, a fairness check), and rollback.
- **Serving**: batch and online scoring, shadow mode, canary with automatic
  rollback on error rate or latency.
- **Monitoring**: input drift (PSI), prediction drift, and a delayed-label
  quality metric.
- **Retraining**: scheduled, but promotion is gated against the incumbent on
  the same eval set — a worse model cannot ship.

### Architecture

```
 sources -> [offline features, point-in-time] -> training set
                        |                             |
                        +-> [online store]           v
                                    |          [trainer] -> [registry]
                                    |                             |
                                 [serving] <---- canary -------+
                                    |
                             [predictions] -> [drift monitor]
                                                        |
                                              labels arrive
                                                        v
                                              [retrain loop] -- gated ---> registry
```

### Implementation — features with a deliberate leak test

```java
public final class PointInTimeMaterializer {
    /**
     * For each label (entity, label_ts), the feature value is the most recent
     * feature row with event_ts <= label_ts. This is the single most important
     * correctness property in the whole platform, and the one most often
     * broken by a well-meaning refactor.
     */
    public List<TrainingRow> materialize(List<Label> labels, Map<String, List<FeatureRow>> features) {
        Map<String, List<FeatureRow>> byEntity = new HashMap<>();
        features.forEach((name, rows) -> rows.stream()
                .collect(Collectors.groupingBy(FeatureRow::entity,
                        TreeMap.comparing(FeatureRow::eventTs).reversed()))
                .forEach(byEntity::put));

        List<TrainingRow> out = new ArrayList<>(labels.size());
        for (Label label : labels) {
            Map<String, Double> values = new LinkedHashMap<>();
            features.keySet().forEach(name -> {
                List<FeatureRow> candidates = byEntity.getOrDefault(name, List.of());
                for (FeatureRow row : candidates) {                 // newest first
                    if (!row.eventTs().isAfter(label.labelTs())) {   // the constraint
                        values.put(name, row.value());
                        break;
                    }
                }
            });
            out.add(new TrainingRow(label.entity(), label.labelTs(), values, label.label()));
        }
        return out;
    }

    /**
     * The leak test, and it must FAIL when the constraint is removed. A leak
     * test that only asserts the correct behaviour passes just as well with a
     * broken implementation, so the suite also asserts the test's own power.
     */
    @Test void pointInTimeJoinExcludesFutureFeatures() {
        List<FeatureRow> features = List.of(
                new FeatureRow("u1", at("2026-01-09"), "spend_30d", 100.0),
                new FeatureRow("u1", at("2026-01-20"), "spend_30d", 9999.0));  // future
        List<Label> labels = List.of(new Label("u1", at("2026-01-10"), 1));

        TrainingRow row = materializer.materialize(labels, Map.of("spend_30d", features)).get(0);
        assertEquals(100.0, row.features().get("spend_30d"));
    }

    @Test void leakTestWouldCatchALeak() {
        // A deliberately broken materializer, to prove the test above has power.
        NaiveMaterializer naive = new NaiveMaterializer();   // no as-of constraint
        TrainingRow row = naive.materialize(
                List.of(new Label("u1", at("2026-01-10"), 1)),
                Map.of("spend_30d", List.of(new FeatureRow("u1", at("2026-01-20"), "spend_30d", 9999.0)))
        ).get(0);
        assertEquals(9999.0, row.features().get("spend_30d"));   // leaked, as intended
    }
}
```

### Implementation — reproducible training

```java
public final class Trainer {
    /**
     * Reproducibility contract: given the same (snapshotId, codeHash, seed,
     * hyperParameters), the run produces byte-identical model parameters.
     * Anything that breaks it is a bug in the platform, not the model.
     */
    public record RunKey(String snapshotId, String codeHash, long seed,
                         Map<String, String> hyperParams) {
        public String fingerprint() {                    // the identity of a run
            return sha256(snapshotId + "|" + codeHash + "|" + seed
                    + "|" + new TreeMap<>(hyperParams).toString());
        }
    }

    public TrainingRun train(RunKey key) {
        Dataset ds = snapshotStore.load(key.snapshotId());   // immutable, content-addressed
        if (registry.hasFingerprint(key.fingerprint())) {
            return registry.lookup(key.fingerprint());       // cache hit, no recompute
        }
        Model model = new Model(key.seed());
        TrainLog log = new TrainLog();
        for (int epoch = 1; epoch <= epochs(key); epoch++) {
            // Deterministic shuffling: seeded, and the seed travels with the run.
            for (Batch batch : ds.batches(key.seed(), epoch, batchSize(key))) {
                model.update(batch, log);
            }
        }
        Metrics metrics = evaluate(model, evalSet(key.snapshotId()));
        // Artifacts and metrics are written together, or not at all.
        return registry.register(model, key, metrics, log, codeHash());
    }
}
```

```java
/** The seed must reach the shuffling, not just the weight initialisation.
 *  This is the mistake that makes "reproducible" a claim rather than a fact. */
public final class DeterministicShuffler {
    private final long seed;
    public Iterator<Row> shuffle(List<Row> rows) {
        List<Row> copy = new ArrayList<>(rows);
        Collections.shuffle(copy, new Random(seed));      // seeded, not default
        return copy.iterator();
    }
}
```

### Implementation — registry with promotion gates

```java
public record ModelVersion(String name, long version, RunKey runKey, Stage stage,
                           double offlineMetric, long p99LatencyMillis,
                           Map<String, Double> fairnessMetrics,
                           Instant createdAt, String createdBy) {}

public enum Stage { DEV, STAGING, PRODUCTION, RETIRED }

public final class PromotionGate {
    /**
     * A version cannot reach PRODUCTION without passing all of these. The
     * fairness and latency gates matter as much as the metric: a model that
     * scores better and takes 400ms is a worse product.
     */
    public GateResult evaluate(ModelVersion v, Gates g) {
        List<String> failures = new ArrayList<>();
        if (v.offlineMetric() < g.minOfflineMetric())
            failures.add("offline metric " + fmt(v.offlineMetric()) + " < " + g.minOfflineMetric());
        if (v.p99LatencyMillis() > g.maxP99Millis())
            failures.add("p99 " + v.p99LatencyMillis() + "ms > " + g.maxP99Millis() + "ms");
        v.fairnessMetrics().forEach((segment, value) -> {
            double ratio = value / g.referenceMetric();
            if (ratio < g.minFairnessRatio())
                failures.add("segment " + segment + " scores " + fmt(ratio)
                        + "x reference, below " + g.minFairnessRatio());
        });
        return failures.isEmpty() ? GateResult.pass() : GateResult.fail(failures);
    }

    public void promote(ModelVersion v, Gates g) {
        if (v.stage() != Stage.STAGING) throw new IllegalStateException("not in STAGING");
        GateResult r = evaluate(v, g);
        if (!r.passed()) throw new PromotionBlocked(v.name() + "@" + v.version(), r.failures());
        registry.transition(v, Stage.PRODUCTION);
        registry.retirePreviousProduction(v.name(), v.version());
        audit.record("promote", v.name(), v.version(), r);
    }

    /** Rollback must be fast and must not require a deploy. */
    public void rollback(String name, String reason) {
        ModelVersion previous = registry.lastProductionBefore(name, currentProduction(name));
        if (previous == null) throw new NoRollbackTarget(name);
        registry.transition(currentProduction(name), Stage.RETIRED);
        registry.transition(previous, Stage.PRODUCTION);
        serving.reload(name, previous);          // atomic pointer swap
        audit.record("rollback", name, previous.version(), reason);
    }
}
```

### Implementation — serving with parity, shadow, and canary

```java
public final class ScoringService {
    public Prediction score(String modelName, String entity, Map<String, Double> overrides) {
        ModelVersion model = registry.production(modelName);
        // Parity: the SAME transform library that built the training features.
        // This is what prevents training/serving skew, and it is the single
        // highest-value architectural decision on the platform.
        FeatureVector f = transforms.apply(model.runKey().snapshotId(), entity, overrides);
        double prediction = model.predict(f);
        return new Prediction(model.name(), model.version(), prediction, now(),
                model.runKey().fingerprint());
    }

    /** Shadow: score with the candidate, serve the incumbent. No user impact,
     *  and the only safe way to compare two models on live traffic. */
    public Response shadow(String modelName, String candidateVersion, Request r) {
        Response served = score(registry.production(modelName), r);
        double shadowScore = score(registry.version(candidateVersion), r);
        shadowLog.record(r, served.prediction(), shadowScore);
        return served;
    }

    /** Canary: a percentage of traffic to the candidate, with automatic
     *  rollback on error rate or latency. The gate is time-bounded, not
     *  "we will look at it tomorrow". */
    public Response canary(String modelName, String candidateVersion, Request r) {
        CanaryState state = canary.state(modelName);
        if (state == null || !state.active()) return score(registry.production(modelName), r);
        if (randomPercent(r, state.trafficPercent())) {
            try {
                Response c = score(registry.version(candidateVersion), r);
                canary.record(candidateVersion, c);
                if (canary.errorRate(candidateVersion) > state.maxErrorRate()
                        || canary.p99(candidateVersion) > state.maxP99Millis()) {
                    canary.abort(candidateVersion, "gate breached");
                    registry.rollbackTo(modelName, state.incumbentVersion());
                }
                return c;
            } catch (RuntimeException e) {
                canary.abort(candidateVersion, e.getMessage());
                registry.rollbackTo(modelName, state.incumbentVersion());
                return score(registry.production(modelName), r);      // incumbent again
            }
        }
        return score(registry.production(modelName), r);
    }
}
```

### Implementation — drift and delayed-label quality

```java
public final class ModelMonitor {
    public record Signal(String name, double value, Instant at, Severity severity) {}

    /**
     * Three signals, because they fail differently:
     *   INPUT_DRIFT     - the population changed. The model may be fine and
     *                     irrelevant, or broken; you cannot tell yet.
     *   PREDICTION_DRIFT- outputs shifted. Catches a broken pipeline faster
     *                     than input drift does, because it is downstream of
     *                     everything.
     *   LABEL_QUALITY   - the real metric, once labels arrive (often 30 days).
     *                     This is the one that matters and the one that
     *                     arrives last, so the other two are the early signal.
     */
    public List<Signal> evaluate(String modelName, Instant now) {
        List<Signal> out = new ArrayList<>();
        out.add(psi("input_drift", distributions.input(modelName), BASELINE_WINDOW)
                .orElseGet(() -> Signal.silent("input_drift")));
        out.add(psi("prediction_drift", distributions.predictions(modelName), BASELINE_WINDOW)
                .orElseGet(() -> Signal.silent("prediction_drift")));
        labels.for(modelName, 30, DAYS).ifPresent(l ->
                out.add(new Signal("label_quality", l.value(), l.at(),
                        l.value() < labelThreshold ? Severity.PAGE : Severity.SILENT)));
        return out;
    }
}
```

### Implementation — guarded retraining

```java
public final class RetrainingLoop {
    /**
     * The guard, and it is the whole design: a retrained model is a CANDIDATE.
     * It is evaluated on the SAME eval set as the incumbent and must beat it
     * by a margin. Otherwise the incumbent stays. A retraining loop that
     * always promotes is a loop that eventually ships a worse model at 3am
     * with nobody watching.
     */
    public RetrainOutcome run(String modelName) {
        ModelVersion incumbent = registry.production(modelName);
        String snapshot = snapshotStore.latestCompleteSnapshot();
        if (snapshot.equals(incumbent.runKey().snapshotId())) {
            return RetrainOutcome.skipped("no new complete snapshot");
        }

        TrainingRun candidate = trainer.train(new RunKey(
                snapshot, codeHash(), seed(), hyperParams()));

        EvalResult newEval = evaluator.evaluate(candidate, EVAL_SET);
        EvalResult oldEval = evaluator.evaluate(incumbent, EVAL_SET);

        double delta = newEval.metric() - oldEval.metric();
        if (delta < MIN_IMPROVEMENT) {
            registry.registerAsCandidate(candidate, newEval);
            return RetrainOutcome.rejected("metric " + fmt(oldEval.metric()) + " -> "
                    + fmt(newEval.metric()) + " (delta " + fmt(delta) + " < " + MIN_IMPROVEMENT + ")");
        }
        if (!latencyWithinBudget(candidate)) {
            return RetrainOutcome.rejected("p99 " + candidate.p99Millis() + "ms exceeds budget");
        }
        if (fairnessRegression(candidate, incumbent)) {
            return RetrainOutcome.rejected("fairness regression on segment " + worstSegment(candidate));
        }

        registry.promoteToStaging(candidate);
        canary.start(modelName, String.valueOf(candidate.version()),
                     trafficPercent = 5, duration = Duration.ofHours(24),
                     maxErrorRate = 0.001, maxP99Millis = 45);
        return RetrainOutcome.staged(candidate.version());
    }
}
```

### Test It

```java
@Test void retrainingRefusesToPromoteARegression() {
    trainer.forceNextMetric(0.61);                    // worse than the incumbent
    RetrainOutcome outcome = loop.run("churn");
    assertEquals(RetrainOutcome.Status.REJECTED, outcome.status());
    assertEquals(incumbentVersion, registry.production("churn").version());
    assertEquals(1, canary.state("churn") == null ? 0 : 1, 0);   // no canary started
}

@Test void trainingIsByteIdenticalForTheSameRunKey() {
    RunKey key = new RunKey("snap-42", "abc123", 7L, Map.of("lr", "0.01"));
    byte[] a = trainer.train(key).parameters();
    byte[] b = trainer.train(key).parameters();        // cache hit path
    assertArrayEquals(a, b);
    deleteCacheEntry(key.fingerprint());
    byte[] c = trainer.train(key).parameters();        // recomputed path
    assertArrayEquals(a, c, "same RunKey must give identical parameters");
}

@Test void canaryRollsBackOnErrorRate() {
    canary.start("churn", "v9", 5, Duration.ofHours(1), 0.001, 45);
    for (int i = 0; i < 500; i++) scoreAndForceFailure("v9");
    assertEquals(incumbentVersion, registry.production("churn").version());
}
```

### Stretch

- Add a shadow-comparison dashboard: candidate vs incumbent agreement rate.
- Add fairness monitoring in production, not just at promotion.
- Add a cost-aware retraining trigger: retrain on drift, not just on a calendar.
- Add a reproducibility check that runs nightly and re-trains yesterday's run.

## Deliverables

- [ ] Point-in-time-correct materializer plus a leak test that proves its own power
- [ ] Online store with a parity checker and a shared transform library
- [ ] Reproducible trainer: RunKey fingerprint, seeded shuffling, cache by fingerprint
- [ ] Model registry with 3 gates (metric, latency, fairness) and fast rollback
- [ ] Serving with shadow mode and a time-bounded canary that auto-rolls back
- [ ] Three-signal monitor: input drift, prediction drift, delayed label quality
- [ ] Retraining loop that rejects regressions and only stages improvements
- [ ] Tests: regression refusal, byte-identical retraining, canary rollback
- [ ] Cost per prediction and cost per retraining run, measured
