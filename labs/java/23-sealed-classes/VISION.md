# VISION — Sealed Classes

## Vision Statement
**Close the hierarchy, open the reasoning** — sealed types list every legal variant, so the compiler (not code review) catches the missing case.

---
## Mental Models
### 1. Permits Is the Allow-List
`sealed interface Expr permits Add, Mul, Lit` — only listed types extend. `permits` + same-module rule enforced by `javac`.
### 2. Three Endgames
Each permitted subtype must be `final`, `sealed`, or `non-sealed`. `non-sealed` reopens one branch deliberately — flag it in review.
### 3. Exhaustiveness Is the Prize
`switch` over sealed needs no `default`; adding a permit breaks unhandled switches at compile time. That's the migration detector.
### 4. Domain Closure
Model closed domains (Payment, Result, AST, Event) sealed; open extension points (plugins) unsealed interfaces. Don't seal what must grow.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Fixed known variants? | Sealed + exhaustive switch |
| Third-party extension? | Non-sealed or plain interface |
| One branch special? | `non-sealed` only that leaf, document why |
| Serialization? | Include type discriminator; test new-permit path |

---
## Career Trajectory
- **L1:** Declare sealed interface + permits, handle with switch.
- **L2:** final/sealed/non-sealed judgment, record leaves.
- **L3:** Exhaustive-switch migration of legacy if-ladders, hierarchy versioning.
- **L4:** Closed-domain architecture (events, errors, protocol messages).

---
## 4-Week Path
```
W1: Sealed syntax, permits, Marshall/compact rules.
W2: Exhaustive switches; default-removal refactor.
W3: Sealed + records: expression evaluator kata.
W4: Payment/event hierarchy with versioning + unknown-type test.
```
## Success Metrics
- [ ] New permit breaks exactly the switches it should
- [ ] Zero default-on-sealed in new code
- [ ] Justify every non-sealed with a comment
