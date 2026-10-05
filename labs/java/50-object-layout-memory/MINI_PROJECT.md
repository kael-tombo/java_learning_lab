# MINI PROJECT — Object Layout: Kill False Sharing in a Ring Counter

## Goal (2 weeks, ~8–10h)
Audit a trading-ish price engine (boxed ticks, shared counters),
prove two layout sins with JOL + JMH, and fix them for measured
throughput + allocation wins.

## Requirements
### Functional
1. JOL audit: `ClassLayout` + `GraphLayout` prints for `Tick`,
   `OrderBook`, `Stats` committed; predict-then-print table (10
   classes, prediction error column).
2. Boxed→primitive swap: `List<Integer>/Long` price path →
   `int[]/long[]` (or Eclipse/Hppc-style if justified); alloc rate
   (JFR) + footprint delta tabulated.
3. False-sharing repro: adjacent `long cursorA/cursorB` hammered by
   2 threads (JMH, scaling collapse); fix with padding
   (`@Contended` or manual 8-long pad); show 2x+ recovery.
4. Header trim: one tiny value (e.g., `Price(long micros)`) as
   value-friendly shape; test compact-headers on/off footprint note
   (`-XX:+UseCompactObjectHeaders` where available).
5. Cache-line proof: `perf`-style coherence note via JMH `-prof perfnorm`
   (cache-misses) or async-profiler proxy where perf unavailable.
6. Regression guard: footprint unit test (JOL size assert ±8B) so
   future fields cannot silently bloat the hot struct.

### Non-functional
- 12+ tests incl. footprint asserts, sharing regression (2-thread
  throughput floor), primitive-parity (same results boxed vs prim).
- Artifacts: JOL prints, JMH JSON, alloc flames before/after.
- README: byte map diagram (header/fields/padding per struct).
- Build flag note for `@Contended` (`-XX:-RestrictContended`).

## Starter Layout
```
src/main/java/com/lab50/engine/{Tick,OrderBook,Sequencer,Stats}.java
src/jmh/java/.../{SharingBench,TickBench}.java
src/test/java/.../{LayoutTest,ParityTest,SharingTest}.java  jol/*.txt
```

## Phases
### Week 1 — Measure (4–5h)
- JOL audit + boxed-path numbers + sharing repro.
- Deliverable: sin list with byte counts + collapsing JMH chart.
### Week 2 — Fix (4–5h)
- Primitive swap + padding + footprint guards.
- Deliverable: fixed engine with perf/alloc proof.

## Test Plan
- Parity: 100k-tick replay identical boxed vs primitive outputs.
- Sharing floor: fixed sequencer ≥2x broken throughput on 2 threads.
- Footprint: `Tick` ≤ target bytes (assert fails if field added).

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| JOL audit | 10 predicted + printed | Printed | Missing |
| Primitive win | Alloc + perf quantified | Swapped | Boxed kept |
| False sharing | Repro + 2x fix | Fixed | Unaddressed |
| Footprint guard | Assert + diagram | Noted | None |
| Tests | 12+ with parity/floor | 8+ | Thin |

Pass ≥ 70. Stretch: off-heap tick ring (`MemorySegment`) comparison;
Lilliput/compact-headers experiment with numbers.

## Demo Checklist
- [ ] JOL print walkthrough of one struct (header → padding)
- [ ] Live JMH: sharing collapse → padded recovery
- [ ] Alloc flame shrink after primitive swap
- [ ] Footprint test fails live when a dummy field is added

## Common Traps
`@Contended` without the unlock flag, benchmarking sharing on one
core, "fixing" cold structs while hot ones bleed.
