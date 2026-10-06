# Lab 05: HRMS Data Migration — Real World Project

## Scenario
A global bank is implementing Oracle HRMS for 20,000 employees across 15
countries, migrating from legacy SAP HR. The extract has poor quality: only 60%
of records pass validation. Supervisors reference employees absent from the
extract, national identifiers fail per-country format rules, dates arrive in
mixed `MM/DD/YY` and `DD-MM-YYYY` formats, and assignment records contain
overlapping effective dates. The go-live date is immovable due to regulatory
compliance deadlines. You own the migration.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/hcm/25d/faipp/ (HCM / HRMS)
- https://docs.oracle.com/database/121/HCMR/ (Oracle HRMS concepts)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
SAP HR extract ──► STAGING (raw preserved) ──► DOMAIN VALIDATION
                                                    │
                        ┌───────────────────────────┼────────────────────┐
                        ▼                ▼          ▼                    ▼
                     PERSON       IDENTIFIER      DATE            ASSIGNMENT
                    validator    + checksum    (reject ambig)   (overlap detect)
                        │                │          │                    │
                        └────────────────┴──────────┴────────────────────┘
                                             │
                              VALID rows only │  ERROR rows → owner report
                                             ▼
                              LOAD PASS 1: people (API)
                                             ▼
                              LOAD PASS 2: assignments (API)
                                             ▼
                              LOAD PASS 3: placeholders ─► manager links
                                             ▼
                              Reconciliation: counts │ hierarchy │ dates │ sample
                                             ▼
                              Cycle detection ─► re-validate loop until 100%
```

## Implementation sketch
```sql
-- Reject ambiguity; never guess a date
IF l_d1 > 12 AND l_d2 <= 12 THEN
  RETURN TO_DATE(p_raw, 'DD/MM/YYYY');
ELSIF l_d2 > 12 AND l_d1 <= 12 THEN
  RETURN TO_DATE(p_raw, 'MM/DD/YYYY');
ELSE
  INSERT INTO xx_mig_error (domain, error_code, bad_value, rule_text)
  VALUES ('DATE','AMBIGUOUS_DATE', p_raw,
          'Both components <= 12; source owner must supply country convention');
  RETURN NULL;
END IF;

-- Pre-flight assertion: this MUST return 0 before supervisors are "loaded"
SELECT COUNT(*) unresolved_managers
  FROM per_all_assignments_f
 WHERE assignment_type = 'E' AND primary_flag = 'Y' AND manager_id IS NULL;
```

## Requirements
- F1: Complete staging layer preserving raw values for all source records.
- F2: Domain-specific validators for person, identifier, date, assignment,
      supervisor, and compensation.
- F3: Machine-readable error codes with field, value, and expected rule.
- F4: Country-specific date normalisation rejecting ambiguous values.
- F5: National identifier validation including checksum verification.
- F6: Overlap detection with HR routing for classification.
- F7: Three-pass loader enforcing dependency order via API calls.
- F8: Placeholder strategy for orphaned managers with explicit marking.
- F9: Four-way reconciliation plus cycle detection.
- F10: Re-validation loop with owner-assigned tail management.
- NF1: 100% of 20,000 records loaded or formally excepted.
- NF2: Zero unresolved managers, orphans, or overlapping assignments.
- NF3: Zero invalid national identifiers reaching payroll.
- NF4: Go-live date met despite an immovable regulatory deadline.
- NF5: Security baseline — PII protected in staging, access restricted.
- NF6: RPO/RTO with a documented restore drill preserving migration state.

## Milestones
- Week 1: Staging built; extract loaded; error report produced.
- Week 2: Validators implemented; error classes quantified and owned.
- Week 3: Date and identifier normalisation; checksum tests passing.
- Week 4: Overlap classification with HR; bulk fixes applied.
- Week 5: Load passes 1–3 with reconciliation; hierarchy verified.
- Week 6: Tail resolution, cycle detection, cutover rehearsal.

## Verification
- All four reconciliation checks return zero breaches.
- Cycle detection returns no path beyond expected depth.
- Spot-check sample sized per confidence calculation, zero mismatches.
- Fault injection: duplicate employee number, orphan manager, invalid checksum.
- Restore drill verifying loaded HR data and staging state survive.

## Rollback
Migration is additive: truncate and reload from preserved staging rather than
attempting an in-place undo. Document rollback steps for every load pass.