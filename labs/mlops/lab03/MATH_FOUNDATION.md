# Model Registry & Versioning - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `stage -> version (atomic pointer)` | Stage model - promotion is a pointer move |
| `shadow_delta = metric(challenger) - metric(champion)` | Shadow comparison - on matured labels |
| `promote if delta > -eps and all gates pass` | Gate - declarative, reviewable |
| `cas(stage, expected, next)` | Compare-and-set - prevents promotion races |
| `rollback: stage -> previous(champion)` | Rollback - instant and audited |
| `retention(days, reachability)` | Retention policy - never delete a reachable version |

## Why the Math Matters

The registry is a small distributed system: pointers, atomicity, linearisability and reachability. Everything else in MLOps that goes wrong at 3 a.m. tends to be one of those four.


---

## 1. Promotion as compare-and-set

```text
stage = read(stage)
if stage != expected: abort (someone else promoted)
write(stage, next)
linearisation point = the successful write
```

CAS makes promotion linearisable. Two concurrent promotions cannot both succeed, so the second caller learns it lost the race rather than silently overwriting.

**Worked example.** Promoter A reads champion=v7; promoter B reads v7. A CASes to v8. B's CAS expects v7, sees v8, aborts. Without CAS, B overwrites v8 with v9 and nobody knows v8 was ever live.


---

## 2. Shadow evaluation window

```text
window needed so labels mature
window >= max label latency + evaluation margin
promote only if delta = metric(challenger) - metric(champion) > -eps
```

Challenger evaluation is a delayed experiment. If labels take days to mature, a fixed short window produces comparisons on partial labels, which is worse than no comparison.

**Worked example.** Churn labels mature in 30 days: a 7-day shadow window compares on 7 days of mature labels and is directionally useful but noisy. 35 days is trustworthy.


---

## 3. Rollback blast radius and time

```text
t_detect = time from guardrail breach to alert
t_decide = approval latency
t_rollback = pointer move + cache invalidation
total = t_detect + t_decide + t_rollback
```

Rollback speed is dominated by detection and decision, not the pointer move. Optimising the technical part of rollback while the approval requires a meeting is theatre.

**Worked example.** Detection 4m, decision 20m (waiting for an approver), rollback 5s. Total 24m: 96% of it is human. Pre-authorise rollback and the number drops to 4m.


---

## 4. Retention and reachability

```text
reachable(v) = any stage or alias points to v
delete only if not reachable(v) and age > retention
archive (cold) before delete
```

Reachability is the safety property: a version a stage or alias can still resolve to must never be deleted. Retention is a cost policy layered on top of it.

**Worked example.** Champion=v8, staging=v8, v7 archived 30 days after being superseded. v7 is not reachable so it can move to cold, but keeping it 30 days means one quick rollback is possible.


---

## Cheat Sheet

- `stage -> version (atomic pointer)` - Stage model
- `shadow_delta = metric(challenger) - metric(champion)` - Shadow comparison
- `promote if delta > -eps and all gates pass` - Gate
- `cas(stage, expected, next)` - Compare-and-set
- `rollback: stage -> previous(champion)` - Rollback
- `retention(days, reachability)` - Retention policy

## Numerical Traps

- Promoting without a CAS, so concurrent promotions race.
- Comparing a challenger on partially matured labels.
- Deleting an archived version that is still reachable via an alias.
- Measuring rollback speed while the approval step still needs a meeting.
- Treating a stage pointer as the artifact and re-uploading on every promotion.

## Self-Check Problems

1. Describe the interleaving where two promotions without CAS lose a version, and what the operator would see.
2. Compute the minimum shadow window for labels with a 14-day maturation plus 2x noise margin.
3. Write a rollback plan with detection, decision and technical times, and compute the total.
4. Define a retention policy for a registry with 10 versions/month and a 90-day rollback window.
5. Design a gate that would have blocked a specific bad promotion, and show the values it evaluated.
