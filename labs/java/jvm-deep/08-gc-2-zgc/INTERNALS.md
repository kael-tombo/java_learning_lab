# Internals: ZGC

## What the color bits encode

Mark states (marked/unmarked generations), a remapped flag, and
forwarding view per reference. The barrier compares a loaded reference's
color against the collector's current global phase: mismatch means the
reference predates the latest relocation and must heal before use.

## Barrier fast and slow paths

Fast path: two or three instructions testing color bits inline on every
load — the single-digit-percent throughput cost on allocation-heavy
workloads. Slow path: trap, locate the forwarding entry, install the
remapped reference, resume. Slow executions are rare in steady state
because most references heal once and stay current until the next cycle.

## Pause anatomy from gc+phases

Three STW lines per cycle: mark-start handshake, mark-end, relocate-start.
Roots scan inside these microsecond windows; graph marking and object
copying run concurrently between them. Lowercase `y:` prefixes mark
young-only minor work; `Y:`/`O:` prefixes mark the young/old phases of a
major. Any analysis that treats the cycle-total seconds figure as pause
time misunderstands the design by three orders of magnitude.

## Minor versus major routing

Minors evacuate young only — most reclamation happens here and old-gen
barriers stay quiet. Majors handle old (with young participating), driven
by old pressure, warmup, timer, or explicit causes (`System.gc`,
`Metadata`, `Clear Soft References`). Reason tokens in parentheses on the
`gc` lines name the trigger per cycle; read them before theorizing.

## Flags that matter

`ZGenerational=true` default selects the young/old split. `ZCollectionInterval`
(default 0.0, off) plus `ZCollectionIntervalMajor/Minor/Only` schedule
pressure-independent majors. `ZFragmentationLimit=5 (%)` tunes relocation
eagerness against fragmentation. All values read off `PrintFlagsFinal`
with `+UseZGC` on the command line — without the opt-in the flags still
print but describe an unselected collector.

## MXBean split

Cycles beans account concurrent work; Pauses beans account STW
handshakes. That separation is the correct observability mirror of the
architecture: dashboard the Pauses beans for latency, the Cycles beans
for reclamation rate, and never sum them into one number.
