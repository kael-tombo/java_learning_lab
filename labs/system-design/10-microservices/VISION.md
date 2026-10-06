# Microservices - Vision

## Why This Lab Exists
Microservices are frequently adopted for reasons that do not apply, and then
abandoned for reasons that were predictable. The failure is rarely the tooling;
it is a boundary decision made by counting tables instead of asking where the
business changes. This lab exists so the trade is understood before the
migration, not after.

## The Mental Model
Microservices trade **runtime complexity** for **change-time autonomy**:

```
  GAINED: independent deploy, independent scale, fault isolation
  PAID:    network in the call path, sagas instead of transactions,
           distributed debugging, N deployables to operate
```

The trade is worth it when organisational coupling dominates technical coupling:
many teams changing the same code concurrently. With a few engineers and one
product area, you pay the whole bill and collect none of the benefit.

## The Three Questions That Decide Everything
1. **Does each service own its data exclusively?** If two services read the
   same tables, the split exists only in a diagram.
2. **Does every remote call have a timeout, a breaker, and a bulkhead?** Without
   them, one slow dependency becomes a process-wide outage.
3. **Can you trace one request end to end?** Without it, a five-hop request
   becomes an outage investigation by guesswork.

If any answer is "no", the decomposition has not bought independence.

## The Distributed Monolith Warning
The most common outcome: microservices' costs with a monolith's coupling.
Symptoms: a change needs three services, one team's outage cascades, cross-
service joins are normal. The cure is fewer services with harder boundaries,
not more services with softer ones.

## Data Ownership Is Non-Negotiable
Cross-service data is **copied**, never shared, and the staleness bound is
written down. The moment two services can break each other with a schema
change, you have not decomposed — you have added network latency to a
monolith.

## Migration Discipline
Never rewrite. Facade, extract, dual write, **verify**, switch, shrink, repeat.
Every step is reversible, and the verification step is the one that matters:
the failure modes of a migration are silent, so a diff measured continuously is
worth more than any review.

## What You Should Be able To Do
- Decompose a monolith on business capability and defend the boundaries.
- Detect a distributed monolith from code, schema, and change-coupling data.
- Size a bulkhead with Little's Law and derive a timeout budget per hop.
- Implement a saga with durable state and classify compensatability.
- Design a Strangler Fig migration with a verification window.
- Diagnose a cascading outage using per-dependency metrics.

## The Anti-Goals
- Not "microservices by default". A modular monolith is frequently correct.
- No service without a data owner.
- No remote call without an explicit timeout. Ever. No defaults.
- No saga step without a stated compensation, including "this is not
  compensatable".

## Success Criteria
You can produce a decomposition with per-service data ownership, per-hop timeout
budgets, per-dependency bulkheads sized from traffic, and a migration plan whose
every step is independently reversible and independently verifiable.

## How To Use This Lab
1. `THEORY.md` for decomposition, communication, failure, migration.
2. `MATH_FOUNDATION.md` for latency, availability, and capacity arithmetic.
3. `CODE_DEEP_DIVE.md` for saga, outbox, breaker, bulkhead, deadlines.
4. `EXERCISES.md` for twelve applied problems; `QUIZ.md` to check yourself.
5. `MINI_PROJECT.md` to build; `REAL_WORLD_PROJECT.md` to migrate.