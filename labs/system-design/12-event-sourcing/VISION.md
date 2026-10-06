# Event Sourcing - Vision

## Why This Lab Exists
Event sourcing is the most powerful and most frequently misused pattern in this
lab set. It is chosen for its buzzwords and abandoned for its consequences,
usually by teams who wanted event *driven* architecture. This lab exists so the
distinction, the costs, and the operational requirements are understood before a
ledger is committed to it.

## The Mental Model
One sentence separates the two patterns:

```
  EVENT SOURCING   the log IS the state; state is a projection
  EVENT DRIVEN     events notify; a table is still the source of truth
```

The test: **delete every projection and rebuild from the log. Is anything
lost?** If yes, you are event-driven, and you do not get the properties that
make event sourcing worth its cost.

## The Trade, Honestly

```
  BOUGHT                          PAID
  full history, always            schema changes are genuinely painful
  temporal queries: yes           reads come from projections you must build
  audit: free                     rebuild and operational discipline
  rebuild from scratch            a real conflict with GDPR erasure
```

Note that "audit: free" is only true if the events are actually complete. An
event-driven system with `AccountUpdated` notifications has lost the account
opening, the correction, and the currency — so it cannot rebuild, and its audit
trail is a notification log, not a record.

## The Three Non-Negotiables
1. **Effective-dated events** — otherwise temporal queries are impossible and
   ordering depends on unsynchronised clocks.
2. **Deterministic projections** — otherwise rebuild produces a different
   answer and verification is worthless.
3. **A tested rebuild** — the safety net you are paying all this complexity for.
   If you cannot rebuild, you have made snapshots authoritative, which is a
   different (and worse) architecture.

## The Most Commonly Missed Requirement
**Never put erasable personal data in the log.** Events carry `customerRef`;
name, email, and address live in a mutable store. Decide this at design time —
retrofitting it means rewriting history, which an immutable log does not allow.

## What You Should Be able To Do
- Distinguish event sourcing from event-driven and prove it with a rebuild test.
- Implement an aggregate that decides, with optimistic concurrency on append.
- Evolve event schemas with upcasting and tolerant readers.
- Build a deterministic, idempotent, checkpointing projection.
- Deploy a projection schema change with blue-green and verification.
- Size snapshots and prove rebuild feasibility from the arithmetic.
- Resolve the audit-versus-erasure conflict.

## The Anti-Goals
- Not "store events and also update a table", which is event-driven with extra
  writes.
- No projection that calls `now()` or reads external mutable state.
- No external side effects inside a projection. A rebuild re-sends them all.
- Never mutate stored events. Interpret them instead.

## Success Criteria
You can delete every read model in your design, rebuild from the log, and prove
the diff is empty — routinely, automatically, with an alert when it is not.

## How To Use This Lab
1. `THEORY.md` for the architecture and the hard parts.
2. `MATH_FOUNDATION.md` for storage, snapshot, rebuild, and lag arithmetic.
3. `CODE_DEEP_DIVE.md` for aggregate, store, projector, snapshot, upcaster.
4. `EXERCISES.md` for twelve applied problems; `QUIZ.md` to check yourself.
5. `MINI_PROJECT.md` to build; `REAL_WORLD_PROJECT.md` to operate.