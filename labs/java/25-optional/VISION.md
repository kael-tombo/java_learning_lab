# VISION — Optional

## Vision Statement
**Absence is a value, not a landmine** — Optional forces callers to handle "nothing" at compile time instead of discovering null at 3 AM.

---
## Mental Models
### 1. Return-Only Wrapper
`Optional` is for return types (maybe-a-user), not fields/params/collections. Field-Optional breaks serialization; param-Optional confuses overloads.
### 2. Pipeline, Not Branch
`map/flatMap/filter/orElseThrow` chains replace `if (x != null)` ladders. `flatMap` when the step already returns Optional.
### 3. Eager vs Lazy Defaults
`orElse` always evaluates; `orElseGet(Supplier)` lazy. Expensive default + `orElse` = hidden cost on every hit.
### 4. Terminal Decision
End every chain with intent: `orElseThrow`, `ifPresentOrElse`, or domain default. Bare `get()` without `isPresent` is just NPE with steps.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Maybe-absent return? | Optional |
| Field/param/collection? | Null-object, overload, or empty collection — not Optional |
| Chained lookup? | flatMap chain, single terminal |
| Default expensive? | orElseGet, never orElse |

---
## Career Trajectory
- **L1:** `ofNullable/map/orElse`, kill `!= null` ladders.
- **L2:** `flatMap/filter`, `orElseThrow`, `ifPresentOrElse`.
- **L3:** Optional across layers (repo→service→controller mapping), perf-aware defaults.
- **L4:** Absence modeling (Optional vs Either vs empty-collection policy org-wide).

---
## 4-Week Path
```
W1: of/ofNullable/map/filter basics; get() ban.
W2: flatMap chains (user→order→coupon); orElse vs orElseGet bench.
W3: Layer bridging: repo Optional → service Either/default → HTTP 404.
W4: Null-hunt kata: convert a null-riddled service, NPE suite → green.
```
## Success Metrics
- [ ] Zero `Optional.get()` without proof in review
- [ ] Explain flatMap-vs-map from memory with example
- [ ] No Optional fields/params in new code
