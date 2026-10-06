# Lab 06: APEX RESTful APIs — Mini Project

## Goal
Publish a versioned, privilege-restricted REST API from APEX and consume an
external one, in 90 minutes.

## Requirements
- R1: ORDS auto-REST enabled on two tables.
- R2: Explicit privileges: public read on one, authenticated read on the other.
- R3: A custom handler producing a nested JSON object.
- R4: Column aliases so JSON keys differ from column names.
- R5: An outbound `APEX_WEB_SERVICE` call with success and error handling.
- R6: JSON parsed with `APEX_JSON` and built with `APEX_JSON`.
- R7: A versioned path with a documented deprecation approach.

## Steps
1. Enable ORDS and publish two tables under `catalog/v1`.
2. Set privileges and test with and without a token.
3. Write a custom handler returning category plus a nested product array.
4. Alias columns in the auto-REST source to produce camelCase keys.
5. Call an external API from a page process; handle 200, 4xx, and 5xx.
6. Parse the response with `APEX_JSON` and display selected fields.
7. Build an outbound payload with `APEX_JSON` for a nested structure.
8. Add the version segment and document the deprecation path.
9. Run a test against every endpoint and record status codes.

## Acceptance criteria
- Public read is only on the intended resource.
- The custom handler returns the documented nested shape.
- JSON keys match the documented contract, not the column names.
- All three HTTP outcomes produce distinct, clear handling.
- Every endpoint returns an expected status code under test.

## Stretch
- Add pagination and confirm the total count is still returned.
- Write a contract test and run it against a schema change.