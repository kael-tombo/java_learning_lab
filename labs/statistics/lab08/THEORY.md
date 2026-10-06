# Experimental Design

**Track:** statistics  |  **Lab:** lab08  |  **Level:** Advanced

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

Before you collect data you must decide what to measure, how many observations you need, and how to assign treatments. Getting this wrong wastes the study; no analysis can repair it.

Design decisions are made once and constrain everything afterwards. A powerful analysis of a confounded design still answers the wrong question.

## 2. Learning Objectives

- State the estimand and the unit of randomisation explicitly
- Compute sample size for means and proportions from alpha, power and MDE
- Choose between completely randomised, blocked and factorial designs
- Estimate main effects and interactions in a factorial design
- Identify blocking variables that reduce variance without biasing
- Diagnose a confounded or underpowered design before running it

## 3. Core Concepts

### 3.1 The estimand comes first

Before any sample size, write down the quantity you want to estimate. 'The effect of price' is ambiguous; 'the change in mean conversion when price rises 10%, averaged over the current population' is a definition. The estimand determines the design and the analysis.

### 3.2 Power is a design property

Power depends on the effect you want to detect, the noise, and n. Computing it before collection turns an ambiguous result into a planned one; computing it afterwards explains a failure you should have prevented.

### 3.3 Blocking reduces variance

Grouping similar units into blocks and randomising within blocks removes the between-unit variation from the error term. Machine, operator and location are classic blocking variables, and blocking on an unmodelled source of variation can cut sample size by an order of magnitude.

### 3.4 Factorial designs answer more per run

Testing two factors in all four combinations estimates both main effects and their interaction. It is far more efficient than running two separate experiments, because each treatment is compared across both levels of the other factor.

### 3.5 Interaction changes the analysis

A significant interaction means main effects must not be interpreted on their own: the effect of one factor depends on the other. Ignoring it and reporting marginal means is the most common error in factorial analysis.

### 3.6 Confounding is a design failure

When two factors vary together, their effects are not separable, and no amount of data fixes it. Replication within cells, randomisation and blocking are what keep effects identifiable.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `n = 2 (z_{1α/2} + z_{1−β})² σ² / δ²` | Sample size for means | per-arm, two-sided |
| `n = (z_{α/2} sqrt(2 p̄ q̄) + z_{1−β} sqrt(p1q1 + p2q2))² / (p1−p2)²` | Sample size for proportions | pooled under the null |
| `SE with blocking: σ sqrt(1/n + 1/N · ρ)` | Blocked variance | rho is the correlation within blocks |
| `main effect A = mean(y at A+) − mean(y at A−)` | Factorial main effect | averaged over B levels |
| `interaction AB = (E++ − E+-) − (E-+ − E--)` | Interaction contrast | the term usually skipped |
| `δ = (z_{1−α/2} + z_{1−β}) σ sqrt(2/n)` | Minimum detectable effect | what your design can see |
| `VIF / variance share = 1 − R²_block` | Variance reduction from blocking | quantifies the gain |

## 5. How the Pieces Fit Together

1. Write the estimand and the unit of randomisation; both constrain everything else.

2. Identify blocking variables and nuisance factors to hold fixed.

3. Choose the design: completely randomised, randomised block, or factorial.

4. Compute sample size from alpha, power and the minimum effect worth detecting.

5. Randomise, execute, and verify randomisation actually happened.

6. Pre-specify the analysis: main effects, interactions and planned contrasts.

## 6. Assumptions and Invariants

- The estimand is defined before data collection and is estimable under the design
- Randomisation is genuinely random and executed, not approximately so
- Blocking variables are chosen before seeing outcomes
- The variance used for power comes from pilot data or a credible prior source
- Replication exists within every factorial cell
- The analysis is pre-specified, including which contrasts are planned

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| The study ran out of power and concluded nothing | sample size never computed | compute power from alpha, MDE and pilot variance before starting |
| A treatment effect is smaller than machine variation | no blocking | block on machine, operator and batch, cutting variance substantially |
| Main effects reported despite a significant interaction | interaction not tested | test the interaction first and interpret conditionally |
| Two factors are confounded | design coupled their levels | replicate cells or redesign; no sample size fixes this |
| Power computed from a pilot variance that is too small | unreliable pilot estimate | inflate the pilot variance before computing n |
| Randomisation done by hand or by a non-random method | randomisation not genuinely random | use a seeded generator with a recorded seed and verify assignment counts |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `SplittableRandom with a recorded seed` | reproducible randomisation |
| `Normal quantile function` | z-values for power and sample size |
| `Blocked arrays for the analysis` | variance reduction visible in the error term |
| `record Design(int factors, int[] levelsPerFactor, int nPerCell, String estimand)` | the plan, recorded before data |
| `Non-central t or normal for power` | power computed for the specified alternative |

## 9. Where This Sits in the Larger System

- **lab03** provides the tests these designs are powered for.
- **lab10** provides the detailed power and effect-size machinery.
- **lab04** is the analysis of the factorial design this lab produces.
- **mlops/lab10** applies this design to live product experiments.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — State the estimand and the unit of randomisation explicitly
- [ ] 0 — cannot yet — Compute sample size for means and proportions from alpha, power and MDE
- [ ] 0 — cannot yet — Choose between completely randomised, blocked and factorial designs
- [ ] 0 — cannot yet — Estimate main effects and interactions in a factorial design
- [ ] 0 — cannot yet — Identify blocking variables that reduce variance without biasing
- [ ] 0 — cannot yet — Diagnose a confounded or underpowered design before running it

## 11. Summary Checklist

- [ ] My estimand is written down and estimable under the design.
- [ ] Sample size comes from alpha, power and a defensible variance.
- [ ] Blocking variables were chosen before seeing outcomes.
- [ ] Randomisation is seeded, recorded and verified.
- [ ] Interactions are tested before main effects are interpreted.
- [ ] The analysis was pre-specified, including planned contrasts.
