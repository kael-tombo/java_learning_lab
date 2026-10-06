# Statistical Power & Effect Size - Vision & Where This Is Going

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

## 1. The Future State

Power analysis becomes continuous and automated: variance and effect-size priors estimated from historical experiments, with designs proposed rather than validated after the fact. Effect sizes in domain units replace universal thresholds.

The test of that future state is boring: a new engineer ships a change to statistical power & effect size on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Planning effect sizes come from business thresholds or literature, never from observed results.
- Pilot variances are inflated with a recorded justification.
- Minimum detectable effect is reported with every design and every null result.
- Multiplicity is priced into both alpha and required sample size.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Size | Required n from alpha, power and an effect size. |
| L2 | Resolve | MDE for a fixed sample, expressed in business units. |
| L3 | Curve | Power curves across n and effects for a budget conversation. |
| L4 | Automate | Priors from historical experiments and design recommendations. |

## 4. Behaviours to Build

Compute power before collecting data and report MDE after it. Translate every effect size into units the business recognises. Never quote post-hoc power.

## 5. Anti-Vision (the failure mode we are avoiding)

- 'Not significant' reported without the MDE that explains it.
- Power computed from the observed effect.
- An uninflated pilot variance used to size a definitive study.
- Cohen's thresholds quoted without a business translation.

## 6. Technology Shifts That Change the Work

1. Automatic effect-size priors from historical experiment outcomes.
1. Bayesian design with prior predictive power as the planning tool.
1. Equivalence and non-inferiority designs requiring their own power treatment.
1. Multiobjective design allocating a fixed budget across many endpoints.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement effect sizes and power for means, reporting MDE alongside.
- **60 days.** Compute power curves and required n with inflated pilot variance.
- **90 days.** Price multiplicity, critique post-hoc power, and publish a full design document.

## 8. How To Tell You Are Actually Getting Better

- My effect size came from a threshold, not from the observed result.
- My variance is inflated if from a small pilot.
- I report the MDE my design can achieve.
- I never quote post-hoc power as evidence.

## 9. Principles That Should Not Change

- **Compute Cohen's d** Compute Cohen's d and related effect sizes with correct pooling
- **Compute power for means, proportions** Compute power for means, proportions and comparisons using correct alternatives
- **Derive the minimum detectable effect for a given sample size** Derive the minimum detectable effect for a given sample size

> Power is what makes a null result explainable, and effect size in business units is what makes a significant result actionable.
