# Lab 03: APEX SQL Workshop — Real World Project

## Scenario
A data team needs to move a legacy on-premises product dataset (180,000 rows in
CSV files) into an APEX application schema so it can be exposed through an
internal API. The team member assigned to the load is a competent SQL developer
new to APEX, and has been creating tables interactively in the Object Browser.
Three weeks in, nobody can reproduce what was created — there are no scripts,
the constraint decisions are undocumented, and one table was created without a
primary key, which will block the ORDS auto-REST exposure they need next month.
They need a controlled path forward.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (SQL Workshop)
- (link removed) (ORDS)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
Legacy CSV files (180,000 rows)
   │
   ▼
SQL Workshop — Data Workshop (column mapping, validation)
   │
   ▼
Staging tables (raw load, no constraints)  ──► validation queries
   │
   ▼
Target tables created by version-controlled DDL script
   ├─ Primary keys (required for ORDS)
   ├─ Foreign keys (referential integrity)
   ├─ Indexes on filter columns
   └─ NOT NULL on mandatory columns
   │
   ▼
Load via insert-select (set-based, one statement per table)
   │
   ▼
Reconciliation: counts, checksums, orphan check
   │
   ▼
ORDS auto-REST enabled — requires the PKs created by script, not the browser
```

## Implementation sketch
```sql
-- Reproducible DDL, version-controlled. NOT created through the browser.
CREATE TABLE product (
  product_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- PK blocks ORDS if absent
  sku          VARCHAR2(40)  NOT NULL UNIQUE,
  name         VARCHAR2(200) NOT NULL,
  category_id  NUMBER,
  price        NUMBER(12,2) NOT NULL CHECK (price >= 0),
  active_flag  CHAR(1) DEFAULT 'Y' NOT NULL
);
CREATE INDEX ix_prod_cat ON product(category_id);

-- Set-based load from staging — one statement, not a row loop
INSERT INTO product (sku, name, category_id, price, active_flag)
  SELECT s.sku, s.name, s.category_id, s.price, COALESCE(s.active_flag,'Y')
    FROM stg_product s
   WHERE NOT EXISTS (SELECT 1 FROM product p WHERE p.sku = s.sku);

-- Reconciliation, not optimism
SELECT (SELECT COUNT(*) FROM stg_product) stg_rows,
       (SELECT COUNT(*) FROM product)   tgt_rows,
       (SELECT COUNT(*) FROM product p WHERE NOT EXISTS
          (SELECT 1 FROM stg_product s WHERE s.sku = p.sku)) unmatched
  FROM dual;
```

## Requirements
- F1: Complete inventory of what exists, including undocumented objects.
- F2: Full DDL script, version-controlled, recreating the schema from scratch.
- F3: Primary keys on every table — a hard prerequisite for ORDS.
- F4: Foreign keys and NOT NULL constraints on mandatory columns.
- F5: Indexes on every column used as a filter.
- F6: Data Workshop load with column mapping and pre-load validation.
- F7: Set-based insert-select load with duplicate protection.
- F8: Reconciliation: counts, checksums, and orphan checks.
- F9: Saved query scripts replacing ad-hoc interactive execution.
- F10: Environment rebuild from the script, proving reproducibility.
- NF1: Schema fully reproducible from version-controlled scripts.
- NF2: Zero tables without a primary key.
- NF3: All 180,000 rows loaded and reconciled.
- NF4: Security baseline — no objects created outside the owning schema.
- NF5: No production change made through a browser session.
- NF6: Documented rollback — rebuild procedure proven on a test schema.

## Milestones
- Week 1: Inventory and gap analysis; DDL script drafted.
- Week 2: Rebuild the schema in a test environment from the script alone.
- Week 3: Data Workshop load with validation and mapping.
- Week 4: Set-based load, reconciliation, and ORDS readiness check.

## Verification
- Drop and recreate the entire schema from the script; confirm identical results.
- Row counts and checksums between staging and target.
- Confirm every table has a primary key by querying the data dictionary.
- Attempt an ORDS auto-REST enablement; confirm it succeeds.
- Reproduce the load end to end on a clean schema and time it.

## Rollback
Truncate and reload from staging rather than attempting an in-place undo; the
DDL script is the source of truth and can recreate any state. Document rollback
steps for every change.