# Mental Models: Generating Functions

## 1. A Sequence Wears a Name Tag

A generating function is just a sequence in costume: (a₀, a₁, a₂, …) ↦ a₀ + a₁x + a₂x² + …. No numbers are plugged in for x; x is a *position marker* whose exponent records the index. This makes algebra on sequences legal: adding sequences = adding series, and — the big one — **convolving sequences = multiplying series**. If you remember only one thing: multiplication of GFs adds indices.

## 2. Multiplication = "Choose a Split"

Why is (A·B)ₙ = Σ_{i+j=n} aᵢbⱼ? Because to build an object of size n as (part of size i) + (part of size n−i), you must pick i. The product's coefficient *is* the sum over all splits — the same case analysis you'd do by hand, packaged once. Coefficients of products are convolution sums, coefficients of 1/(1−x) are cumulative sums, and that is why "divide by (1−x)" means "integrate/accumulate."

## 3. The Dictionary

| Question | GF to write | [xⁿ] gives |
|---|---|---|
| compositions of n (order matters) | x/(1−2x) | 2^{n−1} |
| binary strings avoiding "00" | (1+x)/(1−x−x²) | Fₙ₊₂ (1,2,3,5,8,…) |
| change for n¢ from 1,5,10,25,50 | Π 1/(1−x^c) | coin change (50¢ → 50) |
| permutations (labeled) | EGF 1/(1−x) | n! |
| sets of labeled blocks | EGF exp(eˣ−1) | Bell numbers |

Each row is a *structural* translation: sequence-of → product of GFs, set-of → exp of EGF, choice → sum. Learning the dictionary is the subject.

## 4. Rational GF ↔ Linear Recurrence

A sequence satisfies a constant-coefficient linear recurrence iff its GF is rational P(x)/Q(x). 1/(1−x−x²) ↔ Fibonacci; 1/(1−2x) ↔ doubling. Reading a recurrence *off* a denominator (aₙ = q₁aₙ₋₁ + … + qₖaₙ₋ₖ from Q = 1 − q₁x − … − qₖxᵏ) is the reverse engineering: to solve a recurrence, find or build its GF; to get a closed form, partial-fraction the GF and pull out λⁿ terms.

## 5. Coefficient Extraction Is the Actual Product

After all the algebra, the deliverable is [x⁵⁰] of some series. Two extraction strategies: (a) **compute the series** to degree 50 by truncated multiplication (DP in disguise), or (b) **get a closed form** for [xⁿ] (partial fractions, binomial theorems, extracting roots) and evaluate. Strategy (b) is where O(n) loops become O(1) formulas; strategy (a) is where "no formula exists" lives (partitions). Knowing which you need is the plan.

## 6. Formal Series Are Polynomials With a Future

Treat F(x) as an infinite polynomial where equality means "all coefficients equal." Then division is legal exactly when the divisor's constant term is nonzero (invertible element of the ring), and everything you do to finite polynomials carries over. You never need convergence for enumeration — convergence questions belong to analysis, and confusing the two layers produces the "|x| < 1?" panic that isn't relevant to counting.

## 7. Objects, Not Algebra

The trap: mechanically differentiating/ integrating without saying what the series counts. Keep the narration attached: "this factor 1/(1−x⁵) counts how many 5-cent coins I chose (any number, order irrelevant within the coin type)" — then the product's meaning (choose counts of each coin, sizes add) follows immediately, and the coefficient of x⁵⁰ is the answer to "how many ways to make 50 cents." The algebra is bookkeeping; the model is the story.
