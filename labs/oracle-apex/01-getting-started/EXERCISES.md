# Exercises: APEX Getting Started — Expense Tracker

Grounded in `PROBLEM_WALKTHROUGH.md` (expenses + departments schema).

## 1. Schema + Seed (warm-up)
Create `expenses`, `departments`, `expense_seq`, and the four indexes. Insert the 4 departments and 8 sample expenses.
*Hint:* Copy Step 1 SQL; verify with `SELECT COUNT(*) FROM expenses;` → 8.

## 2. Report Query with Row-Level Security
Write the IR source query joining `expenses e` to `departments d`, filtering `e.department_id = NVL(:G_DEPT_ID, e.department_id)`, ordered by date DESC. Add the `BETWEEN NVL(:P1_DATE_FROM,...)` date-range predicate.
*Check:* As `G_DEPT_ID=10` you see only Engineering rows.

## 3. Duplicate Validation Function
Implement the PL/SQL Function Returning Boolean that blocks identical category/amount/date/description (excluding current `P2_EXPENSE_ID`). Test by inserting a duplicate → expect "A matching expense record already exists."
*See:* `WORKED_EXAMPLE.sql` §2 for a runnable version.

## 4. Dashboard Aggregates
Write the three dashboard queries: summary stats (`COUNT/SUM/AVG/MIN/MAX`), pie by category, bar by `YYYY-MM`. Run each in SQL Workshop and confirm totals match `SELECT SUM(amount) FROM expenses;`.
*Stretch:* Build `mv_expense_summary` and rewrite the pie query against it.

## 5. Security Hardening (challenge)
Add application item `G_DEPT_ID` + After-Authentication computation (`WHERE manager_email = :APP_USER`), apply the `NVL` filter to every report, and restrict the Departments page with an "Is Manager" authorization scheme. Log in as two managers and confirm isolation.

Worked solution starter: see `WORKED_EXAMPLE.sql`.
