# Lab 06: APEX RESTful APIs — Vision

## Where this lab takes you
From consuming a REST API to publishing one — ORDS auto-REST, custom handlers,
and `APEX_WEB_SERVICE` plus `APEX_JSON` for the outbound direction.

## The Arc
1. **REST in the database** — why exposing data directly is a design decision.
2. **ORDS auto-REST** — a table as an endpoint, and its limits.
3. **Custom handlers** — when auto-REST is not enough.
4. **Column aliases** — JSON naming without renaming the table.
5. **Consuming** — `APEX_WEB_SERVICE` for the outbound call.
6. **JSON** — `APEX_JSON` for parsing and building.
7. **Auth** — protecting what you publish.
8. **Versioning** — a contract you can change later.

## Milestones (checkable)
- [ ] M1: Publish a table through ORDS auto-REST and inspect the schema.
- [ ] M2: Restrict it with explicit privileges and test denial.
- [ ] M3: Write a custom handler producing a nested JSON shape.
- [ ] M4: Alias columns so JSON names differ from column names.
- [ ] M5: Call an external API with `APEX_WEB_SERVICE`.
- [ ] M6: Parse and build JSON with `APEX_JSON`.
- [ ] M7: Add versioning and describe the deprecation path.

## Anti-Goals
- Publishing a table with blanket access because it took one click.
- Assuming auto-REST supports the join or aggregation you need.
- Building JSON with string concatenation.
- Exposing an endpoint with no versioning strategy.

## The one-sentence thesis
Publishing a REST API from the database is powerful and easy to overshare — the
table is not the contract, so decide the resource shape and the access rules
before you enable anything.