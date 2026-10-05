# VISION — Delta Lake: ACID Tables on Object Storage
> Where this lab takes you: from "Parquet plus a rename" to a table format
  with transactions, time travel, schema evolution, and incremental writes.

## The Arc
1. **Files** — Parquet data files, commit metadata, the transaction log.
2. **ACID** — optimistic concurrency, conflict detection, isolation levels.
3. **Change** — MERGE, UPDATE, DELETE, overwrite, schema evolution modes.
4. **Time** — time travel, restore, vacuum, retention.
5. **Operate** — streaming writes, compaction, Z-order, small files.

## Milestones (checkable)
- [ ] M1: explain what `_delta_log` contains and how a snapshot is read.
- [ ] M2: perform a MERGE and explain the plan the log recorded.
- [ ] M3: query a table as of a past version and restore it.
- [ ] M4: implement schema evolution through all 4 modes without rewriting data.
- [ ] M5: take a streaming write from 9,000 small files to 30 compacted files.

## Anti-Goals
- A `MERGE` on a key with duplicates and no dedup rule; results are undefined.
- Disabling schema checks to make a load pass.
- `DELETE` on a fact table at scale without thinking about rewrite cost.

## Interview Lens
- "How does Delta know another writer changed my files?"
- "Your table has 40,000 files. What's the cost and the fix?"
- "Why did my MERGE delete 1.2M rows?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT with a transaction log reader.
- Wk3 add time travel + schema evolution. Wk4 REAL_WORLD_PROJECT.

## Done = You Can
- Reason about a Delta transaction log and design a safe write pattern.
