# Lab 07: APEX Advanced Worksheets — Real World Project

## Scenario
A legal document management team has an APEX application where users search a
contract repository and download PDFs. Three problems have accumulated: search
takes 22 seconds because the same reference data is queried on every page render;
a third-party e-signature API key was pasted into a page process and is visible
in the application export; and a notification email is sent synchronously during
a page process, so users wait on the SMTP round trip and a mail server outage
produces a failed transaction. The team also wants charts on the search page and
has been copying APEX JavaScript to customise them.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX collections, cache)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (credentials, plugins)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/

## Architecture
```
Contract search page
   │
   ├─ Collections: one query populates a collection;
   │   3 regions read from it (was 3 queries) — 22 s → ~4 s
   │
   ├─ Cache: reference data cached 10 min, invalidated on reference change
   │
   ├─ Credential: e-signature API key in APEX_CREDENTIAL, not source
   │   └─ Web Source Module performs the call
   │
   ├─ Mail queue: APEX_MAIL + custom queue table; status queryable;
   │   a broker process sends asynchronously
   │
   ├─ Journal: APEX_JOURNAL on contract status for audit
   │
   ├─ PDF: server-side generation from the collection, streamed to download
   │
   └─ Oracle JET charts replace forked JavaScript
```

## Implementation sketch
```sql
-- One query into a collection; three regions read it.
-- Was: 3 separate queries over the same 400k-row contract table.
APEX_COLLECTION.TRUNCATE('CONTRACT_SEARCH');
FOR r IN (SELECT contract_id, title, counterparty, status, signed_date
            FROM contract
           WHERE (:p_search IS NULL OR UPPER(title) LIKE '%'||UPPER(:p_search)||'%')
             AND (:p_status IS NULL OR status = :p_status)) LOOP
  APEX_COLLECTION.ADD_ELEMENT('CONTRACT_SEARCH', r.contract_id, r);
END LOOP;

-- Credential: the secret is stored once, referenced by name.
-- It is NOT in this process body and NOT in the application export.
l_json := APEX_WEB_SERVICE.rest_request(
             p_url => 'https://api.esign.example/v1/send',
             p_cred => 'XX_ESIGN_API');
```

## Requirements
- F1: Collection-based query sharing across all regions on the page.
- F2: Region and page caching with documented invalidation triggers.
- F3: Credential storage replacing the in-source API key.
- F4: Queued, asynchronous mail with a status table and retry.
- F5: Retry policy that does not fail the user transaction.
- F6: PDF generation for contract downloads.
- F7: Journal on contract status changes for audit.
- F8: Oracle JET charts replacing forked JavaScript.
- F9: At least one plugin replacing custom-copied APEX code.
- NF1: Search page loads under 5 seconds (from 22).
- NF2: Zero secrets in the application export.
- NF3: Mail send failures do not fail the user transaction.
- NF4: Security baseline — credential reference by name only.
- NF5: Cache staleness bounded and documented per cached region.
- NF6: Documented rollback for every configuration change.

## Milestones
- Week 1: Collection refactor and cache design with invalidation triggers.
- Week 2: Credential migration and removal of the in-source key.
- Week 3: Mail queue implementation with broker and status tracking.
- Week 4: PDF generation, journal, JET charts, plugin adoption.

## Verification
- Compare query counts before and after on one page render.
- Search the application export for the old API key; confirm it is absent.
- Simulate an SMTP outage; confirm the user transaction still succeeds.
- Change reference data and confirm cache behaviour matches the documented trigger.
- Confirm journal history for a contract status change.

## Rollback
Collections and cache settings are per-region configuration; credential
migration keeps the previous page process until sign-off; the mail queue falls
back to synchronous send as a documented, monitored option. Document rollback
steps for every change.