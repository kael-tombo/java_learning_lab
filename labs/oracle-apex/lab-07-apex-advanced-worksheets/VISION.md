# Lab 07: APEX Advanced Worksheets — Vision

## Where this lab takes you
From building pages to assembling enterprise features — collections, caching,
credentials, mail, PDF generation, Oracle JET charts, and plugins.

## The Arc
1. **Collections** — server-side working sets that survive a request.
2. **Caching** — what to cache, for how long, and what invalidates it.
3. **Credentials** — secrets that never enter application source.
4. **Journal** — change logging for audit.
5. **Mail** — sending from the application, and what must be queued.
6. **Print and PDF** — server-side rendering options.
7. **Oracle JET** — modern chart types and their limits.
8. **Plugins** — extending APEX without forking it.

## Milestones (checkable)
- [ ] M1: Build a collection and use it across multiple regions in one request.
- [ ] M2: Cache a region, name the invalidation trigger, and prove it.
- [ ] M3: Store a credential and use it without it appearing in source.
- [ ] M4: Write a change journal and read an audit trail from it.
- [ ] M5: Queue mail rather than sending synchronously.
- [ ] M6: Produce a PDF and compare the available rendering approaches.
- [ ] M7: Build an Oracle JET chart and explain its limits.
- [ ] M8: Load a plugin and describe what each plugin type can do.

## Anti-Goals
- Using a collection when a bind variable would do.
- Caching without a stated invalidation trigger.
- Sending mail synchronously inside a page process.
- Forking APEX code when a plugin would extend it.

## The one-sentence thesis
APEX hands you collections, caches, credentials, and plugins for the work
components do not do — the discipline is knowing when each is warranted, not
reaching for it first.