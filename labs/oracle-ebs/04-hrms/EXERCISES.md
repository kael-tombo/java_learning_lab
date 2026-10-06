# Lab 04: Employee Lifecycle Management (HRMS) — Exercises

## Exercise 1: Model the State Machine
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Draw the lifecycle with entry/exit criteria and side effects per state.

### Steps
1. Define states: OFFER, ACTIVE, TERMINATED, ALUMNI.
2. For each, write entry criteria, exit criteria, and side effects.
3. Mark which transitions are currently manual.
4. Identify which manual step has the highest error risk.

### Verification
- [ ] Every state has all three attributes written
- [ ] Side effects listed for HIRE and TERMINATE
- [ ] Highest-risk manual step named and justified

---

## Exercise 2: Effective Dating in Practice
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Load 10 employees and future-date one transfer.

### Steps
1. Create person and assignment records with effective dates.
2. Transfer one employee effective next month via the API.
3. Query `PER_ALL_ASSIGNMENTS_F` for that person — expect two rows.
4. Confirm the current row has `effective_end_date` set.

### Verification
- [ ] Two assignment rows exist after the transfer
- [ ] The closed row retains its original position
- [ ] No `UPDATE` was issued against a current assignment row

---

## Exercise 3: `_F` versus `_V`
**Time**: 20 minutes | **Difficulty**: Beginner

### Objective
Prove history and current state differ.

### Steps
1. Run the `_F` query filtered to today's date.
2. Run the `_V` query for the same person.
3. Run `COUNT(*)` versus `COUNT(DISTINCT person_id)` on `_F`.
4. Explain which is correct for headcount and why.

### Verification
- [ ] `COUNT(*)` vs `COUNT(DISTINCT)` difference quantified
- [ ] Correct query identified for headcount as at a past date
- [ ] Overstatement percentage explained

---

## Exercise 4: Build an Idempotent Cascade
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Implement the trigger engine and prove retry safety.

### Steps
1. Create the action table with a unique constraint.
2. Implement `raise_event` using `MERGE`.
3. Fire a HIRE event twice.
4. Confirm exactly four actions exist, not eight.

### Verification
- [ ] Second fire creates no duplicates
- [ ] Unique constraint present as the backstop
- [ ] Each action independently retryable

---

## Exercise 5: Legislative Termination
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Terminate employees in two countries with different notice rules.

### Steps
1. Configure notice periods for two legislation codes.
2. Terminate one employee per country.
3. Confirm notice days differ and come from configuration.
4. Confirm the assignment is closed, not deleted.

### Verification
- [ ] Notice days differ per country
- [ ] Values read from configuration, not literals
- [ ] Person record and history still queryable after termination

---

## Exercise 6: Payroll Integration and Reconciliation
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Build the outbound payload and detect a missing ADP response.

### Steps
1. Build the hire payload as XML/JSON.
2. Create a mock inbound response with one record deliberately missing.
3. Run the reconciliation query.
4. Confirm the missing employee is flagged, not silently dropped.

### Verification
- [ ] Payload contains the required identifying fields
- [ ] Reconciliation flags the missing record
- [ ] Gross pay totals query returns a variance column

---

## Exercise 7: Self-Service Promotion with Approval
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Route a promotion for skip-level approval.

### Steps
1. Define validation: manager must be current manager as at today.
2. Define the grade matrix and budget check.
3. Configure skip-level routing for grade increases.
4. Test a promotion that should and should not escalate.

### Verification
- [ ] Non-manager request rejected
- [ ] Skip-level trigger fires at the right threshold
- [ ] Approved change applied effective-dated via the API

---

## Exercise 8: Offboarding Checklist and Overdue Detection
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Generate the checklist and find overdue items.

### Steps
1. Seed the standard 7-task checklist with due-date offsets.
2. Terminate an employee so the checklist is generated.
3. Run the overdue query.
4. Confirm `REVOKE_SSO` is scheduled for D+0, not D+1.

### Verification
- [ ] Each task has an owner and a due date
- [ ] Overdue detection works
- [ ] Access revocation is same-day, with the risk quantified