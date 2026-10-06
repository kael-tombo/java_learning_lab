# Statistical Power & Effect Size

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

## 1. The Problem This Solves

You have a fixed sample and a question about a real effect. The p-value tells you about noise; the power calculation tells you whether your study could ever have found the truth.

Power is the discipline that makes inconclusive results explicable rather than ambiguous, and effect sizes are what translate a statistical result into a business decision.

## 2. Learning Objectives

- Compute Cohen's d and related effect sizes with correct pooling
- Compute power for means, proportions and comparisons using correct alternatives
- Derive the minimum detectable effect for a given sample size
- Invert power to obtain required sample size
- Choose an effect size from literature or pilot data rather than from the observed result
- Report power alongside every non-significant result

## 3. Core Concepts

### 3.1 Power is about design, not results

Power depends on the effect size you specified in advance, the noise, the sample size and alpha. Since it depends on the assumed effect rather than the observed one, it can and must be computed before data collection.

### 3.2 Cohen's d and its limits

d is the mean difference in pooled standard deviation units, with thresholds of 0.2, 0.5 and 0.8 for small, medium and large. These are conventions rather than universal constants: a 0.2 difference in revenue may be enormous, and in latency catastrophic.

### 3.3 Small studies have huge minimum detectable effects

MDE scales as (z_{1α/2} + z_{1−β}) · σ · sqrt(2/n). With n = 20 per arm and 80% power you can only detect d of about 0.9, so 'no significant difference' in a small study is nearly uninformative.

### 3.4 Directional power depends on the alternative

Power computed under the null alternative is meaningless. You must state the specific effect you want to detect, and power depends on whether it is one-sided or two-sided.

### 3.5 Variance estimates come from elsewhere

Planning power requires an effect size and a variance, and the observed effect is the wrong source for the effect size. Use literature, pilot data or a business threshold, and inflate pilot variance because small pilots understate it.

### 3.6 Power curves are decision documents

Plotting power against n for a range of effects shows what your study can and cannot detect, which is the honest way to discuss a fixed budget or an inconclusive result.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `d = (̄x₁ − ̄x₂) / sₚ` | Cohen's d | pooled standard deviation |
| `Hedges' g = d / (1 − 3/(4n − 9))` | Bias-corrected d | better for small n |
| `r = d / sqrt(d² + 4)` | Effect size as r | relatable to correlation |
| `power = 1 − β` | Power | 1 minus Type II error |
| `MDE = (z_{1−α/2} + z_{1−β}) σ sqrt(2/n)` | Minimum detectable effect | what your n can see |
| `n = 2 (z_{1−α/2} + z_{1−β})² σ² / δ²` | Required n | inverting power |
| `p1, p2 proportions` | Proportion power | pooled variance under the null |
| `pph = 2 arcsin sqrt(p1) − 2 arcsin sqrt(p2)` | Fisher z for rates | propensity differences |

## 5. How the Pieces Fit Together

1. Define the effect worth detecting, from a business threshold or literature, not from data.

2. Estimate the variance from a pilot or historical data, and inflate it.

3. Fix alpha and power, then compute required n per arm and the horizon at your traffic.

4. Compute the MDE your sample can achieve, so the study's resolution is explicit.

5. Plot a power curve across a range of effects and n.

6. Report the power analysis with the study, and the power alongside any non-significant result.

## 6. Assumptions and Invariants

- The assumed effect size is credible and specified before data collection
- The variance estimate is defensible, and inflated if it comes from a small pilot
- Alpha and the chosen power reflect the cost of each error type
- The alternative is the specific effect of interest, correctly sided
- Independence holds, or the effective sample size is reduced accordingly
- Multiple comparisons are accounted for in the alpha used for power

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| 'No significant difference' from n = 20 per arm | study could only detect a huge effect | report the MDE alongside any null result |
| Power computed under the null alternative | power of the wrong hypothesis | specify the effect you want to detect |
| Effect size taken from the observed result | planning on the outcome | use literature, a business threshold, or an inflated pilot |
| Pilot variance used uninflated | small pilots understate variance | inflate by a documented factor and record the reasoning |
| Cohen's 0.5 declared medium | convention treated as universal | translate the effect into business units before deciding |
| Power computed but alpha not adjusted for multiple comparisons | family-wise error inflated | use the alpha you will actually apply |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `Normal quantile function` | z-values for power and MDE, closed form and exact |
| `Non-central t distribution` | exact power for small samples |
| `record PowerResult(double power, double mde, int nPerArm, double alpha)` | resolution reported with the design |
| `Arcane-free business translation` | converting an effect into units the business recognises |
| `Power curve generator` | power across a grid of n and effect sizes |

## 9. Where This Sits in the Larger System

- **lab03** is the test whose power this lab computes.
- **lab08** is where the sample size is applied to a design.
- **lab05** provides the effect sizes that feed power planning.
- **mlops/lab10** applies power and MDE to a live experimentation decision.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Compute Cohen's d and related effect sizes with correct pooling
- [ ] 0 — cannot yet — Compute power for means, proportions and comparisons using correct alternatives
- [ ] 0 — cannot yet — Derive the minimum detectable effect for a given sample size
- [ ] 0 — cannot yet — Invert power to obtain required sample size
- [ ] 0 — cannot yet — Choose an effect size from literature or pilot data rather than from the observed result
- [ ] 0 — cannot yet — Report power alongside every non-significant result

## 11. Summary Checklist

- [ ] My effect size came from a threshold or literature, not the observed result.
- [ ] My variance is defensible and inflated if from a small pilot.
- [ ] Power is computed under the correct sided alternative.
- [ ] I report the MDE my sample can achieve.
- [ ] Non-significant results come with power, not with 'no difference'.
- [ ] My alpha accounts for the comparisons I will actually make.
