# ML Platform — REAL WORLD PROJECT

## Context

An insurer runs 61 models in production: claims triage, fraud, underwriting
referral, churn, pricing elasticity, and 20 more. The platform team is three
engineers supporting 40 data scientists who each train locally. There is one
production model with a documented accuracy of 0.84 and a measured production
AUC of 0.71. Nobody knows when the gap opened, and two models have never been
retrained. You own the platform.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Models | 61 in production, 400+ in development, 40 data scientists |
| Scoring | 340k predictions/sec peak, p99 42ms |
| Retraining | 2 models retrained weekly, 3 have never been retrained, 1 retrained 14 months ago |
| Drift | no monitoring; 2 silent degradations found by users in the last year |
| Cost | $284k/month: 46% inference, 31% training, 14% features, 9% serving infra |
| Compliance | model risk management (SR 11-7 style): documented validation, bias testing, rollback |
| Constraint | cannot stop the data scientists; adoption has to be pulled, not pushed |
| Evidence | every production model needs an owner, a validation date, and a rollback path |

## Architecture (target)

```
 notebooks (40 scientists)
   |  self-serve, no gate to experiment
   v
 [experiment tracking]  every run logged with RunKey, even if it fails
   |
 [training pipelines]  declarative, reproducible, snapshot-pinned
   |
 [model registry]  DEV -> STAGING -> SHADOW -> CANARY -> PRODUCTION
   |   gates: metric vs incumbent, latency, fairness, explainability artifact
   v
 [serving]  shared transform library, shadow + canary, atomic rollback
   |
 [monitoring]  input drift, prediction drift, delayed labels, per-segment
   |
 [retraining]  drift-triggered, guarded, never auto-promotes
```

## Key Implementation — the 0.84 vs 0.71 gap

The gap was the first thing to investigate and it is the most instructive
finding in this project. Three causes, in order of magnitude.

| Cause | Contribution | Evidence |
|---|---|---|
| Training/serving skew in 4 of 61 features | -0.09 AUC | serving implemented `NOW()` where training used the event timestamp; 3 features rounded differently |
| No point-in-time join in 2 feature tables | -0.03 AUC | two models had a target-encoded feature computed on the full dataset, including future rows |
| Concept drift, unmonitored for 9 months | -0.01 AUC | claims volume mix changed; the model is genuinely less suited |

The 0.11 AUC gap decomposed, and the two largest causes were engineering
defects rather than modelling choices. This is the argument that won budget
for the platform: most of the distance between claimed and actual model
performance is pipeline correctness, not model quality.

## Key Implementation — the four changes, with numbers

**Change 1: one transform library, used by both training and serving.** The
skew was not a monitoring gap; it was two implementations of one definition.

```java
/**
 * The architectural decision. A feature is defined ONCE, as code, and both
 * the training pipeline and the serving path call it. There is no second
 * implementation to drift.
 *
 * The consequence people resist: the transform must be pure, deterministic,
 * and free of wall-clock reads. Anything that needs "now" must take it as a
 * parameter - which is exactly the bug that cost 0.09 AUC.
 */
public interface FeatureTransform {
    String name();
    String entityKey();
    double apply(FeatureContext ctx);   // ctx.asOf, never System.currentTimeMillis()
    Duration ttl();
}

public final class FeatureContext {
    private final Instant asOf;        // the only clock
    private final Map<String, Object> inputs;
    public static FeatureContext at(Instant asOf, Map<String, Object> inputs) {
        return new FeatureContext(asOf, inputs);
    }
    // No no-arg constructor. You cannot accidentally read the wall clock.
}
```

Parity is then enforced rather than hoped for:

```java
/** CI gate: for 5,000 sampled (entity, asOf) pairs, the offline value and the
 *  online value must be identical. Any difference is a build failure, because
 *  it is a silent model-quality leak that no metric will catch in time. */
public final class ParityGate {
    static final double TOLERANCE = 1e-9;

    public ParityReport verify(List<SamplePair> samples) {
        List<String> mismatches = new ArrayList<>();
        for (SamplePair s : samples) {
            double offline = transforms.apply(s.name(), s.context());
            double online  = onlineStore.get(s.entity(), s.name(), s.asOf());
            if (Math.abs(offline - online) > TOLERANCE) {
                mismatches.add(s.name() + "@" + s.entity()
                        + " offline=" + offline + " online=" + online);
            }
        }
        return new ParityReport(samples.size(), mismatches);
    }
}
```

Result: production AUC gap narrowed from 0.11 to 0.012, and 4 features were
found to be flat wrong (returning a constant).

**Change 2: a registry with gates that include compliance artifacts.** Model
risk management requires documented validation, bias testing, and a rollback
path. Making those promotion gates means compliance becomes a byproduct rather
than a quarterly scramble.

```java
public record PromotionGates(
        double minMetricDeltaVsIncumbent,      // 0.005: must actually improve
        long maxP99Millis,                     // 45
        Map<String, Double> minSegmentRatio,   // fairness: 0.90 of the overall metric
        boolean requireExplainabilityArtifact, // true
        boolean requireValidationReport,       // SR 11-7 style
        int maxShadowHours) {                  // 48: shadowing is mandatory
}

public GateResult evaluate(ModelVersion candidate, ModelVersion incumbent,
                           List<ValidationReport> validation) {
    List<String> failures = new ArrayList<>();
    if (candidate.stage() == Stage.PRODUCTION) failures.add("already production");
    if (candidate.offlineMetric() - incumbent.offlineMetric() < gates.minMetricDeltaVsIncumbent())
        failures.add("metric does not beat the incumbent by the required margin");
    if (candidate.p99Millis() > gates.maxP99Millis())
        failures.add("p99 " + candidate.p99Millis() + "ms exceeds " + gates.maxP99Millis() + "ms");
    for (String segment : gatedSegments(candidate)) {
        double ratio = candidate.metricOn(segment) / candidate.metricOverall();
        if (ratio < gates.minSegmentRatio().getOrDefault(segment, 0.90))
            failures.add("segment '" + segment + "' at " + fmt(ratio)
                    + "x overall, below the fairness floor");
    }
    if (!candidate.hasExplainabilityArtifact()) failures.add("no explainability artifact");
    if (validation.stream().noneMatch(v -> v.approved()
            && v.coversSubpopulationTesting() && v.coversStabilityAnalysis()))
        failures.add("model risk validation not current");
    if (candidate.shadowHours() < gates.maxShadowHours())
        failures.add("shadowed for " + candidate.shadowHours() + "h, need " + gates.maxShadowHours());
    return GateResult.of(failures);
}
```

**Change 3: rollback measured in seconds, because that is the requirement.**
Not "we can redeploy" — a pointer swap with the previous artifact already warm.

| Model | Before | After |
|---|---|---|
| Median rollback time | 22 minutes (redeploy pipeline) | 4.1 seconds (atomic pointer swap) |
| Models with a tested rollback path | 4 of 61 | 61 of 61 |
| Rollbacks performed last quarter | 0 (too slow to attempt) | 3 |

**Change 4: retraining on drift, gated, never automatic.** Three models had
never been retrained; one was 14 months stale. Automatic retraining without a
gate is how that becomes six months stale in the other direction.

```java
public final class RetrainingPolicy {
    /**
     * Triggers, in priority order:
     *   1. DRIFT: PSI on inputs or predictions above threshold for 3 days.
     *      This is the real trigger; calendars are a fallback.
     *   2. AGE: older than 90 days, as a backstop for genuinely static models.
     *   3. MANUAL: a data scientist requests it.
     *
     * Never a trigger: "we retrained last week so retrain again". Weekly
     * retraining of a stable model costs compute and adds variance to the
     * production metric for no benefit.
     */
    public enum Trigger { INPUT_DRIFT, PREDICTION_DRIFT, AGE, MANUAL }
}
```

| Metric | Before | After |
|---|---|---|
| Models with drift monitoring | 0 | 61 |
| Models retrained on drift within 7 days | n/a | 100% |
| Models older than 180 days | 41 of 61 | 0 |
| Rejected promotions (a worse model) | 0 | 19 |
| Monthly training cost | $88k | $31k (drift-triggered, not weekly) |

Cost fell 65% while coverage went from 20 models to 61, because drift-triggered
retraining does most of the work and the calendar retraining it replaced was
mostly wasted.

## The adoption problem, and how it was solved

Three engineers cannot review 400 models. The platform had to be worth using
without being mandatory, because mandatory platforms get worked around.

- **Zero-friction start**: a `platform init` in a notebook registers an
  experiment in under a minute. 91% of runs are now logged, up from 0%, because
  logging is the default rather than a step.
- **Gates apply only to production promotion**, never to experimentation. The
  friction is exactly where the risk is.
- **Self-serve promotion for models below a risk tier**, with gates enforced
  automatically rather than reviewed. 22 of 61 models are self-serve.
- **A shared transform library means less work, not more**: 40 scientists
  stopped writing their own feature code, which was a net time saving even
  though adoption was framed as compliance.

## Measured outcomes

| Metric | Before | After |
|---|---|---|
| Claimed-vs-actual AUC gap | 0.11 | 0.012 |
| Models with drift monitoring | 0 | 61 |
| Models retrained in the last 90 days | 2 | 54 |
| Experiments logged | ~0% | 91% |
| Median rollback time | 22 min | 4.1 s |
| Models with a validated risk assessment | 4 | 61 |
| Rejected promotions (worse models) | 0 (no process) | 19 |
| Inference cost per 1k predictions | $0.83 | $0.61 (batch path, better packing) |
| Monthly platform cost | $284k | $222k |
| Silent model degradations found by users | 2/year | 0 |

## Failure Modes and the Runbook

1. **Parity gate fires in CI on a data-dependent feature.** Symptom: build
   failures on a feature that "worked yesterday". Cause: the feature reads a
   mutable source, or a transform is not pure. Fix: make the source immutable
   and the transform pure; a feature that cannot be made pure does not belong
   in a shared library.
2. **Canary looks healthy and the model is worse.** Symptom: no alerts, users
   unhappy. Cause: the label lag exceeds the canary window, so quality is
   invisible during the test. Fix: the canary gates on proxy signals
   (prediction distribution, segment mix) and the *real* gate is the delayed
   label check, which is why shadowing duration is mandated at 48 hours.
3. **A retrained model is promoted and degrades a segment.** Symptom: overall
   metric fine, one segment collapses. Fix: the fairness gate compares segment
   ratios to the incumbent, not to an absolute floor, so a segment regression
   blocks promotion even when the overall metric improves.
4. **Rollback targets a version that no longer exists.** Symptom: rollback
   fails at 3am. Fix: the last five production versions per model are retained
   and warm; the rollback path is tested quarterly per model, and a test is a
   promotion gate.
5. **The feature store goes stale and every model degrades together.**
   Symptom: broad metric drop across models within an hour. Fix: a freshness
   SLO per feature class with paging to the platform team, and a circuit
   breaker that falls back to the last-known-good feature values with a
   staleness flag passed to the model.
6. **A data scientist bypasses the platform to ship.** Symptom: a model in
   production that is not in the registry, discovered during an audit. Fix: a
   nightly scan for untracked endpoints, and a self-serve path that is faster
   than the bypass. The bypass exists because the platform was slow, and that
   is a platform problem, not a compliance one.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Feature stores exist to keep training and serving feature computation
  consistent, and point-in-time-correct joins are required to avoid leakage;
  sharing one definition between the two paths is the mechanism that prevents
  training/serving skew.
  - Reference: https://feast.dev/
  - Reference: https://docs.feast.dev/getting-started/concepts/point-in-time-joins
- A model registry records model versions and their lineage and stage, and
  staged promotion with shadow or canary testing is the standard mechanism for
  controlling what reaches production.
  - Reference: https://mlflow.org/docs/latest/model-registry.html
  - Reference: https://mlflow.org/docs/latest/model-evaluation.html
- Drift detection compares a current data distribution to a reference
  (commonly with a population stability index), and retraining is normally
  triggered by monitored drift rather than by a calendar alone.
  - Reference: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.jaccard_score.html
  - Reference: https://docs.greatexpectations.io/docs/reference/metric_library/distance_metrics/psi

## Deliverables

- [ ] AUC gap decomposition with the three causes and their magnitudes
- [ ] Shared pure transform library with an `asOf` clock and a CI parity gate
- [ ] Model registry with 5 gates including fairness and model-risk validation
- [ ] Atomic rollback in under 10 seconds, with a quarterly per-model test
- [ ] Three-signal monitoring with a 7-day drift-to-retrain SLO
- [ ] Drift-triggered retraining that never auto-promotes; 19 rejections logged
- [ ] Adoption plan: zero-friction logging, gates only at promotion, self-serve tiers
- [ ] Before/after table for AUC gap, monitoring coverage, retraining, cost
- [ ] Runbook for the six failure modes
