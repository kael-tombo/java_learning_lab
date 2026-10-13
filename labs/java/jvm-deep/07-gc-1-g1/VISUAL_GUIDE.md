# Visual Guide: G1 GC

## The region map

Draw the heap as a grid of equal squares. Color Eden squares green,
Survivor yellow, Old blue, Humongous red (spanning two squares for the
lab's 2 MB arrays on 1M regions). Between pauses the colors shift —
green squares turn yellow or blue, red squares never change color until
cleanup. The grid motif (not two fixed boxes) is the whole point.

## A young pause, frame by frame

Frame 1: several green squares full, one yellow half full. Frame 2
(freeze): arrows from live objects in green to free space in fresh
yellow/blue squares; dead objects gray out in place. Frame 3: the old
green squares blank (free), the log prints `used->used(heap) Xms`. All
application threads stand still between frames 1 and 3 — that stillness
is the STW pause, measured 2-5 ms here.

## SATB snapshot sketch

Draw the object graph as nodes and arrows. Circle the snapshot moment:
every arrow overwritten after the circle gets a numbered tag (SATB
buffer entry) pointing at its old target. Marking follows both the live
arrows and the tagged old targets. Ghost nodes reachable only through
tags are the floating garbage — shaded, labeled "next cycle".

## Mixed collections ordering

Bar-chart old regions by garbage percentage. Mixed GCs pick the tallest
bars first and evacuate them alongside the young set. Each `Pause Young
(Mixed)` line knocks one or two tall bars down; short bars wait for later
cycles. Garbage-first is literally tallest-bar-first.

## Reading the init log

One line rules them all: `Heap Region Size: 1M` (256m) or `4M` (8g),
plus worker counts (`ParallelGCThreads`, `Concurrent Refinement
Workers`). Sketch these as the map legend — every later interpretation
(region counts, humongous cutoffs) reads through this legend.
