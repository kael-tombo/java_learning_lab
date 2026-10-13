# Visual Guide: JVM Tuning

## The ergonomic derivation tree

Draw RAM at the top (16 GB reference). Two branches: /64 to 256M
initial, /4 to 4G max. A third branch (`-Xmx256m`) bypasses the tree and
lands exactly on 268,435,456 — a straight arrow labeled "explicit beats
ergonomic." Inside containers redraw the root as the cgroup limit, not
host RAM; the whole tree re-derives from the smaller root.

## The generational pie

One pie for the heap: old two thirds, young one third (NewRatio 2). Zoom
the young slice: Eden eight tenths, two survivors one tenth each
(SurvivorRatio 8). Shade survivors to 50% (TargetSurvivorRatio) as the
desired fill line — tenuring adapts to hold that line across cycles.

## TLAB cartoon

Eden as a long strip. Default path: per-thread colored blocks (TLABs)
with private bump arrows inside each; one shared arrow at the strip head
for refills only. `-XX:-UseTLAB` path: every allocation arrow converges
on the single shared head with a lock icon — the visual source of the
~8x timing gap. One glance explains why refill contention, not object
size, dominates.

## Three-plane dashboard sketch

Three side-by-side gauges: heap occupancy (young/old or G1 regions),
CodeHeap fullness (against 240M ceiling — mark the cliff where
compilation stops), Metaspace growth (against no ceiling — mark the
~21M first-trigger line). A red zone on one gauge never justifies turning
another gauge's knob; draw the knobs under their own gauges.

## The one-flag graph

Two bars for ParallelGC young-pause counts: tall at 128m, short at 512m,
labels noting identical code and flags except heap. Beside them two equal
bars for G1 with a "cruise control absorbed it" caption. The three-bar
comparison teaches both the lever and its limits in one figure.
