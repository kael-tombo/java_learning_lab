# Reflection: Multivariate Statistics

## Draw before computing
Given 20 students with (hours studied, sleep, exam score), sketch: the scatter with an estimated regression line; an ellipse suggesting ρ ≈ 0.6; and the *partial* correlation of sleep and score given hours. If the sketch doesn't change when you condition, name what's missing — usually a confounder you didn't draw.

## Questions to work through
1. Why is PCA on unscaled data different from PCA on standardized data, and when does each answer the right question? Construct a two-variable example (variance ratio 100:1) and predict what PC1 will be in each case.
2. Sample Σ from n = 4 observations of p = 6 features: rank? eigenvalues? What exactly fails when you invert it, and what is the *cheapest* fix (drop features / ridge / increase n)?
3. Reproduce by hand: Σ = [[2,1],[1,2]] → λ = 3, 1; PC1 = (X₁+X₂)/√2; explained 75%. Which real-world variable pair does that matrix resemble (equal variances, ρ = 0.5)?
4. Marginal r(X, Y) = 0.6; after conditioning on Z, r(X, Y | Z) = 0.05. Write one sentence interpreting this *without* using the word "causes" — then a second sentence on what extra evidence you'd need to say "Z explains it."
5. Your anomaly detector alarms on (2σ, −2σ) after Mahalanobis scoring but not per-field. Explain to a security engineer why per-field rules missed it, using Σ⁻¹ rather than formulas if you must.

## Self-check table
| Concept | Can state it | Can compute it | Can break it |
|---|---|---|---|
| Covariance vs correlation | | | |
| Sums of squares → r, β, R² | | | |
| PCA eigen-decomposition & variance ratios | | | |
| Mahalanobis / whitening | | | |
| Partial correlation & confounding | | | |
| Conditioning of Σ, shrinkage | | | |

## Milestones
- [ ] Recompute r = 0.7746, ŷ = 2.2 + 0.6x, R² = 0.60 unaided
- [ ] Diagonalize [[2,1],[1,2]] and state explained-variance ratios
- [ ] Explain VIF and why κ(XᵀX) = κ(X)²
- [ ] Name the n/p regime where sample Σ is unusable and two remedies
- [ ] Describe Yule/Simpson with a concrete variable triple

## Questions to answer in writing

1. Describe a real dataset you know where the variables are strongly correlated. Estimate the effective rank (Σλ)²/Σλ² in your head from the correlation matrix — how much of the nominal dimension is real?
2. A paper reports "PCA retained 80% of variance in 3 components." Write the three questions you would ask before believing any downstream conclusion (what matrix? what n? is variance the right target?).
3. Explain to an engineer why inverting Σ with n = 40, p = 35 produces confident nonsense: connect rank deficiency, eigenvalue noise and 1/λ_min amplification in one paragraph.
4. When is a *marginal* (one-variable-at-a-time) analysis the honest one? Give a case where the partial coefficient answers the wrong question and you would deliberately report the unadjusted number.

## Blind spots this lab exposes

- **Units laundering.** Feeding quantities with different physical scales into any covariance-based method and then reading the eigenvectors as "importance."
- **n confusion.** Quoting n as rows used while Σ was computed pairwise per entry with different row counts.
- **Rotation as discovery.** Interpreting PC1 as a mechanism when tied eigenvalues make its orientation arbitrary — check the eigenvalue gaps before naming a component.
- **Confidence without conditioning.** Reporting a Mahalanobis threshold or VIF without the condition number of the matrix it came from.
