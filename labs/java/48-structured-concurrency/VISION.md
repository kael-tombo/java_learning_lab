# VISION — Structured Concurrency & Scoped Values

## Vision Statement
**Concurrency with a shape** — `StructuredTaskScope` makes fan-out a
lexical block: children cannot outlive parents, cancellation flows
down, and results/errors arrive as one well-typed outcome.

---
## Mental Models
### 1. Scope = Lifetime
Fork inside a scope; scope exit joins all. No orphan threads, no
`Future` leaked to a field — structure is the leak fix.
### 2. Policy Is Explicit
`ShutdownOnFailure` (fail fast) vs `ShutdownOnSuccess` (first win)
encode intent the old CF-chain hid in callbacks.
### 3. Cancellation Flows Downhill
Deadline/interrupt on the scope cancels children that honor
interruption. Timeouts belong on the scope, not scattered gets.
### 4. Context Without ThreadLocal Soup
`ScopedValue` carries request context (tenant/trace) across virtual
threads immutably — no `ThreadLocal.remove` roulette.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Parallel I/O, need all? | ShutdownOnFailure + join + throw |
| Hedged/first-win? | ShutdownOnSuccess |
| Context needed? | ScopedValue, never mutable ThreadLocal |
| Legacy CF? | Migrate at scope boundaries, keep inner CF |

---
## Career Trajectory
- **L1:** Scope open/fork/join, subtask exception mapping.
- **L2:** Policies, deadlines, nested scopes, ScopedValue binding.
- **L3:** Migration of CF/pool fan-out to scopes; pinning hygiene.
- **L4:** Fleet cancellation/deadline standards, scope-aware libraries.

---
## 4-Week Path
```
W1: Scope kata — all/success policies + exception aggregation.
W2: Deadline + cancellation lab with JFR pinning check.
W3: ScopedValue context propagation (tenant/trace) + tests.
W4: Migrate one CF gateway to scopes; diff complexity + behavior.
```
## Success Metrics
- [ ] Zero orphan subtasks (thread count flat after scope)
- [ ] Deadline honored end-to-end (<100ms overshoot)
- [ ] Context present in every child (test-proven)
- [ ] CF→scope migration with fewer lines, same behavior

## What This Is Not
Syntax sugar over futures. It is lifetime + cancellation discipline.

> Mantra: **If a task can outlive its caller, it is a bug.**
