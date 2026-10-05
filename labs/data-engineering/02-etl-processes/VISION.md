# VISION — ETL Processes: Transform Logic You Can Trust
> Where this lab takes you: from brittle copy-paste scripts to a layered,
> testable transform pipeline where every row has a known fate.

## The Arc
1. **Extract** — batch files, CDC, APIs, incremental windows.
2. **Transform** — cleaning, mapping, joining, aggregating, typing.
3. **Load** — upserts, partitioning, atomic swaps, dead-letter routing.
4. **Repeat** — SCDs, incremental vs full, watermarking.
5. **Trust** — row counts, checksums, reconciliation.

## Milestones (checkable)
- [ ] M1: write an extractor that reads a file offset-tracked, so a rerun reads nothing new.
- [ ] M2: implement a staging -> conformed -> mart layering with explicit contracts.
- [ ] M3: implement Type 1 and Type 2 SCD logic and prove history is queryable.
- [ ] M4: build a load that publishes atomically (write temp, rename) and never exposes partial state.
- [ ] M5: build a reconciliation report: source counts vs loaded counts, per table, per day.

## Anti-Goals
- Business logic embedded in the load step.
- Full reloads for tables where only 0.1% changed.
- Silently dropping rows; every rejection has a reason and a destination.

## Interview Lens
- "How do you load 500M rows when the target only accepts 50k transactions?"
- "Customer says their history vanished. Walk me through your SCD strategy."
- "How do you know today's load is complete?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT with reconciliation.
- Wk3 add SCD2 and backfill. Wk4 REAL_WORLD_PROJECT, present a war story.

## Done = You Can
- Ship a load that is idempotent, atomic, reconcilable, and boring to operate.
