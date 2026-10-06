# Lab 05: HRMS Data Migration — Exercises

## Exercise 1: Build the Staging Layer
**Time**: 20 minutes | **Difficulty**: Beginner

### Objective
Create staging that preserves raw source values.

### Steps
1. Create `xx_stage_people` with raw string and derived date columns.
2. Create `xx_stage_assignments` similarly.
3. Create the error table with domain, code, value, and rule.
4. Load 20 sample records including four defect types.

### Verification
- [ ] Raw values preserved alongside parsed ones
- [ ] Error table supports grouping by domain and code
- [ ] Defects staged, not lost

---

## Exercise 2: Write Domain Validators
**Time**: 30 minutes | **Difficulty**: Intermediate

### Objective
Implement validators that produce actionable errors.

### Steps
1. Implement the person validator (name, DOB plausibility).
2. Implement the identifier validator.
3. Emit one error per violated rule with field, value, and expectation.
4. Aggregate the error report by domain.

### Verification
- [ ] Multiple rules checked per record, not one "invalid" verdict
- [ ] Every error carries field, value, and rule text
- [ ] Grouping shows which domain dominates

---

## Exercise 3: Date Parsing and Ambiguity Rejection
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Parse dates correctly and reject ambiguity.

### Steps
1. Handle ISO (`YYYY-MM-DD`) and dotted (`DD.MM.YYYY`) forms.
2. For slash forms, test whether either component exceeds 12.
3. Reject both-≤12 cases with `AMBIGUOUS_DATE`.
4. Feed 10 cases including `03/04/2026` and verify rejection.

### Verification
- [ ] Unambiguous cases parsed correctly both directions
- [ ] `03/04/2026` rejected, not guessed
- [ ] Error message names the row and the missing metadata

---

## Exercise 4: Identifier Checksum Validation
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Catch invalid identifiers that pass shape validation.

### Steps
1. Implement shape regexes for 3 countries.
2. Implement an NRIC checksum test.
3. Feed 20 identifiers; count shape-passes that fail checksum.
4. Report both counts separately.

### Verification
- [ ] Shape and checksum reported as distinct outcomes
- [ ] At least one record passes shape but fails checksum
- [ ] Explanation given for why shape alone is insufficient

---

## Exercise 5: Overlap Detection
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Detect overlapping assignments without auto-fixing.

### Steps
1. Self-join on employee number where date ranges intersect.
2. Emit `OVERLAPPING_ASSIGNMENT` errors with both ranges.
3. Route to HR for classification rather than resolving automatically.
4. After HR confirmation, apply the resolution.

### Verification
- [ ] Overlaps detected by interval intersection
- [ ] No automatic truncation occurs
- [ ] Classification step is visibly a business decision

---

## Exercise 6: Dependency Order with Assertion
**Time**: 30 minutes | **Difficulty**: Intermediate

### Objective
Prove the load order matters and detect violating it.

### Steps
1. Load people only.
2. Run the unresolved-manager assertion; record the count.
3. Attempt to link supervisors before assignments; observe the silent failure.
4. Load assignments, then link supervisors, then re-run the assertion.

### Verification
- [ ] Assertion returns non-zero before assignments exist
- [ ] Silent failure (zero rows updated) is recognised as the signal
- [ ] Assertion returns zero after the correct sequence

---

## Exercise 7: Placeholder Strategy
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Preserve hierarchy for orphaned manager references.

### Steps
1. Identify manager IDs referenced but absent.
2. Create one placeholder person per missing ID.
3. Mark them with a `PLACEHOLDER` name and identifier.
4. List them on an exception report with owners.

### Verification
- [ ] Hierarchy intact — zero unresolved managers
- [ ] Placeholders unmistakably marked
- [ ] Exception report names an owner and due date per placeholder

---

## Exercise 8: Four-Way Reconciliation and Cycle Detection
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Verify the migration on four axes and prove the hierarchy is sane.

### Steps
1. Check counts per domain (loaded vs expected).
2. Check for orphan managers.
3. Check for overlapping assignments.
4. Spot-check a sample sized for 95% confidence.
5. Run recursive cycle detection with depth bound.

### Verification
- [ ] All four checks written and passing
- [ ] Sample size justified by calculation, not chosen arbitrarily
- [ ] Cycle detection returns no unexpected deep paths
- [ ] Every threshold is zero, not "within tolerance"

---

## Exercise 9: Idempotency and Re-run Safety
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Prove a re-run creates no duplicates.

### Steps
1. Record row counts after a full load.
2. Re-run pass 1 and pass 2.
3. Compare counts.
4. Verify no duplicate person or assignment rows exist.

### Verification
- [ ] Re-run produces zero new rows
- [ ] Duplicate detection query returns zero
- [ ] Resume-after-failure batching demonstrated