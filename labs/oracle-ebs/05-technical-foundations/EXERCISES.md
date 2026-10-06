# Lab 05: Technical Foundations — Exercises

## Exercise 1: Multi-Mode Design
**Time**: 20 minutes | **Difficulty**: Beginner

### Objective
Design parameter-driven mode dispatch.

### Steps
1. Define VALIDATE_ONLY, PROCESS, ROLLBACK behaviours.
2. Specify what each mode guarantees and what it must never do.
3. Write the dispatch logic.
4. State why one program beats three.

### Verification
- [ ] Each mode's guarantees stated
- [ ] VALIDATE_ONLY makes no business-data DML
- [ ] ROLLBACK requires a run ID parameter
- [ ] Rationale for one program vs three given

---

## Exercise 2: Pure Validation Unit
**Time**: 30 minutes | **Difficulty**: Intermediate

### Objective
Implement validation with no business-data side effects.

### Steps
1. Implement four rules (supplier exists, item active, price > 0, date valid).
2. Log each violation with code, field, and message.
3. Mark lines VALID or ERROR; never modify business tables.
4. Prove purity by snapshotting business data before and after.

### Verification
- [ ] Four rules implemented with distinct error codes
- [ ] Business tables provably unchanged after VALIDATE_ONLY
- [ ] Every error names field, value, and expectation

---

## Exercise 3: Batched Processing with Audit
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Process with bounded undo and a complete audit trail.

### Steps
1. Implement `process` with 500-row batching.
2. Insert an audit row per change with old and new values.
3. Commit per batch and update run progress.
4. Compare processed count against audit row count.

### Verification
- [ ] Commits occur at batch boundaries
- [ ] Audit count equals processed count exactly
- [ ] Undo growth bounded (check with V$TRANSACTION if available)

---

## Exercise 4: Resume After Failure
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Prove a rerun does not duplicate committed work.

### Steps
1. Force a failure at row ~1,200.
2. Confirm batches before the failure are committed.
3. Rerun and confirm only unprocessed rows are handled.
4. Verify the final processed count equals the original target.

### Verification
- [ ] Committed batches survive the failure
- [ ] Rerun processes zero already-processed rows
- [ ] No duplicate audit rows created

---

## Exercise 5: Durable Error Logging
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Make the error log survive an unhandled exception.

### Steps
1. Implement `log_error` with `PRAGMA AUTONOMOUS_TRANSACTION`.
2. Force an unhandled exception mid-run.
3. Query `xx_run_error` immediately — rows must be present.
4. Remove the pragma and repeat; observe the difference.

### Verification
- [ ] Errors present after failure with the pragma
- [ ] Errors absent without it (demonstrating why it matters)
- [ ] Logging never breaks the caller

---

## Exercise 6: MOAC Enforcement
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Enforce operating-unit access and fail loudly.

### Steps
1. Implement `set_moac_context` with an access check.
2. Run with access present; confirm it succeeds.
3. Revoke access and rerun; confirm the error.
4. Show what would happen without the check.

### Verification
- [ ] Access verified before processing
- [ ] Absent access raises a clear error
- [ ] Consequence of omitting the check quantified

---

## Exercise 7: XML Report with Escaping
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Produce well-formed XML output.

### Steps
1. Build the XML with summary, line results, and errors.
2. Insert a supplier name containing `&` and `<`.
3. Validate the output parses as XML.
4. Confirm the escaping is applied.

### Verification
- [ ] XML validates as well-formed
- [ ] Special characters escaped correctly
- [ ] Log and XML report serve different audiences

---

## Exercise 8: Registration and Permissions
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Register the program completely, including submit permissions.

### Steps
1. Register application, executable, and program.
2. Add parameters with token substitution.
3. Assign the program to a test responsibility.
4. Submit as that test user; confirm it runs.

### Verification
- [ ] All registration steps performed
- [ ] Parameters substitute tokens correctly
- [ ] A non-developer account can submit successfully

---

## Exercise 9: Rollback Rehearsal
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Reverse a completed run and verify restoration.

### Steps
1. Record original values for all target records.
2. Run PROCESS on 2,000 lines.
3. Run ROLLBACK referencing the run ID.
4. Compare every value against the original snapshot.

### Verification
- [ ] All values restored exactly
- [ ] Rollback executed in reverse application order
- [ ] A rollback audit record created for each reversal