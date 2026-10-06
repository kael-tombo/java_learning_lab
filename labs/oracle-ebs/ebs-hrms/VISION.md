# EBS HRMS — Vision

## Where this lab takes you
From the person/assignment model to payroll, benefits, absence, and learning —
knowing why HRMS is structured as it is before you build on it.

## The Arc
1. **The data model** — people, assignments, positions, organizations.
2. **Why two tables** — effective-dated `F` and non-dated `V` structures.
3. **Payroll** — elements, earning and deduction rules, processing.
4. **Time and labor** — shifts, hours, absence, and their payroll impact.
5. **Benefits** — enrollment, eligibility, dependent coverage.
6. **Talent** — profiles, competency, performance, succession.
7. **OLM** — learning assignments and completions.
8. **Legislative** — data groups, regions, and why localisation is a separate axis.

## Milestones (checkable)
- [ ] M1: Draw the person/assignment/position relationship model.
- [ ] M2: Explain the difference between `_F` and `_V` views with a concrete query.
- [ ] M3: Define payroll elements and run a payroll for a small population.
- [ ] M4: Record time and show its effect on a payroll result.
- [ ] M5: Enroll an employee in benefits and verify eligibility rules.
- [ ] M6: Record an absence and show the payroll and balance consequences.
- [ ] M7: Assign a learning course and record completion.
- [ ] M8: Explain how a legislative data group changes behaviour.

## Anti-Goals
- Treating `PER_ALL_PEOPLE_F` as a single current-state table.
- Writing to HR base tables instead of using the public APIs.
- Assuming payroll elements are global when they are regional.
- Ignoring the difference between effective-dated history and current state.

## The one-sentence thesis
HRMS is a history database wearing a current-state interface — if you query it
as if the past does not exist, every report you write will be subtly wrong.