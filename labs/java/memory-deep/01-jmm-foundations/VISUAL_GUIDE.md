# Visual Guide: JMM Foundations

## Diagram 1: the three-link chain (every demo)

```
WRITES (program order)      RELEASE             ACQUIRE            READS (program order)
  w1, w2, ... wn ──po──> R ═════ hb ═════> Q ──po──> d1, d2, ... dm
                         ^                  ^
                    one action         one action
                    both sides agree on (start / unlock / volatile write /
                                         countDown ...)
```

Verdict follows from transitivity: wn hb d1. Remove any arrow and no
constraint reaches the reads — that is a race by definition.

## Diagram 2: StartEdge (1499500)

```
main: [v0]=1 [v1]=4 ... [v999]=2998 ──po──> t.start() ═hb═> child first action ──po──> sum all ──> 1499500
                                                ^
                                          single rendezvous
```

All 1000 stores sit left of the rendezvous; all loads sit right. The
child cannot observe a prefix — the edge delivers the set.

## Diagram 3: LockEdge (2000000 as a chain)

```
T_a: lock [count++] unlock ═hb═> T_b: lock [count++] unlock ═hb═> T_c: ... (2M links)
      exclusion: bodies never overlap        visibility: each sees all prior
```

Read it two ways: horizontally as mutual exclusion (one body at a
time), vertically as visibility (each unlock publishes to the next
lock). Either property alone would be insufficient; the monitor gives
both, which is why the total is exact.

## Diagram 4: DRF implies SC (the transcript)

```
racy execution:        ? order ?  (no transcript: stale, reordered, any)
        + edges (race-free)
sequential execution:  T1 ─ T2 ─ T1 ─ T2 ... (ONE total order explains all reads)
```

Debugging with edges means finding the row in the transcript; debugging
without them means arguing with no transcript. The guarantee converts
hardware reasoning into interleaving reasoning.

## Diagram 5: causality floor (values vs order)

```
written:   0  1  2  3 ... 100000        (closed set: reads stay inside)
observed:  5  5  2  900  901  901  40 ... (any order, repeats, skips, reversals)
forbidden: -1, 100001, 42-from-nowhere (outside the set: never observed)
```

The box is the value set; the squiggle is the observation order. Edges
straighten the squiggle; nothing but causality guards the box — and
causality always does, even with no edges at all.

## Diagram 6: observable behavior (the stage)

```
backstage (free): hoisting, elimination, store buffering, OoO issue
  ──may do anything──> LIT STAGE (fixed): sync actions + external effects ──> what programs mean
```

Two runs with identical lit stages are the same program outcome by
definition. Optimizations live backstage; edges are stage directions
the crew must obey.
