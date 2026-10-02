# Theory: Query Optimization

## Index Types

| Type | Use Case | Structure |
|---|---|---|
| B-Tree | Equality + range queries, sorting | Balanced tree, O(log N) |
| Hash | Equality only | Hash table, O(1) |
| GiST | Full-text, geometric, range types | Generalized search tree |
| GIN | Array, JSONB, full-text | Inverted index |
| BRIN | Large tables with natural ordering | Block range index |
| Covering | Index-only scans | Includes INCLUDE columns |

## EXPLAIN Plan Reading

```
Seq Scan on users (cost=0.00..1000.00 rows=10000 width=100)
  Filter: (age > 30)
```
- **cost**: Estimated cost (startup..total) in arbitrary units
- **rows**: Estimated rows returned
- **width**: Average row width in bytes
- **Seq Scan**: Full table scan (table sequential scan)
- **Index Scan**: Index lookup then heap access
- **Index Only Scan**: All needed data in index (no heap visit)

## N+1 Problem
Occurs when code executes one query for the parent entity and N queries for each child collection. In JPA:
```java
// 1 query for departments + 10 queries for employees = 11 queries
List<Department> depts = departmentRepository.findAll();
for (Department d : depts) {
    d.getEmployees().size(); // triggers lazy load per department
}
```

## Query Cost Factors
- **Rows scanned**: Full scan vs index scan vs index-only scan
- **Join methods**: Nested Loop, Hash Join, Merge Join
- **Sorting**: In-memory vs disk-based sort
- **Data locality**: Sequential vs random I/O

## Sourced field notes (fetched Oct 2026 — verify before citing)
- "Index-Only Scan: Avoiding Table Access" — Use-The-Index-Luke by Markus Winand (evergreen guide, site © 2010–2026; fetched Oct 2026) — https://use-the-index-luke.com/sql/clustering/index-only-scan-covering-index — Takeaway tied to covering indexes in this lab: a covering index must contain all columns in the query (WHERE + SELECT); the fetched example builds `(subsidiary_id, eur_value)` to answer `SUM(eur_value) ... WHERE subsidiary_id = ?` with an index-only scan and no table access.
- "Index-Only Scan: Avoiding Table Access" (same source, fetched Oct 2026) — https://use-the-index-luke.com/sql/clustering/index-only-scan-covering-index — Takeaway tied to EXPLAIN plan reading in this lab: plans showing `INDEX RANGE SCAN` without `TABLE ACCESS BY INDEX ROWID` signal an index-only scan; when a new `WHERE sale_date > ?` column is not in the index, the plan regresses to table fetch/Index-scan-plus-table-access despite fewer rows returned.
- "INCLUDE: Non-key Columns" section (same source, PostgreSQL 11+ / SQL Server; fetched Oct 2026) — https://use-the-index-luke.com/sql/clustering/index-only-scan-covering-index — Takeaway tied to Covering/INCLUDE index type in this lab: non-key `INCLUDE(phone_number, first_name)` columns live only in leaf nodes to enable index-only scans without becoming access predicates or widening key limits (e.g. PostgreSQL B-tree ~2713-byte / 32-column limits).
