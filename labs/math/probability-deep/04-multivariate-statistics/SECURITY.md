# Security: Multivariate Statistics

## Anomaly detection is a Mahalanobis question
Per-user behavior (login hour, request rate, session length, bytes) forms a correlated cloud. Euclidean "3σ per field" alarms fire on whichever field has the largest variance and miss anomalies that are *jointly* unusual. d² = (x−μ)ᵀΣ⁻¹(x−μ) scales by the correlation structure; for two fields with ρ = 0.6 (Σ = [[1, 0.6], [0.6, 1]]):
- x = (1.5σ, 1.5σ): Euclidean 2.12σ, Mahalanobis √2.8125 = **1.68σ** — moving *with* the correlation is unsurprising, so per-field rules over-alarm here.
- x = (2σ, −2σ): Euclidean 2.83σ, Mahalanobis √20 = **4.47σ** — each field is only 2σ from its mean, yet the pair is a 4.5σ joint event. Per-field rules under-alarm exactly here.

**Operational caveat:** estimating μ and Σ from a population that includes the attacker poisons the model (masking). Robust estimators (Minimum Covariance Determinant, Rousseeuw & Van Driessen 1999) or per-account baselines are required.

## Correlation ≠ causation in incident data
"Alerts correlate with patch level 0.9" may mean unpatched hosts are mostly the *newly discovered* hosts that generate more scanning — an observation-window confound. Yule/Simpson effects reverse signs in stratified analyses; before tuning controls on a multivariate association, condition on the confounders (age of host, exposure, monitoring coverage) or you will fix the wrong thing.

## PCA and biometric/keystroke authentication
PCA on keystroke dynamics (dwell and flight times) is the classical feature-extraction step for continuous authentication: components capture typing rhythm while discarding per-key noise. The security-relevant failure mode is *score calibration* — PCs fitted on impostor data shift under a keystboard layout change, and a threshold set on the first two PCs (say 12% of variance retained) silently rejects legitimate users. Refit and re-threshold on each environment change.

## Multivariate A/B of security controls
Rolling out MFA or a password policy measured on several metrics at once (login success, help-desk tickets, lockouts) is a multiple-endpoint problem: three metrics at α = 0.05 give P(at least one false positive) = 1 − 0.95³ = 14.3% under the global null. Pre-register the primary endpoint or apply a family-wise correction (lab 07), or the "winning" metric is often pure noise.

## Review checklist
- [ ] Is Σ estimated robustly and from data the attacker could not poison?
- [ ] Are thresholds set on Mahalanobis / joint quantiles rather than per-field σ?
- [ ] For multi-metric rollouts: how many endpoints, and what correction?

## Where multivariate methods meet adversaries

**Covariance poisoning.** Any detector that scores distance from (μ, Σ) can be blinded by contaminating the baseline: a few attacker-controlled sessions inside the training window inflate Σ along their own directions, and their future activity scores as normal (the masking effect noted above). Mitigations with a track record: robust scatter (MCD, Rousseeuw & Van Driessen 1999), trimmed estimators, or per-account baselines so one poisoned global window cannot raise everyone's threshold.

**Feature leakage in released statistics.** Publishing a full correlation matrix over sensitive attributes (diagnosis × zip × employer × age) can be re-identified at the row level when cell sizes are small — the same reason microdata releases are audited. Aggregate or round before publishing Σ; p(p+1)/2 released numbers is p(p+1)/2 opportunities to leak.

**PCA as an attack surface.** Components fitted on attacker-influenced data define the projection everyone is scored in. Two concrete failures: (1) a component can be steered to align with a feature the attacker controls, throwing away the discriminative directions; (2) whitening with a near-singular Σ amplifies an attacker's controllable direction by 1/√λ_min. Fit projections on trusted data, freeze them, and monitor eigenvalue drift.

## Reporting template for a multivariate claim

1. Data provenance: n, p, inclusion rules, and whether n was reduced pairwise or listwise per statistic.
2. Σ estimator: sample, shrinkage (with δ), or robust (with breakdown point); plus the condition number you observed.
3. What the reported associations do *not* establish — name at least one confounder you did not measure.
4. For any threshold (anomaly score, control limit): the false-alarm rate on held-out clean data, not on the fitting sample.
