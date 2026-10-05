# VISION — Data Lake: Storage for Unstructured Scale
> Where this lab takes you: from "HDFS is a filesystem" to a lake with
> lifecycle tiers, file-format discipline, and cost you can explain.

## The Arc
1. **Object** — blobs, keys, listing semantics, eventual listing.
2. **Layout** — partitioning, file sizes, small-file problem.
3. **Format** — Parquet/ORC/Avro, row groups, column pruning, compression.
4. **Zones** — raw/curated/gold, promotion, contracts.
5. **Lifecycle** — storage classes, retention, deletion, cost.

## Milestones (checkable)
- [ ] M1: choose a partition scheme for 3 query patterns and defend it.
- [ ] M2: measure bytes read with column projection and show the 8x reduction.
- [ ] M3: build a compaction job that takes 40k small files to 200 large ones.
- [ ] M4: write a lifecycle policy that moves cold data and expires raw safely.
- [ ] M5: explain why deleting a "directory" on object storage is not free.

## Anti-Goals
- Partitioning by high-cardinality keys (million tiny prefixes).
- CSV in a lake because it is "just for staging".
- A lake with no schema, no ownership, and no expiry.

## Interview Lens
- "Your query scans 4TB. How do you find out why in 5 minutes?"
- "Where does the 9000-file listing cost come from?"
- "How do you delete a customer's data across bronze, silver, and gold?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT with a bytes-read report.
- Wk3 add compaction + lifecycle. Wk4 REAL_WORLD_PROJECT with a cost model.

## Done = You Can
- Design a lake layout that is fast to query and cheap to keep.
