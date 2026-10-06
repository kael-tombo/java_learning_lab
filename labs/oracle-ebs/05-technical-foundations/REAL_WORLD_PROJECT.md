# Lab 05: Technical Foundations — Real World Project

## Scenario
A manufacturing company receives supplier price lists by EDI. Files are staged
automatically, but updating EBS supplier sites, contacts, and purchasing item
prices is manual. The process takes 3 days per price list, buyers work from
spreadsheets, and there is no audit trail of who changed which price. You must
build a production custom PL/SQL concurrent program handling 10,000+ lines per
run in under one hour, with validation, rollback, and full audit.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/database/121/APUG/ (Application Development Guide)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS APIs)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/

## Architecture
```
EDI file ──► xx_price_list_stage (raw, PENDING)
                    │
                    ▼
        ┌─── xx_price_list_main (concurrent wrapper) ───┐
        │  dispatch on mode parameter                    │
        └───┬──────────────┬──────────────┬──────────────┘
            ▼              ▼              ▼
      VALIDATE_ONLY    PROCESS        ROLLBACK(run_id)
            │              │              │
            │              ▼              ▼
            │      APIs (PO/AP/INV)   xx_run_audit
            │              │          (reverse order)
            │              ▼              │
            │      xx_run_audit  ◄────────┘
            │      (old/new values)
            ▼
      FND_FILE log (operator: counts, timings, top errors)
      XML report (business: per-line results)
                    │
                    ▼
      xx_run_error (PRAGMA AUTONOMOUS_TRANSACTION
                    → survives the failing transaction)
```

## Implementation sketch
```sql
-- The detail that makes error logs worth having
PROCEDURE log_error(p_run_id IN NUMBER, p_line_no IN NUMBER,
                    p_code IN VARCHAR2, p_msg IN VARCHAR2) IS
  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
  INSERT INTO xx_run_error (run_id, line_no, error_code, error_msg)
  VALUES (p_run_id, p_line_no, SUBSTR(p_code,1,30), SUBSTR(p_msg,1,1000));
  COMMIT;   -- independent of the caller's transaction
EXCEPTION WHEN OTHERS THEN ROLLBACK;
END;
```

```sql
-- MOAC: fail loudly rather than process the wrong operating units
l_org_id := fnd_global_apps_pr.get_org_id(101);
IF l_org_id = -1 THEN
  RAISE_APPLICATION_ERROR(-20020, 'No MOAC access to operating unit 101');
END IF;
mo_global_ogles.set_org_context(101, l_org_id);
```

## Requirements
- F1: Three-mode execution (VALIDATE_ONLY, PROCESS, ROLLBACK) via parameters.
- F2: Validation factored out so VALIDATE_ONLY is a genuine rehearsal.
- F3: 10,000+ lines processed in under 1 hour with measured throughput.
- F4: Batched commits (500 rows) with a resumable commit boundary.
- F5: Durable error log via autonomous transaction.
- F6: MOAC enforcement with a hard failure on absent access.
- F7: XML detail report separated from the operator log.
- F8: Complete audit trail enabling point-in-time rollback.
- F9: Program registration including responsibility assignment.
- F10: Health check detecting stale runs and untracked changes.
- NF1: Price list update completed in under 1 hour (from 3 days).
- NF2: Zero untracked changes — rollback safety at 100%.
- NF3: Rerun never duplicates work.
- NF4: Security baseline — role-scoped grants, MOAC honoured.
- NF5: Audit trail available for every price change.
- NF6: Documented rollback for every mode and parameter change.

## Milestones
- Week 1: Baseline current process timing; API benchmark on 500 rows.
- Week 2: Staging, validation, and error logging implemented.
- Week 3: Processing through standard APIs with batching and audit.
- Week 4: Rollback mode and XML report completed.
- Week 5: MOAC enforcement, registration, and health checks.
- Week 6: Full-volume load test and production cutover.

## Verification
- VALIDATE_ONLY rehearsal, then PROCESS, compared for identical validation.
- Fault injection: forced failure mid-run; confirm resume and error log.
- ROLLBACK rehearsal on 10,000 lines; confirm full restoration.
- Load test at 15,000 lines against the one-hour target.
- Operator-account test of submission permissions.

## Rollback
Run header records mode, user, and parameters for every run; audit rows make
ROLLBACK a scripted reversal; the program is additive until cutover.
Document rollback steps for every change.