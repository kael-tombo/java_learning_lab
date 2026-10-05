# REAL-WORLD PROJECT — Collections: Catalog Crawls + Phantom Products

## Incident Scenario
After catalog hits 500k SKUs, search p99 4.2s and "ghost" products appear/disappear randomly. Two incidents, one root theme: wrong collection + broken contract.

## Symptoms
- Lookup uses `ArrayList.contains` scan (O(n)) in hot path; `LinkedList.get(i)` pagination O(n²).
- `Product.equals` uses `name` but `hashCode` uses `sku` → HashMap loses 3% of entries; `TreeSet` with inconsistent `compareTo` drops "duplicates" that aren't equal.
- `HashMap` shared across threads → infinite loop on resize (legacy JDK path) / lost updates; iterator `remove` during loop throws CME.

## Investigation Tasks
1. Profiling: JFR `jdk.MethodProfiling` + `jdk.ObjectAllocationInNewTLAB`; `jcmd Thread.print` for hot `contains/get` stacks.
2. Heap: `GC.class_histogram` — `Product`/`Node` bloat; dump + histogram by retained size.
3. Correctness: write contract test (equals/hashCode/compareTo) — fails immediately; count lost keys via full-scan vs map-get diff.
4. Concurrency: `grep -rn "new HashMap.*static\|shared"`; reproduce lost update with 8-thread put test.
5. Logs: CME stack clustering by endpoint.

## Root Cause
O(n) structures in hot path + violated equals/hashCode/compareTo contracts + unsynchronized shared HashMap + in-loop mutation.

## Resolution
- Immediate: `HashMap`→`ConcurrentHashMap` (or guarded), fix contracts (sku-based), `TreeSet` comparator consistent with equals; add index map for search.
- Short-term: collection-choice review (ArrayList vs TreeMap vs Hash), unmodifiable exposure, CME-proof iteration (iterator.remove/collect-then-remove).
- Long-term: catalog search index (exact + full-text), load/perf tests at 1M SKUs, EqualsVerifier-style contract tests in CI.

## Runbook
```
1. Capture JFR + heap histogram before restart.
2. Deploy contract fix + concurrent map.
3. Reindex; verify key-count parity.
4. Load-test p99 gate.
```

## Metrics
- Search p99 < 200ms; lost-key diff = 0; CME = 0; contract tests green; 1M-SKU load pass.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Collections framework: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Map.html
- ConcurrentHashMap: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html
