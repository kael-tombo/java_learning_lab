# Model Monitoring & Observability

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

## 1. The Problem This Solves

A model in production is never the model you validated. Inputs change, predictions change, and quality decays quietly until a business metric notices.

Deployment is the midpoint. Drift detection and performance monitoring are how you learn about degradation in hours rather than at the next quarterly review.

## 2. Learning Objectives

- Distinguish data drift, concept drift and prediction drift
- Compute PSI, KL and JS divergence between reference and current windows
- Monitor performance with delayed labels and sliding windows
- Set alert thresholds from measurement rather than convention
- Instrument the serving path for latency, errors and saturation
- Design a retrain trigger tied to evidence rather than a calendar

## 3. Core Concepts

### 3.1 Three kinds of drift

Data drift is the input distribution moving. Concept drift is the relationship between inputs and outcome changing. Prediction drift is the output distribution moving. Only concept drift necessarily means quality loss, and it is the one you can only detect once labels arrive.

### 3.2 Delayed labels are the hard part

Fraud labels take 90 days, churn takes 30, demand takes a week. So performance monitoring must be structured around label latency: score immediately, evaluate later, and report the delay explicitly rather than hiding it behind a shorter window.

### 3.3 PSI is a practical, not a statistical, tool

The population stability index buckets the reference and current distributions and sums (current - reference) x ln(current/reference). Thresholds of 0.1 and 0.25 are conventions from the credit literature. They are useful for alerting and useless as proof of harm.

### 3.4 Alerting on slope, not threshold

A feature that crosses 0.25 once during a seasonal peak is noise. A feature whose 7-day PSI trend rises steadily is a change. Alerting on sustained slope or on repeated breaches catches problems a threshold alert misses until it is an incident.

### 3.5 Servicing metrics are model metrics

Latency, error rate, queue depth and throttle ratio tell you the model is unhealthy before accuracy tells you it is wrong. Both belong on the same dashboard because the failure modes are different and the response is different.

### 3.6 Retraining on a trigger, not a calendar

A weekly retrain is either wasteful (nothing drifted) or late (drift outpaced it). Trigger on evidence: sustained PSI breach plus a performance drop once labels mature, with a minimum interval so you do not thrash.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `PSI = Σ (a_i - b_i) ln(a_i / b_i)` | Population stability index | bucketed distribution distance |
| `KL(P||Q) = Σ P log(P/Q)` | Kullback-Leibler divergence | asymmetric, infinite when support differs |
| `JS(P,Q) = 0.5 KL(P||M) + 0.5 KL(Q||M)` | Jensen-Shannon | symmetric, bounded |
| `slope = Δpsi / Δt over window` | Drift trend | better than threshold for alerting |
| `quality(t) = metric(scores at t, labels arriving by t + lag)` | Delayed evaluation | explicit about label lag |
| `retrain if sustained_breach AND quality_drop AND interval > min_interval` | Trigger | evidence-based |

## 5. How the Pieces Fit Together

1. Capture a reference distribution from the training data at model publish time.

2. Instrument the serving path: score, features, model version, outcome and latency, per request.

3. Compute drift metrics per feature on a sliding window and store the series.

4. Evaluate performance when labels arrive, joining by prediction id rather than time.

5. Alert on sustained slope or repeated breaches, with thresholds documented and reviewed.

6. Trigger retraining on combined evidence with a minimum interval.

## 6. Assumptions and Invariants

- A reference distribution is stored with the model version
- Scores, features and outcomes are joined by prediction id, not by timestamp
- Label latency is known, documented and built into the evaluation design
- Drift thresholds are set from observed history and reviewed, not copied
- Alerting uses sustained trends rather than single crossings
- Retraining has a minimum interval to prevent thrashing

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| PSI alert fires every Monday morning | weekly seasonality treated as drift | compare against the same weekday or use a seasonal baseline |
| Accuracy looks fine but business revenue dropped | delayed labels and a mismatched business metric | monitor the business KPI alongside model metrics |
| Drift detected on a feature nobody uses | monitoring every column including IDs | monitor features the model actually depends on, weighted by importance |
| Retrain daily and nothing improves | trigger without a minimum interval or without an evaluation | require evidence plus a minimum interval and a post-retrain comparison |
| KL divergence returns infinity | current window has support the reference lacks | bucket identically or use JS, which is bounded |
| Nobody trusts the alert after two false positives | threshold copied from literature with no history | set thresholds from your own reference windows |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `record ScoreEvent(String predictionId, double score, double[] features, String modelVersion, Instant ts)` | the join key that makes delayed labels work |
| `DoubleSummaryStatistics / streaming bucketing` | PSI computed on a sliding window without holding history |
| `AtomicLongArray for histogram buckets` | lock-free counter updates per request |
| `DoubleStream rolling window via a ring buffer` | sustained-slope detection over the last N buckets |
| `Micrometer counters and timers` | servicing metrics on the same dashboard as model metrics |

## 9. Where This Sits in the Larger System

- **mlops/lab10** is where drift statistics meet a significance decision.
- **mlops/lab06** supplies the probes and metrics this lab consumes.
- **mlops/lab01** runs the retraining job this lab triggers.
- **mlops/lab03** holds the promotion gate after a retrain.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Distinguish data drift, concept drift and prediction drift
- [ ] 0 — cannot yet — Compute PSI, KL and JS divergence between reference and current windows
- [ ] 0 — cannot yet — Monitor performance with delayed labels and sliding windows
- [ ] 0 — cannot yet — Set alert thresholds from measurement rather than convention
- [ ] 0 — cannot yet — Instrument the serving path for latency, errors and saturation
- [ ] 0 — cannot yet — Design a retrain trigger tied to evidence rather than a calendar

## 11. Summary Checklist

- [ ] I can distinguish data, concept and prediction drift.
- [ ] Reference distributions are stored with the model version.
- [ ] Labels are joined by prediction id and label latency is explicit.
- [ ] Alerts use sustained slope, not single crossings.
- [ ] Thresholds come from my own history.
- [ ] Retraining triggers require evidence plus a minimum interval.
