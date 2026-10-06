# Statistical Power & Effect Size - Flashcards (60 cards)

**Track:** statistics  |  **Lab:** lab10  |  **Level:** Advanced

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | What does power depend on? | The specified effect size, the variance, the sample size and alpha — never on the observed result. |
| 2 | Why is a non-significant result from a small study uninformative? | Because the study's minimum detectable effect may be far larger than any effect that matters. |
| 3 | What is Cohen's d? | The mean difference in pooled standard deviation units, with conventional thresholds of 0.2, 0.5 and 0.8. |
| 4 | Why use Hedges' g rather than d for small samples? | d is biased upward at small n; Hedges' g corrects for it. |
| 5 | How does MDE scale with n? | As 1/sqrt(n), so quadrupling the sample halves the smallest detectable effect. |
| 6 | Where should a planning effect size come from? | Literature, a business threshold, or an inflated pilot — never the observed result. |
| 7 | Why inflate a pilot variance? | Small pilots give noisy, biased-low variance estimates, which yield under-powered designs. |
| 8 | What does a power curve show? | Power against n for a range of effects, making the design's resolution explicit. |
| 9 | What is Power is about design, not results? | Power depends on the effect size you specified in advance, the noise, the sample size and alpha. |
| 10 | What is Cohen's d and its limits? | d is the mean difference in pooled standard deviation units, with thresholds of 0. |
| 11 | What is Small studies have huge minimum detectable effects? | MDE scales as (z_{1α/2} + z_{1−β}) · σ · sqrt(2/n). |
| 12 | What is Directional power depends on the alternative? | Power computed under the null alternative is meaningless. |
| 13 | What is Variance estimates come from elsewhere? | Planning power requires an effect size and a variance, and the observed effect is the wrong source for the effect size. |
| 14 | What is Power curves are decision documents? | Plotting power against n for a range of effects shows what your study can and cannot detect, which is the honest way to discuss a fixed budget or an inconclusive result. |
| 15 | In this lab, what does `d = (̄x₁ − ̄x₂) / sₚ` mean? | Cohen's d: pooled standard deviation |
| 16 | In this lab, what does `Hedges' g = d / (1 − 3/(4n − 9))` mean? | Bias-corrected d: better for small n |
| 17 | In this lab, what does `r = d / sqrt(d² + 4)` mean? | Effect size as r: relatable to correlation |
| 18 | In this lab, what does `power = 1 − β` mean? | Power: 1 minus Type II error |
| 19 | In this lab, what does `MDE = (z_{1−α/2} + z_{1−β}) σ sqrt(2/n)` mean? | Minimum detectable effect: what your n can see |
| 20 | In this lab, what does `n = 2 (z_{1−α/2} + z_{1−β})² σ² / δ²` mean? | Required n: inverting power |
| 21 | In this lab, what does `p1, p2 proportions` mean? | Proportion power: pooled variance under the null |
| 22 | In this lab, what does `pph = 2 arcsin sqrt(p1) − 2 arcsin sqrt(p2)` mean? | Fisher z for rates: propensity differences |
| 23 | You see ''No significant difference' from n = 20 per arm' in production. What is the cause and the fix? | study could only detect a huge effect Fix: report the MDE alongside any null result |
| 24 | You see 'Power computed under the null alternative' in production. What is the cause and the fix? | power of the wrong hypothesis Fix: specify the effect you want to detect |
| 25 | You see 'Effect size taken from the observed result' in production. What is the cause and the fix? | planning on the outcome Fix: use literature, a business threshold, or an inflated pilot |
| 26 | You see 'Pilot variance used uninflated' in production. What is the cause and the fix? | small pilots understate variance Fix: inflate by a documented factor and record the reasoning |
| 27 | You see 'Cohen's 0.5 declared medium' in production. What is the cause and the fix? | convention treated as universal Fix: translate the effect into business units before deciding |
| 28 | You see 'Power computed but alpha not adjusted for multiple comparisons' in production. What is the cause and the fix? | family-wise error inflated Fix: use the alpha you will actually apply |
| 29 | Which Java API is the backbone of: z-values for power and MDE, closed form and exact | `Normal quantile function` |
| 30 | Which Java API is the backbone of: exact power for small samples | `Non-central t distribution` |
| 31 | Which Java API is the backbone of: resolution reported with the design | `record PowerResult(double power, double mde, int nPerArm, double alpha)` |
| 32 | Which Java API is the backbone of: converting an effect into units the business recognises | `Arcane-free business translation` |
| 33 | Which Java API is the backbone of: power across a grid of n and effect sizes | `Power curve generator` |
| 34 | Why does Power is about design, not results matter operationally? | Power depends on the effect size you specified in advance, the noise, the sample size and alpha. |
| 35 | Why does Cohen's d and its limits matter operationally? | d is the mean difference in pooled standard deviation units, with thresholds of 0. |
| 36 | Why does Small studies have huge minimum detectable effects matter operationally? | MDE scales as (z_{1α/2} + z_{1−β}) · σ · sqrt(2/n). |
| 37 | Why does Directional power depends on the alternative matter operationally? | Power computed under the null alternative is meaningless. |
| 38 | Why does Variance estimates come from elsewhere matter operationally? | Planning power requires an effect size and a variance, and the observed effect is the wrong source for the effect size. |
| 39 | Why does Power curves are decision documents matter operationally? | Plotting power against n for a range of effects shows what your study can and cannot detect, which is the honest way to discuss a fixed budget or an inconclusive result. |
| 40 | In the Statistical Power & Effect Size pipeline, what happens next? Define the effect worth detecting, from a business threshold... | Define the effect worth detecting, from a business threshold or literature, not from data. |
| 41 | In the Statistical Power & Effect Size pipeline, what happens next? Estimate the variance from a pilot or historical data, and i... | Estimate the variance from a pilot or historical data, and inflate it. |
| 42 | In the Statistical Power & Effect Size pipeline, what happens next? Fix alpha and power, then compute required n per arm and the... | Fix alpha and power, then compute required n per arm and the horizon at your traffic. |
| 43 | In the Statistical Power & Effect Size pipeline, what happens next? Compute the MDE your sample can achieve, so the study's reso... | Compute the MDE your sample can achieve, so the study's resolution is explicit. |
| 44 | In the Statistical Power & Effect Size pipeline, what happens next? Plot a power curve across a range of effects and n.... | Plot a power curve across a range of effects and n. |
| 45 | In the Statistical Power & Effect Size pipeline, what happens next? Report the power analysis with the study, and the power alon... | Report the power analysis with the study, and the power alongside any non-significant result. |
| 46 | Exercise focus: Effect sizes | Compute and interpret them. |
| 47 | Exercise focus: Power curves | Power across n and effect sizes. |
| 48 | Exercise focus: MDE analysis | What your design can see. |
| 49 | Exercise focus: Pilot variance inflation | Plan with a defensible variance. |
| 50 | Exercise focus: Multiplicity and power cost | Price the cost of many comparisons. |
| 51 | Exercise focus: Post-hoc power critique | Show why it is uninformative. |
| 52 | State the Cohen's d, pooling and bias result for Statistical Power & Effect Size. | n1 = n2 = 8, difference 1.0, s = 1.0: d = 1.0 but the correction factor is 1 - 3/(4*16 - 9) = 0.955, so g = 0.955. At n = 20 each, the factor is 0.974 and the difference is negligible, which is why the correction is reserved for small samples. |
| 53 | State the Power for a two-sample comparison result for Statistical Power & Effect Size. | delta = 0.5 sigma, n = 64 per arm: two-sided power 0.80. n = 64 one-sided: power 0.90. At n = 20 per arm, two-sided power for d = 0.5 is about 0.26 — the study would miss a medium effect four times out of five. |
| 54 | State the Minimum detectable effect result for Statistical Power & Effect Size. | n = 20 per arm: MDE_d = 2.802 sqrt(0.1) = 0.886, so only an enormous effect is detectable. n = 100: 0.396. n = 400: 0.198. Quadr quadrupling the sample halves the detectable effect, as the 1/sqrt(n) law implies. |
| 55 | State the Power under the wrong alternative result for Statistical Power & Effect Size. | A study with n = 50 per arm and p = 0.08: post-hoc power at the observed effect is around 0.40 and is uninformative. Retrospective power at the planned d = 0.5 is 0.48, which correctly explains why an inconclusive result was likely. |
| 56 | State the Multiplicity and power cost result for Statistical Power & Effect Size. | m = 10 comparisons, alpha' = 0.005: with n = 400 per arm, power for d = 0.2 falls from about 0.85 to 0.63. Reaching 0.85 again needs roughly 600 per arm, a 50% increase in cost. |
| 57 | Why does power depend on sidedness? | A one-sided test rejects at a lower threshold, so it has more power for a directional alternative. |
| 58 | How is an effect size expressed as r? | r = d / sqrt(d² + 4), which makes it comparable to correlation-based intuition. |
| 59 | What is the effect of multiplicity on power? | Adjusting alpha downward for many comparisons reduces power, so the sample must grow. |
| 60 | How do you report power for a completed study? | Retrospective power computed at the effect size you specified a priori, not at the observed effect. |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
