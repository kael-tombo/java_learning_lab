# REAL-WORLD PROJECT — Best Practices: Leaky Helper Takes Down Checkout

## Incident Scenario
A shared `OrderHelper` util (static mutable state, swallowed
`SQLException`, unclosed streams, `SimpleDateFormat` static field)
ships inside checkout. On a promo day it corrupts dates, leaks file
handles, and hides the real DB error — on-call sees "$0 totals" and
"Too many open files" with no stack cause.

## Symptoms
- Intermittent wrong promo dates: static `SimpleDateFormat` races →
  `2026-10-05` parses as year 0126 for ~2% of orders; totals $0.
- `Too many open files` after 6h: CSV export opens streams without
  try-with-resources; `lsof` count climbs 200/min.
- Checkout 500s with `Order failed` message only: `catch (Exception e)
  { log("failed"); }` discards cause; real unique-constraint violation
  invisible for 3h.
- Mutable `public static List<Discount> ACTIVE` mutated by two teams →
  discounts vanish mid-day; heap shows aliased list references.
- Equals missing on `Money`: `Set<Money>` dedup fails → double charges.

## Investigation Tasks
1. Threads + safety: `jcmd <pid> Thread.print` shows checkout threads
   sharing one `SimpleDateFormat`; reproduce with 8-thread parse loop.
2. FD leak: `jcmd <pid> VM.native_memory summary` + OS `lsof -p <pid>
   | wc -l` trending; `jcmd <pid> GC.heap_dump heap.hprof` — thousands
   of unclosed `FileInputStream` / `BufferedReader` (GC roots via
   static helper cache).
3. JFR: `jcmd <pid> JFR.start name=bp settings=profile
   duration=120s filename=bp.jfr`; open in JDK Mission Control —
   `jdk.JavaExceptionThrow` with swallowed causes, `jdk.FileRead`
   without close, `jdk.ThreadPark` pileups on retry storm.
4. Logs: `grep -c "Order failed" app.log` vs `grep "ConstraintViolation
   \|PSQLException" app.log` (zero — swallowed). Confirm with repro on
   staging with cause-preserving patch.
5. Heap: histogram `jhsdb jmap --histo --pid <pid> | grep -i
   "FileInputStream\|Discount"`; prove aliasing via two-reference dump.

## Root Cause
Classic Effective-Java violations at scale: mutable static state,
non-thread-safe statics, ignored exceptions, manual resource close,
missing value semantics. Each is trivial alone; combined they remove
every diagnostic signal during peak load.

## Resolution
- Immediate: static `SimpleDateFormat` → `DateTimeFormatter` (immutable,
  thread-safe); wrap export in try-with-resources; rethrow with cause
  (`new OrderRepositoryException(msg, e)`); hotfix `Money.equals/hashCode`.
- Short-term: `ACTIVE` list → `List.copyOf` + `AtomicReference` config
  reload; add ArchUnit rule "no public mutable static in domain";
  Error Prone `CatchAndPrintLog`/`SwallowedException` as ERROR.
- Long-term: helper → injected `OrderPricingService` with final fields;
  exception taxonomy doc; weekly API-review; NullAway + builder lint.

## Runbook
```
1. Freeze promo + capture: JFR 120s, heap dump, lsof count, app.log slice.
2. Deploy hotfix (DateTimeFormatter + TWR + exception chaining + Money fix) to canary 10%.
3. Verify: date-parse error rate 2% -> 0; fd growth 200/min -> flat; real DB errors visible.
4. Roll 100%; replay failed orders from queue; rebill double-charged Money set.
5. Land gates: ArchUnit no-mutable-static, Error Prone swallowed-exception ERROR, fd-count alert.
6. Postmortem 48h: violation table + owner per rule.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| Wrong-date orders | ~2% | 0% (10k sample) | Parse-property test 1M iters |
| FD growth | +200/min | flat 24h | Alert if +50/5min |
| Swallowed causes | 100% | 0 (cause chain present) | Error Prone ERROR |
| Double charges | 41/day | 0 | Money equals-contract test |
| p99 checkout | 1.9s (retries) | 0.4s | SLO burn alert |

## Prevention Checklist
- [ ] ArchUnit: no public static mutable, no `SimpleDateFormat` import
- [ ] Error Prone + SpotBugs in CI (fail on HIGH)
- [ ] Try-with-resources audit script in pre-commit
- [ ] EqualsVerifier + immutability tests required for value types

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Effective Java / Java SE docs: https://docs.oracle.com/en/java/javase/21/
- Java API documentation (Formatter, try-with-resources): https://docs.oracle.com/en/java/javase/21/docs/api/
