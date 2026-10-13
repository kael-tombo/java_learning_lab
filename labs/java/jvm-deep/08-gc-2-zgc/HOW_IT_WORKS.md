# How It Works: ZGC

The JVM starts with `-XX:+UseZGC -Xmx128m`. Before the application does
anything, a warmup major fires (`Major Collection (Warmup)`): heap
sizing, metadata, initial marking commissioning. This first cycle is
routine on every run, not a pressure signal.

Allocation churn begins. Minor collections track it with parenthesized
reasons: `(Allocation Rate)` when pace predicts exhaustion, `(High
Usage)` past the occupancy watermark. Each cycle opens with `Pause Mark
Start` (~0.012 ms measured): all threads handshake, roots scan, marking
begins. Application threads resume while concurrent marking walks the
young graph.

`Pause Mark End` (~0.010 ms) closes marking; `Pause Relocate Start`
(~0.012 ms) opens relocation. Movers copy live young objects concurrently
while the application keeps loading through barriers — stale references
heal one load at a time, so no thread ever waits for a global fix-up.

The cycle's concurrent span logs as a seconds-scale total (`0.009s`
style); the three `Pause ... ms` lines are the only STW time, each tens
of microseconds. Old-generation pressure eventually schedules a major,
whose log interleaves `Y:` young lines with `O:` old lines as both
generations coordinate.

An idle JVM with the default interval does nothing — `ZCollectionInterval
= 0` means off. Set it to 0.1 and majors fire every ~120 ms with zero
allocation (`Major Collection (Timer)`), because the timer path ignores
pressure entirely. That is the heap-hygiene mode for services that idle
between latency-critical bursts and cannot afford stale garbage in the
next request.

Occupancy deltas (`M(...)` figures) on the collection lines track
reclamation independently of pauses: heap used before and after each
cycle. Read deltas for "did it free," reasons for "why it ran," and
phase lines for "what it cost" — three questions, three log fields, no
substitutions between them.
