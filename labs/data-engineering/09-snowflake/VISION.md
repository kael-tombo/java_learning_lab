# VISION — Snowflake: Warehousing as a Service You Pay For Differently
> Where this lab takes you: from "which warehouse size?" to managing a
> serverless data platform where compute, storage, and query shape are the budget.

## The Arc
1. **Model** — storage vs compute separation, virtual warehouses.
2. **Data** — databases, schemas, stages, file formats, internal/external tables.
3. **Query** — clustering, pruning, caching, micro-partitions.
4. **Semantics** — views, materialized views, dynamic tables, streams/tasks.
5. **Economics** — credits, warehouse sizing, cost per query, governance.

## Milestones (checkable)
- [ ] M1: load Parquet from a stage into an internal table and explain what was copied.
- [ ] M2: size a warehouse for an ELT job and a BI job separately, with numbers.
- [ ] M3: take a table from 40s to under 5s with clustering and explain the cost trade-off.
- [ ] M4: build a dynamic table with a refresh policy and measure freshness.
- [ ] M5: attribute 100% of credit spend to a team and a workload.

## Anti-Goals
- One giant always-on warehouse; idle time is the most expensive thing you own.
- `SELECT *` on wide tables, which defeats micro-partition pruning.
- Loading JSON into a table before validating the shape at the stage.

## Interview Lens
- "Your Snowflake bill doubled. Where do you look in 10 minutes?"
- "Virtual warehouse vs dedicated vs serverless — when?"
- "How do you give analysts access without giving them the whole schema?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT with a credit report.
- Wk3 tune clustering and add a dynamic table. Wk4 REAL_WORLD_PROJECT.

## Done = You Can
- Run a Snowflake estate with predictable freshness and a defensible bill.
