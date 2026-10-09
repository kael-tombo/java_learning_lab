# Visual Guide: Hypothesis Testing

## Rejection region under H₀ (two-sided, α = 0.05)
```
        H₀: N(0,1) sampling distribution of the statistic
   density
     │          ╱╲
     │         ╱  ╲
     │        ╱    ╲
     │    ▓▓▓╱      ╲▓▓▓        ▓ = rejection region, total 0.05
     └───┼───┴───────┴────┼─── statistic
        −1.96            1.96
   |T| > 1.96 ⇒ p < 0.05 (exactly the same decision as CI excluding 0)
```

## The p-value as a tail area
```
   ──────────┼───────────
             t_obs = 1.25 (from STEP_BY_STEP)

   p = 2·P(T₂₄ > 1.25) = 0.223
   ──────────┼────╱───────
             │   ▓▓▓▓      ▓ = 0.1115 each side ⇒ 0.223 total
   ▲ vs t₀.₀₂₅,₂₄ = 2.064 (the actual critical value)
```

## Power curve (δ = 0.5σ, α = 0.05 two-sided)
```
   power
    1.0│                    ___________
       │                 __/
    0.8│              __/   ← n = 63/group gives 0.80
    0.7│           __/      ← n = 25/group gives ≈ 0.71
    0.5│        __/
       │     __/
    0.05│___/
       └──────────────────────────── n per group
       more data ⇒ higher power for a FIXED effect size
```

## Four outcomes of a fixed-n test
```
                    │   H₀ true    │  H₀ false
   ─────────────────┼──────────────┼──────────────
   reject           │  Type I (α)  │  power 1 − β
   fail to reject   │  1 − α       │  Type II (β)
   ─────────────────┴──────────────┴──────────────
   you control the trade only through n (and effect size):
   moving the critical value shifts mass between rows 0 and 1
```

## Multiple testing: 20 shots at α = 0.05
```
   P(≥1 false positive) = 1 − 0.95²⁰ = 0.6415

   p-values under H₀:  .041 .13 .29 .02 .47 ... (uniform!)
   sorted:  .003 .011 .02 .041 .049 .07 ...
            ▲ BH step-up: largest k with p(k) ≤ k·q/m → reject 1..k
   Bonferroni instead compares every p to α/m = .0025
```
