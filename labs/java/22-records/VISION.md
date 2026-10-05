# VISION — Records

## Vision Statement
**Model data, not boilerplate** — records make the state the API: transparent, immutable, and correct by construction.

---
## Mental Models
### 1. Transparent Carrier
`record Point(int x, int y)` — accessors `x()`, canonical ctor, `equals/hashCode/toString` derived from components. No hidden state.
### 2. Compact Constructor Validates
`Point { if (x < 0) throw ...; }` normalizes/defensively copies at construction. After that, immutable forever.
### 3. Shallow Immutability
Record is shallow: `record R(List<String> l)` still aliases a mutable list. Defensively copy (`List.copyOf`) in compact ctor.
### 4. Records Love Patterns
Destructure directly: `case Point(var x, var y)`. Serialization-friendly when libs support canonical ctors.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Pure data holder? | Record |
| Needs setters/inheritance? | Class, not record |
| Mutable component? | Copy in compact ctor, expose unmodifiable |
| Framework mapping? | Verify canonical-ctor support first |

---
## Career Trajectory
- **L1:** Declare records, compact-ctor checks, use as Map keys/DTOs.
- **L2:** Defensive copies, custom accessors (derived views), JSON round-trips.
- **L3:** Record patterns, sealed-record hierarchies, migration from Lombok/POJOs.
- **L4:** Immutable-domain design, canonical event/message schemas.

---
## 4-Week Path
```
W1: Records vs POJO teardown: equals/hashCode/toString behavior.
W2: Validation + defensive copies; mutable-component trap lab.
W3: JSON (Jackson record module) round-trips; versioning strategy.
W4: Order-book kata: records + sealed events + pattern dispatch.
```
## Success Metrics
- [ ] Every record validates + copies in compact ctor
- [ ] Zero setters in domain model
- [ ] JSON round-trip suite green on current lib version
