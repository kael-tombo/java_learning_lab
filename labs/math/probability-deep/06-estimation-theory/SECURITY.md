# Security: Estimation Theory

## Adversaries estimate, too — and poison your estimators
A mean-based detector estimates μ and σ from recent traffic and alarms beyond kσ. An attacker who injects a few extreme "normal-looking" values inflates the estimated σ (variance poisoning): add m decoys with z = 10 and the sample variance jumps enough that their real traffic sits inside the new band. **Fix:** robust estimators — median + MAD (median absolute deviation, consistent for normal with scale 1.4826), or Minimum Covariance Determinant — which ignore up to a contamination fraction α < 50% by construction. Never let the baseline include the attack window.

## Estimating attack rates from logs
Credential-stuffing intensity is a rate: with m events in window T, the MLE is λ̂ = m/T and its 95% interval (Poisson) is roughly λ̂ ± 1.96√(m)/T. For m = 4 that interval is enormous (±98% relative) — alarm thresholds computed from a *point* estimate at low counts are noise. Report the interval; when m < 20 use exact Poisson (Garwood) limits instead of the normal approximation.

## Entropy and key-strength estimation
Plug-in entropy from n observed password samples over m symbols has Miller–Madow bias ≈ (m−1)/(2n) nats — at n = 100, m = 26 that is ~0.18 bits, and the *direction* is typically over-confidence: unseen symbols are missing from the estimator, so a scheme's entropy can be over- or under-stated. Estimating the tail (how many users chose unseen passwords) requires Good–Turing estimation, not the MLE.

## SE and Wald intervals assume the model is right
Wald SEs from observed information assume i.i.d. data from the stated family. Security telemetry is bursty, dependent and contaminated; White's sandwich (1980) variance or block-based estimates are the minimum correction — otherwise "we are 95% confident the false-positive rate is below X" is an overstatement. Deployment gates for security controls must be evaluated with cluster-robust intervals or the control will pass in testing and fail under real dependence.

## What to review
- [ ] Is the baseline estimator robust to a few poisoned points (median/MAD vs mean/σ)?
- [ ] At the observed counts, is the normal/Wald interval valid (m ≥ 20), or are exact limits required?
- [ ] Does the SE model dependence (sandwich/blocks), or silently assume i.i.d.?
- [ ] For entropy claims: what is n relative to the symbol space, and what bias correction (Good–Turing, Miller–Madow) was applied?

## Robust estimation is the actual control

Variance poisoning, quantified: baseline of N ≈ 1000 honest samples (standard normal) plus 50 decoys at z = +10 (5% contamination). The contaminated sample variance becomes E[x²] − E[x]² = (0.95·1 + 0.05·100) − (0.05·10)² = 5.95 − 0.25 = 5.70, so σ̂ = 2.39 — the alarm band at 3σ̂ = **7.2 in true-σ units** instead of 3. An attacker's real traffic at 5–6σ now passes silently. Median/MAD (scale 1.4826) leaves σ̂ at ≈1.0 because 0.5% contamination cannot move the median — this is why "median + MAD" is the default for baselines and mean + σ is not. Breakdown point (fraction of contamination tolerated before the estimate escapes any bound): mean/σ = 0%, trimmed mean = α, median = 50%, MCD with subset fraction α = h/n has breakdown 1 − α (the default h ≈ n/2 gives 50%).

## Low-rate estimation decides whether you ever alarm

Poisson attack-rate estimation with m events in window T: λ̂ = m/T, and the Garwood exact 95% interval for m = 4 is [1.09, 10.24]/T — the point estimate 4/T carries a 9× range. Consequences: (1) thresholds derived from a *point* estimate at low counts fire on noise — use the upper Garwood endpoint as the threshold; (2) switching from Wald (λ̂ ± 1.96√m/T = 4 ± 3.92) to exact matters most exactly when counts are low, which is when security data arrives (a fresh deployment's first hour); (3) report intervals in the incident write-up — "rate quadrupled" is only defensible when the intervals don't overlap.

## Estimation choices to review in a detection pipeline

- [ ] Baseline location/scale: median+MAD (breakdown 50%) or mean+σ (breakdown 0%)? Is the attacker able to write into the training window?
- [ ] Rate alarms: Garwood/exact limits below m = 20, threshold from the upper endpoint not the point estimate?
- [ ] Entropy/complexity claims: n vs alphabet size, Miller–Madow or Good–Turing correction applied?
- [ ] Every reported SE: which variance formula (observed information / sandwich / block bootstrap), and what dependence assumption does it encode?
