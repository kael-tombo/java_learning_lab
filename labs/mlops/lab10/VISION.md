# A/B Testing & Experimentation - Vision & Where This Is Going

**Track:** mlops  |  **Lab:** lab10  |  **Level:** Advanced

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

Experimentation converges on always-valid inference, interference-aware designs, and bandit-style allocation for high volume. The frontier is not more metrics; it is designs that remain honest when teams look at the data constantly, which they always do.

The test of that future state is boring: a new engineer ships a change to a/b testing & experimentation on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Plans are pre-registered with alpha, power, MDE, horizon and stopping rule.
- Assignment is a stable hash and SRM is checked before every read.
- Guardrails have non-inferiority bounds agreed in advance.
- Decisions quote effect size with an interval in business units.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Test | Two arms, fixed horizon, a primary metric. |
| L2 | Design well | Power and MDE computed before launch; SRM checked. |
| L3 | Control error | Sequential or always-valid inference with guardrails. |
| L4 | Scale | Interference-aware designs, multi-arm bandits, shared experimentation. |

## 4. Behaviours to Build

Decide the plan before seeing data. Check SRM before metrics. Treat any uncorrected peek as a design flaw. Translate effects into money and support load before calling a winner.

## 5. Anti-Vision (the failure mode we are avoiding)

- Daily significance checks with a stop at first crossing.
- Calling 'no significant difference' without having computed power first.
- Shipping a treatment because conversion rose 40% and complaints rose 300%.
- Filtering outliers after the result looks wrong.

## 6. Technology Shifts That Change the Work

1. Always-valid confidence sequences removing the need to pre-plan looks.
1. Interference-aware and cluster randomisation for marketplace settings.
1. Bandit allocation replacing fixed A/B for high-volume, low-cost decisions.
1. Shared experimentation platforms standardising metrics and SRM checks across teams.

## 7. Your 30/60/90 Commitment

- **30 days.** Compute power, MDE and horizon for a planned experiment and pre-register it.
- **60 days.** Implement two-arm analysis with SRM checks and effect intervals.
- **90 days.** Add sequential inference and guardrails, and demonstrate both on a simulator.

## 8. How To Tell You Are Actually Getting Better

- My plan was fixed before data collection.
- I check SRM before reading any metric.
- My test cannot be fooled by peeking.
- My decision quotes an effect in business units.

## 9. Principles That Should Not Change

- **Design a randomised experiment with power, MDE** Design a randomised experiment with power, MDE and a fixed horizon
- **Compute significance for proportions, means** Compute significance for proportions, means and ratios correctly
- **Understand why peeking inflates false positives** Understand why peeking inflates false positives and what to do about it

> An experiment you can stop early is worth more than one that is statistically pure and never finishes.
