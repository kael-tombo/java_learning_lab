# Principal Component Analysis - Flashcards (60 cards)

**Track:** ml  |  **Lab:** lab08  |  **Level:** Intermediate

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | What does PCA maximise? | The variance of the projected data along each successive orthogonal direction. |
| 2 | Do you need to centre the data before PCA? | Yes. Without centring the first component points at the mean direction, which is meaningless. |
| 3 | When should you standardise before PCA? | When features have different units or materially different variances; otherwise total variance rather than structure is maximised. |
| 4 | Eigenvalue to explained variance ratio? | λᵢ / sum(λ), the share of total variance captured by component i. |
| 5 | Is the sign of a component meaningful? | No. The eigenvector and its negation are equally valid; fix the convention so runs are reproducible. |
| 6 | Why is SVD numerically better than eigendecomposition? | It works on the data matrix directly, never forms the covariance matrix, so its condition number is not squared. |
| 7 | What is a loading? | The eigenvector coordinates — the direction of the component in original feature space. Not the same as feature importance. |
| 8 | Why does PCA sometimes hurt classification? | It preserves variance, not class signal; with correlated features the useful direction may have low variance. |
| 9 | What is PCA as maximum-variance projection? | PCA finds the orthogonal direction along which the data varies most, then removes it and repeats. |
| 10 | What is Two routes to the same answer? | Eigendecomposition of the covariance matrix works for small p; SVD of the centred data matrix is numerically superior and works for large p, because you never form p×p. |
| 11 | What is Explained variance and choosing k? | Explained variance ratio is λᵢ/Σλ. |
| 12 | What is Loadings, scores and interpretation? | Loadings are the eigenvectors (the directions in feature space). |
| 13 | What is Standardise or not? | Unscaled PCA finds directions of maximum total variance, so a feature in cents dominates. |
| 14 | What is When PCA is the wrong tool? | Sparse text destroys variance-based structure — use truncated SVD on term counts instead. |
| 15 | In this lab, what does `Σ = (1/(n−1)) XᵀX (centred X)` mean? | Sample covariance: the matrix whose eigenvectors we want |
| 16 | In this lab, what does `Σvᵢ = λᵢvᵢ` mean? | Eigenproblem: directions and their variance |
| 17 | In this lab, what does `EV ratio = λᵢ / Σᵢλᵢ` mean? | Explained variance ratio: share of variance per component |
| 18 | In this lab, what does `zᵢ = (xᵢ − μ) Wₖ` mean? | Projection: score in the new basis |
| 19 | In this lab, what does `x̂ = μ + z Wₖᵀ` mean? | Reconstruction: rank-k approximation of X |
| 20 | In this lab, what does `λᵢ = sᵢ² / (n−1)` mean? | Singular-value link: why SVD avoids forming Σ |
| 21 | In this lab, what does `total variance = Σᵢ var(xᵢ)` mean? | Trace relation: explained ratios must sum to 1 |
| 22 | You see 'All the variance ends up in one component' in production. What is the cause and the fix? | features on wildly different scales Fix: standardise before fitting |
| 23 | You see 'Test-time scores look nothing like training' in production. What is the cause and the fix? | PCA refit on the full dataset or on serving data Fix: fit once on the training fold and serialise mean + components |
| 24 | You see 'k chosen by the 95% rule and downstream accuracy drops' in production. What is the cause and the fix? | retained variance is not the same as useful variance Fix: choose k by validation error, not by cumulative variance |
| 25 | You see 'Loadings say feature 7 dominates' in production. What is the cause and the fix? | correlated features split the weight unpredictably Fix: interpret the component, and use permutation importance for the model |
| 26 | You see 'Text classification gets worse after PCA' in production. What is the cause and the fix? | truncated SVD, not PCA, is right for sparse counts Fix: use latent semantic indexing / TruncatedSVD on the sparse matrix |
| 27 | You see 'Components flip sign between runs' in production. What is the cause and the fix? | sign is arbitrary in eigendecomposition Fix: fix the sign convention (largest-magnitude loading positive) and serialise it |
| 28 | Which Java API is the backbone of: the didactic route for small p, plus a symmetric-matrix solver | `Eigenvalue decomposition (QR iteration)` |
| 29 | Which Java API is the backbone of: simple, stable for real symmetric matrices like covariance | `Jacobi eigenvalue algorithm` |
| 30 | Which Java API is the backbone of: keeping eigenvalues and eigenvectors aligned is the classic bug | `Arrays.sort on eigenvalues with paired index sort` |
| 31 | Which Java API is the backbone of: streaming mean and variance for the centring step | `DoubleSummaryStatistics` |
| 32 | Which Java API is the backbone of: the transform plus its metadata, in one serialisable unit | `record PcaModel(double[] mean, double[][] components, double[] eigenvalues)` |
| 33 | Why does PCA as maximum-variance projection matter operationally? | PCA finds the orthogonal direction along which the data varies most, then removes it and repeats. |
| 34 | Why does Two routes to the same answer matter operationally? | Eigendecomposition of the covariance matrix works for small p; SVD of the centred data matrix is numerically superior and works for large p, because you never form p×p. |
| 35 | Why does Explained variance and choosing k matter operationally? | Explained variance ratio is λᵢ/Σλ. |
| 36 | Why does Loadings, scores and interpretation matter operationally? | Loadings are the eigenvectors (the directions in feature space). |
| 37 | Why does Standardise or not matter operationally? | Unscaled PCA finds directions of maximum total variance, so a feature in cents dominates. |
| 38 | Why does When PCA is the wrong tool matter operationally? | Sparse text destroys variance-based structure — use truncated SVD on term counts instead. |
| 39 | In the Principal Component Analysis pipeline, what happens next? Decide whether to standardise: yes if units differ, no if th... | Decide whether to standardise: yes if units differ, no if they are comparable and total variance is meaningful. |
| 40 | In the Principal Component Analysis pipeline, what happens next? Centre the data (mean subtract). PCA does not centre for you... | Centre the data (mean subtract). PCA does not centre for you. |
| 41 | In the Principal Component Analysis pipeline, what happens next? Decompose: eigendecomposition of the covariance matrix for s... | Decompose: eigendecomposition of the covariance matrix for small p, SVD of the centred matrix otherwise. |
| 42 | In the Principal Component Analysis pipeline, what happens next? Sort components by descending eigenvalue; check the eigenval... | Sort components by descending eigenvalue; check the eigenvalue spectrum for a natural elbow. |
| 43 | In the Principal Component Analysis pipeline, what happens next? Choose k from a cumulative-variance target or, better, from ... | Choose k from a cumulative-variance target or, better, from downstream validation error. |
| 44 | In the Principal Component Analysis pipeline, what happens next? Store the scaler, the mean vector and the component matrix t... | Store the scaler, the mean vector and the component matrix together — a transform is not just a matrix. |
| 45 | Exercise focus: Derive and implement PCA by eigendecomposition | Build the covariance matrix and solve the symmetric eigenproblem. |
| 46 | Exercise focus: Eigen versus SVD must agree | Two routes, one answer — this is the numerics lesson. |
| 47 | Exercise focus: Choosing k honestly | Beat the 95% convention with evidence. |
| 48 | Exercise focus: Loadings versus importance | Show why PCA coefficients are not feature importance. |
| 49 | Exercise focus: Whitening for clustering | Fix non-spherical clusters with a linear transform. |
| 50 | Exercise focus: Sparsity stress test | See where covariance PCA fails and TruncatedSVD wins. |
| 51 | State the Variance maximisation as an eigenproblem result for Principal Component Analysis. | A 2D dataset with S = [[3, 2], [2, 3]] has eigenvalues 5 and 1 with eigenvectors (1,1)/√2 and (1,−1)/√2. PC1 keeps 5/6 = 83% of variance. |
| 52 | State the Explained variance and the cumulative curve result for Principal Component Analysis. | Eigenvalues 5.0, 1.0, 0.5, 0.3, 0.2 total 7.0. k = 2 keeps 85.7%, k = 3 keeps 92.9%, k = 4 keeps 97.1%. |
| 53 | State the Eigen-decomposition versus SVD result for Principal Component Analysis. | p = 50,000 features: forming XᵀX needs 20 GB and squares the condition number. Truncated SVD on X_c needs O(p·k) and never forms it. |
| 54 | State the Reconstruction error from the spectrum result for Principal Component Analysis. | Dropping a component with eigenvalue 0.5 out of 7.0 total adds a relative error of 7.1% — visible, but often harmless if that direction is noise. |
| 55 | State the Whitening and why it changes distance geometry result for Principal Component Analysis. | Components with s = 10 and s = 1 contribute 100:1 to unwhitened distance and 1:1 after whitening — a large change in which points look close. |
| 56 | State the Choosing k by downstream performance result for Principal Component Analysis. | For a text classifier, k = 50 keeps 40% of variance but often beats k = 300 which keeps 95%, because the extra dimensions are noise. |
| 57 | What is TruncatedSVD and when do I use it? | A sparse-friendly factorisation that does not centre; it is the right tool for sparse term-count matrices. |
| 58 | How do I pick k in practice? | Sweep k and choose by downstream cross-validated performance, using cumulative variance only as a starting point. |
| 59 | Can PCA be inverted exactly? | Only for a full-rank projection. A rank-k projection is lossy by construction. |
| 60 | How do I detect that PCA is a bad idea here? | Sparse data, categorical features, tiny n relative to p, or a requirement for per-feature interpretability. |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
