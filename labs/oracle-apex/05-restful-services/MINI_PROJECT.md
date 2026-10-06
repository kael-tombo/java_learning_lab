# Lab 05: RESTful Services (ORDS + APEX) — Mini Project

## Goal
Expose an APEX product catalog as a versioned, secured JSON API and call an
external payment gateway, in 90 minutes.

## Requirements
- R1: A `catalog/v1` module with products, categories, and stock endpoints.
- R2: ORDS auto-REST on at least one table, with the schema inspected.
- R3: Explicit privileges so read and write differ, and role A cannot see role B.
- R4: OAuth2 client-credentials protection on every module.
- R5: An outbound call to a payment gateway with success and failure handled
      as distinct outcomes.
- R6: JSON built with `APEX_JSON` rather than concatenation.
- R7: A deliberately triggered 500 diagnosed from `ords_log`.

## Steps
1. Load products, categories, and stock into test tables.
2. Enable ORDS and publish a `catalog/v1` module.
3. Add product, category, and stock resources.
4. Inspect the generated OpenAPI schema for correctness.
5. Set privileges: anonymous read, authenticated write, admin delete.
6. Configure OAuth2 client credentials and test with a token.
7. Attempt an unauthorised role and confirm denial.
8. Call a payment gateway from a page process; handle approval and decline.
9. Build a JSON payload with `APEX_JSON` and verify it parses.
10. Trigger a 500 and read `ords_log` to find the cause.

## Acceptance criteria
- Every endpoint requires a token except deliberately public reads.
- An unauthorised role is denied, and the error is a 403 not a 500.
- The payment gateway path handles decline without raising an error.
- `APEX_JSON` produces valid JSON for a nested structure.
- The 500 is diagnosed from `ords_log`, not by guessing.

## Stretch
- Add pagination with `offset` and `limit` and confirm the total count.
- Write a contract test that runs every endpoint and asserts status codes.