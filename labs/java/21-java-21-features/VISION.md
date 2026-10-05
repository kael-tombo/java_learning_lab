# VISION — Java 21 Features

## Vision Statement
**Write half the code with twice the safety** — records, sealed types, pattern matching, and virtual threads are one coherent upgrade, not a feature list.

---
## Mental Models
### 1. Data as Records
`record` = transparent immutable carrier. Destructure with record patterns instead of getter chains.
### 2. Closed Hierarchies
`sealed interface ... permits` makes illegal states unrepresentable; exhaustive `switch` proves it at compile time.
### 3. Patterns Over Branches
`instanceof` patterns, `switch` patterns, record patterns replace visitor/cast ladders. Compiler checks exhaustiveness.
### 4. Concurrency Default Flips
Virtual threads make blocking code scalable; `SequencedCollection`, string templates (preview), and scoped values complete the modern toolkit.

---
## Decision Framework
| Question | Rule |
|----------|------|
| DTO/Value? | Record (validate in compact ctor) |
| Fixed variants? | Sealed + exhaustive switch |
| Type test + cast? | Pattern variable, never raw cast |
| I/O fan-out? | Virtual threads + structured scope |

---
## Career Trajectory
- **L1:** Records, text blocks, `var`, switch expressions.
- **L2:** Sealed + pattern switch, record patterns, virtual threads.
- **L3:** Exhaustiveness design, guarded-pattern discipline, migration of legacy hierarchies.
- **L4:** Modern-Java architecture: immutable domain + closed types + Loom concurrency.

---
## 4-Week Path
```
W1: Records + compact-ctor validation; sequenced collections.
W2: Sealed hierarchies + exhaustive switches.
W3: Pattern matching (instanceof/switch/record) refactor kata.
W4: Virtual-thread service + full modern rewrite of a legacy module.
```
## Success Metrics
- [ ] Zero instanceof-cast pairs in rewritten code
- [ ] Switch over sealed type compiles without default
- [ ] Virtual-thread load test passes with blocking code
