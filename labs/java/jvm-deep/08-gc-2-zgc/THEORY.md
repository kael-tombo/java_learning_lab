# ZGC — Theoretical Foundation

## Core Concept

ZGC trades throughput for *pause predictability*: nearly all GC work
(marking, relocation) runs concurrently with the application, leaving only
sub-millisecond stop-the-world pauses (measured here: 0.010–0.026 ms).
The mechanisms: **colored pointers** (GC metadata in reference bits),
**load barriers** (every reference load checks color), and — since the
generational design — young/old separation so short-lived garbage rarely
touches the old generation at all.

## Colored Pointers + Load Barriers (the stable core)

Each object reference carries color bits (mark states, remapped flag). On
*every* reference load, a barrier checks the color: a "bad" (stale-view)
color traps into a slow path that heals the reference (remaps/forwards it)
before the application proceeds. Consequences:

- Relocation needs no stop-the-world: movers copy objects concurrently;
  stragglers self-heal on next load. The GC never has to find all
  references at once.
- The barrier costs a few instructions per load (always on — ZGC's
  throughput tax, typically single-digit percent vs G1 on allocation-heavy
  workloads).
- No generational write-barrier complexity for *correctness* of young
  collection... the generational design adds store barriers for old→young
  remembered tracking, but healing still flows through loads.

## Generational ZGC (default on JDK 23 — measured `ZGenerational=true`)

Single-generation ZGC collected the whole heap every cycle. Generational
mode splits young (Eden/Survivor-aged) and old:

- **Minor collections** (`Minor Collection (High Usage)`,
  `(Allocation Rate)`, `(Timer)`) evacuate the young generation only —
  most reclamation happens here, still concurrent with microsecond pauses.
- **Major collections** (warmup at startup, then on old-gen pressure)
  handle the old generation; young participates (`Y: ... (Major)` lines
  interleave with `O:` lines in the phase log).
- The MXBean surface reflects the split: collectors `ZGC Minor/Major
  Cycles` + `ZGC Minor/Major Pauses`, pools `ZGC Young/Old Generation`
  (all four + both verified in this lab).

JEP trail (verified): experimental in 11 (JEP 333), production in 15 (JEP
377), generational in 21 (JEP 439). `-XX:-ZGenerational` restores
single-generation mode; generational is the default on the measured JDK 23.

## The Pause Anatomy (from measured `gc+phases` logs)

```
GC(1) y: Pause Mark Start 0.012ms
GC(1) y: Pause Mark End   0.010ms
GC(1) y: Pause Relocate Start 0.012ms
```

Three STW beats per cycle (mark-start handshake, mark-end, relocate-start);
everything between them — graph marking, object copying — is concurrent.
Lowercase `y` = young-only work; uppercase `Y`/`O` = young/old phases of a
major. Roots are scanned in the microsecond pauses; the heap is walked
concurrently. If a workload can't tolerate even ~50 µs stalls, no HotSpot
collector qualifies — but ZGC is the closest production option.

## Collection Triggers

| Trigger (log reason) | Meaning |
|---|---|
| `(Warmup)` | startup major (always the first cycle) |
| `(Allocation Rate)` | allocation pace predicts exhaustion |
| `(High Usage)` | occupancy crossed the high-water mark |
| `(Timer)` | `ZCollectionInterval` seconds elapsed (default 0 = off) |
| `(System.gc)` / `(Metadata)` / `(Clear Soft References)` | explicit/special causes |

`ZCollectionInterval` (default 0.0 = disabled) schedules periodic majors
independent of allocation — the only way an *idle* JVM collects (verified:
0.1 s interval produced majors every ~120 ms with zero allocation). Idle
heap hygiene for latency-sensitive services that can't wait for pressure.

## ZGC vs G1 vs Shenandoah (one paragraph each)

- **G1** (lab 07): region evacuations in STW young pauses (milliseconds);
  best throughput-per-pause among the three for moderate heaps; pauses grow
  with live-set size.
- **ZGC**: pauses decoupled from heap size (barriers + concurrency cost
  throughput instead); sub-millisecond typical; heap sizes into terabytes
  viable; needs headroom (concurrent relocation must outrun allocation —
  sustained allocation past the concurrent budget triggers allocation
  stalls, the one big pause-equivalent).
- **Shenandoah** (lab 09): also concurrent evacuation (Brooks pointers
  instead of colored pointers); different barrier placement (write-heavy
  vs ZGC's load-heavy); historically lower throughput tax on some shapes,
  higher on others — measure your allocation profile, don't generalize.

## Key Flags (measured, JDK 23)

| Flag | Default | Meaning |
|---|---|---|
| `UseZGC` | off (command line on) | select the collector |
| `ZGenerational` | true | generational mode |
| `ZCollectionInterval` | 0.0 (off) | periodic-major timer, seconds |
| `ZCollectionIntervalMajor/Minor/Only` | -1/-1/false | per-generation timer tuning |
| `ZFragmentationLimit` | 5 (%) | relocation eagerness vs fragmentation |

## Key Invariants

1. Every reference load passes the color check; healing is per-load and
   needs no rendezvous.
2. STW pauses are handshakes (mark/relocate boundaries), never heap walks.
3. Minors collect young only; majors coordinate young + old phases.
4. Timer/off-pressure triggers exist independent of allocation (`(Timer)`).
5. Throughput tax (barriers + concurrency) is the price of size-independent
   pauses — chosen per workload, not assumed.
