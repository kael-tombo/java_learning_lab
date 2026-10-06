# Lab 03: Financials — Exercises

## Exercise 1: Build the Hold Taxonomy
**Time**: 20 minutes | **Difficulty**: Beginner

### Objective
Rank hold reasons by invoice count and value at risk.

### Steps
1. Run the hold taxonomy query against `AP_HOLDS_ALL`.
2. Join `AP_HOLDS_ALL` to `AP_HOLD_CODES` for readable reasons.
3. Record count and value per reason.
4. Compute the cumulative percentage by value.

### Verification
- [ ] Top reason identified with count and value
- [ ] Cumulative percentage calculated
- [ ] Top 2 reasons account for a stated share of value

---

## Exercise 2: Prove the Matching Basis
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Show that invoiced quantity equals received but differs from ordered.

### Steps
1. Run the ordered/received/invoiced comparison query.
2. Identify invoices where `invoiced = received ≠ ordered`.
3. Confirm these are the quantity-held invoices.
4. State the root cause in one sentence.

### Verification
- [ ] Comparison query returns concrete examples
- [ ] Root cause identified as basis mismatch, not supplier error
- [ ] Explanation distinguishes short shipment from over-invoicing

---

## Exercise 3: Derive the Price Tolerance
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Choose a price variance tolerance from the measured distribution.

### Steps
1. Run the price variance distribution query.
2. Build the cumulative percentage view.
3. Identify where cumulative crosses 97–98%.
4. Propose a tolerance and justify it.

### Verification
- [ ] Distribution and cumulative computed from data
- [ ] Tolerance sits above the noise band
- [ ] Large variances confirmed still outside tolerance
- [ ] Justification is auditor-defensible wording

---

## Exercise 4: Change the Matching Rule
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Reconfigure matching to use received quantity and measure the effect.

### Steps
1. Document the current matching configuration.
2. Change the matching basis to received quantity.
3. Re-run the same hold taxonomy query.
4. Compare hold counts before and after.

### Verification
- [ ] Before/after counts recorded with the same query
- [ ] Quantity holds reduced substantially
- [ ] Over-invoice holds still raised (test one)

---

## Exercise 5: Test the Control Still Works
**Time**: 20 minutes | **Difficulty**: Advanced

### Objective
Prove the remediation did not weaken three-way match.

### Steps
1. Create a deliberate 30% over-invoice against a receipt.
2. Validate it and record the outcome.
3. Confirm a hold is raised.
4. Repeat with a 3% variance and confirm it passes.

### Verification
- [ ] Over-invoice test raises a hold
- [ ] Small variance test validates cleanly
- [ ] Conclusion states control strength is preserved

---

## Exercise 6: Build the Batch Release Package
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Create a package that releases holds with mandatory reason codes.

### Steps
1. Create `xx_ap_hold_release_pkg` with the signature.
2. Implement the candidate cursor with narrow, explicit criteria.
3. Call `ap_holds_pkg.release_hold` with a reason code.
4. Add exception handling that logs rather than aborts.
5. Write every release to an audit table.

### Verification
- [ ] No code path releases without a reason
- [ ] Audit table has `NOT NULL` on `release_reason`
- [ ] Failure of one release does not abort the batch
- [ ] Insert without a reason fails at the database level

---

## Exercise 7: Route Holds with Workflow
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Send held invoices to the right approver automatically.

### Steps
1. Define routing rules by value threshold and category.
2. Assign notifications for buyer and AP approver.
3. Add escalation after N hours.
4. Test with three invoices at different values.

### Verification
- [ ] Routing table defined and documented
- [ ] Each test invoice reached the correct approver
- [ ] Escalation triggers after the configured interval

---

## Exercise 8: Build the Regression Dashboard
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Track hold rate and escape rate so regressions are caught.

### Steps
1. Write the hold rate query with a rolling 3-month window.
2. Write the escape rate query.
3. Add an alert threshold at 10% hold rate.
4. Schedule it as a concurrent program.

### Verification
- [ ] Hold rate and escape rate both reported
- [ ] Alert threshold stated and justified
- [ ] Query performs acceptably on production volume (check the plan)