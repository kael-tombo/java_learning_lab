# VISION — Methods

## Vision Statement
**Design small, honest methods** — a method signature is a promise: clear inputs, single outcome, no surprises.

---
## Mental Models
### 1. Contract Model
Precondition → body → postcondition + exceptions. Document with `@param/@return/@throws`.
### 2. Pass-by-Value (Always)
Java copies the value (or reference). You can mutate the object, never rebind the caller's variable.
### 3. Overload Resolution
Compile-time by static types; avoid ambiguous overloads (`foo(int)` vs `foo(long)` traps).
### 4. Varargs + Recursion Cost
Varargs allocate arrays; recursion consumes stack — prefer iteration unless depth is bounded/logarithmic.

---
## Decision Framework
| Question | Rule |
|----------|------|
| >3 params? | Parameter object / builder |
| Boolean param? | Split into two methods |
| Returns null? | Return `Optional`/empty collection |
| Side effects? | Name with verb + document; prefer pure functions |

---
## Career Trajectory
- **L1:** write correct signatures, return values, basic overloads.
- **L2:** varargs, defensive copies, javadoc discipline.
- **L3:** API design, overload hygiene, recursion→iteration judgment.
- **L4:** library API stewardship, binary-compat awareness.

---
## 4-Week Path
```
W1: Signatures, return, scope, static vs instance.
W2: Overloading, varargs, pass-by-value demos.
W3: Recursion, base cases, stack traces.
W4: Utility-library kata with javadoc + unit tests.
```
## Success Metrics
- [ ] Explain pass-by-value with mutation demo
- [ ] Design overload set with zero ambiguity
- [ ] All public methods documented + tested
