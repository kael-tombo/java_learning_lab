# Visual Guide: Reordering

## Diagram 1: Dekker under SC (the impossible cell)

```
all SC interleavings:   Wx < Wy:  Rx sees 1  -->  (r1, r2) in {(1,0),(0,1),(1,1)}
                        Wy < Wx:  Ry sees 1  -->  same set
forbidden cell:         (0,0)  probability EXACTLY 0 under SC
observed on x86:        (0,0)  routine (up to ~79% rendezvoused)
```

One (0,0) refutes SC for the platform. The lab's job is manufacturing
enough simultaneity to watch it happen thousands of times.

## Diagram 2: the store-buffer mechanism (x86)

```
time ──────────────────────────────────────────────>
T1:  [x=1]──> |BUFFER| ..drain.. ──> cache(x=1)
     [r1=y]─────────────────────────> cache(y=0, stale)  reads 0
T2:  [y=1]──> |BUFFER| ..drain.. ──> cache(y=1)
     [r2=x]─────────────────────────> cache(x=0, stale)  reads 0
result: r1 == r2 == 0 (both loads beat both drains)
```

Symmetric buffering plus immediate loads: the cross shape guarantees
each load can miss the peer store. The 1 ns drain inserts settling
time; the picture becomes ordered without changing any box.

## Diagram 3: rendezvous vs free-running vs barrier

```
rendezvous (volatile spin):   T1 window  [====]      tight overlap ~~79%
                              T2 window  [====]
free-running:                 T1 [==]  [==]  [==]    rare overlap ~0%
                              T2   [==]  [==]  [==]
barrier-phased:               T1 [====]              smeared by trip latency
                              T2   [====]            fewer overlaps
```

Same program verdict (race) in all three rows; wildly different rates.
The handshake is the instrument — calibrate it before believing counts.

## Diagram 4: x86-TSO pair table (Sewell et al., 2010)

```
pair        x86 verdict      Dekker/message-passing relevance
LoadLoad    preserved        loads never pass loads
LoadStore   preserved        -
StoreStore  preserved        message-passing passes BY ACCIDENT
StoreLoad   FREE             Dekker fires HERE (only open gate)
```

Three locked gates, one open. Every snippet verdict in labs 02-03 is a
row lookup in this table plus the fence count.

## Diagram 5: three resolutions, three mechanisms

```
plain Dekker:        overlap + no fences   ──> (0,0) nonzero  [no edge]
volatile Dekker:     overlap + SC fences   ──> 0/20000        [ordering]
drained Dekker:      no overlap (timing)   ──> 0/20000        [NOT an edge]
locked Dekker:       no overlap (excl.)    ──> 0/20000        [exclusion]
release/acq Dekker:  overlap + pairwise    ──> 61-90%         [chains, not total]
```

Read rows, not columns: identical zeros (volatile/drain/lock) with
opposite meanings, and identical modes (chain/Dekker) with opposite
verdicts. Mechanism words, not numbers, carry the lesson.

## Diagram 6: Tomasulo in one sketch (1967, IBM 360/91)

```
issue: reservation stations fire when operands ready (out of order)
  ... execution overlaps stalls ...
commit: reorder buffer retires in program order (one thread never sees it)
  ==> across threads: shared-memory effects observable out of order
```

OoO hides latency for one thread and creates the observation problem for many.
