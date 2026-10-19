# Mini Project: Rest Apis With Spring

## The assignment

This REST APIs with Spring mini build produces a working repairs-shop order API you can run locally.
Scope stays deliberately small so every behavior remains observable.
Budget roughly one focused evening for the repairs-shop order API implementation.
Success means demonstrating its judgment, not just compiling code.
Keep a lab journal noting each surprise encountered.
The acceptance checks cap the work; features beyond them wait.

## Parts you will wire

- Controller request mapping.
- Service-layer orchestration.
- Centralized exception translation.
- Request validation.
- Paginated order listing.

## Build order

1. Expose repair-order intake, status, and completion endpoints for the service.
2. Keep dispatch logic in a service the controller delegates to.
3. Translate missing-order faults into 404 payloads centrally.
4. Validate intake payloads and reject blanks with 400.
5. Paginate the order list with explicit sort order.

## Acceptance checks

- [ ] 40 seeded repair orders queryable by status in the solution.
- [ ] Missing order lookup returns 404, never 500 in the platform.
- [ ] Blank intake payload rejected with field-level messages.
- [ ] Paginated listing covers all 40 orders exactly once.
- [ ] Controller and service each carry focused unit tests.

## Stretch

Grow the project by adding one realistic complication you select.
Write the two-paragraph retro: which decision proved hardest.
Walk a peer through the system while they read only the acceptance checks.
