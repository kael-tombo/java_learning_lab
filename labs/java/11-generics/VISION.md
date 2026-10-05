# VISION — Generics

## Vision Statement
**Shift errors from runtime to compile time** — generics make collections self-documenting and `ClassCastException` nearly extinct.

---
## Mental Models
### 1. Erasure Reality
`List<String>` → `List` at runtime; no `instanceof T`, no `new T[]` directly. Compiler inserts casts.
### 2. PECS Rule
Producer `extends`, Consumer `super`: `copy(List<? extends N>, List<? super N>)`.
### 3. Bounds as Contracts
`<T extends Comparable<T>>` constrains to what you actually call; unbounded `<?>` = read-mostly.
### 4. Diamond + Inference
`new ArrayList<>()` infers; method inference (`Collections.emptyList()`) flows from target type.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Raw type? | Never in new code |
| Wildcard vs param? | Wildcard for flexible APIs, param when relating inputs |
| Array of generic? | Use `List<T>`, not `T[]` |
| Unchecked warning? | Fix, or isolate + `@SuppressWarnings` with comment |

---
## Career Trajectory
- **L1:** use `List<T>`, `Map<K,V>`, for-each safely.
- **L2:** write generic methods/classes, PECS.
- **L3:** bounds, variance, type tokens (`Class<T>`).
- **L4:** library generic API design.

---
## 4-Week Path
```
W1: Generic collections, diamond, for-each.
W2: Generic methods/classes, bounds.
W3: Wildcards, PECS drills, erasure traps.
W4: Type-safe `Repository<T,ID>` + `Box<T>` kata.
```
## Success Metrics
- [ ] Apply PECS without hesitation
- [ ] Explain erasure limits from memory
- [ ] Zero raw types / unchecked warnings
