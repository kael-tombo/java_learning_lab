# VISION — Exceptions

## Vision Statement
**Fail loudly, cleanly, and recoverably** — exceptions are control-flow for the unexpected; use them to protect invariants, never for normal branching.

---
## Mental Models
### 1. Checked vs Unchecked Divide
Checked = recoverable, caller must handle (`IOException`); unchecked = programming bug (`NPE`, `IllegalArgument`).
### 2. Resource Safety
`try-with-resources` guarantees close; suppressed exceptions preserve root cause.
### 3. Translation Layers
Catch low-level → throw domain exception with cause chain. Never swallow with empty catch.
### 4. Fail-Fast Validation
Validate public inputs with `Objects.requireNonNull` / `IllegalArgumentException` at boundary.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Normal outcome? | Return Optional/Result, not exception |
| Caller can recover? | Checked; else unchecked |
| Catching? | Handle, translate with cause, or rethrow — never empty |
| Cleanup? | try-with-resources; finally only if needed |

---
## Career Trajectory
- **L1:** try/catch/finally, throws, custom exceptions.
- **L2:** try-with-resources, chaining, validation discipline.
- **L3:** exception taxonomy, retry/idempotency design.
- **L4:** org error-handling standards, observability mapping.

---
## 4-Week Path
```
W1: Hierarchy, checked/unchecked, throws.
W2: try-with-resources, multi-catch, chaining.
W3: Custom domain exceptions, validation.
W4: File-import pipeline kata with error report + tests.
```
## Success Metrics
- [ ] Zero empty catches / printStackTrace in code
- [ ] Every resource in try-with-resources
- [ ] Exception carries actionable context + cause
