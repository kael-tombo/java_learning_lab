# VISION — Polymorphism

## Vision Statement
**Write code that welcomes new types without modification** — depend on abstractions; let dynamic dispatch absorb variation.

---
## Mental Models
### 1. Static vs Dynamic Binding
Overloading = compile-time (static types); overriding = runtime (actual object). Don't confuse them.
### 2. Program to Supertype
`List<Order> orders = new ArrayList<>()` — swap implementations without callers caring.
### 3. Dispatch Table Intuition
Virtual calls ~ vtable lookup; `final`/`sealed` enable devirtualization but design clarity matters more.
### 4. Pattern Matching Bridge
`instanceof` patterns + switch dispatch replace visitor boilerplate when hierarchy is closed.

---
## Decision Framework
| Question | Rule |
|----------|------|
| if-else on type? | Polymorphic method or pattern switch |
| Need new behavior? | New class, not modified switch |
| Performance worry? | Measure; megamorphic only if profiler says so |
| Overload ambiguity? | Rename; don't rely on implicit widening |

---
## Career Trajectory
- **L1:** override correctly, use supertype refs.
- **L2:** chaining, covariant returns, instanceof patterns.
- **L3:** strategy/state patterns, dispatch-aware design.
- **L4:** plugin architectures, SPI design.

---
## 4-Week Path
```
W1: Overriding, @Override, dynamic dispatch demos.
W2: Overloading traps, instanceof patterns.
W3: Strategy/state with polymorphism.
W4: Payment-method plugin kata (add type, zero if-edits).
```
## Success Metrics
- [ ] Add new subtype without touching existing logic
- [ ] Explain overload vs override binding precisely
- [ ] Replace type-switch with polymorphism on demand
