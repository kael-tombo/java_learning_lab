# Step-by-Step Guide: Multivariate Statistics

## Worked example: correlation, regression, and PCA on 5 points

Data: x = (1, 2, 3, 4, 5), y = (2, 4, 5, 4, 5).

### Step 1 — Center
x̄ = 3, ȳ = 4. Deviations x: (−2, −1, 0, 1, 2); y: (−2, 0, 1, 0, 1).

### Step 2 — Sums of squares
Sxx = 4+1+0+1+4 = 10
Syy = 4+0+1+0+1 = 6
Sxy = (−2)(−2) + (−1)(0) + (0)(1) + (1)(0) + (2)(1) = 4 + 0 + 0 + 0 + 2 = 6

### Step 3 — Correlation
r = Sxy/√(Sxx·Syy) = 6/√60 = 6/7.7460 = **0.7746**

### Step 4 — Least-squares line
slope β₁ = Sxy/Sxx = 6/10 = **0.6**
intercept β₀ = ȳ − β₁x̄ = 4 − 1.8 = **2.2** → ŷ = 2.2 + 0.6x
R² = r² = 0.60 — the line explains 60% of the y-variance.

### Step 5 — Fisher z interval (why n matters)
z = atanh(0.7746) = ½·ln((1+0.7746)/(1−0.7746)) = ½·ln(7.873) = 1.0317
SE = 1/√(n−3) = 1/√2 = 0.7071 → z ± 1.96·SE = [−0.354, 2.418] → r ∈ **[−0.34, 0.98]**
With n = 5, the true correlation is barely constrained.

## Worked example: PCA of a 2×2 covariance matrix

Σ = [[2, 1], [1, 2]].

### Step 1 — Eigenvalues
det(Σ − λI) = (2−λ)² − 1 = 0 → λ = 3 and λ = 1.

### Step 2 — Eigenvectors
λ = 3: (2−3)v₁ + v₂ = 0 → v = (1, 1)/√2.
λ = 1: v = (1, −1)/√2.

### Step 3 — Read off
Explained variance: 3/(3+1) = **75%** for PC1 and 25% for PC2; total variance = trace = 4 (unchanged by rotation). PC1 = (X₁+X₂)/√2, PC2 = (X₁−X₂)/√2 — perfectly correlated variables collapse onto one axis.

## Verification checklist
- [ ] Sxx, Syy, Sxy computed on *centered* data; r ∈ [−1, 1] and |r| ≤ 1 by Cauchy–Schwarz
- [ ] Regression line passes through (x̄, ȳ): 2.2 + 0.6·3 = 4.0 ✓
- [ ] PCA eigenvalues sum to the trace of Σ; eigenvectors orthonormal
- [ ] Sample sizes stated with every r (Fisher z SE = 1/√(n−3))
