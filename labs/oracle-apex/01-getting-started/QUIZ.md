# Quiz: APEX Getting Started — CRUD with Interactive Report + Form

Test your understanding of building a first APEX expense-tracker app (see `PROBLEM_WALKTHROUGH.md`).

## Questions

1. Which two page types do you create from the Create Application wizard for the expenses CRUD prototype?
2. What is the purpose of the `expense_seq` sequence?
3. Why are indexes created on `expense_date`, `department_id`, `category`, and `status`?
4. In the Interactive Report SQL, what does `WHERE e.department_id = NVL(:G_DEPT_ID, e.department_id)` accomplish?
5. How do you link an Interactive Report row to its edit Form?
6. What does setting the Form page to Modal Dialog change for the user experience?
7. Which processing type saves the Form (insert/update) without hand-written DML?
8. Write the intent of the duplicate-check validation in one sentence.
9. What are the two summary chart queries on the Dashboard page (give label/value shape)?
10. Why is a materialized view (`mv_expense_summary`) suggested for the dashboard?

## Answers

1. **Interactive Report** (on `EXPENSES`) and **Form** (on `EXPENSES`, linked), plus a departments report and a blank Dashboard page.
2. Generates surrogate primary keys (`expense_id`) via `expense_seq.NEXTVAL` so inserts never collide.
3. They accelerate the report's filter/sort/order columns and keep the 2-second SLA on 10,000 rows.
4. Row-level security: a manager sees only their department (`:G_DEPT_ID`); when the item is NULL (e.g. admin) all rows show.
5. Set the Expense ID column as a **Link Column** targeting Page 2 with `P2_EXPENSE_ID` = `#EXPENSE_ID#`.
6. The form opens as an overlay dialog; user stays in report context, Cancel/close returns without full navigation.
7. **Automatic Row Processing (DML)** — Fetch Row on load + DML process on submit handles INSERT vs UPDATE by PK.
8. It counts rows with identical category/amount/date/description (excluding the current PK) and rejects the submit if count > 0.
9. Pie: `SELECT category AS label, SUM(amount) AS value ... GROUP BY category`; Bar: `SELECT TO_CHAR(expense_date,'YYYY-MM') AS label, SUM(amount) AS value ... GROUP BY month`.
10. Pre-aggregates counts/totals by department/category/month so charts read one small object instead of scanning `expenses` every load.
