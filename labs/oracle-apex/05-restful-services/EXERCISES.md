# EXERCISES — RESTful Services

## 1. Paginate honestly (beginner)
Build the `products/` handler + count query on a 250-row test table.
Fetch pages of 25 via cURL; assert every row appears exactly once across
pages and `X-Total-Count` matches. Then drop the `ORDER BY` and show
duplication/gaps across two runs. *Reflection: why is unordered offset
nondeterministic?*

## 2. One handler, two shapes (beginner)
Call with and without `:id`. Verify collection JSON array vs single
object, and that the count query agrees in both cases. Break it: pass
`:product_id` instead of `:id` and record the exact 500 + log row.

## 3. Lock it with OAuth2 (intermediate)
Define the privilege, register a client, and call with (a) no token, (b)
expired token, (c) valid token. Capture status codes + `ords_log` rows.
Confirm the audit trail records client ID per call.

## 4. Idempotent charges (intermediate)
Extend the outbound call with an idempotency key + retry-on-5xx (max 3,
exponential backoff). Simulate gateway 500s; prove exactly one charge
exists server-side. Explain why retry-without-idempotency double-charges.

## 5. 500 drill (advanced)
Inject each of the five listed 500 causes (missing COMMIT, ambiguous
column, bind mismatch, bad JSON, revoked credential) one at a time.
For each: reproduce via cURL, find it via the ordered triage
(log → isolated SQL → binds → privileges), fix, and log mean-time-to-find.
