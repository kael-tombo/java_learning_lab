# EBS Technical Architecture — Real World Project

## Scenario
A shared services centre operates EBS R12.2 supporting 14 business units. The
custom codebase is 340,000 lines of PL/SQL, much of it written before 12.1 and
now written directly against `_ALL` tables. A recent CPU update broke three
custom programs in ways that were not covered by testing, and nobody can state
which customizations touch which standard objects. You own the technical debt
and the upgrade-readiness evidence it produces.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/index.html (Application Development Guide)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS technical docs)

## Architecture
```
Custom code layer
   ├── Direct DML on _ALL tables  ──► upgrade breakage risk
   ├── Public API usage          ──► supported, upgrade-safe
   └── Support model             ──► which standard objects are touched?
        │
        ▼
Concurrent program wrapper ─► Concurrent Manager ─► Logs + error handling
        │
        ├─► PL/SQL packages (API-based)
        └─► OAF / OA Framework ─► BC4J ─► JTT (Java transaction tech)
                                        │
                              Forms personalization layer
```

## Implementation sketch
```sql
-- Support model: custom code touching standard objects
SELECT a.owner, a.name custom_unit, b.owner standard_owner, b.name standard_unit,
       COUNT(*) reference_count
  FROM all_source a
  JOIN all_source b
    ON UPPER(a.text) LIKE '%' || b.name || '%'
 WHERE a.owner LIKE 'XX%' AND b.owner IN ('AP','AR','GL','FA','PO','OM','INV')
 GROUP BY a.owner, a.name, b.owner, b.name
 ORDER BY reference_count DESC;

-- Undeclared direct DML on core tables (upgrade breakage candidates)
SELECT owner, name, type FROM all_source
 WHERE owner LIKE 'XX%'
   AND (UPPER(text) LIKE 'UPDATE %' OR UPPER(text) LIKE 'INSERT INTO %')
   AND REGEXP_LIKE(UPPER(text), '(GL|AP|AR|FA|PO|OM|INV)_[A-Z_]+_ALL')
   AND ROWNUM <= 50;
```

## Requirements
- F1: Complete custom code inventory with an owner and risk rating per package.
- F2: Support model mapping every custom unit to the standard objects it uses.
- F3: Direct-DML detection report listing all upgrade breakage candidates.
- F4: Refactoring plan converting high-risk code to public APIs.
- F5: Standard custom concurrent program template with logging and rollback.
- F6: Regression test suite that runs before every CPU or patch.
- F7: Forms personalization inventory with removal procedures.
- F8: OAF/BC4J architecture documentation for web-tier customizations.
- F9: Coding standard requiring API usage, enforced by a static check.
- F10: Monthly upgrade-readiness report generated automatically.
- NF1: Next upgrade completed with zero production defects from custom code.
- NF2: Regression suite executes in under 4 hours with no manual steps.
- NF3: 100% of new code uses public APIs (static check enforced).
- NF4: Security baseline — static analysis for injection risk on all packages.
- NF5: RPO/RTO with a documented restore drill including custom code.
- NF6: Documented rollback for every code deployment.

## Milestones
- Week 1: Inventory and support model built; risk rating agreed.
- Week 2: Direct-DML detection report produced and triaged.
- Week 3: Regression suite built and green on current code.
- Week 4: Top 20 high-risk packages refactored to public APIs.
- Week 5: Standard templates and coding standard adopted.
- Week 6: Monthly upgrade-readiness reporting live.

## Verification
- Run the regression suite against a patched non-production instance.
- Static check confirms zero direct DML on core tables in new code.
- Restore drill verifying custom packages and their metadata survive recovery.
- Peer review sign-off on the refactored packages.

## Rollback
Code deployments are version-controlled with a prior-version redeploy path;
support model and reports are regenerable; the static check is advisory until it
becomes a gate. Document rollback steps for every change.