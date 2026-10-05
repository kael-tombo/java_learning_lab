# MINI PROJECT — Date & Time: Multi-Zone Booking API

## Goal (2 weeks, ~8–10h)
Build a booking service that stores UTC, renders zoned, survives DST gaps/overlaps, and proves formatter thread-safety — with Clock-injected tests.

## Requirements
### Functional
1. `Booking(id, title, Instant start, Duration len, ZoneId zone)`; create from `ZonedDateTime` input (gap → shifted-forward with warning, overlap → earlier offset + flag).
2. Daily recurrence: 09:00 local × 10 days across `America/New_York` + `Europe/Berlin` spring-2026 DST boundary — list shows correct UTC shifts, not naive +24h.
3. `Clock` injection everywhere (`Clock.systemUTC()` prod, fixed in tests); no `now()`/`System.currentTimeMillis` in domain.
4. `DateTimeFormatter` (immutable, thread-safe) for ISO + user patterns; legacy `SimpleDateFormat` race demo (10 threads, wrong years) vs safe formatter.
5. CLI/REST-lite: create, list-by-day (zoned), export ISO-8601 with offset.
### Non-functional
- Persistence as ISO Instant strings (no local-time storage); JDBC-style mapping note if DB used.
- 16+ tests: gap shift, overlap disambiguation, recurrence across DST, formatter race, Clock determinism, invalid-zone error.
- README: Instant/Local/Zoned decision table + DST screenshots/table of the 2 transition days.
- Load: 10-thread format/parse soak, zero corruption.

## Phases
### Week 1 — Core (4–5h)
- Booking model, gap/overlap rules, Clock tests.
- Deliverable: DST fixture suite green.
### Week 2 — Recur + Prove (4–5h)
- Recurrence, formatter race demo, CLI/export.
- Deliverable: cross-zone schedule + race report.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Type choices | Instant/Zoned/Local exact | Correct | Local for instants |
| DST | Gap+overlap handled+tested | Handled | Ignored |
| Clock | Injected, deterministic | Used | now() in domain |
| Formatter | Thread-safe + race demo | Safe used | SimpleDateFormat kept |
| Tests | 16+ incl. DST pair | 10+ | No zone tests |

Pass ≥ 70. Stretch: iCal-ish RRULE subset; overlap-resolution policy config (earlier/later) with test matrix.
