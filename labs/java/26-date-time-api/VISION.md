# VISION — Date & Time API

## Vision Statement
**Time is data with rules** — `java.time` makes zones, DST gaps, and formats explicit so scheduling math stops being string math.

---
## Mental Models
### 1. Instant vs Local vs Zoned
`Instant` = machine timestamp (UTC); `LocalDate(Time)` = wall-clock without zone (never schedule with it); `ZonedDateTime` = wall + zone rules. Store Instant, display zoned.
### 2. Immutable + Fluent
All types immutable; `plusDays/withHour` return new. `Period` (date-based) vs `Duration` (time-based) — mixing them breaks DST math.
### 3. Gaps and Overlaps Are Real
Spring-forward gap (02:30 doesn't exist), fall-back overlap (01:30 twice). `ZonedDateTime` resolves via rules; `LocalDateTime` silently pretends.
### 4. Format at the Edge
`DateTimeFormatter` thread-safe (unlike `SimpleDateFormat`); parse/format only at I/O, keep domain as typed objects. Always persist ISO-8601 with offset.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Timestamp event? | Instant (UTC) |
| User-visible meeting? | ZonedDateTime + ZoneId |
| Birthday/no-zone? | LocalDate only, never convert silently |
| Recurring math? | Period for days, Duration for hours |

---
## Career Trajectory
- **L1:** LocalDate/Instant basics, ISO parse/format, plus/minus.
- **L2:** ZonedDateTime, ZoneId, DST gap/overlap handling.
- **L3:** Scheduling (cron + zone), JDBC `OffsetDateTime` mapping, clock injection for tests.
- **L4:** Multi-region scheduling architecture, ticketing/calendar correctness audits.

---
## 4-Week Path
```
W1: Local/Instant/Duration/Period; formatter thread-safety demo.
W2: Zones, gaps/overlaps lab (America/New_York spring/fall).
W3: Scheduler kata: daily 09:00 local across zones + Clock tests.
W4: Booking API: store Instant, render zoned, DST regression suite.
```
## Success Metrics
- [ ] Explain gap vs overlap with a concrete 2026 date
- [ ] Zero SimpleDateFormat/Calendar in new code
- [ ] DST test suite green for 2 zones
