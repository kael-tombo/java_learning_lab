# VISION — Java Memory Model (JMM)

## Vision Statement
**Concurrency correctness is visibility + atomicity, not luck** — reason in
`happens-before`, publish safely, and choose `volatile`/`VarHandle`/
`java.util.concurrent` deliberately so code is right on every core count.

---

## Mental Models
### 1. Happens-Before Is the Only Guarantee
`volatile` write→read, monitor unlock→lock, thread start/join, `final` freeze.
Without an edge, another thread may see stale or half-constructed state —
forever on some hardware.
### 2. Safe Publication or Broken
Immutable (`final` fields, no `this`-escape) publishes freely; mutable needs
`volatile`/`synchronized`/concurrent-collection handoff. Double-checked
locking requires `volatile` — no exceptions.
### 3. Atomicity ≠ Visibility
`volatile` fixes visibility, not `count++` (read-modify-write). Use
`AtomicLong/LongAdder` or locks for compound actions; `LongAdder` for hot
counters.
### 4. Test with Stress, Not Luck
`jcstress` interleaves executions; single-run "works on my laptop" proves
nothing. JFR `jdk.JavaMonitorEnter` + thread dumps expose contention, not
correctness.

---

## Decision Framework
| Question | Rule |
|----------|------|
| Share a flag? | `volatile boolean`, never plain |
| Lazy singleton? | Enum or `volatile` DCL, not racy check |
| Counter? | `LongAdder` (hot) / `AtomicLong` (read-heavy) |
| Publish object? | Final-field immutable or guarded handoff |
| Prove it? | jcstress test, not 1000-loop main |

---

## Career Trajectory
- **L1:** volatile, synchronized, AtomicX, safe-publication rules.
- **L2:** DCL, immutable design, ConcurrentHashMap semantics.
- **L3:** VarHandles, jcstress suites, lock-free reasoning.
- **L4:** Concurrency standards (review gates, contention budgets).

---

## 4-Week Path
```
W1: Visibility demos (stale flag), volatile fix, final freeze.
W2: Atomicity (lost update), LongAdder vs AtomicLong bench.
W3: Safe publication + DCL + immutable value design.
W4: jcstress suite + contention-fix capstone (JFR proof).
```
## Success Metrics
- [ ] Every shared field has a documented visibility story
- [ ] jcstress test fails-before/passes-after a fix
- [ ] No `++` on shared plain longs; no this-escape
