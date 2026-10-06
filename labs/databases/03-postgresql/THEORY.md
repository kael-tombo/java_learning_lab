# Theory: PostgreSQL

## Architecture (Process Model)
```
Postmaster (supervisor)
    ├── Backend process (per client connection)
    ├── Writer (shared buffer → disk)
    ├── WAL Writer (WAL buffer → WAL segment)
    ├── Checkpointer (checkpoint)
    ├── Autovacuum (cleanup dead tuples)
    ├── Stats Collector (query statistics)
    ├── Archiver (WAL archiving)
    └── Background workers (extensions, replication)
```

## Shared Memory
- **Shared Buffers**: Cache for data pages (default 128MB, recommend 25% RAM)
- **WAL Buffer**: Write-ahead log cache (default 16MB)
- **CLOG**: Commit log (transaction status)
- **LWLock**: Lightweight locks for shared structures

## MVCC in PostgreSQL
- Each tuple has: `xmin` (creating XID), `xmax` (deleting XID), `ctid` (physical location)
- `t_infomask` bitfield for tuple state
- No UNDO log (unlike Oracle) – VACUUM cleans dead tuples
- `HOT` (Heap-Only Tuple) updates optimize index usage

## Data Type Categories

| Category | Types |
|---|---|
| Numeric | INTEGER, BIGINT, NUMERIC/DECIMAL, REAL, DOUBLE, MONEY |
| Character | VARCHAR(n), CHAR(n), TEXT |
| Binary | BYTEA |
| Date/Time | DATE, TIME, TIMESTAMP, TIMESTAMPTZ, INTERVAL |
| Geometric | POINT, LINE, LSEG, BOX, PATH, POLYGON, CIRCLE |
| Network | INET, CIDR, MACADDR |
| JSON | JSON, JSONB |
| Arrays | TEXT[], INTEGER[], etc. |
| Range | INT4RANGE, TSRANGE, DATERANGE, etc. |
| Bit String | BIT(n), BIT VARYING(n) |
| Text Search | TSVECTOR, TSQUERY |
| UUID | UUID |
| XML | XML |

## Index Types

| Type | Use Case |
|---|---|
| B-tree | Default, equality + range |
| Hash | Equality only |
| GiST | Geometric, full-text, custom |
| GIN | JSONB, arrays, full-text |
| BRIN | Large, physically-ordered tables |
| SP-GiST | Partitioned trees (quadtree, k-d tree) |

## Sourced field notes (fetched Oct 2026 — verify before citing)
- "PostgreSQL 18 Documentation — Chapter 11. Indexes (18 is the current release; 19 is in beta)" (PostgreSQL Global Development Group, current/18 docs — accessed Oct 2026) — https://www.postgresql.org/docs/current/indexes.html — Takeaway tied to lab index-type exercise: match the lab's type table (B-tree default for equality+range, Hash equality-only, GiST/GIN for geometric/JSONB/full-text, BRIN for large physically-ordered tables) against the official type list before choosing an index in `EXPLAIN` drills.
- "PostgreSQL 18 Documentation — Chapter 11. Indexes (18 is the current release; 19 is in beta)" (PostgreSQL Global Development Group, current/18 docs — accessed Oct 2026) — https://www.postgresql.org/docs/current/indexes.html — Takeaway tied to lab multicolumn/ordering configs: use sections 11.3–11.4 to verify column order in composite indexes and `ORDER BY` compatibility rather than assuming any multicolumn index accelerates sorting.
- "PostgreSQL 18 Documentation — Chapter 11. Indexes (18 is the current release; 19 is in beta)" (PostgreSQL Global Development Group, current/18 docs — accessed Oct 2026) — https://www.postgresql.org/docs/current/indexes.html — Takeaway tied to lab partial/expression index exercises: sections 11.7–11.8 define when expression and partial indexes apply, so confirm query predicates match the index predicate before expecting index-only scans (11.9).
- "PostgreSQL 18 Documentation — Chapter 11. Indexes (18 is the current release; 19 is in beta)" (PostgreSQL Global Development Group, current/18 docs — accessed Oct 2026) — https://www.postgresql.org/docs/current/indexes.html — Takeaway tied to lab overhead/MVCC discussion: the chapter's warning that indexes speed reads but add write/maintenance overhead justifies the lab's HOT/VACUUM notes — re-check index usage with 11.12 (`pg_stat_user_indexes`) instead of adding indexes blindly.
