# Visual Guide - Data Pipelines

## 1. DAG sketch

Boxes extract -> validate -> transform -> serve with retry counts on
nodes and contracts (schema + SLA) on edges. Failures color the node,
never the whole graph - locality is the point.

## 2. Idempotency diagram

Two arrows (batch, replay) into one sink box, one state out, labeled
with the fixed-point equation. The unchanged 3-row map printed beside
makes the abstraction concrete.

## 3. Quality gate panel

Three gauges: rows vs source, nullRate with threshold line (demo 0.333
vs 0.10 policy), drift vs reference. Red gauge quarantines the batch
visually before any table updates.

## 4. Compat matrix

Grid of change types (add field, drop field, rename, retype, widen)
vs verdict color. The two demo verdicts anchor it: currency green,
retype red.

## 5. Window assignment sketch

Timeline of event times with window brackets (event-time) vs arrival
order arrows showing lates landing outside their bracket. The side
output for lates drawn as an explicit box, not an afterthought.

## 6. Backfill diff view

Staging vs production: count delta, key-overlap Venn, mismatch-rate bar
against tolerance lines. Promotion stamped only when all three clear -
the picture reviewers actually sign.

## 7. Freshness clock

Per-table dial showing event-time of newest served record vs now, with
SLA ring. Staleness shows as the hand leaving the ring - on-call sees
lateness without opening a single query.

## 8. Lineage trace view

Click a served number, see its run id, code version, input range, and
check verdicts inline. Lineage that investigators actually open beats
documentation they never find - build the trace, not the wiki.
