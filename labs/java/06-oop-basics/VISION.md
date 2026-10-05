# VISION — OOP Basics

## Vision Statement
**Model behavior, not just data** — classes encapsulate invariants; good objects make illegal states unrepresentable.

---
## Mental Models
### 1. Encapsulation Wall
`private` fields + validated constructors/setters. No naked public mutable fields.
### 2. Construction Guarantees
Constructor establishes invariant; factory methods name intent (`Order.paid(...)`); `final` fields = safe publication.
### 3. Static vs Instance
`static` = class-level, no `this`; overuse = procedural code in OO clothing.
### 4. Composition First
Prefer composition over ad-hoc inheritance; `record` for pure data carriers.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Data only? | `record` |
| Needs validation? | Compact constructor / factory |
| Shared helper? | `static` pure function; else instance method |
| Mutable state? | Minimize; defensive copies on in/out |

---
## Career Trajectory
- **L1:** classes, constructors, getters/setters.
- **L2:** encapsulation, static/final, records.
- **L3:** domain modeling, aggregates, immutability patterns.
- **L4:** bounded contexts, module boundaries.

---
## 4-Week Path
```
W1: Classes, fields, constructors, this.
W2: Encapsulation, static/final, toString/equals intro.
W3: Records, composition, UML sketching.
W4: Bank-account/order domain kata with invariant tests.
```
## Success Metrics
- [ ] No public mutable fields in portfolio code
- [ ] Every class documents its invariant
- [ ] Prefer record vs class with justification
