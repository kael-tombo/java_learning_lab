# Lab 01: APEX Getting Started — Mini Project

## Goal
Build a department expense tracking application — Interactive Report, form page,
and row-level security — in 90 minutes.

## Requirements
- R1: Schema tables for departments, users, and expenses.
- R2: An Interactive Report listing expenses with sorting, filtering, search.
- R3: A form page supporting create, edit, and delete with confirmation.
- R4: Navigation between list and form passing the expense ID via session state.
- R5: Validation on amount, date, and required fields.
- R6: Department-scoped row security limiting users to their own department.
- R7: A summary region showing totals by category and month.
- R8: Responsive layout verified at tablet width.

## Steps
1. Create the schema and load departments, users, and 200 expense rows.
2. Build the list page with an Interactive Report and enable filtering/search.
3. Add the summary region with totals by category and month.
4. Build the form page with page items mapped to the columns.
5. Add the create, save, and delete processes with a delete confirmation.
6. Wire navigation so the ID passes through session state.
7. Add validation: amount > 0, date not in the future, category required.
8. Implement the department filter in every region's query.
9. Test with two users from different departments.
10. Export the app and re-import it to a second workspace.

## Acceptance criteria
- A user sees only their department's expenses in every region.
- Delete requires a confirmation step.
- Validation rejects an invalid amount and a future date.
- The app is usable at tablet width without horizontal scrolling.
- The export re-imports and runs with no manual fixes.

## Stretch
- Add a monthly comparison chart.
- Add an approval workflow so expenses over a threshold need sign-off.