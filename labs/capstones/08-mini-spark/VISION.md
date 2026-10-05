# VISION — Mini Spark Capstone

> Build a distributed compute engine and learn, concretely, where the time goes:
> shuffle, skew, task overhead, and the physical plan.

## Why this capstone

Spark is a framework built on two ideas: move computation to the data, and
build a DAG of stages separated by shuffles. Everything you need to reason
about performance follows from those. Building the engine makes the abstractions
concrete in a way that using it never will.

## The Arc

1. **RDD** — partitioning, dependencies, laziness, lineage.
2. **Execution** — stages, tasks, scheduler, speculation.
3. **Shuffle** — the map/shuffle/reduce boundary and its cost.
4. **Plan** — Catalyst-style analysis, predicate pushdown, join selection.
5. **Scale** — skew, adaptive execution, small files, and the memory model.

## Milestones (checkable)
- [ ] M1: build a lazy RDD with narrow/wide dependencies and materialize it.
- [ ] M2: implement a stage-based scheduler and explain where stages form.
- [ ] M3: implement a shuffle and measure its cost against a non-shuffle baseline.
- [ ] M4: implement predicate pushdown and a broadcast-join selection rule.
- [ ] M5: fix a skew case and show the stage time drop, with AQE-style coalescing.

## Anti-Goals
- An eager engine; the laziness is the point.
- `cache()` without measuring reuse.
- Skipping the cost model and tuning by intuition.

## Interview Lens
- "Walk me through a shuffle, physically."
- "Your job is 10x slower than last week. What is your first command?"
- "Explain adaptive query execution."

## 30-Day Plan
- Wk1 RDD + lineage + materialization. Wk2 stage scheduler + shuffle + cost model.
- Wk3 Catalyst-style optimizer + join selection. Wk4 skew + AQE + benchmarks.

## Done = You Can
- Read any physical plan, name the shuffles, and fix the expensive one.
