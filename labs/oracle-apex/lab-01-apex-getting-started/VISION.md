# Lab 01: APEX Getting Started — Vision

## Where this lab takes you
From an empty schema to a working CRUD application with row-level security —
the foundation every later APEX lab builds on.

## The Arc
1. **The model** — workspaces, schemas, and the relationship between them.
2. **Pages** — what a page is and how regions compose one.
3. **Interactive Reports** — display, sort, filter, search.
4. **Forms** — insert, update, and delete with validation.
5. **Reports and pages** — linking them with session state.
6. **Row-level security** — scoping data to the user's department.
7. **Responsive** — working on desktop and tablet.
8. **Iterating** — from prototype to a deliverable in a week.

## Milestones (checkable)
- [ ] M1: Describe the workspace/schema relationship and where your data lives.
- [ ] M2: Build an Interactive Report with sorting, filtering, and search.
- [ ] M3: Build a form page supporting insert, update, and delete.
- [ ] M4: Link the report to the form, passing the ID through session state.
- [ ] M5: Add validation to the form and confirm it rejects bad input.
- [ ] M6: Implement department-scoped row security and test cross-department denial.
- [ ] M7: Confirm the application works at tablet width.
- [ ] M8: Export the application and re-import it to a second workspace.

## Anti-Goals
- Skipping row-level security on the first build and adding it later.
- Building separate pages for list and detail instead of linking them.
- Using page items to hold state instead of session state.
- Delivering a prototype that only works on a 27-inch monitor.

## The one-sentence thesis
APEX is a page-and-region model over your schema — get the state handling right
and the rest is composition.