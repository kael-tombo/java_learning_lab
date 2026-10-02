# Snowflake Data Cloud Theory

## Architecture Layers
Snowflake's three-layer architecture: Storage Layer (compressed columnar data in S3/Azure/GCS with micro-partitioning), Compute Layer (virtual warehouses as elastic clusters of VMs), and Services Layer (authentication, metadata, optimizer, security). Each layer scales independently.

## Virtual Warehouse Sizing
X-Small (1 credit/hr) through 5X-Large (256 credits/hr). Larger warehouses have more memory and CPU for complex queries. Multi-cluster warehouses auto-scale horizontally for concurrency.

## Micro-Partitioning
Data automatically divided into 50-500 MB micro-partitions. Columnar storage within partitions. Automatic metadata collection (min, max, null count, distinct count) enables pruning — eliminating irrelevant partitions at query time without manual indexing.

## Time Travel & Fail-safe
Standard: 1 day Time Travel. Enterprise: 90 days. Fail-safe: additional 7 days (Snowflake-managed recovery only). AT/BEFORE syntax for point-in-time queries. UNDROP for table recovery.

## Zero-Copy Cloning
Creates metadata-only snapshot pointing to same storage fragments. Copy-on-write: only new/modified data consumes additional storage. Metadata-only operation completes in seconds regardless of table size.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Micro-partitions & Data Clustering — Snowflake Documentation (evergreen; verified Oct 2026) — https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions#label-what-are-micropartitions — Takeaway for the Micro-Partitioning section (50–500 MB units): micro-partitioning is automatic on every table with per-column min/max/distinct metadata, so no upfront static-partition design is needed unlike a traditional warehouse.
- Micro-partitions & Data Clustering — Snowflake Documentation (evergreen; verified Oct 2026) — https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions#label-micropartitions-query-pruning — Takeaway for the architecture/warehouse-sizing section: pruning skips whole micro-partitions plus unreferenced columns at runtime, so filter-heavy queries scale by scanning ~the selected fraction (e.g. one hour of a year ≈ 1/8760th) rather than full tables.
- Micro-partitions & Data Clustering — Snowflake Documentation (evergreen; verified Oct 2026) — https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions#label-clustering-depth — Takeaway for large-table performance work: monitor clustering depth/overlap via SYSTEM$CLUSTERING_INFORMATION and add clustering keys only when sustained DML degrades pruning on multi-terabyte tables, since depth alone is not an absolute health score.
