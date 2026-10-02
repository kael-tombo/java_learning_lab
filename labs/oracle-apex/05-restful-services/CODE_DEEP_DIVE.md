# CODE_DEEP_DIVE — RESTful Services walkthrough code

All references are to `PROBLEM_WALKTHROUGH.md` in this lab.

## 1. Product handler (Problem 1, lines 30–46)

- `JSON_OBJECT('product_id' KEY p.product_id, …)` with table aliases —
  aliases are load-bearing: without `p.`/`c.` the join's duplicate column
  names make the JSON ambiguous (one of the walkthrough's listed 500
  causes).
- `WHERE (:id IS NULL OR p.product_id = :id)`: collection-or-item in one
  handler. `ORDER BY product_name` before `OFFSET/FETCH` — pagination
  without deterministic order returns overlapping/gapped pages.
- Separate `COUNT(*)` with the *same* predicate: totals must reflect the
  filter, or `X-Total-Count` lies and clients over/under-fetch.

## 2. Privilege definition (Problem 2, lines 81–91)

- `ORDS.DEFINE_PRIVILEGE(p_privilege_name, p_roles, p_patterns,
  p_module_id)`: the pattern `/catalog/v1/products/*` scopes exactly the
  catalog templates; `COMMIT` persists (same forgotten-commit gotcha as
  the EBS `fnd_profile.save` lesson).
- Flow: `POST /oauth/token (grant_type=client_credentials)` → token →
  `Authorization: Bearer` → ORDS validates → extracts user → checks
  privilege → audit row. Each arrow is independently testable with cURL.

## 3. Outbound charge call (Problem 3, lines 127–153)

- Body built with `JSON_OBJECT` from page items (`:P4_AMOUNT`,
  `:P4_CARD_TOKEN`) — binds, never concatenation.
- `MAKE_REST_REQUEST(url, POST, body, credential=>'PAYMENT_GW',
  wallet=>'file:/etc/oracle/wallet')`: credential store holds the key,
  wallet holds TLS trust. Response parsed with `APEX_JSON.PARSE` +
  `GET_VARCHAR2('transaction_id'/'status')` into page items.
- `EXCEPTION WHEN OTHERS → :P4_ERROR := SQLERRM`: surfaces gateway/parse
  failures in the UI instead of an unhandled 500. Missing piece to add:
  retry-on-5xx with idempotency key (exercise 4).

## 4. 500 triage queries (Problem 4, lines 188–201)

- `ords_log WHERE status_code=500 AND created_on > SYSDATE-1 ORDER BY
  created_on DESC`: the failing URL + method + error in one screen.
- `APEX_DEBUG.ENABLE(C_LOG_ALL)`: session-scoped tracing for the
  reproduce pass. Handler-SQL-in-isolation with identical binds is the
  step that distinguishes SQL bugs from ORDS-config bugs.
