# VISION — Apache Iceberg: Open Table Format for Huge Datasets
> Where this lab takes you: from "which table format do we standardise on?" to
  running Iceberg across five engines with manifests, snapshots, and branching.

## The Arc
1. **Table** — metadata, snapshots, manifests, data files vs metadata files.
2. **Hidden partitioning** — partition transforms, why spec > folder layout.
3. **Evolution** — add/drop/rename/reorder, defaults, compatibility.
4. **Branching** — snapshot isolation, tags, branches, WAP pattern.
5. **Multi-engine** — Spark/Flink/Trino/Athena/Presto reads and writes.

## Milestones (checkable)
- [ ] M1: trace a table read from a query to specific Parquet files via the manifest list.
- [ ] M2: define a partition spec with transforms and explain the pruning gain.
- [ ] M3: perform a schema change in all 4 flavours without breaking readers.
- [ ] M4: create a branch, write to it, and merge with conflict detection.
- [ ] M5: read the same table from 3 engines and prove identical results.

## Anti-Goals
- Folder-partitioned tables pretending to be Iceberg.
- `PARTITIONED BY` on a column with high cardinality.
- Assuming snapshot isolation means no write conflicts; it does not.

## Interview Lens
- "Delta or Iceberg for a multi-engine lakehouse?"
- "How does Iceberg avoid listing the whole table?"
- "What is the WAP pattern and when do you need it?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT writing a metadata reader.
- Wk3 add branching and schema change. Wk4 REAL_WORLD_PROJECT.

## Done = You Can
- Operate an Iceberg table across engines and reason about its metadata.
