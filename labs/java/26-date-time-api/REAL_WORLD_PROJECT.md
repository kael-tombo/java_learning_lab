# REAL-WORLD PROJECT — Date & Time: DST Deletes 200 Standups

## Incident Scenario
After spring-forward, 200 recurring standups vanish for a week and EU/US joint meetings show an hour off. A shared `SimpleDateFormat` also starts printing year 2025 under load.

## Symptoms
- Recurrence adds `Duration.ofHours(24)` to `ZonedDateTime` → skips the gap day (meeting lands 10:00 instead of 09:00, then filter drops it as "outside window").
- Meetings stored as `LocalDateTime` (no zone) → rendering in another zone shifts by offset;overlap day creates double-booked 01:30.
- Static `SimpleDateFormat` shared across request threads → corrupted parses under contention (JFR shows same instance on N threads).
- `System.currentTimeMillis()` in scheduler makes DST regression untestable — tests pass/fail by run date.

## Investigation Tasks
1. Data: dump 5 missing bookings (stored local vs Instant); convert and show gap-day shift.
2. JFR/threads: `jcmd <pid> Thread.print` — N threads inside `SimpleDateFormat.parse` (not thread-safe); JFR `jdk.ExecutionSample` confirms shared instance.
3. Logs: `grep "outside window\|ParseException.*2025" scheduler.log`; histogram of off-by-one-hour meetings by zone.
4. Repro: 09:00 × 5 days over 2026-03-08 America/New_York with +24h vs `Period.ofDays(1)` — show divergence; formatter race with 20 threads.
5. Config: `ZoneId.systemDefault()` per node differs (US vs EU) → same Instant renders differently in two DCs.

## Root Cause
Duration-for-date recurrence across DST, zone-less storage, shared non-thread-safe formatter, wall-clock calls untestable, heterogeneous node default zones.

## Resolution
- Immediate: recurrence with `Period` on `ZonedDateTime` (or local-date + zone re-resolve), backfill gap-week schedule, `DateTimeFormatter` static-safe swap, pin `ZoneId` per booking + UTC node default.
- Short-term: DST regression suite (both transitions, 2 zones), formatter ban lint, `Clock` injection mandate.
- Long-term: scheduling service with zone rules versioning (tzdata update runbook), booking audit (stored Instant + zone + resolution flag).

## Runbook
```
1. Dump bookings + node zones + JFR 60s.
2. Deploy Period-recurrence + formatter + pinned-zone hotfix.
3. Regenerate gap-week instances; notify owners.
4. Verify dual-zone render matrix exact.
5. Land DST suite + formatter/clock lints.
```

## Metrics
- Missing-instance = 0 over next transition; cross-zone offset errors = 0; formatter corruption = 0 over 100k-race; scheduler tests deterministic (fixed-clock).

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- java.time API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/package-summary.html
- Date-Time tutorial: https://docs.oracle.com/javase/tutorial/datetime/
