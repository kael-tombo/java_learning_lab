# MINI_PROJECT — Probability: Simulator & Estimator Lab
> Implement + simulate + compare. ~3 hours.

## Goal
Build a CLI that runs Monte Carlo simulations for dice, cards, Monty Hall, and
coin runs, estimating probabilities with confidence intervals vs analytic values.

## Build Steps
1. `Sim.java`: coin/die/card samplers with a seedable RNG.
2. `MontyHall.java`: strategy switch|stay; report win rates over N runs.
3. `CI.java`: normal-approx 95% CI on a proportion p̂: `p̂ ± 1.96√(p̂(1-p̂)/N)`.
4. `Runs.java`: count maximal runs in coin sequences; compare to theory `E[runs]`.
5. Driver: N=100k per scenario; table of analytic vs estimate ± CI.

## Sample Output
```
Monty Hall switch win rate: 0.667 ± 0.003 (theory 2/3)
2-of-3 dice sum=7: 0.1667 ± 0.0012 (theory 1/6)
coin runs E≈... vs empirical ...
```

## Benchmark Table (fill)
| scenario | N | empirical | analytic | CI ok? |
|----------|---|-----------|----------|--------|
| Monty switch | 1e5 | | 0.6667 | |
| sum=7 | 1e5 | | 0.1667 | |
| runs | 1e5 | | | |

## Acceptance
- [ ] Monty Hall switch converges to ~2/3.
- [ ] CI contains analytic value in ≥95% of repeat runs.
- [ ] Seeded runs are reproducible.

## Extensions
- Birthday paradox simulator; graph the p(n) curve.
- Bayesian beta-binomial coin estimator plot.
