# Lab 05: RESTful Services (ORDS + APEX) — Real World Project

## Scenario
A wholesaler built a product catalog in APEX and three channel partners need
programmatic access to it: a marketplace that syncs stock hourly, a mobile app
that reads categories, and an internal pricing service that reads and updates
prices. Today partners receive nightly CSV extracts emailed to a shared mailbox,
which is manual, unauthenticated, and cannot support anything near real time.
The team must publish a proper API. They have already hit their first problem:
enabling ORDS auto-REST exposed every table to every authenticated user, and
`ords_log` is full of 500s nobody can explain.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/rest-data-services/ (ORDS)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX web services)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/

## Architecture
```
                    ORDS (reverse proxy in front of the schema)
                    ┌──────────────────────────────────────┐
   Partner ────────►│  /catalog/v1/products                │
   (OAuth2 token)   │  /catalog/v1/categories             │
                    │  /catalog/v1/stock                   │
                    │  /pricing/v1/prices  (internal only) │
                    └──────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   auto-REST            custom handler        guarded handler
   (read-only           (aggregations,         (write: price
    catalog tables)      computed fields)       update + audit)

OAuth2 client credentials ──► privilege per role ──► scoped access
Outbound: APEX_WEB_SERVICE ──► payment gateway (approval / decline)
Debugging: ords_log ──► request, error, stack trace
```

## Implementation sketch
```sql
-- Guarded write handler: validate, update, audit — never bare auto-REST
BEGIN
  APEX_JSON.open_object('product');
  FOR r IN (SELECT product_id, name, price, stock_qty
              FROM product WHERE product_id = :product_id) LOOP
    APEX_JSON.open_object(null);
    APEX_JSON.open_array('lines');
    APEX_JSON.close_array;              -- placeholder for nested detail
    APEX_JSON.close_object;
  END LOOP;
  APEX_JSON.close_object;
END;
/
-- Read the failure from the server, not from the client:
SELECT id, datetime, uri, method, status_code, ora_error_message
  FROM ords_log
 WHERE status_code >= 500
   AND datetime > SYSDATE - 1
 ORDER BY datetime DESC;
```

## Requirements
- F1: Versioned `catalog/v1` and `pricing/v1` modules.
- F2: Auto-REST for catalog tables with read-only privileges.
- F3: Custom handlers for aggregations and computed fields.
- F4: Guarded write handler for price updates with validation and audit.
- F5: OAuth2 client credentials with per-client privileges and scopes.
- F6: Explicit least privilege — no blanket table access.
- F7: Outbound payment gateway call with approval and decline handling.
- F8: JSON built with `APEX_JSON` for nested structures.
- F9: `ords_log` monitoring integrated into the operations dashboard.
- F10: Published contract test asserting status codes for every endpoint.
- NF1: Partner sync moves from nightly CSV to hourly API.
- NF2: p95 response under 500 ms for catalog reads.
- NF3: Zero unauthorised data access across the privilege matrix.
- NF4: Security baseline — no table exposed beyond the intended catalog.
- NF5: Every 5xx investigated within one business day via `ords_log`.
- NF6: Documented rollback for every privilege and module change.

## Milestones
- Week 1: API design — resources, versioning, and the privilege matrix.
- Week 2: `catalog/v1` auto-REST published with read-only privileges.
- Week 3: Custom handlers for aggregations and the guarded price write.
- Week 4: OAuth2 client credentials and per-client scopes.
- Week 5: Payment gateway integration and error handling.
- Week 6: Contract tests, `ords_log` monitoring, partner onboarding.

## Verification
- Contract test runs every endpoint and asserts expected status codes.
- Privilege matrix test with each partner role against each endpoint.
- Fault injection: malformed body, missing token, oversized payload.
- Payment gateway decline path verified without an unhandled error.
- Load test at hourly sync volume (10,000 records).

## Rollback
Module and privilege changes are configuration and reversible; guarded handlers
can be disabled in favour of read-only access; partners keep CSV access until the
API is signed off. Document rollback steps for every change.