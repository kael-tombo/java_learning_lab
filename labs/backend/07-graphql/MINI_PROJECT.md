# Mini Project: Graphql

## The assignment

This GraphQL mini build produces a working authors-and-books graph you can run locally.
Scope stays deliberately small so every GraphQL behavior remains observable.
Budget roughly one focused evening for the authors-and-books graph implementation.
Success means demonstrating GraphQL judgment, not just compiling code.
Keep a lab journal noting each GraphQL surprise encountered.
Acceptance checks define the edge, and no additions go past them.

## Parts you will wire

- Schema type definitions.
- Queries for reading.
- Mutations for changes.
- Nested field resolution.
- Query-depth awareness.

## Build order

1. Draft a schema linking authors to their books and reviews for the service.
2. Serve nested author-book-review queries in one round trip.
3. Add mutations creating reviews with validation.
4. Resolve nested fields without one query per row.
5. Reject an abusive deeply-nested query deliberately.

## Acceptance checks

- [ ] Schema serves 25 authors, 60 books, 150 reviews in the solution.
- [ ] One nested query replaces 3 REST round trips in the platform.
- [ ] Review mutation validates rating range 1 to 5.
- [ ] Nested listing avoids per-row query explosion.
- [ ] Depth guard rejects the crafted abusive query.

## Stretch

One realistic complication of your choosing goes into the project.
Write the two-paragraph retro: which GraphQL decision proved hardest.
Give the demo to a peer whose only map is the acceptance checks.
