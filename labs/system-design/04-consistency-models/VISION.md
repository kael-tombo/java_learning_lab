# Consistency Models - Vision

## Why This Lab Exists
Every distributed system makes a promise about what a reader will see after a
write. Almost every production incident involving "stale data" is a system that
made a promise nobody wrote down. This lab exists so the promise becomes a
deliberate, per-field, per-workload decision.

## The Mental Model
Consistency is a **spectrum, chosen per read**, not a database setting:

```
  Linearizable -> Sequential -> Causal -> Read-your-writes -> Monotonic
  (strongest)                                              (weakest)
```

Each step down trades a guarantee for latency and availability. The design
skill is picking the *weakest* model that still makes the product acceptable.

## Two Axes People Confuse
- **Consistency** (what you will see) is not **replication** (where the data is
  copied). A single-node store can be linearizable; a 40-node store need not be.
- **Consistency** is not **durability**. Durability is about surviving crashes;
  consistency is about what concurrent readers observe.

## What You Should Be Able To Do
- State, in one sentence, the guarantee your "read your own write" flow needs.
- Choose linearizable vs. stale-while-revalidate for a given UI surface and
  defend it.
- Explain why LWW registers need a tiebreak, and what that tiebreak costs.
- Describe read-repair and hinted handoff and when each is a last resort.
- Recognise the moments where "eventually consistent" means "we never noticed".

## The Anti-Goals
- Not a CAP-tour. CAP is one axis; this lab is about the guarantees *within*
  the no-partition branch, which is where product behaviour is decided.
- No "eventual consistency" without a stated staleness bound and a repair path.

## Success Criteria
For any read path you review, you can state: the consistency model, the
observed staleness bound, and the user-visible symptom when that bound is
violated.

## How To Use This Lab
1. `THEORY.md` for the model-by-model walkthrough.
2. `MATH_FOUNDATION.md` for quorum intersection, staleness probability, LWW.
3. `CODE_DEEP_DIVE.md` for vector clocks, quorum reads, conflict resolution.
4. `MINI_PROJECT.md` to implement RYOW and read-your-writes plumbing.
5. `REAL_WORLD_PROJECT.md` for a mixed-consistency commerce platform.
