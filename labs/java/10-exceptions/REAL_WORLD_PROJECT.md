# REAL-WORLD PROJECT — Exceptions: Import Job Dies at Row 900k, No Clue Which Row

## Incident Scenario
Nightly import (1M rows) fails at 03:12 with `Exception in thread "main" java.lang.Exception` and rolls back everything. 6h SLA breached; no row-level context.

## Symptoms
- `catch (Exception e) {}` in row loop swallows 40k bad rows silently for weeks; final `throws Exception` loses type.
- Reader not in try-with-resources — on failure, file handle leaks; 3 nights of `Too many open files`.
- Suppressed close-failure hides real parse error in one stack.

## Investigation Tasks
1. Logs: only `java.lang.Exception: null` — no cause/row#; `grep -c "SKIPPED"` = 0 (proof swallowing).
2. FDs: `jcmd <pid> VM.native_memory` + `lsof -p` showing leaked handles; `jcmd GC.class_histogram` for buffered-reader buildup.
3. JFR: `jdk.ExceptionThrown` + `jdk.FileRead` events to locate failing offset.
4. Repro: craft 10-row adversarial file (bad date/currency/quote); run importer, observe useless message.
5. Audit: `grep -rn "catch (Exception\|printStackTrace\|throws Exception"`.

## Root Cause
Exception anti-patterns: catch-and-ignore, untyped throws, missing try-with-resources, no error taxonomy/report.

## Resolution
- Immediate: typed taxonomy + cause chains + row# in message; try-with-resources; continue-with-cap + error-report CSV; rerun from checkpoint.
- Short-term: validation layer, idempotent resume (processed-ID set), alert on error-rate > 1%.
- Long-term: batch framework (Spring Batch chunk/skip/retry) + dead-letter queue + recon dashboard.

## Runbook
```
1. Preserve log + partial output; lsof snapshot.
2. Deploy typed-error build; rerun with --resume.
3. Triage error-report.csv; fix source feed.
4. Enable skip-limit + DLQ alerts.
```

## Metrics
- Rows with actionable error 100%; handle leaks = 0 (lsof stable); partial success supported; MTTR < 1h.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- try-with-resources: https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html
- Spring Batch: https://docs.spring.io/spring-batch/reference/
