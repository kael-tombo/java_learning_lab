# Lab 02: APEX Page Builder — Mini Project

## Goal
Build a responsive dashboard page in Page Designer with reports, charts, filters,
and a dynamic action — in 90 minutes.

## Requirements
- R1: A page laid out in a 12-column grid with three logical rows.
- R2: An Interactive Report region in row 1.
- R3: Two chart regions in row 2 and one bar chart in row 3.
- R4: Date-range page items bound into all four region queries.
- R5: A Dynamic Action refreshing all regions when either date changes.
- R6: A page process with a condition, demonstrating server-side logic.
- R7: A branch for conditional navigation.
- R8: A computation and a validation, both tested.

## Steps
1. Create a blank page and define the layout grid.
2. Place the Interactive Report spanning the full width in row 1.
3. Add two chart regions side by side in row 2.
4. Add the bar chart in row 3 with an appropriate span.
5. Create the two date-range items in a Static Content region.
6. Bind both date items into every region query with bind variables.
7. Add the Dynamic Action on Change, refreshing all four regions.
8. Add a process with a condition and verify it runs only when intended.
9. Add a branch and a computation; test the validation.
10. Test the layout at tablet and mobile widths.

## Acceptance criteria
- All four regions filter by both date items.
- The Dynamic Action refreshes without a page submission.
- The process runs only when its condition is true.
- The branch navigates correctly from both entry points.
- The layout holds at tablet width without horizontal scrolling.

## Stretch
- Add a second page and branch to it conditionally.
- Convert one chart to a different type and compare readability.