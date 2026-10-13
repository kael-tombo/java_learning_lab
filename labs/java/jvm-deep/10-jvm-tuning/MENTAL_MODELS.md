# Mental Models: JVM Tuning

## 1. Ergonomics as a tailor's tape

The JVM measures you on arrival (RAM, cores, cgroup limits) and cuts a
default suit: heap RAM/4, young a third, workers by core count. Off the
rack fits most; `-Xmx` is made-to-measure. Never quote another body's
measurements — re-run the tape (`PrintFlagsFinal`) per deployment.

## 2. TLABs as personal notebooks

Eden is a shared whiteboard with one marker (the allocation top) — every
writer queues. A TLAB tears off a personal notebook page per thread: most
writing happens privately, and only page refills queue at the board. The
~8x gap is queuing theory, not silicon speed.

## 3. Compressed oops as zip codes

Full 64-bit addresses are street addresses; compressed oops are zip codes
plus a known city (heap base) and block size (shift). Mail sorts faster
and envelopes shrink — until the city outgrows the zip system (~32 GB)
and full addresses return. Size just under the boundary or far above it,
never straddling by accident.

## 4. Three planes as three budgets

Heap, code cache, and Metaspace are rent, equipment, and payroll —
separate budgets, separate overruns, separate fixes. A payroll blowout
(classloader leak) never resolves by raising the rent (`-Xmx`). Graph all
three; fund each from its own evidence.

## 5. One-flag experiments as clinical trials

One variable, treatment versus control, pre-registered endpoint (pause
count, pause ms, throughput). Two flags is polypharmacy — recovery proves
nothing about which drug worked. The ParallelGC heap-size pair (128m vs
512m, everything else identical) is the double-blind miniature.

## 6. G1 adaptivity as cruise control

Fixed collectors (Parallel) are manual throttle: heap size directly sets
Eden and pause cadence. G1 is cruise control: it re-aims young sizing at
the pause target as conditions change, absorbing your heap lever. Test on
manual first to learn the lever, then on cruise to learn the absorption.
