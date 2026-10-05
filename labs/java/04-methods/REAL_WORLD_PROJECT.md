# REAL-WORLD PROJECT — Methods: The Mutating Helper That Corrupted Carts

## Incident Scenario
11:05 — carts showing other users' items intermittently. No DB corruption; in-memory cart service suspected. Restart masks it for 1h.

## Symptoms
- `CartService.applyDiscount(items)` mutates caller's `List` (sorts + trims) due to pass-by-reference misunderstanding; shared cached list poisoned.
- Overload `discount(int)` vs `discount(double)` picks wrong one for `discount(null)`-style calls and `long` values — silent wrong-rate.
- 6-param `createOrder(...)` with two booleans swapped by one caller.

## Investigation Tasks
1. Logs: trace cart IDs cross-contaminating; `grep cartId` session fan-out.
2. Heap: `jcmd <pid> GC.class_histogram`; inspect retained `ArrayList` shared across sessions.
3. JFR: allocation + `jdk.JavaMonitorEnter` to rule out race vs aliasing; prove single-threaded mutation.
4. Repro: unit test showing caller list mutated after `applyDiscount`; overload-resolution demo with `javap -c`.
5. Call audit: `grep -rn "createOrder("` to find swapped-boolean caller.

## Root Cause
Method aliased + mutated caller's list (pass-by-value-of-reference confusion); ambiguous overloads; boolean-param API enabling swap bugs.

## Resolution
- Immediate: defensive copy + unmodifiable return in `applyDiscount`; fix swapped caller; flush poisoned cache.
- Short-term: parameter objects (`OrderRequest`), split boolean methods, `@CheckForNull`/Optional returns, overload audit.
- Long-term: immutable cart model (records + `List.copyOf`), ArchUnit "no boolean params" + purity annotations, contract tests.

## Runbook
```
1. Drain + clear cart cache; snapshot affected carts.
2. Deploy copy-on-entry fix; verify no aliasing test fails.
3. Reconcile carts; notify affected users.
4. Land API-lint gates.
```

## Metrics
- Cross-cart incidents = 0; method complexity ≤ 8; boolean params = 0 in new APIs; defensive-copy test coverage 100% on service boundary.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Passing values (pass-by-value): https://docs.oracle.com/javase/tutorial/java/javaOO/arguments.html
- Overloading: https://docs.oracle.com/javase/tutorial/java/javaOO/methods.html
