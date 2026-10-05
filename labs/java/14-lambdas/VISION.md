# VISION — Lambdas

## Vision Statement
**Behavior as data** — lambdas let you pass intent (what to do) instead of building ceremony classes; every callback, filter, and handler becomes one line.

---
## Mental Models
### 1. SAM: One Method, Many Shapes
A lambda is an anonymous implementation of a `@FunctionalInterface`. Target type drives the signature — same `->` adapts to `Predicate`, `Function`, `Comparator`.
### 2. Capture Is Read-Only
Lambdas capture *effectively final* locals by value (copy), not by reference. Mutating the outer variable afterwards breaks compilation by design.
### 3. invokedynamic, Not Anonymous Classes
`javac` emits `invokedynamic + LambdaMetafactory`, not a `$1.class` per lambda. First call links a hidden class; later calls are cheap. Startup cost once, steady-state fast.
### 4. Method Refs Are Named Lambdas
`String::length`, `this::validate`, `Order::new` — prefer refs when the lambda only forwards. Clearer stack traces, easier reuse.

---
## Decision Framework
| Question | Rule |
|----------|------|
| One-off behavior? | Lambda inline |
| Reused/named/tested? | Method ref or static method |
| Needs state/multiple methods? | Real class, not lambda |
| Checked exception inside? | Wrap in unchecked or use sneaky `ThrowingFunction` adapter |

---
## Career Trajectory
- **L1:** `Predicate/Function/Consumer/Supplier`, `forEach`, `sort` with comparator lambda.
- **L2:** Custom `@FunctionalInterface`, method refs, exception-wrapping utilities.
- **L3:** Capture/heap semantics, `invokedynamic` cost, serialization hazards (`SerializedLambda`).
- **L4:** API design with function composition (`andThen/compose`), allocation-free hot paths.

---
## 4-Week Path
```
W1: Syntax (no-paren/single/multi), target typing, effectively-final.
W2: java.util.function zoo + composition; method refs (static/bound/unbound/ctor).
W3: Checked-exception adapters, comparator chaining, debugging lambdas.
W4: Event-router kata: replace 12 anonymous classes with lambdas + refs.
```
## Success Metrics
- [ ] Convert any anonymous SAM class to lambda/ref in < 2 min
- [ ] Explain capture-by-value and why mutation fails
- [ ] Zero lambdas with side effects in stream pipelines
