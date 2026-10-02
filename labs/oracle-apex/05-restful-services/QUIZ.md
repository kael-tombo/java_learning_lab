# QUIZ — RESTful Services

## 1. Module vs template vs handler?
<details><summary>Answer</summary>Module scopes/version (`catalog/v1/`); template binds URL patterns (`products/:id`); handler runs SQL per HTTP verb.</details>

## 2. Why must pagination always include ORDER BY?
<details><summary>Answer</summary>OFFSET without deterministic order returns overlapping/gapped pages across requests — the database makes no order promises.</details>

## 3. What binds the count query to the list query, and why?
<details><summary>Answer</summary>The identical WHERE predicate. Totals must reflect the same filter or `X-Total-Count` lies.</details>

## 4. `DEFINE_PRIVILEGE` pattern scoping: why `/catalog/v1/products/*`?
<details><summary>Answer</summary>Least privilege — the privilege covers exactly the catalog templates, nothing else in the module.</details>

## 5. Client-credentials flow in three steps?
<details><summary>Answer</summary>POST token endpoint with grant_type → receive access_token → Bearer header per call; ORDS validates + checks privilege + audits.</details>

## 6. Outbound credentials: store vs hard-code?
<details><summary>Answer</summary>Web-credential store + wallet path. Hard-coded keys leak in exports/logs and can't rotate without redeploy.</details>

## 7. Why `APEX_JSON.PARSE` before `GET_VARCHAR2`?
<details><summary>Answer</summary>Parse builds the DOM once; getters navigate it. Skipping parse (or re-parsing per field) is the standard beginner error.</details>

## 8. Retry-on-5xx without idempotency key: outcome?
<details><summary>Answer</summary>Double charges — each retry is a new charge server-side. Key first, retry second.</details>

## 9. 500 triage order?
<details><summary>Answer</summary>ords_log (newest 500s) → reproduce handler SQL with same binds → bind/column/JSON check → privileges → missing COMMIT.</details>

## 10. POST-handler missing COMMIT: symptom?
<details><summary>Answer</summary>200 response, zero persisted rows — success theater. The walkthrough lists it first among common 500-adjacent causes for a reason.</details>
