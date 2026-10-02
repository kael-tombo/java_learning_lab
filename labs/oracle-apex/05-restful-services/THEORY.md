# THEORY — APEX RESTful Services

## 1. ORDS is the HTTP front door

ORDS maps URL → SQL: **Module** (`catalog/v1/`) scopes versioning,
**Template** (`products/:id`) binds path patterns with `:bind` variables,
**Handler** runs the SQL per HTTP verb. The response serializes to JSON
with `Content-Type: application/json`. Version in the path (`v1`) is what
lets mobile clients survive breaking changes — never version by hoping.

## 2. Pagination is a contract, not a feature

`OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY` + deterministic
`ORDER BY product_name` + `X-Total-Count` from the count query. Three
rules: always order (offset without order is nondeterministic), always
return the total (clients can't page blind), always use binds (string
interpolation is injection). The `:id IS NULL OR product_id = :id`
idiom makes one handler serve collection + item — at the cost of a
plan that must handle both shapes.

## 3. Security: privilege → OAuth → audit

`ORDS.DEFINE_PRIVILEGE('catalog_api', roles, '/catalog/v1/products/*',
module)` draws the authorization perimeter; the OAuth2 client-credentials
flow (token endpoint → Bearer header → ORDS validation → privilege check)
draws authentication. Every call logs client ID + timestamp — the audit
trail that turns "who broke it" from archaeology into a query.

## 4. Outbound calls invert the trust

Inbound: you validate callers. Outbound (`MAKE_REST_REQUEST` to the
payment gateway): the gateway validates *you* via stored web credentials
(never hard-coded keys), TLS via wallet path, `APEX_JSON` parsing of the
response, and explicit 5xx retry — transient gateway failures are normal
and must not become double charges. Idempotency keys belong in the JSON
body for exactly this reason.

## 5. Debugging 500s in order

`ords_log` (filter 500s, newest first) → reproduce handler SQL with the
*same binds* in SQL Workshop → check bind names, ambiguous columns, JSON
syntax → verify privileges/credentials → confirm POST-handler `COMMIT`.
Random order wastes hours; this order converges in minutes.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- About Oracle RESTful Services in Oracle APEX (Oracle APEX 22.1 SQL Workshop Guide, 2022) — https://docs.oracle.com/en/database/oracle/apex/22.1/aeutl/about-oracle-RESTful-services-in-application-express.html — Takeaway tied to lab §1: ORDS Resource Module → Template → Handler is the official structure; the lab's `catalog/v1/` module + `products/:id` template mirrors the docs' `hr/employees/:id` pattern.
- Resource Handlers map 1:1 to HTTP verbs/CRUD (same Oracle APEX 22.1 page, 2022) — https://docs.oracle.com/en/database/oracle/apex/22.1/aeutl/about-oracle-RESTful-services-in-application-express.html — Takeaway tied to lab §2/§5: one handler per GET/POST/PUT/DELETE keeps SQL per verb testable and makes the 500-debug order (ords_log → reproduce SQL with binds) converge.
- RESTful Service configuration requirements: ORDS 20.x+ and workspace/instance enablement (same Oracle page, 2022) — https://docs.oracle.com/en/database/oracle/apex/22.1/aeutl/about-oracle-RESTful-services-in-application-express.html — Takeaway tied to lab §3–§4: privilege/OAuth and outbound-credential failures are often config, not code — confirm ORDS version, workspace enablement, and privilege/credential grants before chasing handler logic.
