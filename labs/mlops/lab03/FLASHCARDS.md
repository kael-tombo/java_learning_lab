# Model Registry & Versioning - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | Why is a model version immutable? | Same bytes, same hash, forever. Mutating a published version breaks reproducibility and rollback. |
| 2 | What is the difference between a version and a stage? | A version is the artifact; a stage is a pointer to a version. Promotion moves the pointer. |
| 3 | What is a champion/challenger setup? | The champion serves; the challenger scores live traffic in shadow for comparison before promotion. |
| 4 | Why require lineage on a registry entry? | So a rollback three months later needs no archaeology. |
| 5 | How do you prevent two racing promotions? | Compare-and-set on the expected current version, so the second one fails loudly. |
| 6 | What should a promotion gate check? | Metrics within tolerance on matured labels, complete lineage, required sign-offs, latency and fairness budgets. |
| 7 | Why compare on matured labels? | Offline metrics can drift from live behaviour; matured labels are what actually happened. |
| 8 | What does a shadow deployment do? | Scores live traffic without affecting decisions, so you compare before you promote. |
| 9 | What is Versions, stages and aliases? | A version is immutable: same bytes, same hash, forever. |
| 10 | What is Champion and challenger? | The champion serves. |
| 11 | What is Gates, not opinions? | A promotion gate is a declarative check: metrics within tolerance, lineage complete, fairness review signed off, latency budget met. |
| 12 | What is Atomicity and concurrency? | Two promotions racing will corrupt the stage pointers. |
| 13 | What is Lineage and reproducibility? | A registry entry should point back to the tracking run, the data version, the commit and the evaluation report. |
| 14 | What is Deprecation and retention? | Registry growth is unbounded. |
| 15 | In this lab, what does `stage -> version (atomic pointer)` mean? | Stage model: promotion is a pointer move |
| 16 | In this lab, what does `shadow_delta = metric(challenger) - metric(champion)` mean? | Shadow comparison: on matured labels |
| 17 | In this lab, what does `promote if delta > -eps and all gates pass` mean? | Gate: declarative, reviewable |
| 18 | In this lab, what does `cas(stage, expected, next)` mean? | Compare-and-set: prevents promotion races |
| 19 | In this lab, what does `rollback: stage -> previous(champion)` mean? | Rollback: instant and audited |
| 20 | In this lab, what does `retention(days, reachability)` mean? | Retention policy: never delete a reachable version |
| 21 | You see 'Two promotions raced and production is now on an unvetted model' in production. What is the cause and the fix? | no compare-and-set on the stage pointer Fix: use CAS on expected current version; the second promotion must fail loudly |
| 22 | You see 'A rollback needed the code commit and nobody had it' in production. What is the cause and the fix? | no lineage on the registry entry Fix: lineage is a gate, not optional metadata |
| 23 | You see 'The challenger was promoted on an offline metric and got worse live' in production. What is the cause and the fix? | no shadow evaluation on matured labels Fix: require a shadow window with matured-label comparison |
| 24 | You see 'A published version was edited in place' in production. What is the cause and the fix? | mutating an immutable artifact Fix: versions are content-hashed; a change is a new version |
| 25 | You see 'Registry has 400 versions and nobody can find the champion' in production. What is the cause and the fix? | no stage model or aliases Fix: use stages and aliases; archive by policy |
| 26 | You see 'Rollback itself failed because the artifact store was down' in production. What is the cause and the fix? | artifact not pinned locally Fix: cache the current champion locally for fast rollback |
| 27 | Which Java API is the backbone of: compare-and-set style promotion | `AtomicReference / synchronized on the stage pointer` |
| 28 | Which Java API is the backbone of: immutable registry entry | `record ModelVersion(String name, int version, String artifactHash, Lineage lineage)` |
| 29 | Which Java API is the backbone of: explicit stage set with legal transitions | `EnumMap for stages` |
| 30 | Which Java API is the backbone of: publishing artifacts without half-written reads | `java.nio.file.Files.copy with ATOMIC_MOVE` |
| 31 | Which Java API is the backbone of: archiving unreachable versions on a schedule | `Duration-based retention sweep` |
| 32 | Why does Versions, stages and aliases matter operationally? | A version is immutable: same bytes, same hash, forever. |
| 33 | Why does Champion and challenger matter operationally? | The champion serves. |
| 34 | Why does Gates, not opinions matter operationally? | A promotion gate is a declarative check: metrics within tolerance, lineage complete, fairness review signed off, latency budget met. |
| 35 | Why does Atomicity and concurrency matter operationally? | Two promotions racing will corrupt the stage pointers. |
| 36 | Why does Lineage and reproducibility matter operationally? | A registry entry should point back to the tracking run, the data version, the commit and the evaluation report. |
| 37 | Why does Deprecation and retention matter operationally? | Registry growth is unbounded. |
| 38 | In the Model Registry & Versioning pipeline, what happens next? Train and track the run (Lab 02), producing an immutable art... | Train and track the run (Lab 02), producing an immutable artifact with a content hash. |
| 39 | In the Model Registry & Versioning pipeline, what happens next? Register the artifact with a version, lineage (run, data ver... | Register the artifact with a version, lineage (run, data version, commit) and evaluation report. |
| 40 | In the Model Registry & Versioning pipeline, what happens next? Deploy to shadow; it scores live traffic without affecting d... | Deploy to shadow; it scores live traffic without affecting decisions. |
| 41 | In the Model Registry & Versioning pipeline, what happens next? Evaluate the challenger against the champion on matured labe... | Evaluate the challenger against the champion on matured labels for a fixed window. |
| 42 | In the Model Registry & Versioning pipeline, what happens next? Run the gate: metrics within tolerance, lineage complete, si... | Run the gate: metrics within tolerance, lineage complete, sign-offs recorded. |
| 43 | In the Model Registry & Versioning pipeline, what happens next? Promote with compare-and-set; watch guardrails; roll back wi... | Promote with compare-and-set; watch guardrails; roll back with one command if a guardrail breaches. |
| 44 | Exercise focus: Registry with CAS promotion | Get the concurrency story right first. |
| 45 | Exercise focus: A gate that explains itself | Gate failures must teach. |
| 46 | Exercise focus: Shadow evaluation | Compare on matured labels, not hopeful ones. |
| 47 | Exercise focus: Retention and reachability | Never delete something reachable. |
| 48 | Exercise focus: Lineage end to end | From a rollback to the original commit. |
| 49 | Exercise focus: Rollback drill | Rehearse the operation you hope never to need. |
| 50 | State the Promotion as compare-and-set result for Model Registry & Versioning. | Promoter A reads champion=v7; promoter B reads v7. A CASes to v8. B's CAS expects v7, sees v8, aborts. Without CAS, B overwrites v8 with v9 and nobody knows v8 was ever live. |
| 51 | State the Shadow evaluation window result for Model Registry & Versioning. | Churn labels mature in 30 days: a 7-day shadow window compares on 7 days of mature labels and is directionally useful but noisy. 35 days is trustworthy. |
| 52 | State the Rollback blast radius and time result for Model Registry & Versioning. | Detection 4m, decision 20m (waiting for an approver), rollback 5s. Total 24m: 96% of it is human. Pre-authorise rollback and the number drops to 4m. |
| 53 | State the Retention and reachability result for Model Registry & Versioning. | Champion=v8, staging=v8, v7 archived 30 days after being superseded. v7 is not reachable so it can move to cold, but keeping it 30 days means one quick rollback is possible. |
| 54 | How fast is rollback if the artifact store is down? | It should be instant: cache the current champion locally so rollback needs no network fetch. |
| 55 | Why not delete old versions immediately? | You may need to roll back to any version within the retention window, and reachability matters. |
| 56 | What is an alias for? | A stable name like 'champion' or per-region pointers, so consumers never hardcode version numbers. |
| 57 | How do you handle a model that was promoted by mistake? | Roll back with CAS, then investigate why the gate passed — the gate is usually the bug. |
| 58 | Assumption / invariant to defend: Published versions are immutable and content-hashed... | Published versions are immutable and content-hashed |
| 59 | Assumption / invariant to defend: Stage transitions go through a service, not direct database edits... | Stage transitions go through a service, not direct database edits |
| 60 | Assumption / invariant to defend: Lineage is complete before a version can be staged... | Lineage is complete before a version can be staged |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
