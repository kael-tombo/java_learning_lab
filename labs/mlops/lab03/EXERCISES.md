# Model Registry & Versioning - Exercises

**Track:** mlops  |  **Lab:** lab03  |  **Level:** Intermediate

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
cd lab03
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out ModelRegistryLab
```

## Exercise 1: Registry with CAS promotion

**Task.** Get the concurrency story right first.

**Steps**
- Implement versions, stages and atomic CAS promotion.
- Force two concurrent promotions; assert exactly one wins.
- Implement rollback through the same path.
- Audit every transition with actor and versions.

**Deliverable.** A registry where concurrent promotion is provably safe.

## Exercise 2: A gate that explains itself

**Task.** Gate failures must teach.

**Steps**
- Implement metrics, lineage, latency, fairness and artifact checks.
- Return every failing reason, not just the first.
- Verify a bad model is blocked with a readable message.
- Show a good model passing every check.

**Deliverable.** A gate with readable refusals.

## Exercise 3: Shadow evaluation

**Task.** Compare on matured labels, not hopeful ones.

**Steps**
- Route live traffic to both champion and challenger.
- Store both predictions per request.
- Join labels as they mature and compute the delta.
- Enforce a minimum-mature-label threshold.

**Deliverable.** A shadow comparison that refuses to conclude early.

## Exercise 4: Retention and reachability

**Task.** Never delete something reachable.

**Steps**
- Implement archive and delete with a reachability check.
- Sweep a registry with 40 versions; show what is preserved.
- Verify aliases are respected.
- Produce a storage report.

**Deliverable.** A sweeper plus a preserved/deleted report.

## Exercise 5: Lineage end to end

**Task.** From a rollback to the original commit.

**Steps**
- Store run, data version and commit on every entry.
- Write a lookup from version to lineage.
- Roll back a version and reconstruct its run.
- Verify the reconstruction matches the tracked run.

**Deliverable.** A lineage query that reconstructs a past run.

## Exercise 6: Rollback drill

**Task.** Rehearse the operation you hope never to need.

**Steps**
- Pick a guardrail breach scenario.
- Time detection, decision and technical rollback.
- Find the bottleneck (usually decision latency).
- Pre-authorise rollback and re-time.

**Deliverable.** A timed drill with the bottleneck identified and fixed.

## Exercise 7: Multi-environment promotion

**Task.** Dev to staging to production.

**Steps**
- Add environments as stages with their own gates.
- Require stricter gates as you promote.
- Test that production promotion requires a staging record.
- Report the gate results per environment.

**Deliverable.** A promotion path with escalating gates.

## Exercise 8: Disaster: registry corruption

**Task.** What if the metadata store is lost?

**Steps**
- Export the registry to a signed backup.
- Rebuild from the backup plus artifact hashes.
- Verify restored entries still promote.
- Write a drill.

**Deliverable.** A tested backup and restore procedure.


---

## Self-Check Before You Move On

- [ ] Concurrent promotions cannot corrupt the stage pointer.
- [ ] A bad promotion is blocked by a named gate check.
- [ ] Rollback is one command and I have timed it.
- [ ] Every entry traces back to a run, a data version and a commit.
