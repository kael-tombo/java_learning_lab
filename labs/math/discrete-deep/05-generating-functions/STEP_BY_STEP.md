# Step-by-Step: Coin Change for 50 Cents via Generating Function

US coins: 1¢, 5¢, 10¢, 25¢, 50¢. Question: how many ways to make exactly 50 cents, order of coins irrelevant?

## 1. Write the GF for One Coin Type

The number of times we take a c-cent coin can be 0, 1, 2, …, each adding c to the total — so one coin type contributes the factor

1/(1 − x^c) = 1 + x^c + x^{2c} + x^{3c} + …   (exponent = cents contributed by this coin)

## 2. Multiply the Five Factors

```
G(x) = 1 / [ (1 − x)(1 − x⁵)(1 − x¹⁰)(1 − x²⁵)(1 − x⁵⁰) ]
```

Choosing (i, j, k, l, m) copies of the five coins gives the term x^{i + 5j + 10k + 25l + 50m}; the coefficient of x⁵⁰ counts exactly the tuples with i + 5j + 10k + 25l + 50m = 50 — i.e., the change-making ways. **Answer = [x⁵⁰] G(x)**; now compute it.

## 3. Build It One Coin at a Time (Convolution Order)

Start with f₀(n) = 1 for all n (only 1-cent coins: one way, since n ones are forced).

**Add the 5¢ coin:** f₁(n) = Σ_{j=0..⌊n/5⌋} f₀(n − 5j) → number of j = ⌊n/5⌋ + 1.
- f₁(50) = 50/5 + 1 = **11**

**Add the 10¢ coin:** f₂(n) = Σ_{j=0..⌊n/10⌋} f₁(n − 10j).
For n = 50: f₁(50)+f₁(40)+f₁(30)+f₁(20)+f₁(10)+f₁(0) = 11 + 9 + 7 + 5 + 3 + 1 = **36**
(and f₂(25) = f₁(25)+f₁(15)+f₁(5) = 6 + 4 + 2 = **12**, f₂(0) = **1**)

**Add the 25¢ coin:** f₃(n) = f₂(n) + f₂(n − 25) + f₂(n − 50).
- f₃(50) = f₂(50) + f₂(25) + f₂(0) = 36 + 12 + 1 = **49**

**Add the 50¢ coin:** f₄(n) = f₃(n) + f₃(n − 50).
- f₄(50) = f₃(50) + f₃(0) = 49 + 1 = **50**

## 4. Answer

**[x⁵⁰] G(x) = 50 ways** (49 without using a half-dollar coin, plus the single way that is one 50¢ piece). Cross-check at a smaller size: [x²⁵] = f₃(25) = f₂(25) + f₂(0) = 12 + 1 = **13 ways to make 25¢** — the familiar "12 without a quarter, 13 with."

## 5. The Same Thing as a Recurrence

The GF construction *is* the DP: processing coins left to right,

```
f_k(n) = f_k(n − c_k) + f_{k−1}(n)      (use one more coin of type k, or none)
```

which is exactly the coefficient relation from multiplying by 1/(1 − x^{c_k}). Table for 50¢:

| coins used | {1} | {1,5} | {1,5,10} | {1,5,10,25} | +{50} |
|---|---|---|---|---|---|
| ways for 50¢ | 1 | 11 | 36 | 49 | 50 |

Complexity of this table: Σ over coin types of (n/cᵢ + 1) additions = Θ(K·n) with K = 5 coin types (more precisely Σᵢ n/cᵢ ≈ n·(1 + 1/5 + 1/10 + 1/25 + 1/50) ≈ 1.37n ≈ 69 additions for n = 50).

## 6. Where Closed Forms Fail Here

Unlike Catalan or Fibonacci, Π 1/(1 − x^{cᵢ}) is *not* rational when all five coins are present (it has infinitely many poles at roots of unity), so there is no constant-coefficient linear recurrence for the full sequence and no partial-fraction closed form. The GF's value is that it *is* the specification; extraction is by DP. Knowing that distinction — rational GF ⇒ recurrence ⇒ possible closed form, non-rational GF ⇒ compute the series — is the performance decision from lab 05's PERFORMANCE file.
