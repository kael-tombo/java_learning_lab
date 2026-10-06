# Lab 02: APEX Page Builder — Vision

## Where this lab takes you
From using the Page Designer to understanding its three phases — rendering,
processing, and shared components — so you can predict what APEX will do before
you click.

## The Arc
1. **Three phases** — render, process, and where shared components live.
2. **Regions** — Static Content, Reports, Charts, and layout.
3. **Items** — types, naming, and the page-items tree.
4. **Buttons** — page and region level, and what they submit.
5. **Dynamic Actions** — the event/condition/action model.
6. **Processes** — server-side logic and when conditions fire.
7. **Branches** — conditional navigation.
8. **Computations and validations** — derived values and rules.
9. **Layout** — grids, spans, and responsive behaviour.

## Milestones (checkable)
- [ ] M1: Draw the three-phase model and state what runs in each.
- [ ] M2: Build a dashboard with IR, two charts, and a bar chart in a grid.
- [ ] M3: Add date-range items and bind them into every region query.
- [ ] M4: Create a Dynamic Action refreshing all three on filter change.
- [ ] M5: Explain when a process runs and write its condition correctly.
- [ ] M6: Add a branch for conditional navigation.
- [ ] M7: Add a computation and a validation, and test both.
- [ ] M8: Explain why layout is set on the page and not per region.

## Anti-Goals
- Adding regions without deciding whether the query needs bind variables.
- Using a process where a Dynamic Action would do.
- Setting page layout in the theme instead of in Page Designer.
- Adding branches for conditions that belong in a process condition.

## The one-sentence thesis
Page Designer is not a canvas — it is a declaration of three execution phases, and
almost every confusion comes from expecting work to run in the wrong one.