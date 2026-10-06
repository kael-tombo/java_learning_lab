# Lab 05: Technical Foundations (Custom Concurrent Program) — VISION

## Where this lab takes you
From a 3-day manual price list update to an under-hour concurrent program that
can validate before it processes, resume after failure, and roll back on command.

## The Arc
1. **Unit of work** — the concurrent program as an operational unit, not a script.
2. **Modes** — parameter-driven behaviour with one source of validation truth.
3. **Validation isolation** — a pure, callable unit so VALIDATE_ONLY is honest.
4. **API discipline** — correctness over the 1.5% runtime overhead.
5. **Batching** — bounded undo, bounded restart cost, resumable.
6. **Error durability** — autonomous transactions so the log survives failure.
7. **MOAC** — fail loudly rather than process the wrong operating units.
8. **Audit** — keyed by run ID so rollback is a lookup.

## Milestones (checkable)
- [ ] M1: Design the mode dispatch so VALIDATE_ONLY calls the same validation.
- [ ] M2: Implement `validate` as a pure procedure with no business-data DML.
- [ ] M3: Process 10,000 lines with batched commits and measured throughput.
- [ ] M4: Demonstrate resume: interrupt a run and restart it from the batch boundary.
- [ ] M5: Prove the error log survives an unhandled exception.
- [ ] M6: Enforce MOAC and show it raising an error with access removed.
- [ ] M7: Generate the XML report with proper escaping, verified as well-formed.
- [ ] M8: Register the program including responsibility assignment, tested as an operator.

## Anti-Goals
- Using direct DML on `PO_HEADERS_ALL` because APIs are "too slow".
- Holding 10,000 API calls in one transaction.
- Logging errors with `DBMS_OUTPUT` only.
- Rerunning the whole program instead of resuming.
- Omitting `org_id` filters and relying on MOAC to catch it.
- Packing 10,000 result rows into the concurrent program log.
- Deploying the package without testing submit permissions.

## The one-sentence thesis
Production-grade means the failure path is as carefully designed as the success
path — validate before you process, batch so you can resume, log durably, and
audit so you can reverse.