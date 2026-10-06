# Architecture Patterns - Vision

## Why This Lab Exists
Architecture patterns are named, reusable solutions to recurring structural
problems. They exist so that a team can say "use sidecar" instead of redrawing
the same box diagram for the fourth time this quarter. The payoff is not
elegance — it is **shared vocabulary under pressure**.

## The Mental Model
A pattern is a *force* diagram made concrete. Every pattern in this lab is
traded against four forces:

```
  Coupling  <------->  Latency budget
  Correctness         Operational cost
```

Pick a pattern and you have silently bought into the trade-offs on both sides
of that balance. The skill being trained is naming the trade, not reciting the
diagram.

## What You Should Be Able To See
- Monolith -> modular monolith -> services is a *sequence*, not a jump.
- Layered vs. hexagonal vs. clean: dependency direction is the whole argument.
- Sidecar / ambassador: per-language concerns without a shared runtime.
- Strangler fig: how you leave a legacy system without a big-bang rewrite.
- CQRS, event sourcing, bulkhead, circuit breaker: the vocabulary of the
  reliability chapter of any architecture review.

## The Anti-Goals
- Not a catalogue to memorise. Every pattern listed here has a documented
  failure mode in `COMMON_MISTAKES.md`.
- Not "microservices by default." A modular monolith is a legitimate, often
  superior, answer.
- No pattern fixes a missing data ownership boundary.

## Success Criteria
You can look at a 3-box diagram and name the pattern *and* its cost in under
five seconds, and justify the choice against a stated constraint (team size,
consistency need, latency budget, blast radius).

## How To Use This Lab
1. `THEORY.md` for the catalogue and force diagrams.
2. `MATH_FOUNDATION.md` for the coupling and cost numbers behind the claims.
3. `CODE_DEEP_DIVE.md` for runnable Java sketches of each pattern.
4. `MINI_PROJECT.md` to apply two patterns to one small system.
5. `REAL_WORLD_PROJECT.md` for a production decomposition with consequences.
