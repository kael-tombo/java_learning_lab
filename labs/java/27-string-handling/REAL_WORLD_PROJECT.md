# REAL-WORLD PROJECT — String Handling: Promo Blast OOM + Mojibake

## Incident Scenario
Black-Friday promo job renders 2.4M SMS messages, OOM-kills at 70% and the
survivors ship mojibake (`Ã©` for `é`) plus wrong names for Turkish users
(`I` vs `ı` casing bug). Marketing halts the blast; carrier bills for dupes.

## Symptoms
- Heap climbs linearly; Young GC every 2s, then `OutOfMemoryError: Java heap`.
- French/Spanish names show `Ã©`, `Ã±`; Turkish `İlker` lowercases wrong.
- Throughput 800 msgs/s, p99 render 45ms; retry doubles sends (no idempotency).
- Logs show `Pattern.compile` per message and `+` concat in a loop.

## Investigation Tasks
1. Heap/JFR: capture `jcmd <pid> GC.heap_dump`, start JFR
   `jcmd <pid> JFR.start filename=strings.jfr settings=profile duration=120s`.
2. Open JFR in JDK Mission Control: `jdk.ObjectAllocationInNewTLAB` —
   expect `char[]/byte[]/String` top, stack = `Template.render` loop.
3. Check events `jdk.GCHeapSummary`, `jdk.GarbageCollection`, `jdk.ThreadDump`
   (`jcmd <pid> Thread.print`) for single-threaded render bottleneck.
4. Repro: 50k-row slice locally; diff bytes with `hexdump` — confirm
   `getBytes()` platform-charset read of a UTF-8 file on windows-1252 host.
5. Regex audit: `grep -rn "Pattern.compile\|String.split" src/`; count
   compilations per render via JFR method-profiling sample.
6. Locale audit: find `toLowerCase()/toUpperCase()` without `Locale.ROOT`
   or user-locale arg; test Turkish (`tr`) names explicitly.
7. Idempotency: grep send-path for dedupe key; confirm retry re-sends.

## Root Cause
Loop `+` concatenation (O(n^2) garbage) + per-message `Pattern.compile` +
implicit-charset file read (mojibake) + locale-blind casing + no dedupe key,
compounded by single-threaded render with no backpressure.

## Resolution
- Immediate: `StringBuilder` with capacity, hoist `Pattern` to `static final`,
  read files with `Files.readString(path, UTF_8)`, locale-explicit casing,
  stop blast, add carrier-suppression list (message-id dedupe).
- Short-term: template pre-parse to segments; `String.join` for lists;
  `Normalizer` on ingest; quarantine bad rows; parallel render with
  `Files.lines` + bounded pool; golden-file tests (FR/TR/emoji).
- Long-term: streaming renderer, allocation budget in CI (JFR assert),
  charset-lint (forbid bare `getBytes`), locale matrix tests, idempotent
  send ledger.

## Runbook
```
1. Freeze job; save heap dump + JFR + bad output sample.
2. Flip to fixed build (builder + charset + hoisted pattern) on canary 5%.
3. Verify: heap flat, no Ã© in sample, TR names golden-pass.
4. Resume with dedupe ledger ON; monitor carrier callbacks.
5. Postmortem: lint rules + golden files + allocation gate.
```

## Metrics
- Heap < 1GB at 2.4M renders; throughput >= 8k msgs/s; p99 render < 5ms.
- Zero mojibake in 10k-locale sample; TR casing 100% golden-pass.
- Duplicate sends = 0 on retry; `String/char[]` allocation down >= 80%.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- String API (immutability, encoding): https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html
- Text blocks / strings tutorial: https://docs.oracle.com/javase/tutorial/java/data/strings.html
