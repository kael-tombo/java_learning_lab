# EBS HRMS — Mini Project

## Goal
Onboard, adjust, and offboard a small employee population through HRMS in
90 minutes, then run a payroll that reflects the changes.

## Requirements
- R1: Tables/models for person, assignment, and position for 10 employees.
- R2: Effective-dated records demonstrating at least one assignment change.
- R3: A query contrasting `_F` (history) with `_V` (current) behaviour.
- R4: Payroll elements for a salary and two deductions.
- R5: A payroll run producing net pay per employee.
- R6: A time entry and an absence record affecting the payroll result.
- R7: Benefits enrollment with one eligibility rule enforced.
- R8: An offboarding checklist that ends in an inactive person record.

## Steps
1. Create the organizational structure and positions.
2. Hire 10 employees with effective-dated person and assignment records.
3. Transfer one employee mid-period and observe both history and current state.
4. Query `_F` and `_V` and explain the difference in your notes.
5. Define payroll elements and link them to the earnings/deduction types.
6. Run a payroll and record gross, deductions, and net per employee.
7. Add a time entry and an absence; re-run and compare the results.
8. Enroll in benefits, test the eligibility rule, then offboard one employee.

## Acceptance criteria
- The `_F` vs `_V` explanation is backed by a query that demonstrates it.
- The payroll result changes correctly after the time and absence entries.
- The eligibility rule rejects at least one enrolment attempt.
- The offboarded employee is inactive, not deleted, with history intact.

## Stretch
- Add a legislative data group and show one behaviour that differs.
- Build a query listing everyone with a gap in their assignment history.