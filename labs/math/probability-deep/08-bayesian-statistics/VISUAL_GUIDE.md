# Visual Guide: Bayesian Statistics

## Prior → likelihood → posterior (Beta–Binomial, 9H/1T)
```
   π(θ)          L(θ)              π(θ|D)
   Beta(2,2)     θ⁹(1−θ)           Beta(11,3)
    ╱╲              ▲                  ▲
   ╱  ╲            ╱│╲                ╱│╲
  ╱    ╲          ╱ │ ╲              ╱ │ ╲
 ╱______╲________╱__│__╲____________╱__│__╲____ θ
 0    0.5    1       ~0.9            0.786
 prior mean 0.5     data mean 0.9    posterior mean 11/14 = 0.786
                                     (between the two, weighted by counts)
```

## Odds form of Bayes
```
   prior odds ─── × likelihood ratio ──→ posterior odds
     1 : 99     ×        19.8         =   0.2 : 1  =  1/6 ≈ 16.7%

   hypotheses whose likelihood is 19.8× higher get 19.8× the odds —
   but they must overcome the prior odds first
```

## Credible interval vs confidence interval
```
   95% CREDIBLE (posterior):        95% CONFIDENCE (procedure):
   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓              |─■ |■ |  ■|■─| ─|■ |─ ...
   └──── 95% of posterior ────┘     ■ = repeated intervals covering θ
   statement about THIS θ           statement about the METHOD
   (given model + prior)            (frequentist, prior-free)
```

## MCMC: an autocorrelated walk through the posterior
```
   θ
    │     ╭╮   ╭╮
    │  ╭──╯╰╮╭─╯╰──╮╭╮          warmup ─→ retained draws
    │──╯    ╰╯     ╰╯╰──
    └──────────────────────── iteration
   draws are correlated:  100 000 iterations, τ = 50  ⇒  ESS ≈ 2 000
   4 chains must interleave (split-R̂ < 1.01) or a mode was missed
```

## Prior strength vs data: who wins
```
   prior mean     0.5   (Beta(2,2)     =  4 pseudo-observations)
   data mean      0.9   (9H/1T         = 10 observations)
   posterior mean 0.786 = (2 + 9)/(4 + 10) ... up to reweighting
   with n = 1000 flips the prior's share is 4/1004 ≈ 0.4% — it disappears
```
