# Phaser — README

`java.util.concurrent.Phaser` (Java 7, JSR-166) is a reusable barrier with
dynamic membership: parties register and deregister mid-execution, phases
advance 0, 1, 2, ..., and each phase completes only when every registered
party has arrived. Unlike `CyclicBarrier` (fixed gang) and `CountDownLatch`
(one-shot), a Phaser grows, shrinks, and repeats.

## The seven verbs

| Call | Arrives? | Waits? | Leaves? |
|---|---|---|---|
| `register()` / `bulkRegister(n)` | adds unarrived parties | no | no |
| `arrive()` | yes | no | no |
| `arriveAndAwaitAdvance()` | yes | yes | no |
| `arriveAndDeregister()` | yes | no | yes |
| `awaitAdvance(p)` | no | yes, until past `p` | no |
| `awaitAdvanceInterruptibly(p)` | no | yes, interruptible | no |
| `onAdvance(p, parties)` override | — | — | terminates if true |

## Return-value asymmetry (source-verified)

- `arrive()` returns the ARRIVAL phase k (await it with `awaitAdvance(k)`).
- `arriveAndAwaitAdvance()` returns the POST-ADVANCE phase k+1.
- `awaitAdvance(p)` returns once the current phase differs from `p`.
- Terminated phasers report negative phases; post-termination every call
  passes through — an open gate, not a broken barrier.

## Key rules

- `register()` adds UNARRIVED parties to the current phase: late joiners
  hold the phase until they arrive or deregister.
- Termination comes from `onAdvance` returning true (default: true only at
  zero parties) or `forceTermination()`.
- `onAdvance` must stay a fast predicate — it runs at the advance point
  with all parties waiting.
- Tier with `new Phaser(parent)` for thousands of parties; single-level
  suffices until profiling says otherwise.
- Phases are `int`s; 2^31 advances wrap to negative (spurious termination).

## Lab map

- THEORY.md / CODE_DEEP_DIVE.md — authoritative semantics + runnable demos.
- HOW_IT_WORKS.md, INTERNALS.md, ARCHITECTURE.md — mechanism and state.
- STEP_BY_STEP.md, VISUAL_GUIDE.md, MENTAL_MODELS.md — learning scaffolds.
- EXERCISES.md, QUIZ.md, FLASHCARDS.md — practice and recall.
- COMMON_MISTAKES.md, DEBUGGING.md, PERFORMANCE.md — failure modes.
- HISTORY.md, REFERENCES.md, MATH_FOUNDATION.md — context and models.
- SECURITY.md, REFACTORING.md, REFLECTION.md — hardening and transfer.
- WHY_IT_EXISTS.md, WHY_IT_MATTERS.md — motivation and payoff.
