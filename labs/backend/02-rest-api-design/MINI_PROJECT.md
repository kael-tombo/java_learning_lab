# Mini Project: Rest Api Design

## What to build

This REST API design mini build produces a working book-catalog resource API you can run locally.
Scope stays deliberately small so every REST API design behavior remains observable.
Budget roughly one focused evening for the book-catalog resource API implementation.
Success means demonstrating REST API design judgment, not just compiling code.
Keep a lab journal noting each REST API design surprise encountered.
Stick to the acceptance checks and refuse scope that runs beyond them.

## Steps

1. Model books, authors, and loans as addressable resources for the service.
2. Assign creation, replacement, and removal to POST, PUT, DELETE.
3. Return 201 with location on creation and 404 on missing books.
4. Make repeated PUT and DELETE calls converge safely.
5. Add page parameters with stable ordering guarantees.

## Architecture in miniature

- Resource-oriented URI modeling.
- Correct status codes per outcome.
- PUT and DELETE idempotent semantics.
- Pagination envelope shape.
- Problem-style error payloads.

## How it is judged

- [ ] Catalog holds 60 seeded books across 8 authors in the solution.
- [ ] POST returns 201 with a working location header in the platform.
- [ ] Five repeated PUT calls leave identical book state.
- [ ] Unknown identifiers return 404 with a stable error shape.
- [ ] Page traversal over 60 books yields zero duplicates or gaps.

## Extension

Add a single realistic complication to the project, your pick.
Write the two-paragraph retro: which REST API design decision proved hardest.
Walk a peer through the system while they read only the acceptance checks.
