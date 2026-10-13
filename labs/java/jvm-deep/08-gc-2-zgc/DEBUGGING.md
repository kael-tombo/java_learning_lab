# Debugging: ZGC

## Separate pauses from spans first

Open `gc+phases` output and grep `Pause ... ms` with a line-end-anchored
`(\d+\.\d+)ms\s*$` pattern. Those matches are STW time (expect
hundredths of a millisecond). Everything logging seconds (`0.009s`
cycle totals) is concurrent span — including it in pause math inflates
the answer a thousandfold. Snippet 3's regex encodes this split.

## Read the reason token

Each `gc` collection line carries its trigger: `(Warmup)` (first cycle,
always), `(Allocation Rate)`, `(High Usage)`, `(Timer)`, `(System.gc)` /
`(Metadata)` / `(Clear Soft References)`. Diagnose in that order: warmup
is commissioning, rate/usage are pressure, timer is schedule, explicit
causes are callers. A warmup major is never a finding.

## Minor/major triage

Minors-only under churn is healthy young reclamation. Majors joining
means old pressure (or timer): check which `Y:`/`O:` phases dominate and
whether old occupancy climbs between cycles. Frequent majors on a
young-heavy workload point at premature promotion, not pause mechanics.

## Tag syntax trap

`-Xlog:gc+phases` works; `-Xlog:gc,phases` does not print what you want.
The `+` joins tags within one log selection; the comma separates
selections. This lab repeats lab 07's lesson because it bites once per
collector — verify the phase lines exist before analyzing their absence.

## Allocation-stall signals

When concurrent relocation loses the race, mutators stall — the closest
ZGC gets to a pause event. Stalls plus high allocation rate plus a tight
heap mean headroom exhaustion: grow the heap or slow the producer, not
pause-tune. No flag shrinks work that must happen concurrently.

## Bean-level cross-check

Confirm the running collector's identity in-process: collectors `ZGC
Minor/Major Cycles` and `ZGC Minor/Major Pauses`, pools `ZGC Young/Old
Generation`. A dashboard showing G1 pool names against a ZGC JVM is
misconfigured monitoring, not missing data.
