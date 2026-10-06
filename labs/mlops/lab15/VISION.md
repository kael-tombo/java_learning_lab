# Production ML Architecture - Vision & Where This Is Going

**Track:** mlops  |  **Lab:** lab15  |  **Level:** Advanced

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

Production ML architectures converge on composable inference graphs with per-node fallbacks, consistency expressed as a per-interaction policy, and feedback loops that include deliberate exploration. The load-bearing skill is enumerating failure behaviour per dependency before writing any code.

The test of that future state is boring: a new engineer ships a change to production ml architecture on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Training, serving and feedback are separate systems with isolated failure domains.
- Every dependency has an owner, an SLO, a metric and a stated failure behaviour.
- The serving path has a degradation ladder shorter than the detection cycle.
- Rollout stages have guardrails, and rollback is pre-authorised and rehearsed.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Sketch | Three paths with dependencies named. |
| L2 | Budget | Latency, availability and cost allocated per dependency. |
| L3 | Degrade | A tested degradation ladder and rollback with guardrails. |
| L4 | Learn | Feedback loops with documented latency and deliberate exploration. |

## 4. Behaviours to Build

Write the failure story before the happy path. Assume every dependency will fail at 3 a.m. and decide what your service does. Keep rollback a button, not a meeting.

## 5. Anti-Vision (the failure mode we are avoiding)

- One diagram with one arrow and no stated behaviour when it breaks.
- Adding a hot-path dependency for a small functional gain.
- A degradation ladder that takes longer to traverse than your detection.
- Quality metrics published without cost per decision.

## 6. Technology Shifts That Change the Work

1. Composable inference graphs with per-node fallback policies.
1. Consistency expressed as per-interaction policy rather than platform default.
1. Deliberate exploration budgets so feedback loops can learn new behaviour.
1. Cost-aware routing between model tiers based on per-decision value.

## 7. Your 30/60/90 Commitment

- **30 days.** Draw the three paths and require a failure mode on every edge.
- **60 days.** Allocate latency and availability budgets per dependency with enforcement.
- **90 days.** Build a tested degradation ladder, a pre-authorised rollback, and a unit economics model.

## 8. How To Tell You Are Actually Getting Better

- My diagram is also my failure playbook.
- Every dependency has a stated behaviour when it breaks.
- My degradation ladder is shorter than my detection cycle.
- I can state cost per 1,000 decisions.

## 9. Principles That Should Not Change

- **Design an end-to-end architecture with explicit data, control** Design an end-to-end architecture with explicit data, control and feedback paths
- **Separate the training path from the serving path deliberately** Separate the training path from the serving path deliberately
- **Design for degradation: what each component does when its dependencies fail** Design for degradation: what each component does when its dependencies fail

> Architecture is complete when you can say what happens when each arrow breaks, not when the boxes line up.
