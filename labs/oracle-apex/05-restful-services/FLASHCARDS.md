# FLASHCARDS — RESTful Services

| # | Front | Back |
|---|-------|------|
| 1 | ORDS URL anatomy? | Module (version) → template (`:binds`) → handler (verb+SQL). |
| 2 | Pagination triple? | ORDER BY + OFFSET/FETCH binds + matching COUNT for total. |
| 3 | `:id IS NULL OR` idiom? | One handler serves collection + item. |
| 4 | Ambiguous JSON columns? | Alias every selected column (`p.x`) — joins duplicate names → 500. |
| 5 | Privilege tuple? | Name + roles + URL patterns + module id. |
| 6 | Client-credentials flow? | Token endpoint → Bearer → validate → privilege → audit. |
| 7 | Outbound auth storage? | Web-credential store; TLS via wallet path. |
| 8 | Response parse pair? | `APEX_JSON.PARSE` once, then `GET_VARCHAR2` per field. |
| 9 | 5xx handling? | Retry with backoff AND idempotency key — else double charge. |
| 10 | WHEN OTHERS destination? | Page error item (`:P4_ERROR`), not an unhandled 500. |
| 11 | 500 first query? | `ords_log` 500s, last 24 h, newest first. |
| 12 | Bind mismatch symptom? | `:id` vs `:product_id` → 500; reproduce SQL with same binds to catch. |
| 13 | Versioning strategy? | Path version (`v1`) — clients survive breaking changes. |
| 14 | Audit per call? | Client ID + timestamp — "who broke it" becomes a query. |
| 15 | Debug session tool? | `APEX_DEBUG.ENABLE(C_LOG_ALL)` for the reproduce pass. |
