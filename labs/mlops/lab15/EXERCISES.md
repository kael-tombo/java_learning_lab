# Production ML Architecture - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab15
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out ProductionMLArchitectureLab
```

## Exercise 1: Draw and validate the architecture

**Task.** Three paths, every edge owned.

**Steps**
- Draw training, serving and feedback paths separately.
- Give every edge a metric, SLO, owner and failure mode.
- Write a validator that rejects an edge without a failure mode.
- Verify it rejects an incomplete diagram.

**Deliverable.** A validated architecture spec.

## Exercise 2: Latency budget allocation

**Task.** Make the budget real.

**Steps**
- Set a 60 ms end-to-end budget across four terms.
- Enforce per-term timeouts.
- Simulate a dependency slipping and verify the ladder degrades.
- Report per-term p99 as well as the total.

**Deliverable.** A budget with enforcement and a degradation test.

## Exercise 3: Degradation ladder design

**Task.** Order the fallbacks by quality cost.

**Steps**
- Define full, cached, baseline and rules rungs.
- Quantify the quality loss at each rung.
- Verify the ladder is traversable inside the detection cycle.
- Test the terminal behaviour when all rungs fail.

**Deliverable.** An ordered, tested ladder.

## Exercise 4: Consistency choices per interaction

**Task.** Choose deliberately and write the reason.

**Steps**
- List five user interactions and choose a consistency level for each.
- Justify each choice in one sentence.
- Identify where a stale read would actually bother a user.
- Verify one profile update shows up immediately in a recommendation.

**Deliverable.** A consistency table with reasons and one verified behaviour.

## Exercise 5: Availability arithmetic

**Task.** Find the weakest link.

**Steps**
- Compute availability for a read path with four dependencies.
- Evaluate the effect of caching the model locally.
- Evaluate the effect of removing the registry from the hot path.
- Choose the architecture on the numbers.

**Deliverable.** An availability comparison driving a design choice.

## Exercise 6: Rollout and rollback design

**Task.** Shadow, canary, ramp, and back.

**Steps**
- Design the three stages with guardrails at each.
- Specify what is measured in shadow versus canary.
- Pre-authorise rollback with recorded reasons.
- Time the rollback using the local model cache.

**Deliverable.** A rollout plan with a timed rollback.

## Exercise 7: Chaos the dependencies

**Task.** Break each edge on purpose.

**Steps**
- Simulate a feature store outage, a registry outage and an event stream stall.
- Verify the documented degradation for each.
- Measure detection and mitigation time per edge.
- Fix the slowest response.

**Deliverable.** A chaos report with measured response times.

## Exercise 8: Unit economics

**Task.** The number leadership asks for.

**Steps**
- Model cost per 1,000 decisions from hardware, traffic and amortised training.
- Compute breakeven traffic for the current design.
- Evaluate the effect of the degradation ladder on cost.
- Publish it alongside quality metrics.

**Deliverable.** A unit economics model on a dashboard.


---

## Self-Check Before You Move On

- [ ] My diagram is also my failure playbook.
- [ ] Every dependency has a stated behaviour when it breaks.
- [ ] My degradation ladder is shorter than my detection cycle.
- [ ] I can state cost per 1,000 decisions.
