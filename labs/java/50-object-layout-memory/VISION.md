# VISION — Object Layout & Memory Internals (JOL)

## Vision Statement
**Every field has an address and a cost** — headers, alignment, and
false sharing decide cache behavior: measure with JOL, prove with
perf, and stop guessing why "same data" runs 3x slower.

---
## Mental Models
### 1. Object = Header + Fields + Padding
12–16B header (mark + klass) + aligned fields + tail padding.
`CompactObjectHeaders`/`UseCompressedOops` shift the math.
### 2. Layout Order Is Policy
Field order + `@Contended` + class hierarchy change footprint and
sharing. JOL (`ClassLayout.parseInstance`) is ground truth.
### 3. Cache Lines Are 64B Truth
Two hot fields on one line → false sharing → coherence ping-pong.
Padding/striping (`LongAdder`, `@Contended`) buys lines.
### 4. Arrays/Collections Multiply
Header + length + elements + boxing: `List<Integer>` vs `int[]`
is 4–8x. Footprint math precedes any "optimize later".

---
## Decision Framework
| Question | Rule |
|----------|------|
| Footprint unknown? | JOL print first, estimate never |
| Hot counter contended? | Pad/stripe; verify with perf counters |
| Big in-memory index? | Primitive arrays/off-heap, not boxed lists |
| Header-heavy small objs? | Compact headers, fewer tiny objects |

---
## Career Trajectory
- **L1:** JOL prints, header/field/padding reading.
- **L2:** CompressedOops/compact headers, array vs boxed math.
- **L3:** False-sharing diagnosis (perf/JMH), @Contended use.
- **L4:** Cache-conscious data design for hot paths fleet-wide.

---
## 4-Week Path
```
W1: JOL kata — 10 classes, predict-then-print footprint.
W2: Boxing/array audit of one service; primitive-swap win.
W3: False-sharing repro (JMH) + padded/striped fix.
W4: Hot-path struct redesign with footprint + perf proof.
```
## Success Metrics
- [ ] Predict layout within 8B before JOL print (8/10)
- [ ] One boxed→primitive swap with alloc + perf delta
- [ ] False-sharing repro fixed 2x+ (measured, not claimed)
- [ ] Hot struct footprint cut with no behavior change

## What This Is Not
Bit-twiddling for sport. It is cache economics on hot data.

> Mantra: **JOL first, pad hot, box never on hot paths.**
