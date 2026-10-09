# Reflection: Hypothesis Testing

## Reconstruct a test in five lines
For n = 25, x̄ = 102, s = 8, H₀: μ = 100: statistic? reference distribution and df? p? decision at α = 0.05? interval? If any line is missing (the df, the tail direction, the interval), you're not testing — you're computing a number.

## Questions to work through
1. A startup runs 12 A/B variants, ships the "winner" at p = 0.04. Compute the FWER (1 − 0.95¹²) and then the Bonferroni threshold. What should they report instead of "significant"?
2. p = 0.06 at n = 30 and p = 0.0006 at n = 30 000 with identical effect size. Which is the "better" result? Define better two ways (compatibility, precision) and reconcile them.
3. Your monitoring dashboard stops an experiment "as soon as p < 0.05." Explain with the random-walk crossing argument why the realized false-positive rate explodes, and name two procedures that fix it (group sequential, SPRT).
4. A clinical trial with power 0.95 reports "no significant difference." What can you conclude? Now suppose the 95% CI is [−0.01, 0.02] on a clinically meaningful margin of ±0.10 — what changed and what test (TOST) formalizes it?
5. Given 2×2 table counts [[8, 2], [3, 7]], decide between χ² and Fisher's exact (expected counts?), compute which cell drives the result, and state the p's meaning in one sentence using P(data | H₀) — no "probability the effect is real" allowed.

## Self-check table
| Concept | Can state it | Can compute it | Can break it |
|---|---|---|---|
| p-value meaning (P(D\|H₀)) | | | |
| α, β, power geometry | | | |
| test ↔ CI inversion | | | |
| multiple testing (Bonferroni/Holm/BH) | | | |
| peeking & sequential boundaries | | | |
| assumptions: t vs Welch vs permutation | | | |

## Milestones
- [ ] Reproduce t = 1.25, p = 0.223, CI (98.70, 105.30) unaided
- [ ] Derive n = 63/group for δ = 0.5, 80% power
- [ ] Compute 1 − 0.95²⁰ = 0.6415 and explain which correction you'd pick and why
- [ ] State what α guarantees — and one action (peeking, ad-hoc endpoint) that voids it
- [ ] Explain to a PM why p < 0.05 is not "95% likely to work"

## Blind spots this lab exposes

- **Counting tests, not hypotheses.** The family is everything you *inspected* — dashboard cards, subgroup cuts, "one more look." If it influenced the story, it's in the family, logged or not.
- **Treating the threshold as the result.** p = 0.049 vs 0.051 is noise around a continuous quantity; the effect estimate and its interval carry the information, the star carries the procedure's error rate.
- **Using absence as evidence without power.** "No effect" from an underpowered study is silence; quote the interval and the MDE the design could see (n = 63/arm at δ = 0.5σ).
- **Peeking without a sequential design.** Any stopping rule chosen after the data exists has an unquantified false-positive rate — often far above 5%, sometimes ~1 under continuous monitoring.
- **Quoting p without its n.** The same effect yields p = 0.06 at n = 30 and p = 0.0006 at n = 30 000; without n and the interval, the p is uninterpretable.
