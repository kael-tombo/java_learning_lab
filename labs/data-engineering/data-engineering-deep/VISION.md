# VISION — data-engineering-deep: The Judgement Layer

> Where this module takes you: from operating tools competently to being the
> person who decides which tool, and who can prove the decision was right.

## The Arc

1. **Mechanics** — run the tool correctly (labs 01-20).
2. **Models** — hold the ten mental models that survive tool changes.
3. **Diagnosis** — read metrics and plans like an operator, not a user.
4. **Judgement** — choose between valid options and defend the choice.
5. **Proof** — demonstrate correctness, and demonstrate the cost of it.

## Why this module is separate from the numbered labs

The labs teach `Flink`, `Spark`, `Kafka`, `Airflow`, `Delta`, `Iceberg`. Those
names have half-lives. The reasoning does not: idempotency, event time,
back-pressure, schema evolution, and cost are the same problems in any engine,
and they are what a senior interview and a senior on-call shift actually test.

## Milestones (checkable)

- [ ] M1: state all thirty rules in `THEORY.md` from memory, grouped by model.
- [ ] M2: size a topic for throughput *and* parallelism, and show the arithmetic.
- [ ] M3: read a Spark physical plan and name every exchange and its cost.
- [ ] M4: explain a checkpoint barrier sequence and predict the effect of each failure.
- [ ] M5: diagnose "streaming disagrees with batch" with a ranked hypothesis list.
- [ ] M6: compute a cost model and identify which line item is actually movable.
- [ ] M7: write a data contract that would have caught a real incident.
- [ ] M8: design a backfill that cannot corrupt production results.
- [ ] M9: score 13+ on `QUIZ.md`.
- [ ] M10: present `REAL_WORLD_PROJECT.md` and survive the questions.

## Anti-Goals

- Memorizing configuration values instead of reasoning about them.
- Treating a tool's default behaviour as a design decision you made.
- "It matches the other pipeline" as a correctness argument.
- A monitoring design that cannot say which failure classes it cannot catch.

## The five questions this module exists to answer

1. **What is actually happening?** Read plans, metrics, and logs at the level
   of mechanism, not symptom. (`CODE_DEEP_DIVE.md`)
2. **Is it correct?** Prove it with an independent check, not a mirror. (R18)
3. **What does it cost?** Per question, not per system. (R16)
4. **What is the worst thing that could happen here?** And what stops it?
5. **What would I do differently at 10x, and at 1/10x?** Design that survives
   both is design that is finished.

## Interview Lens

Expect these, in this order of difficulty:

- "Walk me through a shuffle." (mechanics)
- "Your numbers differ from the ledger. Debug it." (diagnosis)
- "Why did you choose streaming over batch here?" (judgement)
- "How do you know your pipeline is correct?" (proof)
- "What would you do differently with 10x the volume?" (scale judgement)

The last two are where the separation is. Most candidates can answer the first
two.

## 30-Day Plan

- **Wk1** `THEORY.md` + `MATH_FOUNDATION.md`; exercises E1-E12.
- **Wk2** `CODE_DEEP_DIVE.md`; exercises E13-E24; flashcards pass 1.
- **Wk3** `QUIZ.md` until 13+; re-read `THEORY.md` for the weak models.
- **Wk4** `MINI_PROJECT.md` including the crash-recovery step; then
  `REAL_WORLD_PROJECT.md` as a written design review.

## Done = You Can

You are done when you can be handed an unfamiliar pipeline, a "the numbers are
wrong" message, and an unfamiliar stack, and produce a ranked diagnosis, an
estimate of the blast radius, a fix, and a monitoring addition — within an
hour — without needing to be told which of the ten models applies.

Then read `THEORY.md` one more time. It will read differently.
