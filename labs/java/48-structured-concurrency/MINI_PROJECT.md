# MINI PROJECT — Structured Concurrency: Deadline-Bound Trip Planner

## Goal (2 weeks, ~8–10h)
Build a trip-planner (`flights + hotels + pricing`) with
`StructuredTaskScope`, dual policies, deadlines, and `ScopedValue`
context — replacing a tangled `CompletableFuture` version line-for-line.

## Requirements
### Functional
1. `plan(trip)`: fork flights/hotels/pricing in
   `ShutdownOnFailure`; 1.5s scope deadline; aggregated errors as
   typed `PlanFailure` (not CompletionException soup).
2. Hedged path: `cheapestQuote()` via `ShutdownOnSuccess` racing 3
   providers; losers cancelled; winner + cancellation proof in test.
3. Nested scope: pricing fans out again (fees + taxes) inside child
   scope with inherited deadline (remaining-time propagation).
4. `ScopedValue<Tenant>` + `ScopedValue<TraceId>`: bound per request,
   read in all subtasks; test asserts presence + immutability
   (rebind fails correctly).
5. No pinning: `ReentrantLock` cache only; JFR `VirtualThreadPinned`
   ≈ 0 on hot path; virtual-thread executor throughout.
6. CF comparison: keep legacy `CompletableFuture` impl behind flag;
   README table (LOC, branches, error types, orphan risk) favors scope.

### Non-functional
- 16+ tests: policy behavior, deadline overshoot <100ms, nested
  cancel, ScopedValue inheritance, no-orphan (thread count flat),
  error aggregation shape.
- JFR + `Thread.print` artifacts during deadline/Cancel runs.
- README: scope-tree diagram + "why this policy" per call.
- `--enable-preview` documented if scope API needs it (JDK 21 note).

## Starter Layout
```
src/main/java/com/lab48/trip/{Planner,HedgedQuotes,PricingScope,
  TenantContext}.java
src/test/java/.../{PolicyTest,DeadlineTest,ScopeValueTest,OrphanTest}.java
```

## Phases
### Week 1 — Scopes + Policies (4–5h)
- All/success scopes, error mapping, hedged quotes.
- Deliverable: both policies tested with cancellation proof.
### Week 2 — Context + Deadline (4–5h)
- ScopedValue, nested deadlines, CF comparison, JFR check.
- Deliverable: planner + comparison table + tuning note.

## Test Plan
- Kill one provider → ShutdownOnFailure aborts siblings <100ms.
- Slow providers → hedged returns first, others interrupted.
- Scope exit → `ThreadMXBean` count returns to baseline.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Scopes | Both policies correct | One correct | Raw threads/CF |
| Deadline | Propagated + measured | Present | Scattered gets |
| ScopedValue | Bound + tested | Used | ThreadLocal kept |
| Cancel/orphan | Proven zero orphans | Cancels | Leaks |
| CF compare | LOC + behavior table | Mentioned | Missing |

Pass ≥ 70. Stretch: custom `StructuredTaskScope` subclass (result
collector); scope-aware retry with backoff inside deadline.

## Demo Checklist
- [ ] Live kill of a provider → clean typed failure, no orphans
- [ ] Hedged race with cancellation log
- [ ] Deadline bar: scope aborts at 1.5s on the dot
- [ ] ScopedValue visible in every child log line

## Common Traps
Forking outside scope lifetime, catching `InterruptedException`
without re-interrupt, ThreadLocal across virtual threads.
