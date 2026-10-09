# REAL-WORLD PROJECT — Arrays & Strings: Import Outage + Mojibake

## Incident Scenario
09:40 — supplier import (80k SKUs) OOMs the pod, then names render as `Café`. Catalog frozen; search degraded.

## Symptoms
- Log: `OutOfMemoryError: Java heap space` at `report += line` in loop (O(n²) concat on 80k rows).
- `sku.split(",")` breaks on quoted `"12, inch"` → shifted columns, FK violations.
- File read with platform charset (windows-1252 vs UTF-8) → mojibake; `==` string compare misses dedupe.

## Investigation Tasks
1. Heap: `jcmd <pid> GC.heap_dump /tmp/dump.hprof` + `GC.class_histogram` — top is `char[]/String`.
2. JFR: `jdk.ObjectAllocationInNewTLAB` shows `StringBuilder`-less concat (`StringConcatHelper`) hot spot; flight recording 60s during import.
3. Logs: `grep "ArrayIndexOutOfBounds\|FK violation"`, sample 20 bad rows.
4. Encoding: `file -i supplier.csv`, hexdump accented bytes; confirm reader charset missing.
5. Repro: 5k-row slice with quotes/emoji; time concat vs Builder.

## Root Cause
Loop concatenation (quadratic + garbage), naive `split(",")` ignoring quotes, implicit-charset reader, `==` dedupe bug.

## Resolution
- Immediate: stream rows + `StringBuilder` batching; proper CSV parse (quote-aware); `InputStreamReader(UTF_8)`; `.equals` fix; raise heap only as bridge.
- Short-term: chunked import (1k batches) with skip-and-report file; charset validation gate; perf test on 100k fixture.
- Long-term: import pipeline (validation → staging table → merge) + encoding contract + OOM alert on `char[]` growth.

## Runbook
```
1. Capture heap dump + JFR before restart.
2. Quarantine bad file; restore last-good catalog snapshot.
3. Deploy streaming parser; dry-run on copy.
4. Re-import; verify row counts + sample accents.
```

## Metrics
- Import p95 < 60s for 100k rows; heap peak < 512MB; mojibake rows = 0; rejected-row report 100% actionable.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- String concatenation & Builder: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/StringBuilder.html
- Charset/UTF-8: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/charset/StandardCharsets.html
