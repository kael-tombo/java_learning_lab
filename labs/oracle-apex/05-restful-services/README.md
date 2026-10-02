# 05 — RESTful Services (ORDS + APEX integration)

## Overview

Expose an APEX product catalog as a versioned JSON API (`catalog/v1/`),
secure it with OAuth2 client-credentials + privileges, call an external
payment gateway outbound via `APEX_WEB_SERVICE`, and debug the 500s with
`ords_log` + `APEX_DEBUG`.

## Learning Objectives

- [ ] Build module → template (`products/:id`) → GET handler with `:offset`/`:limit` pagination + `X-Total-Count`
- [ ] Lock it down: privilege → OAuth2 client → Bearer validation → audit
- [ ] Call out: web credentials + `MAKE_REST_REQUEST` + `APEX_JSON` parse + 5xx retry
- [ ] Debug methodically: `ords_log` 500s → handler SQL in isolation → binds → privileges → missing COMMIT

## Topics Covered

### 1. Inbound module (Problems 1)
`catalog/v1/` + `products/:id`; `JSON_OBJECT` handler; `OFFSET/FETCH`
pagination; count query for totals. Walkthrough Problem 1.

### 2. OAuth2 + privileges (Problem 2)
`ORDS.DEFINE_PRIVILEGE('catalog_api', …)`; client-credentials flow
(token → Bearer); audit by client ID. Walkthrough Problem 2.

### 3. Outbound call (Problem 3)
Credential store → web source → `MAKE_REST_REQUEST(POST /charge,
p_credential, p_wallet_path)` → `APEX_JSON` extract → `WHEN OTHERS`
error capture. Walkthrough Problem 3.

### 4. 500 triage (Problem 4)
`ords_log` filter; `ords.debug`; handler-SQL-in-isolation; bind-name
match (`:id` vs `:product_id`); ambiguous JSON columns; POST-handler
COMMIT. Walkthrough Problem 4, `WORKED_SQL_EXAMPLE.sql` §3.

## Prerequisites

- ORDS + APEX workspace; SQL (`JSON_OBJECT`, `OFFSET/FETCH`); OAuth2 client-credentials basics

## Further Reading

- ORDS REST Enabling SQL + `ORDS.DEFINE_PRIVILEGE` reference
- `../03-security/` for the auth/audit discipline this API inherits
