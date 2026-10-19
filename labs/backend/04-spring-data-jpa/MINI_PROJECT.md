# Mini Project: Spring Data Jpa Querying

## The assignment

This Spring Data JPA querying mini build produces a working staff-directory query service you can run locally.
Scope stays deliberately small so every behavior remains observable.
Budget roughly one focused evening for the staff-directory query service implementation.
Success means demonstrating its judgment, not just compiling code.
Keep a lab journal noting each surprise encountered.
Hold the line at the acceptance checks; nothing extra sneaks in beyond them.

## Parts you will wire

- Derived query methods.
- Paged and sorted access.
- Specification-style dynamic filters.
- Entity graphs for fetch control.
- Query-method auditing fields.

## Build order

1. Model departments, roles, and staff with associations for the service.
2. Express six common lookups as derived query names.
3. Add paging plus sorting to directory browsing.
4. Combine department, role, and tenure filters dynamically.
5. Tame one N+1 case with explicit fetch planning.

## Acceptance checks

- [ ] 120 staff across 6 departments seed cleanly in the solution.
- [ ] All 6 derived lookups return expected subsets in the platform.
- [ ] Directory paging covers 120 staff with no repeats.
- [ ] Combined filter of 3 facets returns correct intersection.
- [ ] N+1 case drops from 40+ queries to under 5 per page.

## Stretch

Grow the project by adding one realistic complication you select.
Write the two-paragraph retro: which decision proved hardest.
Demo time: the peer sees the system with just the acceptance checks as the guide.
