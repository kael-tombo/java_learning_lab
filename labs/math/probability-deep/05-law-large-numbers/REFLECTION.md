# Reflection: Law of Large Numbers and CLT

## State each theorem precisely before using it
Fill in the blanks: WLLN — X̄ₙ converges to μ *in what sense, under what assumptions*? SLLN — same question, plus: how does it differ from WLLN? CLT — what exactly converges to N(0,1), and what does it say about X itself? If any answer includes "the data become normal," stop and reread COMMON_MISTAKES #4.

## Questions to work through
1. Compute by hand: n = 36 dice → SE = 0.2846; n = 144 → 0.1423. Now predict the n needed for P(|X̄ − 3.5| < 0.05) ≥ 0.95 via CLT and via Chebyshev. Which answer do you trust, and why the gap?
2. St. Petersburg: E[payoff] = Σ₂ᵏ · 2⁻ᵏ = Σ1 = ∞. What does the LLN say about the running average of this game's payoffs? What would you need to estimate instead (median? truncated mean?) and why?
3. Your service logs show autocorrelation ρ̂₁ = 0.85 in request inter-arrival gaps. n = 2000 observations. What is n_eff, and how much does your published ±3% error bar change?
4. The law of the iterated logarithm permits excursions of order √(n log log n)/n infinitely often. A monitoring dashboard shows the mean leaving its 95% band once per day. Is that evidence of a bug, of non-stationarity, or of expected behavior? Argue each.
5. Give one real process where the CLT is valid and one where the analogous-looking process is a trap (name the failure: infinite variance, dependence, maxima vs means, non-identical distribution).

## Self-check table
| Concept | Can state it | Can compute it | Can break it |
|---|---|---|---|
| Var(X̄) = σ²/n derivation | | | |
| Chebyshev bound vs CLT approximation | | | |
| 1/√n scaling & sample-size math | | | |
| WLLN vs SLLN vs LIL | | | |
| n_eff for correlated data | | | |
| Stable laws / infinite variance | | | |

## Milestones
- [ ] Reproduce SE = 0.2846 (n = 36) and the 0.081 Chebyshev bound unaided
- [ ] Derive n ≥ 1068 for a ±3% 95% proportion interval
- [ ] Explain gambler's fallacy in one sentence using X̄ vs Xₙ
- [ ] State Berry–Esseen with its meaning for choosing n
- [ ] Diagnose a "non-converging mean" from assumptions (moments? independence? summation?) without guessing

## Blind spots this lab exposes

- **Quoting an error bar without its n_eff.** "±3%" is a joint claim about data *and* independence; publish the pair or the claim is unauditable.
- **Buying precision without checking the bias floor.** The √n rule buys only the random half of the error; ask what it converges *to* before quadrupling n.
- **Reading one trajectory as the theorem.** Convergence in probability describes ensembles; a single wandering mean is expected behavior (LIL), not evidence.
- **Citing the CLT for a statistic it doesn't govern.** Means and sums only — quantiles, maxima and ratios need their own limit theory (EVT, delta method).
- **Stopping at "the theory says normal."** Normality of X̄ is a claim about a rate too (Berry–Esseen): at your actual n, how close is close? If you can't say, you're asserting, not checking.
