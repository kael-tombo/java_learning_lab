# math-for-ai-deep — Quiz

15 multiple-choice questions across the ten modules. Answer key and score guide at the
bottom.

## Questions

**Q1.** Why does production code solve least squares with QR or SVD rather than
`(A'A)^-1`?
- A) QR and SVD are exact while inversion is not
- B) Forming `A'A` squares the condition number (`cond(A'A) = cond(A)^2`), destroying
      precision
- C) Inversion is slower for large matrices
- D) QR requires fewer operations

**Q2.** For a symmetric matrix, what is guaranteed?
- A) All eigenvalues are positive
- B) All eigenvalues are real and there is an orthogonal eigenbasis
- C) It is invertible
- D) Its singular values equal its eigenvalues

**Q3.** The singular values of `A` relate to the eigenvalues of `A'A` by:
- A) `sigma_i = lambda_i`
- B) `sigma_i = sqrt(lambda_i)`
- C) `sigma_i = lambda_i^2`
- D) `sigma_i = 1/lambda_i`

**Q4.** What does `cond(A) = sigma_max / sigma_min` measure?
- A) The computational cost of multiplying by `A`
- B) How much `A` can stretch some directions relative to others; the amplification of
      relative error
- C) The number of nonzeros
- D) The memory footprint

**Q5.** Why does softmax need the max-shift `exp(x_i - max(x))`?
- A) It improves accuracy of the result
- B) Without it, `exp` of a large logit overflows to infinity; the shift cancels in the
      normalization and is mathematically exact
- C) It makes the computation faster
- D) It ensures the probabilities sum to 1

**Q6.** In `L = f(x) + lambda'(c(x) - b)`, what does KKT complementary slackness state?
- A) `lambda >= 0` and `c(x) - b <= 0`
- B) For each constraint, `lambda_i * (c_i(x) - b_i) = 0` — an inactive constraint has zero
      multiplier
- C) The Hessian is positive definite
- D) `x` is unique

**Q7.** Cross-entropy relates to KL divergence as:
- A) `H(p,q) = D_KL(p||q)`
- B) `H(p,q) = H(p) + D_KL(p||q)`
- C) `H(p,q) = D_KL(p||q) - H(p)`
- D) They are unrelated

**Q8.** Why is Jensen-Shannon divergence preferred over KL for monitoring?
- A) It is faster to compute
- B) It is symmetric, bounded, and zero only when the distributions are equal, so drift
      alerts cannot be gamed by an asymmetric blow-up
- C) It is a true metric with a triangle inequality
- D) KL requires a reference distribution

**Q9.** The data processing inequality says:
- A) More data improves the bound
- B) Applying any channel cannot increase mutual information
- C) Entropy decreases monotonically under training
- D) The KL divergence is always non-negative

**Q10.** Beta-Binomial conjugacy: after `s` successes and `f` failures with prior
  `Beta(alpha, beta)`, the posterior is:
- A) `Beta(alpha + s, beta + f)`
- B) `Beta(alpha - s, beta - f)`
- C) `Binomial(s + f, alpha/beta)`
- D) `Beta(s, f)` with the prior discarded

**Q11.** In variational inference, the ELBO is:
- A) The exact log marginal likelihood
- B) A tractable lower bound: `E_q[log p(D|theta)] - KL(q||p)`, and the gap to the truth is
      the variational gap
- C) The KL between the variational and prior distributions
- D) An upper bound that can be maximized without approximation

**Q12.** For `L`-smooth objectives, the largest stable gradient-descent step is approximately:
- A) `eta = 1/L`
- B) `eta = 2/L`
- C) `eta = L`
- D) Any `eta`; divergence is not a real risk

**Q13.** Why does small-batch SGD often generalize better than full-batch GD?
- A) It uses less memory
- B) Its gradient noise, scaling as `1/sqrt(B)`, acts as a regularizer and helps escape
      saddle points
- C) It computes the gradient more accurately
- D) It converges faster per epoch

**Q14.** Adam's bias correction exists because at early steps:
- A) The moments are too noisy
- B) The exponential moving averages are biased toward zero, so `m_hat` and `v_hat` are
      needed for a correctly scaled update
- C) The learning rate is too small
- D) The second-moment estimate needs a square root

**Q15.** Classical Gram-Schmidt loses orthogonality mainly because:
- A) Division by zero
- B) Subtracting projections that are already inaccurate, so errors accumulate; modified
      Gram-Schmidt with re-orthogonalization fixes this
- C) It requires a basis change
- D) It only works for orthonormal inputs

## Answer Key

| Q | Answer | Why |
|---|--------|-----|
| 1 | B | Squaring the condition number removes most of the available precision. |
| 2 | B | Spectral theorem: real eigenvalues, orthogonal eigenvectors. Positivity and invertibility are separate questions. |
| 3 | B | `A'A = V D^2 V'`, so `sigma_i = sqrt(lambda_i)`. |
| 4 | B | Condition number is the relative-error amplification factor. |
| 5 | B | The shift is exact after normalization and prevents `exp` overflow. |
| 6 | B | Complementary slackness ties multipliers to binding constraints. |
| 7 | B | Cross-entropy decomposes into entropy plus KL. |
| 8 | B | JS is bounded and symmetric; KL can blow up in one direction and be near zero in the other. |
| 9 | B | The formal statement that lossy processing cannot add information. |
| 10 | A | Sufficient statistics add: `alpha + s, beta + f`. |
| 11 | B | The ELBO is a lower bound with a measurable gap; that gap is what you report. |
| 12 | B | `eta = 2/L` is the boundary; above it, divergence. |
| 13 | B | `1/sqrt(B)` noise is implicit regularization, not an accuracy improvement. |
| 14 | B | `E[g^2]_t = sigma^2 (1 - beta^t)`, so the running estimate starts near zero. |
| 15 | B | Projection errors accumulate; re-orthogonalization removes them. |

## Score Guide

| Score | Verdict |
|-------|---------|
| 15/15 | Ready to read any ML paper's math and debug any numerical issue. |
| 12-14 | Solid. Revisit your misses against THEORY.md. |
| 9-11 | Knows the formulas, not the reasons. Redo Q1, Q2, Q5, Q8, Q11. |
| 6-8 | Re-read THEORY.md, then redo EXERCISES for modules 02, 03, 10. |
| 0-5 | Restart with modules 01, 02, 04 before probability and information theory. |

## Scoring Notes

- Single answer per question; no partial credit.
- Retake after re-reading the relevant module.
- Mastery threshold: 13/15 with no misses on Q1, Q2, Q5, Q8, Q11.
