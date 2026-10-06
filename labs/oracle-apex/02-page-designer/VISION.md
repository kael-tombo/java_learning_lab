# Lab 02: APEX Page Designer — VISION

## Where this lab takes you
From four unfiltered region queries taking 11 seconds to four filtered ones
taking 1.2 — by understanding which phase each feature runs in and binding the
filters that were never bound.

## The Arc
1. **Three phases** — rendering, processing, after; and which feature runs where.
2. **Layout** — the grid defines responsive behaviour; spans replace pixels.
3. **Shared filters** — every region query, or the dashboard lies.
4. **Dynamic Actions** — replace page submits with targeted AJAX refresh.
5. **Conditions** — prevent refreshing on a half-set filter state.
6. **Computations** — defaults that exist before any query runs.
7. **Drill-through** — session state with keys, not labels.
8. **Empty states** — hide what has no data rather than rendering an empty box.

## Milestones (checkable)
- [ ] M1: Draw the three phases and place 8 APEX features correctly.
- [ ] M2: Build the 4-region dashboard on a 12-column grid using spans.
- [ ] M3: Bind the date items into all four region queries and verify.
- [ ] M4: Add the Dynamic Action with a condition and confirm no page submit.
- [ ] M5: Prove the AJAX path by checking the SQL count on filter change.
- [ ] M6: Add a computation default and confirm it appears on first load.
- [ ] M7: Implement drill-through passing a key and an ID.
- [ ] M8: Add an empty-state display condition and a lazy-loaded region.

## Anti-Goals
- Adding a page process and expecting it to run on page load.
- Adding a filter item without binding it into every affected query.
- Using a page submit where a Dynamic Action refresh would do.
- Omitting the Dynamic Action condition, producing a half-set range.
- Absolute positioning or fixed pixel widths.
- Passing labels instead of keys in drill-through.
- Rendering empty regions with no indication.

## The one-sentence thesis
A page is three execution phases, not a canvas — know which phase your feature
runs in, and bind the filter that was never bound.