# Mental Models: Multivariate Statistics

## 1. Data as a Cloud, Statistics as Projections
Each variable is an axis; each observation a point. Correlation measures how stretched the cloud is along a diagonal; regression fits the shadow of the cloud on the x-axis; PCA finds the directions along which the cloud is longest. Every multivariate method is a question about the cloud's *shape, orientation and thickness*.

## 2. Σ Is a Metric, Not a Table
Mahalanobis distance d² = (x−μ)ᵀΣ⁻¹(x−μ) asks "how far, measured in units this cloud actually uses?" Highly correlated directions are *compressed* (moving along them is unsurprising), independent directions are measured by their own σ. Euclidean distance implicitly assumes Σ = I — wrong whenever variables correlate.

## 3. Partial Correlation = Conditioning Out a Variable
r(X, Y | Z) is the correlation of the *residuals* after both are regressed on Z. If the raw r vanishes after conditioning, Z was the driver (ice cream/drowning/temperature). This one operation distinguishes association from confounded association — the Yule/Simpson lesson made mechanical.

## 4. PCA Is Eigenvectors of Variance
Rotation (orthonormal V) never changes total variance (trace invariant) but redistributes it: new variances are the eigenvalues of Σ, new directions the eigenvectors. Retaining k components is an optimal k-dimensional reconstruction in squared-error sense (Eckart–Young). "75% explained" means 75% of the trace, nothing more.

## 5. Correlation Is Ellipse Shape
The bivariate normal's iso-density contours are ellipses whose orientation is set by ρ. ρ = 0 → axis-aligned circles (if σs match); ρ → ±1 → a degenerate line. All bivariate inference (hotelling's T², discriminant) is really statements about these ellipses.

## 6. Curse of Dimensionality: Volume Grows, Data Doesn't
The unit ball's volume in p dimensions, V_p ≈ (2πe/p)^{p/2}/√(πp), tends to zero while the enclosing cube stays 1 — so in high p almost all the volume is in the corners and every point's "nearest" neighbour is nearly as far as its farthest. Distance-based methods (kNN, clustering, MDS) lose discrimination, and holding a fixed data *density* needs exponentially many samples. Every multivariate technique is a fight against this.

## Model 7: Whitening Is the Universal Adapter

Any elliptical cloud can be transformed to a sphere: z = L⁻¹(x − μ) with Σ = LLᵀ. After whitening, Euclidean distance *is* Mahalanobis distance, PCA *is* axis alignment, and every direction is equally important. If a method behaves strangely on your data, picture it after whitening — the strangeness that survives is in the data, the rest was Σ's geometry. This is also why LDA, anomaly detection and clustering can be discussed in one language.

## Model 8: The Effective Dimension Is the Spectrum, Not p

p = 100 variables do not mean 100 dimensions of information. The eigenvalue spectrum λ₁ ≥ … ≥ λₚ tells the real story: λ's sum is total variance (trace), and a fast decay means the cloud is a thin slab. A useful scalar: effective rank = (Σλⱼ)² / Σλⱼ² — for eigenvalues (5, 4, 1) it is 100/42 = 2.38, i.e. ~2.4 effective dimensions out of 3. Anything that reports "variance explained" without showing the spectrum is hiding this number.

## Model 9: Sample Σ Is Itself Noisy Data

S = Σ + E: the sample covariance has p(p+1)/2 noisy entries, each with error ~ σᵢσⱼ/√n. With p = 100 and n = 50 there are 5 050 parameters estimated from 50 observations' worth of joint information — the off-diagonals are mostly noise. Two consequences: eigenvector estimates of nearly-tied eigenvalues wander (any rotation is equally good), and inversion squares the problem because errors in S become 1/λ_min-sized errors in Σ⁻¹. Shrinkage (Ledoit–Wolf) trades a little bias for a large variance cut — the same bias–variance trade as lab 06, played on a matrix.
