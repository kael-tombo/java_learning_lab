# REAL-WORLD PROJECT — I/O & NIO: Import Job Leaks FDs and OOMs

## Incident Scenario
Nightly CSV import (2M rows) dies at 3 AM with `Too many open files`, and on retry with raised ulimit it OOMs instead. Morning backlog blocks billing.

## Symptoms
- `new BufferedReader(...)` per chunk never closed (exception path skips `close`) → FD count climbs to 65k; `lsof | wc -l` confirms.
- Retry reads whole file with `Files.readAllLines` → 2M strings + split arrays spike heap to 6GB.
- Default-charset parse corrupts `café` → `caf�` on one node (different `file.encoding`); checksums mismatch downstream.
- Partial write: crash mid-write leaves half `billing.csv`; next job appends → duplicate billing.

## Investigation Tasks
1. FDs: `ls /proc/<pid>/fd | wc -l` trend; `lsof -p <pid> | head`; `jcmd <pid> VM.info` for handle growth.
2. Heap/JFR: `jcmd <pid> GC.heap_dump`; JFR `jdk.GCHeapSummary` + `jdk.FileRead/FileWrite` events — `String[]/char[]` dominance.
3. Logs: `grep "Too many open files\|OutOfMemory\|MalformedInput" import.log`; diff node charsets (`java -XshowSettings:properties | grep file.encoding`).
4. Repro: 100k-row slice with old code — FD leak in 20 iterations; full-slurp heap spike measured.
5. Output: `ls -l billing.csv*`; show half-written file without atomic rename.

## Root Cause
Unclosed readers on exception paths, unbounded full-file slurp, platform-default charset, non-atomic in-place overwrite.

## Resolution
- Immediate: try-with-resources everywhere, `Files.lines` streaming + batch commits (1k rows), explicit `UTF_8`, temp-then-`ATOMIC_MOVE` output.
- Short-term: FD/heap alerts, row-cap + truncation guard, charset ArchUnit-style check (no `new String(bytes)` without charset).
- Long-term: chunked resumable import (offset checkpoint), mmap for huge sorts, JFR file-I/O tracing in CI perf gate.

## Runbook
```
1. Capture lsof + heap dump + JFR before kill.
2. Roll streaming/close/charset hotfix to one node.
3. Replay 100k slice; verify FD flat + heap < 1GB.
4. Atomic-write + rerun full import; diff row counts vs source.
5. Land FD/heap monitors + checklist.
```

## Metrics
- FD steady < 200 through full 2M import; heap p99 < 1GB; charset errors = 0; partial-file incidents = 0; import p95 within window.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- java.nio.file API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/package-summary.html
- File I/O tutorial: https://docs.oracle.com/javase/tutorial/essential/io/file.html
