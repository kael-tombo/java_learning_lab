# Lab 02: APEX Page Designer — Theory

## The Scenario

A sales dashboard: an Interactive Report at the top, two pie charts in the
middle, a bar chart at the bottom, all filtered by a user-selected date range,
with drill-through on bar click. It currently takes 11 seconds because every
region runs its own unfiltered query. The developer building it is new to Page
Designer and does not know when their SQL executes.

## Principle 1: A page has three phases, and most confusion is phase confusion

```
1. RENDERING     — regions query, rows sent to browser, HTML produced
                   Runs on every page load

2. PROCESSING    — page processes, validations, computations
                   Runs only when the page is submitted

3. AFTER PROCESSING — branches navigate away
                   Runs only if a branch condition is true
```

**The classic error**: adding a page process and pressing Refresh, then
wondering why it does nothing. Processes run on **submit**, not on render. To
run server-side logic on page load you need a process with the "On Page Load"
condition, or — much better — a computation, or better still, a bind variable
doing the work in the query.

```
Goal: filter a region on page load
  Wrong:  a process that sets an item (doesn't re-run the region query)
  Right:  the item is already set; the query binds to it

Goal: set a default date range
  Right:  a Computation "Before Header" with type "Static Value" or an
          expression — runs on every render
```

### Where things run

| Feature | Phase | Runs on |
|---------|-------|----------|
| Region query | Rendering | Every load |
| Page item default | Rendering | Every load |
| Computation | Rendering (Before Header) | Every load |
| Page process | Processing | Submit only |
| Validation | Processing | Submit only |
| Dynamic Action | Client-side | User interaction |
| Branch | After Processing | Submit, if condition true |

## Principle 2: Layout is a page property, not a region property

In Page Designer you set the **page layout** once:

```
Layout: 12-column grid
Row 1: height auto
Row 2: height auto
Row 3: height auto
```

Then each region declares **where** it sits (new row / start column / column
span) and **what height** (fixed or auto). Regions do not each define their own
grid.

**Why it matters beyond tidiness**: APEX's Universal Theme computes responsive
behaviour from the layout definition. Regions placed manually with absolute
positioning or fixed pixel widths break it, and the page that looks perfect at
1440 px scrolls horizontally at 375 px.

Rule: **use the layout grid and spans; never absolute positioning.**

## Principle 3: Shared filters must reach every query

A filter that exists as a page item but is absent from a region query does
nothing. This is the most common dashboard bug.

```
Page item: P1_START_DATE, P1_END_DATE

Region A query:  uses both        ✓
Region B query:  uses both        ✓
Region C query:  MISSING          ✗ looks unfiltered, always shows all data
```

**Two symptoms of a forgotten region:**
1. The region does not change when the filter changes.
2. It shows more rows than the others for the same period.

The prevention is a review step: after adding a region, ask what filters apply to
it. A dashboard where every region honours the same filter set is
*self-consistent*; one where it does not is actively misleading, because the
reader compares regions assuming they are comparable.

## Principle 4: Dynamic Actions replace page submits

A Dynamic Action is a client-side rule:

```
Event      → on what (page load, region selection, item change, ...)
Condition  → when it should fire
True action→ what happens
False action→ what happens otherwise
```

### Why this matters for performance

```
Page submit for a filter change:
  → submits the form
  → server runs ALL processes
  → EVERY region re-queries
  → full HTML page re-rendered
  → scroll position, focus, and page state lost

Dynamic Action (Refresh regions, AJAX):
  → only the targeted regions re-query
  → no full page re-render
  → scroll position and other state preserved
```

On a dashboard with 4 regions where only 2 depend on the changed filter, the
difference is 2 queries versus 4, and no full re-render.

### The condition matters as much as the action

```
Event:   Change  on P1_START_DATE
Condition: page item P1_END_DATE is not null    <-- prevents a half-range
Action:  Refresh → the dependent regions
```

Without the condition, choosing a start date before an end date refreshes with
an empty or invalid range, which the user sees as a transient error.

## Principle 5: Processes, Dynamic Actions, and branches are different tools

| Need | Use | Why |
|------|-----|-----|
| React to a UI event (no server round trip) | **Dynamic Action** | Immediate, client-side |
| Run PL/SQL, set items, call a package | **Page process** | Server-side, submit-time |
| Navigate conditionally | **Branch** | Only meaningful after processing |
| Change a value before render | **Computation** | Runs on every load |

The most common misuse is reaching for a page process when a Dynamic Action would
do — a submit costs a full page render for what should be a 50 ms AJAX refresh.

Conversely, a page process is the right tool for anything touching the database
that must complete before the user proceeds. There is no client-side substitute.

## Principle 6: Computations run before the header

A Computation is the correct way to set an item's value before any region
queries.

```sql
-- Computation: "Default Date Range", type = SQL Expression, Before Header
CASE WHEN :P1_FROM_DATE IS NULL THEN
       TO_CHAR(TRUNC(SYSDATE) - 30, 'YYYY-MM-DD')
     ELSE :P1_FROM_DATE END
```

This runs on **every render**, so the default appears immediately and a user who
clears the filter gets it reset on the next load — which is usually the
behaviour they want, and occasionally a surprise. Decide deliberately.

## Principle 7: Drill-through needs session state and a branch

Clicking a bar should open the detail page filtered to that region and month.

```
On chart click (Dynamic Action):
  → Execute JavaScript to read the clicked value
  → set :P2_REGION and :P2_MONTH in session state
  → Branch: Page 3

Page 3 binds both items in its query.
```

**Pass IDs, not labels.** A region label can be renamed or duplicated; an ID
cannot. This is the same rule as in the EBS reporting lab, and the failure mode
is identical — a silent link that stops working when a name changes.

## Principle 8: Region display conditions handle emptiness

A chart with no data should not render an empty box with axes. A region display
condition handles it:

```
Condition: the region query returns at least one row
Action:    hide the region (or show a "no data" static region)
```

Without this, a dashboard with no sales in the selected period shows four empty
visualisations and the reader has to infer "no data" from their absence of marks.

## Principle 9: Query count is the dashboard's budget

```
Regions: 4 (1 IR + 3 charts)
Queries per render: 4 (+ LOvs, + count)

Every one runs on every render regardless of what the user changed.
```

Two levers, in order of return:

1. **Share a query across regions** — a collection populated once, read by
   several regions. Four queries become one. (See Lab 07.)
2. **Lazy-load** — load a region only when the user expands it.
3. **Display condition** — skip the query entirely when not applicable.

Removing regions is the least effective of these, because framework overhead
dominates and you removed little.

## Principle 10: Responsive is verifiable, not assumed

Test at three widths and check the layout holds:

```
375 px   mobile   single column, stacked rows
768 px   tablet   fewer columns per row
1440 px  desktop  full layout
```

Common failures:
- Fixed-width chart regions.
- A region spanning all 12 columns containing a wide table.
- Custom CSS with pixel widths.

The Universal Theme handles this if you use the grid and spans. It cannot fix
absolute positioning.

## Diagnostic Order

1. Which phase should this run in — render, processing, or after?
2. Does this region query bind the shared filter items?
3. Is a Dynamic Action available that avoids a page submit?
4. Does the Dynamic Action condition prevent the half-set state?
5. Is layout using the grid, not absolute positioning?
6. Are drill-through values IDs rather than labels?
7. Is there an empty-state display condition?
8. How many queries does this page issue per render?

## Anti-Patterns

- Adding a process and expecting it to run on page load.
- Adding a filter item without binding it into every affected query.
- Using a page submit where a Dynamic Action refresh would do.
- Missing the condition on a Dynamic Action, producing a half-set range.
- Absolute positioning or fixed pixel widths instead of the layout grid.
- Passing labels rather than IDs in drill-through.
- Empty regions rendering with no "no data" indication.
- Optimising PL/SQL while a region query takes 900 ms.

## Summary

The 11 seconds was four unfiltered queries, and the confusion was phase
confusion — features run in one of three phases and most of them only on submit.
The fix was shared bind variables across every region, a Dynamic Action with a
condition replacing the page submit, a computation for defaults that must be
present before any query runs, and grid layout so the page holds at every width.