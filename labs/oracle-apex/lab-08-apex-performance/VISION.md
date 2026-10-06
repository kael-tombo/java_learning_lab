# Lab 08: APEX Performance — Vision

## Where this lab takes you
From "the dashboard takes 12 seconds" to a component-level diagnosis and a
prioritised fix list — learning to read the timing breakdown before changing
anything.

## The Arc
1. **Measure first** — APEX Debug and the timing breakdown.
2. **Attribution** — which component owns which milliseconds.
3. **Queries** — binds, indexes, and what pagination really does.
4. **Regions** — fewer regions, lazy loading, and interactive report cost.
5. **Session state** — an underappreciated source of page overhead.
6. **Caching** — the right layer for the right problem.
7. **Static resources** — CSS, JS, and theme optimisation.
8. **Database** — the layer APEX cannot compensate for.

## Milestones (checkable)
- [ ] M1: Capture an APEX Debug timing breakdown for a slow page.
- [ ] M2: Attribute the 12 seconds to named components.
- [ ] M3: Identify and fix the single largest contributor.
- [ ] M4: Explain what pagination does and does not do for the database.
- [ ] M5: Add or verify an index for the slow query.
- [ ] M6: Remove one region and measure the improvement.
- [ ] M7: Audit session state and remove unnecessary content.
- [ ] M8: Enable a cache and prove the improvement.

## Anti-Goals
- Optimising without a timing breakdown.
- Adding an index before checking whether the predicate can use one.
- Assuming pagination means the query is cheap.
- Micro-optimising PL/SQL while a region takes 3 seconds to query.

## The one-sentence thesis
Performance work starts with attribution — a 12-second page has one largest
contributor, and finding it takes one Debug run, not a week of guesses.