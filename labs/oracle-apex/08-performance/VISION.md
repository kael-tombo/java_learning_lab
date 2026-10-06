# Lab 08: APEX Performance — Vision

## Where this lab takes you
From 12 seconds to 2.75 seconds p95 — by attributing first, checking sargability
before indexing, fixing hard parses, choosing the right cache layer, and enabling
the theme compression nobody thinks of.

## The Arc
1. **Attribute** — one Debug run; two components are 52% of the time.
2. **Sargability** — functions on the left of a comparison kill the index.
3. **Bind variables** — hard parses become library cache latch contention.
4. **Cache layers** — region, page, session state, result; pick deliberately.
5. **PL/SQL** — `FORALL` instead of a cursor loop; fix it after the regions.
6. **Rendering** — consolidating dynamic actions is a cheap win.
7. **Theme assets** — 2.5 seconds of transfer the server timings never show.
8. **Escalate** — know where the application's responsibility ends.

## Milestones (checkable)
- [ ] M1: Capture the Debug breakdown and rank components by time.
- [ ] M2: Make the dominant region's predicate sargable and confirm the plan.
- [ ] M3: Replace literal SQL with binds and confirm one statement remains.
- [ ] M4: Choose the cache layer per problem; refuse page cache on personalised content.
- [ ] M5: Audit session state size and remove the largest items.
- [ ] M6: Convert a row loop to `FORALL` and measure.
- [ ] M7: Enable theme minification and gzip; measure the transfer reduction.
- [ ] M8: Report p95 from the activity log and check `v$system_event` for waits.

## Anti-Goals

- Optimising without a Debug breakdown.
- Adding indexes without checking sargability.
- Concluding "APEX is slow" from database metrics alone.
- Retrying pagination as a performance fix.
- Page-caching a page with per-user data.
- Micro-optimising PL/SQL while a region takes 3 seconds.
- Ignoring theme assets and network transfer time.
- Optimising the average against a p95 requirement.
- Rewriting an application problem that is a storage problem.

## The one-sentence thesis
Twelve seconds had one region holding 27% of it and another 25% in rendering —
the 15-minute theme fix outranked the four-hour PL/SQL fix, and both outranked the
seven regions that together took under a second.