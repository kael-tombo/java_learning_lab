# Lab 05: HRMS Data Migration — Theory

## The Scenario

20,000 employees migrate from SAP HR to EBS HRMS across 15 countries. The
go-live date is immovable (regulatory). Only **60% of records pass validation**.

Four failure classes:

1. Supervisor assignments referencing employees not in the extract
2. National identifiers failing per-country format validation
3. Dates in mixed formats (`MM/DD/YY` and `DD-MM-YYYY`)
4. Assignment records with overlapping effective dates

## Principle 1: Never load directly from source into the target

The naïve flow:

```
SAP extract ──► EBS HRMS
```

Every bad record becomes a failure *inside* HRMS, mid-transaction, with a
partial load and no easy way to identify what was skipped.

The correct flow:

```
SAP extract ──► STAGING ──► VALIDATE ──► LOAD (clean only) ──► RECONCILE
                   │            │             │
                   └─ raw       └─ error     └─ only records
                      preserved    report       with zero errors
```

Staging gives three things:

- **Preservation** — the raw record survives even if validation rejects it, so
  errors can be corrected without re-extracting.
- **Isolation** — HRMS never sees invalid data. No partial loads, no orphaned
  rows, no API rollback surprises.
- **Reportability** — the error report is a query against staging, not a
  reconstruction from load logs.

**The single most important migration decision is where invalid data is allowed
to fail.** In staging, cheaply and repeatably. In the target, expensively and
opaquely.

## Principle 2: Validate by domain, not by record

A flat "is this row valid?" check cannot express HRMS's data model. Validate
each domain separately, because each has distinct rules and distinct owners.

| Domain | Rule | Owner |
|--------|------|-------|
| Person | Name present, DOB plausible, person type valid | HR |
| National ID | Format valid for the country | Payroll/HR |
| Date | Parseable, plausible, unambiguous | HR systems |
| Assignment | Position/org exist, no overlap with another assignment | HR |
| Supervisor | Manager exists in the population | HR |
| Compensation | Grade/salary band valid | Comp & Ben |

Grouping errors by domain gives a much more actionable report than a list of
20,000 rejected rows. It also tells you which team owns the fix.

## Principle 3: Validation must be *specific*

```
BAD:  "Invalid employee record"
GOOD: "National identifier '123-45-678' fails SIN format (9 digits, no dashes)
       for legislation CA at row 14,332"
```

A vague error costs a full investigation cycle. A specific error — with the
value, the rule, the expected format, and the row — can usually be fixed in
minutes, often by the person who created the record.

Include in every error message:

1. The **row number** in the source extract
2. The **offending value**
3. The **rule** that was violated
4. The **expected format**
5. A **machine-readable error code** for grouping

## Principle 4: Dependency order is a partial order, not a sequence

The four tables have real dependencies:

```
people ──────┬──► assignments ──┬──► payroll elements
             │                   └──► benefits
             └──► supervisors (references BOTH people AND assignments)
```

**The trap**: supervisors look like they belong with people (both describe a
human), so teams naturally load them second:

```
people ──► supervisors ──► assignments
                  ✗ WRONG: assignments not loaded yet, so manager_id
                    cannot be set → NULL for everyone
```

Correct order:

```
people ──► assignments ──► supervisors ──► payroll/benefits
```

Enforce it with a **pre-flight assertion**, not a convention:

```sql
SELECT COUNT(*) FROM per_all_assignments_f WHERE manager_id IS NULL;
-- Must return 0 before supervisors are considered loaded
```

## Principle 5: Missing supervisors get placeholders, not NULLs

An orphaned `manager_id` breaks three things: the org chart, approval routing
in self-service, and any report that walks the hierarchy.

Options:

| Option | Result |
|--------|--------|
| Leave NULL | Hierarchy breaks; approvals misroute |
| Drop the assignment | Employee disappears — unacceptable |
| **Create a placeholder person** | Hierarchy intact; real data can be filled later |

Placeholder pattern:

```sql
-- One placeholder per missing manager, marked clearly
INSERT INTO per_all_people_f (person_id, person_last_name, person_first_name,
       person_type, effective_start_date, effective_end_date)
SELECT DISTINCT s.manager_id,
       'PLACEHOLDER', 'MGR_' || s.manager_id, 'EMPLOYEE',
       DATE '2000-01-01', DATE '9999-12-31'
  FROM xx_stage_assignments s
 WHERE s.manager_id IS NOT NULL
   AND s.manager_id NOT IN (SELECT person_id FROM per_all_people_f);
```

This preserves the hierarchy, keeps every employee loadable, and puts the
missing data on an explicit exception report rather than silently losing it.

**Mark them** (`PLACEHOLDER` in the name, a data-quality flag) so they can be
replaced when HR supplies the real records. Unmarked placeholders become
permanent ghosts in the org chart.

## Principle 6: Normalize dates and identifiers per country

Mixed date formats are a **parsing** problem, and the danger is silent success:
`03/04/2026` is 3 April in the UK and 4 March in the US, and both are valid.

```
Wrong:  TO_DATE(value, 'MM/DD/YYYY') applied to all rows
Right:  Determine format from the source system's known convention,
        then validate: parse, then verify the result is plausible,
        then reject anything still ambiguous
```

### Validation that catches the problem

```sql
-- A date that parses differently under two interpretations is REJECTED
l_mm := TO_NUMBER(SUBSTR(v, 1, 2));
l_dd := TO_NUMBER(SUBSTR(v, 4, 2));
IF l_mm > 12 AND l_dd <= 12 THEN
  l_date := TO_DATE(v, 'DD/MM/YYYY');   -- definitely DD/MM
ELSIF l_dd > 12 AND l_mm <= 12 THEN
  l_date := TO_DATE(v, 'MM/DD/YYYY');   -- definitely MM/DD
ELSE
  -- both ≤ 12: ambiguous, must be rejected for human resolution
  RAISE_ERROR('AMBIGUOUS_DATE', v, row_number);
END IF;
```

**Reject ambiguity rather than guess.** A guessed date that is 40 days wrong is
worse than a rejected record, because it will not be discovered until a payroll
run produces wrong tax.

### National identifiers

Format rules differ by country, and the identifier feeds tax reporting:

| Country | Format | Example |
|---------|--------|---------|
| US | 9 digits, no dashes | `123456789` |
| UK | 2 letters + 6 digits + 1 letter | `AB123456C` |
| DE | 11 digits, no separators | `12345678901` |
| SG | NRIC/FIN: letter + 7 digits + letter | `S1234567D` |
| IN | Aadhaar: 12 digits, Verhoeff checksum | `1234 5678 9012` |

The **checksum** matters. `S1234567D` passes a shape check but fails the
Verhoeff algorithm — and an invalid NRIC blocks payroll tax filing. Validate
shape *and* checksum.

## Principle 7: Overlapping effective dates must be resolved before loading

If an employee has two assignments both active on the same date:

```
Person 1001: 2015-01-01 → 2020-06-30  (Analyst)
             2020-01-01 → 2020-12-31  (Senior Analyst)   ← OVERLAP
```

HRMS cannot represent this. The loader will fail, or worse, silently
truncate. Resolve it explicitly:

```
1. Detect overlaps
2. Classify: is the later record a correction, a transfer, or a genuine double-role?
3. Close the earlier row at (later.effective_start - 1 day)
4. Load in effective_start order
```

The classification step is a business decision. Do not automate the choice —
automate the detection, and route the classification to HR.

## Principle 8: First-pass rate is a vanity metric; convergence is real

60% first-pass sounds bad. But the schedule risk is not the first pass — it is
the **tail**.

```
Pass 1: 20,000 × 60%              = 12,000 loaded, 8,000 rejected
Pass 2: fix 70% of rejects         =  5,600 accepted, 2,400 remaining
Pass 3: fix 85% of remainder       =  2,040 accepted,   360 remaining
Pass 4: fix 95% of remainder       =    342 accepted,    18 remaining
Pass 5: manual resolution          =     18 accepted,     0 remaining
```

Each pass fixes an increasing *proportion* of a *smaller* set. The final 18
records consume disproportionate effort because each is an edge case.

**Plan for the tail explicitly**: name an owner for each remaining record, a
method (usually a phone call to the source-system owner), and a deadline.
Projects that optimise first-pass rate still miss go-live because the tail was
unplanned.

## Principle 9: Load through APIs, never direct DML

Direct `INSERT` into `PER_ALL_PEOPLE_F` skips validation, cross-entity
propagation, and audit. It also breaks on the next patch.

```
Direct DML:  faster, unsupported, invisible failures, upgrade risk
API:         slower, validated, logged, upgrade-safe
```

At 20,000 records the API overhead is acceptable and buys correctness. The
migration is a one-off cost; the consequences of bad data are permanent.

## Principle 10: Reconcile four ways

A single "20,000 loaded, 20,000 expected" check proves nothing.

| Check | Proves |
|-------|--------|
| Row count per domain | Nothing was lost or duplicated |
| Hierarchical integrity | `manager_id` all resolve; no cycles |
| Effective-date sanity | No overlaps, no open-ended gaps in required fields |
| Spot sample vs source | Values match the legacy system |

The **hierarchy check** catches the migration's most damaging failure — a
subtly wrong org chart — which no count-based reconciliation would detect.

```sql
-- Hierarchy integrity
SELECT COUNT(*) orphan_managers
  FROM per_all_assignments_f a
 WHERE a.manager_id IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM per_all_people_f p
                    WHERE p.person_id = a.manager_id);

-- Cycle detection (recursive, bounded depth)
SELECT employee_id FROM xx_emp_path WHERE depth > 25;
```

## Migration Diagnostic Order

1. Stage everything first — preserve the raw extract.
2. Validate by domain, with specific messages.
3. Fix normalization (dates, identifiers) before anything else.
4. Detect overlaps and route classification to HR.
5. Load in dependency order with a pre-flight assertion.
6. Create placeholders for missing supervisors; mark them.
7. Reconcile counts, hierarchy, dates, and a sample.
8. Loop until the tail is empty and every record has an owner.

## Anti-Patterns

- Loading directly from source into HRMS.
- One flat "invalid record" error message.
- Loading supervisors before assignments.
- Setting `manager_id = NULL` for missing managers.
- Guessing an ambiguous date rather than rejecting it.
- Loading through direct DML for speed.
- Optimising first-pass rate while the tail is unplanned.
- Reconciling by row count only.

## Summary

The 60% pass rate was not a data quality emergency — it was the absence of a
staging layer and domain-specific validation. The fix was to move failure into
staging where it is cheap and visible, validate by domain with messages specific
enough to act on, normalize per country while rejecting ambiguity, load in true
dependency order with placeholders preserving hierarchy, and manage the tail
explicitly rather than optimising the first pass.