# VISION — Data Warehousing: Star Schemas and Columnar Storage
> Where this lab takes you: from OLTP row stores you cannot scan, to a
> dimensional warehouse that answers business questions in one query.

## The Arc
1. **Why** — OLTP vs OLAP, row vs columnar, why scans win.
2. **Model** — fact tables, dimensions, grain, star vs snowflake.
3. **Storage** — partitions, clustering, pruning, compression.
4. **Speed** — pre-aggregation, materialized views, cube design.
5. **Operate** — compaction, statistics, cost per query.

## Milestones (checkable)
- [ ] M1: design a star schema for retail orders and state the grain in one sentence.
- [ ] M2: build the fact + 4 dimensions and answer 5 ad-hoc questions with a single join.
- [ ] M3: partition by date, cluster by the second-most-used key, explain the choice.
- [ ] M4: write a query that scans <1% of the fact table using partition + predicate pushdown.
- [ ] M5: estimate the storage cost and cut it by 3x with compression choices.

## Anti-Goals
- Storing text where a surrogate key belongs.
- Modelling two grains in one fact table.
- Optimizing a query before measuring where the bytes are read.

## Interview Lens
- "Why did your BI dashboard get slow after data grew 10x?"
- "Snowflake or a star schema on Postgres? When would you switch?"
- "How many rows does this fact table have, and at what grain?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT, measure scan bytes per query.
- Wk3 add a materialized aggregate and a clustering change. Wk4 REAL_WORLD_PROJECT.

## Done = You Can
- Model, tune, and cost a warehouse that answers real questions predictably.
