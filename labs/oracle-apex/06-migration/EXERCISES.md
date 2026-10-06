# Lab 06: APEX Migration — Exercises

## Exercise 1: Build the Inventory
**Time**: 30 minutes | **Difficulty**: Intermediate

### Objective
Produce an accurate object inventory from the source.

### Steps
1. Query the Forms source for objects by type.
2. Count triggers by category: POST-QUERY, KEY-QUERY, WHEN-NEW, PRE-DML,
   WHEN-BUTTON.
3. Count LOVs, alerts, menus, and form procedures.
4. Compare against a screen-count estimate.

### Verification
- [ ] Inventory produced by query, not interview
- [ ] Trigger counts by category recorded
- [ ] Screen-count estimate compared and the ratio stated
- [ ] Highest-volume trigger category identified

---

## Exercise 2: Classify Every Object
**Time**: 30 minutes | **Difficulty**: Intermediate

### Objective
Assign each object to 1:1, simplified, redundant, or new.

### Steps
1. Build the mapping table.
2. Classify each object with a written justification.
3. Confirm every REDUNDANT classification with a real user.
4. Compute the redundant percentage and its effort share.

### Verification
- [ ] Every object classified with justification
- [ ] Redundant items confirmed with users before deletion
- [ ] Percentage and effort share computed
- [ ] Explanation given for why 1:1 for everything is the wrong target

---

## Exercise 3: Delete a POST-QUERY
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Absorb a per-record lookup into region SQL.

### Steps
1. Read the POST-QUERY trigger and identify what it populates.
2. Write the region query with the equivalent join.
3. Remove the trigger from the mapping as DELETED.
4. Count queries for 50 records before and after.

### Verification
- [ ] Trigger logic fully absorbed, not partially
- [ ] Query count reduced from 50 to 1 for 50 records
- [ ] Mapping records the deletion with a reason
- [ ] No per-record trigger remains

---

## Exercise 4: Convert WHEN-NEW-ITEM-INSTANT
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Replace a client-tier item default with a Dynamic Action.

### Steps
1. Read the trigger and identify the event and the effect.
2. Build the Dynamic Action: event, condition, and Set Value action.
3. Add the non-null condition so it does not overwrite manual entry.
4. Test that it fires on change but not on refresh.

### Verification
- [ ] Event and condition correct
- [ ] Does not clear a value the user entered manually
- [ ] Does not fire spuriously on page refresh
- [ ] Behaviour matches the Forms trigger

---

## Exercise 5: PRE-DML Validation to Two Homes
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Enforce validation in the database and explain it in APEX.

### Steps
1. Identify the Forms validation level for the rule.
2. Create the database constraint.
3. Add the APEX page validation with a message naming the bad value.
4. Test both paths: the UI and a direct SQL insert.

### Verification
- [ ] Constraint exists and rejects a direct insert
- [ ] APEX validation gives an actionable message
- [ ] Constraint coverage before and after is identical
- [ ] Explanation given for why constraint coverage must not drop

---

## Exercise 6: Return-Value LOV
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Replace Forms LOV return-value assignment with a Dynamic Action.

### Steps
1. Identify which items the Forms LOV returns values to.
2. Build the APEX popup LOV with a depends-on item.
3. Add a Dynamic Action on selection to set the dependent item.
4. Test with a filtered LOV so the filter behaviour is verified.

### Verification
- [ ] Dependent item populates on selection
- [ ] Filtering behaves as users expect
- [ ] No reliance on Forms-style automatic assignment
- [ ] Failure mode (no selection) handled

---

## Exercise 7: Redesign Navigation
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Replace a 4-level Forms menu with a workable APEX structure.

### Steps
1. List the Forms menu tree.
2. Identify how users actually navigate.
3. Design breadcrumbs (max 3 levels) and a flat navigation menu.
4. Validate the design with two real users.

### Verification
- [ ] Breadcrumbs within 3 levels
- [ ] Navigation menu items reduced to a findable number
- [ ] Validated with users who do the work daily
- [ ] Cost of copying the tree versus redesigning stated

---

## Exercise 8: Stage the Cutover
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Sequence delivery so each stage is independently valuable.

### Steps
1. Classify pages by risk: read-only, CRUD, complex transaction.
2. Build the stage plan with durations.
3. Define the parallel-run comparison approach.
4. Define the cutover gate.

### Verification
- [ ] Read-only first, complex transactions last
- [ ] Each stage delivers standalone value
- [ ] Cutover gate is on stop-the-line discrepancies, not all discrepancies
- [ ] Rollback strategy stated per stage

---

## Exercise 9: Parallel-Run Discrepancy Triage
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Distinguish real bugs from cosmetic differences.

### Steps
1. Generate 100 comparison records with a realistic defect mix.
2. Classify each discrepancy: cosmetic, timing, logic, or data-written.
3. Identify which require cutover to be blocked.
4. Compute the expected rate of each category.

### Verification
- [ ] Every discrepancy classified
- [ ] Cosmetic differences correctly separated from logic errors
- [ ] Stop-the-line cases identified
- [ ] Explanation given for why a zero-discrepancy gate never ends