# Visual Guide: Estimation Theory

## Log-likelihood curvature = Fisher information = 1/SE²
```
   ℓ(θ)
    │        ___/\___           sharp peak: high information
    │      /   θ̂    \          I = −ℓ″(θ̂) large → small SE
    │    /            \
    │  /                \
    └────────────────────── θ

   ℓ(θ)
    │    ______________         flat: data can't distinguish θ values
    │   /    θ̂    θ̂′  \       I ≈ 0 → SE huge, CI wide
    │  /                \
    └────────────────────── θ

   CI ≈ {θ : ℓ(θ) ≥ ℓ(θ̂) − 1.92}   (likelihood-based 95%)
```

## Bias–variance decomposition of MSE
```
   MSE = bias² + variance
   estimator A:    |----|  biased low, tight        bias²=1, var=0.25 → MSE 1.25
   estimator B:    |------| unbiased, wider         bias²=0, var=1.00 → MSE 1.00
   estimator C:    |------| biased, wide            bias²=1, var=1.00 → MSE 2.00
                   ▲ θ
   unbiased ≠ minimal MSE — the tradeoff is an allocation, not a virtue
```

## Sampling distribution vs your one estimate
```
   θ̂'s distribution (repeated samples):     your single sample:
    ╱╲                                     │
   ╱  ╲  95% of θ̂ land here                │ ← this one (lucky/unlucky)
  ╱    ╲                                   │
 ─┼──────┼──────── θ        ────────────────┼──────── θ
       θ̄                                        the interval either
   the CI is a procedure covering in 95%    covers θ or it doesn't —
   of repeated samples                     "95% probability" is lab 08
```

## Coverage of 100 Wald intervals (simulation)
```
   |─■  |■ |─■ |■■─| ─|■ |─ |■─|■ ...
   ■ = interval contains θ      ~5 misses expected out of 100
   systematic misses on one side → bias or skew, not a sampler bug
```

## Cramér–Rao: precision floor
```
   Var(θ̂)
     │ ╲
     │   ╲  1/(n·I(θ))      ← no unbiased estimator beats this
     │     ╲
     │       ╲___________________   x̄ for the normal attains it
     │
     └──────────────────────────── n
   more data buys variance ∝ 1/n; the floor itself moves with information
```
