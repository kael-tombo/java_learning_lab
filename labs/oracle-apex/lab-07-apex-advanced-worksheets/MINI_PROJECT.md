# Lab 07: APEX Advanced Worksheets — Mini Project

## Goal
Assemble an enterprise feature set — collections, caching, credentials, mail,
PDF, JET charting, and a plugin — in 90 minutes.

## Requirements
- R1: A named collection populated in a process and read by three regions.
- R2: A region cache with a stated invalidation trigger and proof it works.
- R3: A credential used by a web service call, absent from source.
- R4: A journal on one table producing a readable audit trail.
- R5: A queued mail flow with status tracking rather than synchronous send.
- R6: A PDF generated from report data.
- R7: An Oracle JET chart, with its limitations documented.
- R8: One plugin loaded and its type identified.

## Steps

1. Create a collection in a before-report process from a base query.
2. Bind three regions to the collection; confirm they share one query result.
3. Cache the heaviest region for 10 minutes; name the trigger.
4. Change the underlying data; confirm the cache serves stale data until expiry.
5. Invalidate explicitly and confirm freshness returns.
6. Create a credential and call an external API from a page process.
7. Create a journal and update, then read the change history.
8. Queue a mail and process the queue separately.
9. Generate a PDF of the report data.
10. Add an Oracle JET chart and a plugin; document both.

## Acceptance criteria
- Three regions read from one collection with a single underlying query.
- Caching is demonstrably stale before expiry and fresh after invalidation.
- The credential secret does not appear in any page process body.
- The journal shows who changed what and when.
- Mail is queued and its status is queryable.
- The plugin loads and the application still functions.

## Stretch
- Measure the query reduction from sharing the collection.
- Compare PDF rendering approaches on fidelity and time.