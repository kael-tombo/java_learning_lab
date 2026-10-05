# VISION — Inheritance

## Vision Statement
**Inherit behavior deliberately, not conveniently** — `extends` is the strongest coupling in Java; use it only for true is-a substitutable relationships.

---
## Mental Models
### 1. Is-A vs Has-A
`Dog extends Animal` (is-a) vs `Car has Engine` (has-a → composition). When in doubt, compose.
### 2. Liskov Substitution
Subclass must honor superclass contract; no strengthened preconditions or weakened postconditions.
### 3. Construction Chain
`super(...)` first; fields init top-down; never call overridable methods from constructors.
### 4. Object Contract
Override `equals/hashCode/toString` together; inheritance breaks symmetry — prefer composition with forwarding.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Reuse code only? | Composition + delegation, not extends |
| Framework requires base? | Extend narrowly, seal otherwise |
| Changing semantics? | New type, not subclass |
| Need equals across hierarchy? | Avoid; use composition or final classes |

---
## Career Trajectory
- **L1:** extends/super, @Override, Object methods.
- **L2:** Liskov checks, constructor chaining, equals pitfalls.
- **L3:** template-method vs strategy, sealed hierarchies.
- **L4:** framework extension-point design.

---
## 4-Week Path
```
W1: extends, super, overriding, Object basics.
W2: Constructors, field hiding, final/sealed.
W3: equals/hashCode contract, Liskov violations.
W4: Shape/employee hierarchy refactored to composition kata.
```
## Success Metrics
- [ ] Spot Liskov violation in review in <5 min
- [ ] Implement equals/hashCode honoring symmetry
- [ ] Justify every extends with is-a argument
