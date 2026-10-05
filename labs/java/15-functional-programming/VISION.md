# VISION — Functional Programming

## Vision Statement
**Compose, don't control** — pure functions, immutability, and higher-order combinators replace branching state machines with testable pipelines.

---
## Mental Models
### 1. Purity: Same In, Same Out
No hidden reads/writes. Pure functions are cacheable, reorderable, parallel-safe. Push I/O to the edges.
### 2. Immutability by Default
`final` fields, unmodifiable collections, copy-on-write updates. Eliminates aliasing bugs that locks only hide.
### 3. Higher-Order Combinators
`map/filter/fold` over custom types; `Optional`/`Stream`/`CompletableFuture` are just containers with `map/flatMap`. Learn one shape, reuse everywhere.
### 4. Totality + Explicit Effects
Partial functions (`get`, `parse` that throws) become total via `Optional/Either/Try`. Errors are values, not control-flow surprises.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Shared mutable state? | Make immutable or isolate in one owner |
| Null/exception as signal? | Return Optional/Result type |
| Loop with accumulator? | fold/reduce with pure reducer |
| Side effect needed? | Single impure shell, pure core |

---
## Career Trajectory
- **L1:** Pure helpers, immutable DTOs, `map/filter/reduce`.
- **L2:** `Optional` chains, function composition, Either-style error types.
- **L3:** Lazy evaluation, memoization, property-based testing of laws.
- **L4:** Functional-core/imperative-shell architecture, effect-system judgment.

---
## 4-Week Path
```
W1: Purity refactor: extract pure core from a service; final/immutable models.
W2: HOF + composition (andThen/compose), currying/partial application.
W3: Optional/Either error-as-value; Try patterns without vavr if desired.
W4: Pricing-engine kata: pure rules + property tests (100 random cases).
```
## Success Metrics
- [ ] 80%+ of domain logic pure and unit-tested without mocks
- [ ] No null returns in new code; errors as values
- [ ] Property test proves refactor ≡ original on random inputs
