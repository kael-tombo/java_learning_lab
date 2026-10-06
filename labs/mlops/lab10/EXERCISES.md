# A/B Testing & Experimentation - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab10
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out ABTestingLab
```

## Exercise 1: Power and sample size

**Task.** Design before you launch.

**Steps**
- Implement the sample size formula for means and proportions.
- Compute n for your baseline and target lift.
- Derive the MDE at that n.
- Convert n into a horizon at your daily traffic.

**Deliverable.** A pre-registered plan with n, MDE and a horizon date.

## Exercise 2: Two-arm analysis

**Task.** The statistics, done correctly.

**Steps**
- Implement two-proportion and two-mean tests with pooled SE.
- Cross-check against a hand calculation.
- Compute the effect size with a confidence interval.
- Verify on a known-effect synthetic dataset.

**Deliverable.** An analysis module with verified statistics.

## Exercise 3: SRM detection

**Task.** Catch the bug that invalidates everything.

**Steps**
- Implement the chi-square SRM check.
- Inject an assignment bug and confirm detection.
- Show that without the check you would read a meaningless result.
- Add SRM to the monitoring path.

**Deliverable.** A test proving an assignment bug is caught.

## Exercise 4: Peeking and sequential tests

**Task.** Stop lying to yourself.

**Steps**
- Simulate 20 tests with a true null effect and daily looks.
- Measure the false positive rate with and without correction.
- Implement an alpha-spending policy and re-measure.
- Show power loss versus early-stopping benefit.

**Deliverable.** A measurement of the inflation and the fix.

## Exercise 5: Guardrails

**Task.** Protect the downside.

**Steps**
- Define 3 guardrails with non-inferiority bounds.
- Simulate a treatment that wins on primary and breaches a guardrail.
- Verify the test stops.
- Write the stop and communicate procedure.

**Deliverable.** A guardrail implementation with a demonstrated stop.

## Exercise 6: Shadow test

**Task.** Learn something without exposure.

**Steps**
- Score a challenger on 100% of live traffic.
- Measure score distribution, latency and disagreement.
- Show what a shadow test can and cannot tell you.
- Define the exposure criteria it feeds.

**Deliverable.** A shadow analysis with explicit limits.

## Exercise 7: Practical significance

**Task.** Translate the effect into value.

**Steps**
- Compute the effect with an interval.
- Convert to business units (revenue, complaints, support load).
- Compare against rollout cost.
- Write a recommendation that is not just 'significant'.

**Deliverable.** A decision memo in business units.

## Exercise 8: Full experiment simulator

**Task.** Run the whole thing end to end.

**Steps**
- Simulate traffic, assignment, metrics and label delay.
- Include novelty effects and weekly seasonality.
- Compare fixed-horizon and sequential policies across scenarios.
- Report false positive rate and average time to decision.

**Deliverable.** A simulator with a policy comparison.


---

## Self-Check Before You Move On

- [ ] My alpha, power, MDE and horizon were fixed before launch.
- [ ] I check SRM before reading metrics.
- [ ] My test cannot be fooled by peeking.
- [ ] I have a guardrail with a stop rule.
