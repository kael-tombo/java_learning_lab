# Lab 06: APEX RESTful APIs — Real World Project

## Scenario
A B2B wholesaler's customers have been polling a nightly CSV for stock
availability. The commercial team wants a real API so partner sites can check
stock and price in real time. Enabling ORDS auto-REST looked like the answer and
was done in an afternoon — which is now a security incident: nine tables are
published, including `pricing_margin` and `customer_credit_terms`, with access
granted to any authenticated ORDS principal, and 400 partner applications were
given credentials within a day. The team needs to redesign the API surface and
roll back the exposure without breaking the partners already integrating.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/rest-data-services/ (ORDS)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX web services)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
Partner applications (400)
   │  OAuth2 client credentials, per-partner principal
   ▼
ORDS /partner/v1  (the only published surface)
   ├─ GET  /products        public-safe fields only
   ├─ GET  /products/{sku}  includes stock, price
   ├─ POST /quote-requests  rate-limited, audited
   └─ (internal /pricing/v1  NOT published to partners)

Explicitly NOT published:
   pricing_margin · customer_credit_terms · audit tables · APEX metadata

Deprecation path: v1 → v1 sunset headers → v2, 6-month notice
```

## Implementation sketch
```sql
-- Column aliases let JSON be camelCase without renaming the table.
-- Select ONLY the fields partners are entitled to see.
SELECT product_id            AS "productId",
       sku                   AS "sku",
       name                  AS "name",
       price                 AS "unitPrice",
       stock_qty             AS "availableQty",
       category_name         AS "category"
  FROM product_v
 WHERE active_flag = 'Y';
-- pricing_margin deliberately absent: it is not part of this contract.

-- Roll back exposure per principal rather than per endpoint
DELETE FROM ords_privileges WHERE principal_name = :partner_principal
   AND privilege_name LIKE 'catalog%';
```

## Requirements
- F1: Full inventory of every currently published endpoint and its exposure.
- F2: Urgent removal of the unintended tables from the partner surface.
- F3: Per-partner principal rather than a shared credential.
- F4: Explicit field-level contract — only entitled columns returned.
- F5: `pricing_margin`, `customer_credit_terms`, and audit tables unpublished.
- F6: Rate limiting on write endpoints.
- F7: Outbound call pattern for ERP replenishment using `APEX_WEB_SERVICE`.
- F8: `APEX_JSON` for all payload construction and parsing.
- F9: Versioned paths with a documented deprecation and notice policy.
- F10: Contract test suite covering every published endpoint.
- NF1: Zero unintended tables exposed within 24 hours of engagement.
- NF2: Every partner on an individual principal with least privilege.
- NF3: Rate limits enforced and observable.
- NF4: Security baseline — no internal pricing or credit data externally visible.
- NF5: Breaking changes require a new version, never an in-place change.
- NF6: Documented rollback — privileges reversible per principal.

## Milestones
- Week 1: Exposure inventory and emergency privilege cleanup.
- Week 2: Redefined `partner/v1` contract with field-level entitlements.
- Week 3: Per-partner principals, credentials rotation, rate limiting.
- Week 4: Contract tests, versioning, and partner communication.

## Verification
- Attempt to reach each unintended table; confirm all denied.
- Contract test across every endpoint and every principal class.
- Rate-limit test: confirm throttling and that it is logged.
- Field-level test: confirm no unentitled column appears in any response.
- Rotate one partner's credentials and confirm only that partner is affected.

## Rollback
Revoke privileges per principal immediately; retain endpoint definitions for the
partners already integrating while the contract is stabilised. Document rollback
steps for every change.