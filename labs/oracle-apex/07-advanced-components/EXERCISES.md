# Lab 07: APEX Advanced Components — Exercises

## Exercise 1: IG or IR
**Time**: 20 minutes | **Difficulty**: Beginner

### Objective
Choose the component from the editing question.

### Steps
1. List eight APEX use cases.
2. Classify each as IG or IR from the editing requirement alone.
3. Identify which two would be wrong either way.
4. State the cost of choosing wrong in each direction.

### Verification
- [ ] All eight classified
- [ ] Justification based on editing, not preference
- [ ] Both misclassification costs described

---

## Exercise 2: Primary Key Requirement
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Prove editing requires row addressability.

### Steps
1. Build an IG over a keyless query; enable editing.
2. Attempt a save and record the behaviour.
3. Add a key column and configure it as the IG primary key.
4. Confirm editing now works.

### Verification
- [ ] Keyless behaviour captured
- [ ] Behaviour after key configuration captured
- [ ] Explanation given for why a synthetic key is a warning sign

---

## Exercise 3: Cell Validation Feedback
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Make errors surface during editing.

### Steps
1. Add three cell validations.
2. Enter a bad value and confirm immediate feedback.
3. Compare against the equivalent row validation.
4. Time how long each takes to resolve.

### Verification
- [ ] Cell validations fire during editing
- [ ] Messages name the entered value
- [ ] Resolution time compared and the difference explained

---

## Exercise 4: Row Validation for a Cross-Row Rule
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Enforce a rule that spans rows.

### Steps
1. Write an order-level discount rule that cannot be a cell rule.
2. Implement it as a row validation.
3. Test that it fires on Save, not during editing.
4. Explain why it cannot be moved to cell level.

### Verification
- [ ] Rule implemented at row level
- [ ] Firing timing confirmed
- [ ] Explanation given for why the rule needs multiple rows

---

## Exercise 5: Computed Column Recalculation
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Recalculate a derived column without persisting it.

### Steps
1. Add a computed `line_total` column.
2. Write the JavaScript to recalculate on cell change.
3. Handle the new-row case.
4. Confirm the value is never written to the table.

### Verification
- [ ] Recalculation fires on each relevant cell change
- [ ] New rows initialise correctly
- [ ] Database confirms no stored computed column
- [ ] Explanation given for why storing it risks disagreement

---

## Exercise 6: Save Row Guard
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Refuse an unreasonably large submission.

### Steps
1. Build the save process with a 500-row guard.
2. Submit 50 rows; confirm it saves.
3. Submit 600 rows; confirm refusal with a clear message.
4. Confirm no partial state exists after refusal.

### Verification
- [ ] Normal save works
- [ ] Over-limit submission refused with a specific message
- [ ] No partial or inconsistent state
- [ ] Explanation given for why refusing beats attempting

---

## Exercise 7: Master-Detail Grid Pair
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Link two grids through the master's selection.

### Steps
1. Build the master IG with an aggregated summary.
2. Add the Dynamic Action on selection to set the item and refresh.
3. Build the detail IG bound to that item.
4. Confirm no page submission occurs.

### Verification
- [ ] Detail loads the selected order's lines
- [ ] No page submission
- [ ] Detail cannot address another order's rows
- [ ] Latency compared against a submit-based approach

---

## Exercise 8: Per-User State Management
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Persist layout preferences without unbounded growth.

### Steps
1. Enable saved state and change a layout.
2. Reopen and confirm the layout persisted.
3. Break the layout; test the reset action.
4. Write and run the tidying query.

### Verification
- [ ] State persists across sessions
- [ ] Reset restores the default layout
- [ ] Tidying removes stale state without affecting active sessions
- [ ] State size measured

---

## Exercise 9: Control Break and Aggregation
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Add rollups without extra regions.

### Steps
1. Add a control break on category.
2. Add SUM and COUNT aggregations.
3. Change the grouping interactively; confirm no page round trip.
4. Enable the chart view and compare against a separate chart region.

### Verification
- [ ] Control break and aggregations work
- [ ] Grouping changes without a round trip
- [ ] Comparison of IG chart view versus a separate region documented
- [ ] Explanation given for which suits exploration and which suits communication

---

## Exercise 10: Plugin Versus Shared Component
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Decide when a plugin earns its cost.

### Steps
1. Build a behaviour on one page as a Dynamic Action.
2. Reuse it on a second page as a shared component.
3. Package it as a plugin and install it.
4. Compare the cost of each against the reuse count.

### Verification
- [ ] Plugin builds and installs
- [ ] No framework file copied
- [ ] Cost per approach computed against reuse count
- [ ] Break-even upgrade count stated

---

## Exercise 11: Chart Data Limits
**Time**: 20 minutes | **Difficulty**: Intermediate

### Objective
Keep a chart legible.

### Steps
1. Build a JET chart over 400 daily points; measure render time.
2. Aggregate to monthly; measure again.
3. Compare legibility.
4. Add a 12-point cap to the SQL.

### Verification
- [ ] Both render times measured
- [ ] Legibility difference documented
- [ ] SQL-level cap implemented
- [ ] Explanation given for why the cap belongs in the query