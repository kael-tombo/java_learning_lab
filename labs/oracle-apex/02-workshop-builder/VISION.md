# Lab 02: Workshop Builder — Vision

## Where this lab takes you
From clicking a row and waiting for a page reload to selecting a row and having
the detail region update instantly — mastering master-detail patterns in APEX.

## The Arc
1. **The problem** — full page submission per selection is wasteful and slow.
2. **Shared state** — page items carrying the selection between regions.
3. **Refresh** — a Dynamic Action refreshing only the detail region.
4. **No page submit** — the AJAX pattern and when it is appropriate.
5. **Initial state** — deciding what loads before any selection exists.
6. **Multiple masters** — extending the pattern beyond one pair.
7. **Error handling** — what happens when the selection is invalid.

## Milestones (checkable)
- [ ] M1: Build a master region with row selection and a page item holding the ID.
- [ ] M2: Write the detail query filtered by that page item.
- [ ] M3: Add the Dynamic Action that refreshes detail on row selection.
- [ ] M4: Prove no full page submission occurs (verify with APEX Debug).
- [ ] M5: Handle the initial state — no selection, detail empty and readable.
- [ ] M6: Handle an invalid selection gracefully rather than erroring.
- [ ] M7: Extend the pattern to a second detail region.
- [ ] M8: Measure the latency improvement against the submitting version.

## Anti-Goals
- Submitting the whole page just to change a detail region.
- Leaving the detail region showing the previous selection on first load.
- Triggering refresh on every page load and defeating the purpose.
- Using it where the detail set is large enough that lazy loading is pointless.

## The one-sentence thesis
Master-detail is a state problem, not a navigation problem — put the selection
in shared state, refresh only what depends on it, and never submit the page.