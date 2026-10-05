# VISION — Data Types

## Vision Statement
**Choose types that prevent bugs and preserve precision** — every `int` vs `long` vs `BigDecimal` decision is a correctness and money decision.

---
## Mental Models
### 1. Bits Have Meaning
`signed 32-bit int` wraps; `long` delays overflow; `double` approximates. Money → `BigDecimal`, never `float/double`.
### 2. Primitive vs Reference
Primitives hold values; references hold addresses. `==` compares identity for objects, value for primitives.
### 3. Wrapper + Autoboxing Cost
`Integer` can be null, costs heap + NPE risk; autoboxing in loops = hidden allocation.
### 4. Inference (`var`) Discipline
`var` is type-safe but hides intent — use only when type is obvious from RHS.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Money/precision? | `BigDecimal` + explicit `RoundingMode` |
| Count/ID that may grow? | `long` by default |
| Nullable? | Wrapper/`Optional`, validate at boundary |
| Parsing input? | `parseX` with try/catch + range check |

---
## Career Trajectory
- **L1:** declare primitives, cast safely, avoid overflow.
- **L2:** wrapper pitfalls, `BigDecimal` arithmetic, `var` judgment.
- **L3:** serialization size impact, DB type mapping (int/BIGINT/DECIMAL).
- **L4:** org-wide numeric standards, currency handling policy.

---
## 4-Week Path
```
W1: Primitives, ranges, casting, overflow demos.
W2: Wrappers, autoboxing, String↔number parsing.
W3: BigDecimal, rounding, var + type inference drills.
W4: Price-calculator kata with tests for edge values.
```
## Success Metrics
- [ ] Predict overflow result before running
- [ ] Justify every BigDecimal vs double choice
- [ ] No NullPointerException from unboxing in review
