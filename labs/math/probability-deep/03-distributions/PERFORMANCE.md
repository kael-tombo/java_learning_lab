# Performance: Probability Distributions

## Evaluating densities and CDFs
- **Normal CDF** Φ(x) via erf: the Abramowitz–Stegun 7.1.26 rational approximation is accurate to 7.5×10⁻⁸ absolute; erfc for the far tail avoids computing 1 − tiny. Evaluating P(X < −40) as `1 - Φ(40)` returns exactly 0 in double — always use the complement directly (erfc), or work in logs.
- **Poisson/Binomial pmf**: recursive ratios (P(k+1) = P(k)·λ/(k+1)) cost one multiply and one divide per term, no factorials and no overflow. Summing to a target CDF is O(k); the normal or saddlepoint approximation is O(1) once k ≫ λ.
- **Gamma function Γ(n)**: Lanczos approximation (~15 correct digits, 6–8 terms) instead of Stirling for small n; log-gamma (`lgamma`) for any computation that would overflow (binomial coefficients for n > 170 exceed double range).

## Sampling costs, by method
| Method | Setup | Per draw | Used for |
|---|---|---|---|
| Inverse CDF | O(k) table | O(log k) | discrete, Uniform |
| Box–Muller | O(1) | 2 uniforms, sin/cos | Normal |
| Marsaglia–Tsang ziggurat | ~256 table entries | 1 uniform avg, rejection | Normal, Gamma |
| Knuth λ-reduction | O(λ) | O(1) for small λ | Poisson |
| PTRS / rejection | O(1) | O(1) expected | Gamma, Poisson large λ |

Knuth's Poisson loop iterates λ times in expectation — for λ = 10⁶ use the normal or transformed-rejection (Hörmann, 1993) sampler, which is O(1) per draw.

## Precision that matters numerically
- Work in **log space** for any product of densities: log p = Σ log f(xᵢ). Likelihoods of 10⁵ normal observations underflow long before the log-likelihood does.
- The Poisson recurrence drifts ~n·ε over n steps (ε ≈ 2.2e-16); renormalize the pmf after the sweep (divide by the accumulated sum) — one pass, restores Σp = 1 to 1e-15.
- Don't tabulate a normal density on a fixed grid narrower than ±8σ (truncation error > 1e-15 of mass) or wider than ±40σ (denormals in the tails).

## What is actually expensive
Mixture models: evaluating k mixture components per point is O(n·k); the EM loop (lab 06/08) repeats it per iteration. FFT-based convolution of two discrete distributions is O(k log k) versus O(k²) naive — worth switching at k ≈ 10³.

## Cost of sampling by family

| Family | Naive cost per draw | Optimized cost | Note |
|---|---|---|---|
| Uniform | O(1) | O(1) | Direct from RNG bits |
| Exponential | O(1) | O(1) | −ln U / λ; one log per draw |
| Normal | O(1) | O(1) | Box–Muller gives 2 normals per 2 logs; ziggurat ~O(1) with rejection |
| Poisson (small λ) | O(λ) inversion | O(1) Knuth for λ < 10; transformed rejection for large λ | Knuth's product-of-uniforms loop degrades linearly — bad for λ = 10⁶ |
| Binomial | O(min(np, n(1−p))) | O(1) BTPE algorithm (Kachitvichyanukul & Schmeiser 1988) | Direct summation of Bernoullis is np coin flips — avoid |
| Gamma (shape α) | O(α) for α < 1 via boosting | O(1) Johnk / Marsaglia–Tsang | Marsaglia–Tsang is the standard: two normals and a log per draw |
| Multinomial | O(k) per draw | O(k) unavoidable | One categorical pass over cumulative probabilities |

Rule of thumb: any sampling loop whose cost scales with a *parameter* (λ, np, shape) will surprise you at realistic sizes; prefer rejection/transform algorithms with constant expected cost.

## Practical

- `numpy.random.default_rng().poisson(4, 10**7)` uses the latter class — avoid writing your own Knuth loop "for clarity" in hot paths; clarity belongs in a test that checks mean ≈ λ.
