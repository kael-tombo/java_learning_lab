# REAL-WORLD PROJECT — Generics: ClassCastException at 2 AM After "Harmless" Refactor

## Incident Scenario
Deploy adds `List` caching layer with raw types. 02:00 — checkout throws `ClassCastException: Integer cannot be cast to String` on 5% of requests.

## Symptoms
- `Map cache = new HashMap()` (raw) stores `Integer` promo IDs and `String` SKUs under same prefix; reader casts blindly.
- `String[] arr = (String[]) list.toArray()` crashes; `instanceof T` hack added then fails post-erasure.
- `-Xlint` shows 43 unchecked warnings ignored for months.

## Investigation Tasks
1. Logs: `grep ClassCastException` + cache-key prefix distribution.
2. Heap: `jcmd GC.class_histogram`; dump cache map — mixed value types under one namespace.
3. JFR: allocation of `Integer` vs `String` in cache-put path; exception events pinpoint reader line.
4. Repro: minimal raw-map put/get test demonstrating heap pollution.
5. Lint: `javac -Xlint:all` count; `grep -rn "List [a-z]\|Map [a-z]"` raw-type scan.

## Root Cause
Raw types + heap pollution + erasure misunderstanding (`toArray` wrong overload); unchecked warnings normalized.

## Resolution
- Immediate: namespace keys (`promo:` vs `sku:`), `toArray(new String[0])`, typed `Cache<K,V>` wrapper; flush poisoned entries.
- Short-term: generic `Cache<V>` with `Class<V>` token + `get(key, type)`; `-Werror -Xlint:all` gate; PECS-correct utils.
- Long-term: typed cache library (Caffeine with generics) + ArchUnit "no raw types" + generics kata for team.

## Runbook
```
1. Flush cache shard; pin to previous build if needed.
2. Ship typed wrapper + key namespacing.
3. Canary with exception-rate watch.
4. Enable lint-as-error gate.
```

## Metrics
- ClassCast = 0 for 14d; unchecked warnings = 0; cache-hit rate restored ±1%; raw-type occurrences = 0.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Generics/erasure: https://docs.oracle.com/javase/tutorial/java/generics/erasure.html
- Wildcards/PECS: https://docs.oracle.com/javase/tutorial/java/generics/wildcards.html
