# Visual Guide: Random Variables

## PMF (discrete) and CDF (staircase) of heads in 3 flips
```
  PMF  0.375 |        ##          ##
             |        ##          ##
             |   ##   ##   ##     ##
             |   ##   ##   ##     ##
             +------------------------ k
                0    1    2    3

  CDF  1.000 |                 ########
             |           ########
             |      #####
             |  ####
  0.000  +------------------------ k
             0    1    2    3
        jumps of 1/8, 3/8, 3/8, 1/8 — jump size = P(X = k)
```

## Continuous: PDF ↔ CDF ↔ balance point
```
   f(x)  ┌──────┐  Uniform(0,2), f = 1/2
         │      │
         │      │  ∫₀² f = 1
   ──────┴──────┴──── x
         0  ↑   2
          E[X] = 1 (center of mass)

   F(x)  ──────────╮  smooth: F′ = f
                   │
         ──────────╯
         0        2
```

## Pushing Ω through a random variable
```
   Ω (coin sequences)         X: Ω → ℝ
   {HHH, HHT, HTH, ...}  →    0     1     2     3
   8 equally likely points    1/8   3/8   3/8   1/8

   many abstract outcomes collapse onto few numbers —
   that compression is why we can compute at all
```

## Jensen's inequality in one picture
```
        E[g(X)] ●─────────── sits ABOVE the curve
               ╱ ╲
              ╱   ╲  convex g
             ╱     ╲
        ────●───────●──── g(E[X]) on the curve
            μ⁻      μ⁺
   average of the curve ≥ curve of the average
```

## Mean vs median for lognormal(0,1)
```
   density
     │  ╱╲
     │ ╱  ╲__
     │╱      ╲___
     ┼┼───┼───────╲____────────── x
      1   1.649
    median  mean (pulled by the long right tail)
   reporting the mean as "typical" overstates by 65%
```

## Reading a QQ plot without fooling yourself

A straight line means the sample quantiles track the theoretical ones. The four standard distortions, in one line each: **S-shape** (both tails curve together) → wrong skew; **tails peel away symmetrically** → heavy or light tails, check kurtosis; **step pattern** → ties from discrete data, use a discrete reference; **line parallel but shifted** → right shape, wrong location, re-estimate μ. On n = 20 only the far tails (about the largest 2 points) are visually detectable, so a clean small-sample QQ plot is weak evidence, not confirmation.

## ECDF versus histogram

The empirical CDF is a step function climbing from 0 to 1; it never loses information to bin choice. Compare it to the model's CDF directly: the vertical gap at any x is exactly the probability you would have misjudged by using the model there. The Kolmogorov–Smirnov statistic is precisely the largest such gap.
