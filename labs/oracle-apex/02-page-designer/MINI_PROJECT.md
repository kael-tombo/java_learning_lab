# Lab 02: APEX Page Designer — Mini Project

## Goal
Build a responsive four-region dashboard with shared filters, a Dynamic Action,
drill-through, and empty states in 90 minutes.

## Requirements
- R1: A 12-column grid layout with three rows.
- R2: Four regions positioned by row and span.
- R3: Two date items bound into all four region queries.
- R4: A Dynamic Action refreshing all four regions via AJAX, with a condition.
- R5: A computation setting the default 30-day range.
- R6: A validation rejecting an inverted date range with a specific message.
- R7: Drill-through from the bar chart passing a month key and a region ID.
- R8: A display condition plus a "no data" region.
- R9: A process with a condition, demonstrated as conditional.

## Steps
1. Create the sales tables and load 50,000 rows across 24 months.
2. Create the page and define the layout grid with three rows.
3. Add the Static Content filter region with two date items and two LOVs.
4. Add the IR region spanning 12 columns and bind both date items.
5. Add two pie regions at columns 1 and 7 and a bar region spanning 12.
6. Bind the date items into all three chart queries.
7. Add the computation for the default range; confirm on first load.
8. Add the Dynamic Action with the non-null condition; check for page submit.
9. Add the inverted-range validation and test it.
10. Add the drill-through and the empty-state condition.
11. Verify at 375, 768, and 1440 px.

## Acceptance criteria
- All four regions filter by the selected date range.
- Changing either date refreshes without a page submission.
- The computation default is present on the first load.
- The inverted range produces a specific validation message.
- Drill-through opens the detail page filtered to that region and month.
- An empty period hides the charts and shows the "no data" region.
- The layout holds at all three widths.

## Stretch
- Measure page load before and after adding the filters.
- Make the category LOV cascade from the region item.