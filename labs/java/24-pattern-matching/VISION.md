# VISION — Pattern Matching

## Vision Statement
**Ask what it is, once** — patterns fuse type-test, cast, and destructure into one checked expression; the compiler tracks what you forgot.

---
## Mental Models
### 1. instanceof With a Name
`if (o instanceof String s)` — binding scoped to where it must be true (flow scoping). No cast, no `ClassCastException`.
### 2. Switch Becomes an Expression
`switch` with type patterns + guards (`case String s when s.isBlank()`) returns a value. Order matters: specific before general, else dominance error.
### 3. Record Patterns Destructure
`case Point(var x, var y)` pulls components out. Nested patterns (`Order(Customer(var name), _)`) kill getter chains.
### 4. Exhaustiveness + Null Discipline
Sealed switches checked exhaustive; `case null` explicit (or NPE-by-design). Guards don't count toward exhaustiveness — keep total cases unguarded.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Test + cast? | Pattern variable |
| Branch on shape? | Switch pattern, specific-first |
| Getter chain > 2? | Record pattern |
| Null input? | `case null` explicitly or document NPE |

---
## Career Trajectory
- **L1:** instanceof patterns, flow scoping.
- **L2:** Switch patterns + guards, arrow cases, yield.
- **L3:** Record/nested patterns, sealed-exhaustive design.
- **L4:** AST/event-dispatch architecture without visitors.

---
## 4-Week Path
```
W1: instanceof patterns; scoping puzzles.
W2: Switch patterns, guards, dominance errors.
W3: Record + nested patterns on domain events.
W4: JSON-event router kata: untyped map → sealed events via patterns.
```
## Success Metrics
- [ ] Zero explicit casts in pattern-covered code
- [ ] Explain dominance error and fix ordering
- [ ] Sealed switch exhaustive without default
