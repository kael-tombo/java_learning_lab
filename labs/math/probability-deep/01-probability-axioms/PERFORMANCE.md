# Performance: Probability Axioms Implementation

## Exact vs. enumerated computation

- **Inclusion–exclusion over n events** expands to 2ⁿ − 1 intersection terms. Exact union probability for arbitrary dependent events is therefore exponential in n; exploit independence (complement product), a Markov structure, or fall back to sampling.
- **Enumerating a joint space** of |A| × |B| states costs O(|A|·|B|) time and space. Conditioning must not allocate a second table: accumulate the numerator and denominator in one pass, then divide once.
- **Factoring the joint** turns exponential into linear: naive Bayes over K classes with F features is O(K·F) per prediction instead of O(|X₁|…|X_F|).

## Numerical cost of multiplying probabilities

- A product of n doubles each ≈ 0.5 enters the subnormal range near n ≈ 1024 (2⁻¹⁰²² is the smallest normal) and reaches exactly zero near n ≈ 1074. Keep products in log space — sum logs — and normalize with log-sum-exp: `logsumexp(v) = m + log Σ e^(v_i − m)`.
- Summing n probabilities naively accumulates error O(n·ε) with ε ≈ 2.2e-16; compensated (Kahan/Neumaier) summation keeps the error near one ulp of the result. Probabilities renormalized from tables should be checked with `|Σp − 1| < 1e-12`.
- Comparing probabilities for equality is meaningless at double precision; compare odds ratios, or use exact `BigInteger` fractions when the denominators are small (dice, card combinatorics).

## Estimating probabilities by sampling

Monte Carlo estimate p̂ from N independent trials has standard error √(p(1−p)/N) ≤ 1/(2√N):

| N | worst-case SE |
|-------|---------------|
| 10² | 0.05 |
| 10⁴ | 0.005 |
| 10⁶ | 0.0005 |

The error shrinks like N^(−1/2): four times more precision costs 16 times more samples. Seed the generator explicitly, or two "independent" simulations silently return the same p̂.

## What not to do
Do not cache conditional tables keyed by exact double values of the conditioning event, and do not invert a covariance-free joint by repeated marginalization — it is O(2^n) work where one normalization pass suffices.

## Cost summary

| Operation | Cost |
|---|---|
| Union / intersection of bitset events (≤ 64 outcomes) | O(1) |
| Inclusion–exclusion over n arbitrary events | O(2ⁿ) — exponential by construction |
| Conditioning a table over \|Ω\| cells | O(\|Ω\|), one division |
| Product rule over a factored model (naive Bayes) | O(K·F) instead of O(\|X₁\|…\|X_F\|) |
| Monte Carlo estimate to ±e at 95% | 0.96/e² trials (from SE ≤ 1/(2√N)) |

These are identities from the algorithms themselves — no timing claims. The practical rule: exact beats sampling whenever the state space factors, and sampling wins the moment it does not.
