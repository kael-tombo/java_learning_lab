# Lab 05: Technical Foundations (Custom Concurrent Program) — Theory

## The Scenario

A manufacturer receives supplier price lists via EDI. Files land in a staging
table. A custom concurrent program must:

1. Validate supplier data against EBS supplier master
2. Create/update supplier sites and contacts
3. Update purchasing item prices
4. Generate a comprehensive execution report

The manual process takes **3 days**. The target is **under 1 hour** for
10,000+ lines, with multi-mode execution, error handling, rollback, and audit.

## Principle 1: The concurrent program is the unit of operational work

PL/SQL you invoke from SQL*Plus is a script. PL/SQL invoked by the Concurrent
Manager is an **operational unit** — it has:

- A request ID that appears in `FND_CONCURRENT_REQUESTS`
- A log that operators read when it fails
- A schedule
- A defined owner and security group

That framing changes the design. Before writing logic, decide:

```
Who runs this?        (responsibility / sysadmin)
What privileges?      (database role, MOAC orgs)
What logs exist?      (log file, error table, audit)
How does it fail?     (retry, rerun, rollback)
How is it observed?   (concurrent request monitor)
```

A program with no error log is a program that fails invisibly.

## Principle 2: Parameter-driven multi-mode beats four programs

The requirement mentions VALIDATE_ONLY, PROCESS, and ROLLBACK. Three options:

| Option | Assessment |
|--------|-----------|
| Three separate programs | Duplicated validation logic that drifts apart |
| **One program, mode parameter** | Single source of truth for validation |
| Mode inferred silently | Unpredictable — never |

Multi-mode in one package matters because **the validation logic must be
identical** whether you are previewing or executing. If validation lives in one
place, a VALIDATE_ONLY run is a genuine rehearsal of the PROCESS run.

```
VALIDATE_ONLY : run everything, write to log, make no DML
PROCESS       : run everything, apply DML through APIs
ROLLBACK      : undo the DML from a named prior run
```

ROLLBACK as a *parameter* rather than a script is deliberate: it must know the
run ID it is reversing, and a standalone script cannot.

## Principle 3: Validation must be a separate, callable unit

```
xx_price_list_pkg.validate(p_run_id, p_mode)   -- pure, no DML
xx_price_list_pkg.process(p_run_id)            -- assumes validate passed
xx_price_list_pkg.rollback(p_run_id)           -- reverses process
```

Why this matters:

1. **VALIDATE_ONLY becomes honest** — it calls the same code as PROCESS.
2. **Testing is possible** — validate can be exercised without side effects.
3. **PROCESS stays short** — it does not re-derive validation logic.
4. **The error report is authoritative** — one implementation.

The common failure is validation logic inlined in the process loop, which means
VALIDATE_ONLY is a *reimplementation* and drifts within two releases.

## Principle 4: APIs are not ceremony

```
Direct DML into PO_HEADERS_ALL:
  ✗ Skips validation (dates, statuses, number generation)
  ✗ Skips cross-entity propagation (to PO_LINES, distributions)
  ✗ Skips audit and change history
  ✗ Breaks on the next patch or upgrade
  ✗ Can leave the instance in an inconsistent state
```

`PO_REQ_CREATE_PUB.create_purchase_order`:

```
  ✓ Validates inputs and returns structured errors
  ✓ Generates document numbers correctly
  ✓ Propagates to all related tables
  ✓ Respects MOAC
  ✓ Is a supported, upgrade-safe interface
```

**Performance objection**: APIs are slower. For 10,000 lines the API overhead is
minutes, and the manual alternative is 3 days. The API is not the bottleneck.

The real test: would you accept a production error caused by an unsupported
insert in exchange for 30 minutes of runtime? No — because you cannot detect it
and it may surface months later during an upgrade.

## Principle 5: Batch, commit, and make it resumable

10,000 API calls in a single transaction is a design error.

| Concern | Single transaction | Batched |
|---------|-------------------|---------|
| Undo growth | Severe — all 10,000 changes held | Bounded per batch |
| Lock duration | Hours | Seconds per batch |
| Failure cost | Restart all 10,000 | Resume from last commit |
| Rollback | Massive `ROLLBACK` | Reverse committed batches |

```
Batch size: 500 rows
On failure in batch 7 → batches 1-6 are committed and done
                    → re-run with p_resume_from = 3001
```

**The resume capability is the point.** A rerun that processes all 10,000 rows
again is not a rerun, it is a duplicate risk. Design the resume path:

```sql
-- Skip rows already processed in this run
WHERE status = 'PENDING' OR run_id <> p_run_id
```

And make processing **idempotent**: check whether the API call is needed before
making it, or make the effect naturally idempotent.

## Principle 6: The error log must survive the failure

Consider three designs:

```
A)  DBMS_OUTPUT only           → lost the moment the session ends
B)  One big string accumulator → lost on unhandled exception, huge memory
C)  Row-by-row INSERT as you go → committed per batch, survives everything
```

**C is correct**, with one subtlety: row-level inserts inside a batch are part
of that batch's transaction, so a batch failure rolls back its own error rows.
Two options:

1. Use `PRAGMA AUTONOMOUS_TRANSACTION` for the error log (independent commit).
2. Accept per-batch granularity and note that batch errors are lost on failure.

Option 1 is right for a production error log. The log must be queryable
**during** the failure investigation, not after a successful rerun.

```sql
PROCEDURE log_error(p_run_id, p_line_no, p_code, p_msg) IS
  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
  INSERT INTO xx_run_error (...) VALUES (...);
  COMMIT;   -- survives the failed transaction
END;
```

## Principle 7: MOAC is a correctness requirement, not a feature

Without MOAC handling, a program that honours the caller's context may
process or update records across **all** operating units — because your WHERE
clause has no `org_id` filter.

The obligation is twofold:

1. **Read** the caller's accessible orgs via `fnd_global_apps_pr.get_org_id`
   or `MO_GLOBAL_OGS`/`FND_GLOBAL_OGS` APIs.
2. **Write** with `mo_global_ogles.set_org_context` so triggers populate
   `org_id` correctly.

```sql
l_org_id := fnd_global_apps_pr.get_org_id(101);  -- business unit
IF l_org_id = -1 THEN
  RAISE_APPLICATION_ERROR(-20020, 'No MOAC access to org 101');
END IF;
mo_global_ogles.set_org_context(101, l_org_id);
```

**Failing loudly when access is absent is correct.** Silently processing
everything is the failure mode that gets discovered during an audit.

## Principle 8: XML output is a report format, not a log

Two outputs, two purposes:

```
Concurrent program log  → operator-facing: counts, timings, top errors
XML detail report       → business-facing: line-by-line results
```

The log is read when something failed. The XML is read when someone asks
"which lines updated and what prices did they get?" Compressing 10,000 line
results into the log makes the log unreadable.

Structure the XML by audience:

```xml
<summary>              <!-- log: counts, duration, mode -->
<line_results>         <!-- XML report: per-line outcome -->
<errors>               <!-- both, summarised in log / detailed in XML -->
```

## Principle 9: Audit every DML

```
xx_run_audit (run_id, object_type, object_id, operation,
              field_name, old_value, new_value, actor, created_at)
```

Requirements:

- **Every** create, update, and delete records what changed.
- The actor is the concurrent program user, recorded explicitly.
- Runs are keyed by `run_id` so ROLLBACK can find exactly what to reverse.
- The audit table is append-only, like any ledger.

Without this, ROLLBACK is guesswork and "who changed this price" is unanswerable.

## Principle 10: Registration is part of the deliverable

A package in the schema is not a deployed program. Registration requires:

```
1. Concurrent Program Executable (application, executable, path/PLSQL)
2. Concurrent Program (linked to executable)
3. Parameters (with validation, defaults, token substitution)
4. Responsibility assignment (who can submit/run)
5. Schedule (if batch)
```

Miss step 4 and operators get `ORA-06550: no privilege` at 2am. **Submit
permissions are part of the deliverable**, tested by a real operator account
rather than the developer's.

## Design Order

1. Define modes and what each guarantees.
2. Separate validation as a pure, callable unit.
3. Choose API calls and confirm MOAC handling.
4. Set batch size and commit points; design the resume path.
5. Build the autonomous-transaction error log.
6. Structure audit records around the `run_id`.
7. Write log output and XML report separately, each for its audience.
8. Register: executable, program, parameters, permissions, schedule.
9. Test VALIDATE_ONLY first, then PROCESS, then ROLLBACK.

## Anti-Patterns

- Direct DML on PO/AP/INV base tables for "speed".
- 10,000 rows in one transaction.
- Error logging via `DBMS_OUTPUT` only.
- Rerunning the whole program instead of resuming.
- No `org_id` filter, silently processing all business units.
- Packing 10,000 result rows into the concurrent program log.
- Deploying the package without registering submit permissions.
- VALIDATE_ONLY as a separate reimplementation of validation logic.

## Summary

The 3-day process became under an hour through structure, not cleverness:
one program with parameter-driven modes, validation factored out so VALIDATE_ONLY
is a genuine rehearsal, standard APIs instead of unsupported inserts, batching
with a resumable commit strategy, an autonomous-transaction error log that
survives failure, MOAC enforced rather than assumed, and audit records keyed by
run ID so ROLLBACK is a lookup rather than an archaeology project.