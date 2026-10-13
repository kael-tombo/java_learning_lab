# Visual Guide: Memory Barriers

## Diagram 1: the 2x2 taxonomy (the whole lab on one card)

```
              later LOAD            later STORE
earlier LOAD  LoadLoad ──┐          LoadStore ──┐
                         ├─ ACQUIRE (after)     ├─ both halves
earlier STORE StoreLoad ─┘ (SC extra, after)   StoreStore ─┘─ RELEASE (before)
                                            + StoreLoad after each volatile store = SC
```

Acquire pins successors; release pins predecessors; SC pins the diagonal too.

## Diagram 2: the ladder (x86 measured shape)

```
ns/op   1        2        5        10        18
plain store    [##]  ~1.0-1.2
release store  [###] ~1.3-1.4  (rock-stable, compiler barrier only)
volatile read  [###] ~1.0-1.4  (acquire nearly free on TSO)
volatile store [####################] ~10-18 (XCHG StoreLoad fence)
shape: plain <= release < volatile (writes); reads ~= parity
```

Heights vary by box; the shape (0/0/1 fence counts) does not. Read the
shape across machines, the heights only within one JVM.

## Diagram 3: roach motel (movement map)

```
BEFORE region        SYNC POINT          AFTER region
plain ops ......... drift DOWN past .... acquire (in from above: allowed)
                    successors PINNED (escape above: FORBIDDEN)
predecessors PINNED (sink below: FORBIDDEN)
                    ......... drift UP past ..... release (in from below: allowed)
result: motel admits from both sides, releases nothing early
publication (data->flag release): SAFE   |   post-hoc observation: UNORDERED
```

Draw every handoff on this map: writes above the release line,
reads below the acquire line, nothing straddling.

## Diagram 4: the accident (snippet 4 anatomy)

```
writer (plain):   data = 42 ──SS??──> flag = true     (SS kept by TSO luck)
reader (plain):   spin flag ──??───> read data         (hoisting legal, unused today)
coherence:        values delivered                     (0/2000 today)
JMM verdict:      RACE (no edge)                        (red on ARM, red after hoist)
conversion:       volatile flag ──SS+SC──> ordered      (same 0/2000, verdict green)
```

Three layers (hardware luck, compiler restraint, model verdict) in one
picture — output, mechanism, and guarantee disagreeing by design.

## Diagram 5: chains vs net (snippet 5 anatomy)

```
release/acquire:   Wx ═pair1═> Ry      Wy ═pair2═> Rx     CROSS: unconstrained ──> 61-90%
volatile (SC):     Wx ═══ both ═══> Ry  Wy ═══ both ═══> Rx  CROSS: StoreLoad-fenced ──> 0
lock:              [Wx; Ry] EXCLUDE [Wy; Rx]              NO OVERLAP ──> 0 (exclusion)
```

Ropes hold pairs; nets hold systems; helicopters skip the climb. Match
gear to terrain: message-passing traverses one rope (50000 intact),
Dekker crosses the crevasse (only nets or helicopters).

## Diagram 6: mode lattice (price vs promise)

```
mode:      plain    opaque    release/acq    volatile      lock
atomic:      N        Y          Y              Y            Y
ordered:     never    never      pairs          total        serialized
x86 price:   ~1 ns    ~1 ns      ~1.3 ns        ~10 wr       tens of ns
use:         scratch  stats      pipelines      flags/DCL    exclusion
rule:        never cross threads unordered | chains for handoff | SC/lock for systems
```

Climb deliberately, one rung per shape analysis.
