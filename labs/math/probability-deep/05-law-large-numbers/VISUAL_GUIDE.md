# Visual Guide: Law of Large Numbers and CLT

## One path of the sample mean (n = 500 fair dice, μ = 3.5)
```
  X̄ₙ
  4.2│•
  4.0│ ••
  3.8│    •••
  3.6│        •••••
  3.5┼──────────────•••••••••••••••••••••  ← μ = 3.5
  3.4│
  3.2│   •••
  3.0│      ••••
     └──────────────────────────────────── n
      early: wide swings   late: hovers, still moves ±SE
   the path NEVER becomes flat: oscillation ≈ 1.71/√n
```

## The 1/√n funnel (spread of X̄ₙ vs n)
```
   spread
    │╲
    │ ╲
    │  ╲____
    │       ╲____
    │            ╲______     ← halves when n quadruples
    │                     ╲________
    └──────────────────────────────── n
      10      100      1000    10000
   n =  36 → SE = 0.2846
        144 → SE = 0.1423   (exactly half)
```

## CLT: non-normal input, normal output
```
  input X                sum of n=2           sum of n=12
  ┌────┐                 ╱╲                   ╱╲
  │    │ uniform        ╱  ╲  triangular     ╱  ╲   ≈ N(6, 1)
  │    │             ╱╱    ╲╲             ╱╱      ╲╲
  └────┘          ╱╱          ╲╲       ╱╱            ╲╲
  0        1   0       2      4    4    5     6     7    8

  (X̄ − μ)/(σ/√n) → N(0,1) regardless of input shape
```

## Weak vs strong law — what each statement quantifies
```
  WLLN:  P(|X̄ₙ − μ| > ε) → 0        — a probability for a FIXED n
  SLLN:  P(X̄ₙ → μ as n → ∞) = 1     — one event for the WHOLE path

  WLLN tolerates rare wild paths; SLLN says they stop eventually,
  but LIL allows excursions of order √(n log log n)/n infinitely often
```

## Dependence eats sample size
```
  independent:     • • • • • • • • • •     n_eff = n
  AR(1), ρ=0.9:    •～•～•～•～•～•～•～•    n_eff ≈ n/19
                    each new point mostly repeats the last
  Var(X̄) = (σ²/n)(1 + 2Σ ρₖ)  — the correction most people skip
```
