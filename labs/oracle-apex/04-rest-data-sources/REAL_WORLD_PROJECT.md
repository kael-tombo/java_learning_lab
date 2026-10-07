# Lab 04: REST Data Sources — Real World Project

## Scenario
A utility company has an APEX portal for field technicians. Technicians need to
view current readings from a third-party smart-meter API, upload meter
inspection reports as CSV, and download completed inspection PDFs. Today the
integration calls the meter API directly from APEX page processes with the API
key pasted into the process source — readable by any APEX developer and captured
in application logs. The 10,000-row meter import takes 45 minutes because each
row triggers a separate HTTP call. The security review has flagged the embedded
credential as a finding.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX web services)
- (link removed) (ORDS)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
APEX page
  │
  ├─ Web Credential (APEX_CREDENTIAL) ──┐  secret stored once, never in code
  │                                     │
  └─ Web Source Module ─────────────────┘  reusable, parameterised call
        │  OAuth2 / API key auth
        ▼
  Third-party meter API ──► Web Service Synchronous (AJAX for latency)
                             Web Service Asynchronous (for bulk)
        │
        ├─ Rate limiting 429 ─► backoff and queue
        └─ 401 ─► refresh token, not blind retry

Bulk import:
  Upload ─► staging table ─► validate ─► BATCH process (set-based)
        │                        │
        └─ reject log           └─ apply in one statement, not per row

ORDS exposure:
  Meter + Inspection tables ─► auto-REST ─► explicit privileges per role
```

## Implementation sketch
```sql
-- Web Service Synchronous: reference the credential, never inline the secret
-- Body (APEX process):
--   l_json := APEX_WEB_SERVICE.rest_request(
--       p_url => 'https://api.metervendor.com/v2/readings',
--       p_method => 'GET',
--       p_cred  => 'XX_METER_API',        -- Web Credential, not the key
--       p_body  => NULL);
--
-- The secret lives in APEX_CREDENTIAL. No developer can read it from source.

-- Bulk: set-based, not a loop of HTTP calls
INSERT INTO meter_reading (meter_id, read_ts, kwh)
  SELECT staging.meter_id, staging.read_ts, staging.kwh
    FROM meter_import_staging staging
   WHERE staging.validation_status = 'VALID'      -- rejected rows excluded
     AND NOT EXISTS (SELECT 1 FROM meter_reading m
                      WHERE m.meter_id = staging.meter_id
                        AND m.read_ts   = staging.read_ts);
```

## Requirements
- F1: Web Credential replacing all inline secrets; evidence of removal.
- F2: Web Source Modules encapsulating every external call.
- F3: OAuth2 with token refresh, plus API key and mTLS patterns where needed.
- F4: Explicit handling of 429 rate limiting with backoff and queuing.
- F5: Explicit handling of 401 with token refresh, not blind retry.
- F6: File upload validating extension, size, and content type.
- F7: File download serving stored blobs with correct headers.
- F8: Bulk CSV import as a set-based batch with a reject log.
- F9: ORDS auto-REST exposure with explicit per-role privileges.
- F10: Audit of every outbound call: endpoint, user, outcome, duration.
- NF1: No secret readable in application source.
- NF2: 10,000-row import completes in under 5 minutes (from 45).
- NF3: Bulk import issues one set-based operation, not 10,000 HTTP calls.
- NF4: Security baseline — least-privilege ORDS, no blanket table access.
- NF5: Every outbound call audited and observable.
- NF6: Documented rollback for every credential and module change.

## Milestones
- Week 1: Inventory every external call and every embedded secret.
- Week 2: Web Credential and Web Source Module implementation.
- Week 3: Auth patterns: OAuth2 refresh, API key, error handling.
- Week 4: Upload/download validation and hardening.
- Week 5: Bulk import rebuilt as a set-based batch with reject log.
- Week 6: ORDS privileges, outbound audit, security retest.

## Verification
- Search the application export for the old API key; confirm it is gone.
- Fault injection: 429, 401, 500, malformed JSON, oversized file.
- Bulk import of 10,000 rows with 5% deliberate defects.
- ORDS privilege test with an unauthorised role.
- Outbound audit completeness check for a full day of traffic.

## Rollback
Web Source Modules are configuration; credentials can be rotated; the bulk
process retains the prior row-by-row path until the new one is validated.
Document rollback steps for every change.