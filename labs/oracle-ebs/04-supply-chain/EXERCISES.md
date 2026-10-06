# Lab 04: Supply Chain (Cycle Counting) — Exercises

## Exercise 1: Build the ABC Classification
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Classify SKUs by annual dollar usage with cumulative percentages.

### Steps
1. Sum 12 months of `transaction_quantity × actual_cost_per_unit`.
2. Exclude intercompany segments from costing.
3. Rank descending and compute cumulative percentage.
4. Assign A/B/C at the 80% and 95% cumulative boundaries.

### Verification
- [ ] Cumulative percentage computed correctly
- [ ] ~80% of value lands in ~20% of SKUs
- [ ] A/B/C boundary counts reported

---

## Exercise 2: Overlay Movement
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Find items pure ABC under-protects.

### Steps
1. Count transactions per item over 3 months.
2. Join to the ABC result.
3. Identify mid-value items with high transaction counts.
4. Rank them as `ELEVATED` risk despite a B or C class.

### Verification
- [ ] At least two under-protected items identified
- [ ] Risk rank combines value and movement
- [ ] Explanation given for why ABC alone misses them

---

## Exercise 3: Derive Count Frequency
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Compute a max count interval from materiality arithmetic.

### Steps
1. Take the highest-value A item: note monthly throughput.
2. Apply `Interval ≤ Materiality / (disc_rate × monthly_value)`.
3. Show the arithmetic step by step.
4. Compare the derived interval with the "A = monthly" default.

### Verification
- [ ] Formula applied correctly with units shown
- [ ] Derived interval stated
- [ ] Comparison with default convention discussed

---

## Exercise 4: Build the Rotation Schedule
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Create a count schedule across 3 warehouses and 4 weeks.

### Steps
1. Define counts per ABC class and warehouse.
2. Rotate the assigned counter, not just the location.
3. Vary the time of day.
4. Write the rotation view and confirm each week is covered.

### Verification
- [ ] Every warehouse appears in the rotation
- [ ] Counters are rotated, not fixed
- [ ] Coverage in a 4-week cycle is complete

---

## Exercise 5: Configure Tolerance Correctly
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Set tolerance with both percentage and value caps.

### Steps
1. Define A/B/C tolerances: 0.5% / 2% / 5%.
2. Add absolute value caps: $5,000 / $2,000 / $500.
3. Create three test variances: within %, over %, within % but over value.
4. Confirm the approval path for each.

### Verification
- [ ] Percentage escalation works
- [ ] Value-cap escalation works independently
- [ ] The third case escalates despite passing the percentage test

---

## Exercise 6: Implement the Scanner Path
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Capture counts by barcode with validation.

### Steps
1. Resolve a barcode to an inventory item.
2. Find the open count record for that item and subinventory.
3. Record the count quantity and an audit row.
4. Test an unknown barcode and capture the error.
5. Test a duplicate scan and confirm it does not double-count.

### Verification
- [ ] Valid barcode updates the count
- [ ] Unknown barcode raises an error
- [ ] Duplicate scan is idempotent or explicitly flagged

---

## Exercise 7: Enforce Root Cause Coding
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Make cause coding structurally mandatory.

### Steps
1. Create `xx_count_discrepancy` with a cause code check constraint.
2. Make `root_cause_code` `NOT NULL`.
3. Attempt to close a variance discrepancy with no code; capture the error.
4. Record all 20 coded discrepancies and run the Pareto.

### Verification
- [ ] Check constraint restricts codes to the allowed list
- [ ] Uncoded closure fails
- [ ] Pareto shows cumulative percentages

---

## Exercise 8: Build the Accuracy Dashboard
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Track accuracy by class and build the programme health check.

### Steps
1. Write the monthly accuracy query grouped by ABC class.
2. Compare against targets (A 98%, B 95%, C 90%).
3. Write the health check flagging stale open counts and uncoded discrepancies.
4. Produce the value-at-risk query with and without the programme.

### Verification
- [ ] Accuracy computed as zero-variance items / counted
- [ ] Targets compared per class
- [ ] Health check flags both failure modes
- [ ] Business-case figure uses recovered loss, not labour saving

---

## Exercise 9: Diagnose the Dominant Cause
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Determine whether the problem is counting or security.

### Steps
1. Code 20 discrepancies with root causes.
2. Run the cause Pareto by value.
3. If `CYCLE_SHRINK` dominates, write the security recommendation.
4. Explain why additional counting will not fix it.

### Verification
- [ ] Cause distribution quantified by value
- [ ] Correct root problem identified
- [ ] Recommendation routed to the right owner, not to operations