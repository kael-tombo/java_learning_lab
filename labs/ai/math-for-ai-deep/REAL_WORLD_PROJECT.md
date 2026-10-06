# math-for-ai-deep — Real-World Project

## Project: A Forecasting and Anomaly Platform Built on Mathematical Guarantees

Build a demand forecasting and anomaly detection platform where the mathematics is the
specification: uncertainty intervals that are honest because they come from a stated
posterior, drift statistics that are symmetric because of Jensen-Shannon, a Kalman filter
that is numerically stable because of Cholesky, a truncated SVD denoiser with a proven
error bound, and a resource planner that uses convergence theory rather than empirical
tuning.

## Context

Forecasting platforms fail in predictable ways: intervals that are too narrow, drift alerts
that fire constantly, filters that diverge on ill-conditioned data, and capacity plans tuned
by guesswork. Each of those is a mathematical defect, and each is fixed by choosing the
right object — a posterior instead of a point estimate, a symmetric divergence instead of
KL, a stable factorization, and a rate bound instead of a spreadsheet.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "The Kalman Filter is a Bayesian Filter" — practical treatment in
  https://huggingface.co/learn — takeaway for this lab: a Kalman update is exactly the
  Normal-Normal conjugate update, where the prediction's precision and the observation's
  precision are combined; this platform implements the filter from that identity rather than
  from a framework, and the accompanying lesson that monitoring residuals rather than
  states catches filter divergence earlier is what drives the monitoring design here.
- "Out-of-Sample Detection of Drift" — https://arxiv.org/abs/1612.04848 — takeaway for
  this lab: drift can be detected in an unsupervised, label-free way by comparing
  distributions on a held-out reference window, which is what lets the platform alert before
  labels arrive; the practical guidance to prefer bounded and symmetric divergences and to
  pre-bin on the reference window is precisely the design used in the drift monitor here.

## System Architecture

```
  ingest                    forecast                     anomaly
  ------                    --------                     -------
  events + time series -->  feature build          -->  residual analysis
      |                         |                        |
      |                    hierarchical model            likelihood-ratio tests
      |                    + quantiles                 |
      |                         |                   posterior predictive checks
      |                    posterior intervals          |
      |                         |                   robust covariance (MCD)
      |                    predictive draws               |
      |                         |                        |
      v                         v                        v
  Kalman filter  -->  reconciliation  --------->  drift monitor (JS divergence)
  (Cholesky)          (information-theoretic          |
                       data reconciliation)        change-point detection
                             |
                        capacity planner
                   (convergence-rate bound)
                             |
                     SVD denoiser (error bound)
```

## Component Specs

### 1. Feature Construction and Alignment
- Time-indexed series with explicit handling of missing values, calendar effects, and
  promotions. Missing values imputed with a state-space prediction rather than a mean, and
  the imputation uncertainty carried forward.
- **Leakage prevention**: every feature's `as_of` timestamp precedes the prediction target
  time; a point-in-time correctness test fails the build.
- Seasonal decomposition via additive decomposition with a numerically stable smoother; the
  decomposition is verified to sum back to the original within tolerance.

### 2. Hierarchical Forecasting with Coherence
- Forecast at multiple levels (total, region, product) and reconcile so that lower-level
  forecasts sum to upper-level ones.
- **Bottom-up plus MinT reconciliation**: projection onto the coherent subspace in the
  weighted least-squares sense, with the mixing matrix `S` and the weighting `W`.
- Reconciliation solved in the SVD basis of `W^(1/2) S`:

```
P = S (S'W^-1 S)^-1 S'W^-1
```

  and the rank of `S` used to size the reduced problem. The minimum trace property of MinT
  means no other weighting gives a lower total error variance — a theorem, which is why it
  is the default rather than a tunable.
- Incoherence measured and reported before and after reconciliation. A system shipping
  incoherent forecasts is shipping arithmetic errors.

### 3. Uncertainty That Is Honest
- **Quantile regression** at the 10th, 50th, and 90th percentiles, plus a full predictive
  distribution from the posterior.
- Intervals from a stated posterior, so their width follows from the posterior variance
  rather than from a heuristic multiplier on a residual standard deviation.
- **Interval calibration monitored, not assumed**: PIT (probability integral transform)
  uniformity as a diagnostic, plus the fraction of actuals falling inside each stated
  interval. An interval whose coverage is 70% when it claims 90% is a defect, and only a
  monitored statistic catches it.
- Conditional coverage checked by segment, because a globally calibrated interval can be
  badly miscalibrated for every individual segment.

### 4. Kalman Filter From the Conjugate Update
- State-space model with observation noise; the update is the Normal-Normal conjugate
  posterior:

```
S      = H P H' + R                    predictive covariance
K      = P H' S^-1                     Kalman gain
loglik += -0.5 (log det S + e' S^-1 e)
x_post = x_pred + K e
P_post = (I - K H) P_pred
```

- `S^-1` computed via **Cholesky**, not an explicit inverse: `S` is symmetric positive
  definite by construction, and Cholesky is half the cost and detects numerical breakdown
  directly.
- The log-likelihood accumulates the `-0.5 log det S` term, so the filter reports its own
  goodness of fit — no separate metric needed.
- **Numerical guardrails**: symmetrize `P` after every update (accumulated asymmetry
  degrades Cholesky), reject a non-positive-definite innovation covariance with a clear
  error rather than a NaN cascade, and monitor the ratio `||P_post|| / ||P_pred||`.
- Filter divergence detection: innovation statistics (mean, variance, autocorrelation) with
  control limits; a filter that has stopped tracking is caught by its own likelihood, not by
  a downstream metric.

### 5. Anomaly Detection with Multiple Statistical Views
- **Residual-based**: standardized residuals from the model, with the null distribution
  stated rather than assumed normal.
- **Likelihood-ratio test** between a fitted model and a constrained alternative, with the
  Wilks approximation for the reference distribution.
- **Robust covariance** via minimum covariance determinant (MCD): use a concentration step
  to find a clean subset, then estimate covariance on it. A single contaminated point can
  destroy a sample covariance completely; MCD is the standard defence.
- **Isolation Forest and LOF** for the multivariate case, with PR-AUC — not accuracy — as the
  metric at realistic anomaly rates.
- **Predictive-distribution checks**: is the actual inside the stated predictive
  distribution, and is the PIT uniform? A distributional violation is often more informative
  than a point outlier flag.
- Threshold chosen by expected cost with the false-positive and false-negative costs stated,
  and the confusion matrix at the operating point reported.

### 6. Drift Monitoring With Bounded Statistics
- **Jensen-Shannon divergence**, not KL. Reason: KL is asymmetric and unbounded, so a
  small mass shift into an uncovered region produces a huge one-sided number, and a
  two-sided comparison is unusable.
- Pre-binning on a **reference window** so that the divergence is comparable over time.
  Re-binning each window makes the statistic non-comparable and every alert becomes noise.
- **Population stability index** computed from the JS per bin, aggregated, with the
  conventional thresholds (below 0.1 stable, above 0.25 material) and the caveat that they
  are conventions rather than derived constants — reported as such.
- **Covariate shift versus concept drift**: with labels available, test whether
  `p(y)` changed (no drift) or `p(y|x)` changed (real drift). This distinction determines
  whether retraining helps at all, and it is the most useful thing the drift monitor
  produces.
- **Change-point detection** with a sequential test (CUSUM or a Bayesian online change point
  detector) so the alert has a location and a magnitude, not just a boolean.
- Detector-output drift monitored too: if the anomaly detector's own alert rate changes,
  that is an alert about the monitoring system.

### 7. SVD Denoiser With a Proven Bound
- Low-rank approximation of a noisy multivariate series, truncated by the singular value
  spectrum.
- **Error bound, not a guess**: `||A - A_k||_F = sqrt(sum_{i>k} sigma_i^2)`. Choose `k` as
  the smallest value meeting a stated Frobenius tolerance; the bound then certifies the
  error.
- Singular values provide the noise floor estimate: for white noise of variance `sigma^2`,
  the tail singular values cluster around `sigma sqrt(n)`, so the spectrum separates signal
  from noise without knowing `sigma` in advance.
- Reconstruction must sum back: verify `A_hat` reproduces the low-rank structure and that
  the discarded energy matches the bound.

### 8. Capacity and Compute Planning from Convergence Rates
- Number of iterations to reach a target for gradient-based solvers, from the analytic
  contraction factor for an `L`-smooth `mu`-strongly convex objective:

```
eta <= 1/L,   contraction = 1 - mu/L,   k >= log(target/initial) / log(1 - mu/L)
```

- For momentum, use the improved factor `(1 - beta sqrt(mu/L))/(1 + beta sqrt(mu/L))`. The
  planning conclusion is that momentum reduces iterations by roughly the square root of the
  condition number — a number you can compute before running anything.
- Learning-rate range test run in production-like conditions, but the **analytic bound is
  the constraint**: `eta > 2/L` diverges, so the search range is bounded a priori rather
  than by trial and error.
- Compute the conditioning of the system being solved (`cond(H)` from SVD) and report the
  predicted iteration count beside the observed one. A large discrepancy is a
  implementation finding, not a curiosity.
- Throughput planning for the forecast batch job: measured per-stage cost, projected for
  the expected data volume, with headroom for the peak.

### 9. Statistical Process Control Around Everything
- Control charts on residuals with control limits derived from the fitted model, not from
  the observed variance (which the outliers themselves inflate).
- Western Electric rules for run length and trend, applied to residual statistics.
- Every alert carries: the statistic, the value, the threshold, the reference window
  identity, and a runbook link.
- Alert fatigue tracked as a first-class metric: alerts per day, false-positive rate
  estimated from a holdout, and precision of each detector.
- **Detector coverage monitored**: if a data source stops arriving, the drift monitor must
  alert on the absence rather than reporting "no drift".

### 10. Reconciliation, Governance, and Reproducibility
- Forecast and interval definitions versioned; a forecast published without its interval
  and its model version is incomplete.
- Decisions derived from forecasts record the model version, the interval, and the
  threshold — so a decision can be audited against what was knowable at the time.
- Retraining triggered by drift thresholds, but gated on the reconciliation and calibration
  checks passing first. A retrained model that is incoherent or miscalibrated is worse than
  a stale one.
- Model card per forecast: scope, training window, performance overall and per segment,
  known limitations, owner.
- Backtesting with a rolling origin and no look-ahead; the backtest protocol itself
  versioned.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Forecast accuracy, 90-day horizon | MASE <= 1.15 against a seasonal naive baseline |
| Interval coverage (90% interval) | 87-93%, monitored monthly |
| Conditional coverage per segment | Within 5 points of marginal coverage |
| Hierarchical coherence residual | <= 0.5% of total magnitude |
| Forecast latency, full pipeline | <= 5 minutes for the daily batch |
| Drift detector precision | >= 0.6 at a 10 alerts/day budget |
| Anomaly PR-AUC at 1% rate | >= 0.5 |
| Filter log-likelihood | Non-decreasing over the validation window; divergence alert on violation |
| SVD denoiser error | Within the stated Frobenius bound |
| Capacity plan error | Predicted versus observed iterations within 30% |
| Reprocessing determinism | Same data and seed gives byte-identical forecasts |
| Alert precision tracked | Reported monthly per detector |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Symmetric sigmoid destroys gradient signal | Near-zero gradient norm in early layers | Zero-centred activations; ReLU family |
| Numerical overflow in variance propagation | `Inf`/`NaN` in filter state | Symmetrize P after each update; Joseph form for covariance |
| Cholesky breakdown | Non-positive pivot, explicit error | Recompute P from square root; check conditioning |
| QR without column pivoting on correlated columns | Unstable rank estimate | Column-pivoted QR; report rank with a tolerance |
| KL-based drift alert fires constantly | Alert rate far above budget | Jensen-Shannon divergence with fixed reference binning |
| Re-binned reference each window | Statistic not comparable across time | Bin once on a frozen reference window |
| Intervals too narrow | Coverage far below nominal | Interval construction from a stated posterior; PIT monitoring |
| Globally calibrated, segment-wise wrong | Segment PIT non-uniform | Conditional coverage checked per segment |
| Incoherent hierarchical forecasts | Reconciliation residual large | MinT reconciliation; incoherence reported |
| Retraining on drifted data bakes in the drift | Model performance unchanged after retrain | Investigate pipeline before retraining; pipeline-first ladder |
| Isolation tree method wrong for the data | PR-AUC near baseline | Compare with LOF and a robust covariance method |
| Gradient descent diverges | Loss NaN | Bound `eta <= 1/L` from the estimated `L` |
| Convex assumption silently invalid | Predicted versus observed iteration gap | Verify convexity; report the assumption |
| Forecast published without interval | Completeness check | Publication requires interval and model version |
| Missing data source looks like "no drift" | Absence detector | Monitor arrival as well as distribution |
| Sampled correlation treated as causal | Feature analysis flags near-duplicate | Source-level feature provenance |

## Milestones

- **M1** — time-series store with point-in-time features and alignment tests.
- **M2** — additive decomposition with reconstruction verified.
- **M3** — hierarchical forecasting with MinT reconciliation; incoherence reported.
- **M4** — quantile and posterior-predictive intervals with calibration monitoring.
- **M5** — Kalman filter from the conjugate update, Cholesky-based, with a log-likelihood.
- **M6** — filter diagnostics: innovation statistics, divergence detection, symmetrization.
- **M7** — anomaly suite: residual tests, likelihood ratios, robust covariance, IF/LOF.
- **M8** — threshold selection by expected cost; PR-AUC reporting.
- **M9** — drift monitor with Jensen-Shannon and a frozen reference window.
- **M10** — covariate versus concept drift discrimination.
- **M11** — sequential change-point detection with location and magnitude.
- **M12** — SVD denoiser with a certified Frobenius error bound.
- **M13** — capacity planner with analytic convergence bounds and the range test.
- **M14** — SPC layer with alert-fatigue metrics.
- **M15** — backtesting with rolling origin; model cards and governance.

## Deliverables

1. Forecast pipeline: decomposition, hierarchical models, MinT reconciliation.
2. Honest uncertainty: posterior predictive intervals with coverage and PIT monitoring.
3. Kalman filter and state-space estimation with diagnostics and divergence detection.
4. Anomaly detection suite with cost-based thresholds.
5. Drift monitoring with Jensen-Shannon, change-point detection, and shift discrimination.
6. Capacity planner using convergence theory.
7. `REPORT.md` — the platform posture: forecast accuracy against the seasonal naive baseline,
   interval coverage overall and per segment, reconciliation residual, filter likelihood
   and diagnostics, anomaly PR-AUC and thresholds, drift detector precision and alert
   budget, SVD bound certification, capacity plan accuracy, and residual risks accepted with
   reasons.

## Definition of Done

- [ ] Point-in-time correctness test fails when a feature timestamp follows the target time.
- [ ] Decomposition reconstructs the original within tolerance.
- [ ] Hierarchical coherence residual at or below 0.5% after MinT reconciliation, with the
      before/after incoherence reported.
- [ ] 90% interval coverage between 87% and 93% overall, and within 5 points per segment.
- [ ] PIT approximately uniform (KS p-value above 0.05) reported.
- [ ] Kalman filter uses Cholesky for the innovation solve and reports its own
      log-likelihood.
- [ ] Covariance symmetrized every step; a deliberate asymmetry injection is caught.
- [ ] Filter divergence detected by innovation statistics in a simulated failure.
- [ ] Anomaly PR-AUC at or above 0.5 at a 1% rate, reported with the threshold in force.
- [ ] Drift statistic bounded and symmetric; a KL-based comparison shown to be unusable on
      the same data.
- [ ] Reference binning frozen; re-binning shown to break comparability.
- [ ] Covariate shift and concept drift correctly distinguished on a constructed example.
- [ ] SVD denoiser error within the stated Frobenius bound.
- [ ] Predicted versus observed iteration counts within 30% on a quadratic.
- [ ] Data-source absence detected as an alert, not as "no drift".
- [ ] Forecasts published only with an interval and a model version.
- [ ] Backtesting is rolling-origin with no look-ahead, verified by test.
