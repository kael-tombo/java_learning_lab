# VISION — Control Flow

## Vision Statement
**Make branching and looping obviously correct** — control flow is where bugs hide; structure it so the happy path and edge cases are visible at a glance.

---
## Mental Models
### 1. Guard-Clause Model
Validate early, return early. Nesting depth > 2 is a smell.
### 2. Switch-as-Classifier
Modern `switch` expressions return values exhaustively; prefer over `if-else` chains on enums/sealed types.
### 3. Loop-Invariant Model
Every loop needs invariant + termination proof: what stays true, what shrinks.
### 4. Branch-Cost Model
Branch mispredicts matter in hot loops; but readability beats micro-optimization first.

---
## Decision Framework
| Question | Rule |
|----------|------|
| >3 else-ifs on type? | Switch expression / polymorphism |
| Deep nesting? | Extract method + guard clauses |
| Loop + flag var? | Rewrite with `break`/stream `anyMatch` |
| Fall-through? | Explicit `yield` or comment; never accidental |

---
## Career Trajectory
- **L1:** if/switch/loops without off-by-one.
- **L2:** exhaustive switch, labeled break/continue judgment, refactoring nests.
- **L3:** pattern-matching switch, control-flow-aware reviews.
- **L4:** complexity budgets (cyclomatic), static-analysis gates.

---
## 4-Week Path
```
W1: if/ternary, switch expressions, scope.
W2: for/while/do-while, break/continue, off-by-one drills.
W3: Pattern switch, guards, refactoring nests.
W4: State-machine kata (order status) with tests.
```
## Success Metrics
- [ ] Rewrite nested code to flat guards on demand
- [ ] Write exhaustive switch with no default-abuse
- [ ] Keep methods under complexity 10
