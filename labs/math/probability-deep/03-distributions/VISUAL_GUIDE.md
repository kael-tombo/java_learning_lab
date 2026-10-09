# Visual Guide: Probability Distributions

## Discrete: Binomial(n=10, p=0.5) pmf and its staircase CDF
```
   pmf                        cdf
   .25 |       ###             1.0 |            ##########
   .20 |      #####             .8 |         #####
   .15 |     #######            .6 |      ####
   .10 |    #########           .4 |   ###
   .05 |  ############          .2 | ##
       +------------ k            +------------ k
         0 2 4 6 8 10              0 2 4 6 8 10
   mean = np = 5,  sd = √(np(1−p)) = √2.5 ≈ 1.58
```

## Continuous: Normal, Exponential, Lognormal (normalized to mean 1)
```
   f(x)
    │      Normal         Exponential        Lognormal
    │       ╱╲             ╲                  ╱╲
    │      ╱  ╲             ╲                ╱  ╲___
    │     ╱    ╲             ╲_             _╱       ╲____
    │────╱──────╲──────────────╲───────────╱────────────────
    └──────────────── x         └──────────────── x
   symmetric, σ exists   memoryless hazard   right-skewed, heavy tail
   variance = σ²         mean = 1/λ          mean = e^(μ+σ²/2) > median = e^μ
```

## CDF vs survival function in the tail
```
   CDF F(x) ────────────────●─────── → 1   (loses precision near 1)
                           ╱
                        ╱                    for P(X > 40σ) use
                     ╱                            the SF, not 1−F
   ────────────────●
   survival S(x) = 1 − F(x): starts at 1, still resolved where F ≈ 1
```

## Fingerprint scatter: sample variance vs sample mean
```
   Var
    │            ╱  Pareto / negative binomial
    │          ╱      (Var grows faster than mean)
    │        ╱
    │      ╱   ← Poisson: Var = mean
    │    ╱
    │  ╱_______________ Binomial: Var ≤ mean/4 (flat-ish)
    └────────────────────── Mean
   Plotting (x̄, s²) of grouped data often identifies the family
   before any formal goodness-of-fit test
```

## Poisson(4) computed by recurrence
```
   P(0) = e^-4 = 0.018316
   P(k+1) = P(k) · 4/(k+1)        0.018316 → 0.073263 → 0.146525 → 0.195367
   P(X ≤ 3) = 0.433471    P(X ≥ 4) = 0.566529
```
