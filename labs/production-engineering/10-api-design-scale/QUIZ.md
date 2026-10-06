# Lab 10: API Design & Evolution at Scale — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. What is the difference between backward and forward compatibility?**
- A) They are the same thing
- B) Backward = new server works with old clients; forward = old server works with new clients. In practice you need backward compatibility, because you cannot force clients to upgrade
- C) Forward compatibility is always required
- D) Backward compatibility only applies to JSON

**Answer: B** — And they are in tension: a change that is backward-compatible (add a field) is usually not forward-compatible (old server rejects the unknown field). Accept the tension; buy forward compatibility only where you control clients.

---

**Q2. Adding an optional field to a response is generally safe. What makes it unsafe?**
- A) Adding any field
- B) A strict client that rejects unknown properties (`FAIL_ON_UNKNOWN_PROPERTIES`), a client with a polymorphic/typed model that switches on the new value, or adding a field to a response where clients do exhaustive `switch`/sealed-type matching
- C) Only if the field is null
- D) Only for arrays

**Answer: B** — The risk lives in the client, which you cannot observe. Verify with contract tests against *your* clients, not just your schema.

---

**Q3. Why is `PUT` idempotent and `POST` not, and what does that buy you?**
- A) It is a naming convention
- B) `PUT` fully replaces the resource at a known URI, so repeating it has the same effect; `POST` creates. This lets the server/client retry safely and lets the gateway deduplicate replays
- C) POST is idempotent if it returns 201
- D) PUT cannot create

**Answer: B** — Idempotency is what makes retries safe without coordination. `DELETE` is idempotent too, in effect.

---

**Q4. Why require an `Idempotency-Key` on payment-creating `POST`s?**
- A) For caching
- B) Because `POST` is not naturally idempotent, and network timeouts leave the client unable to distinguish "failed" from "succeeded"; the key lets the server store the first result and replay it identically
- C) To prevent CSRF
- D) For rate limiting

**Answer: B** — Scope the key per client identity + endpoint, store it for at least the client's maximum retry window, and return the *original* response (including status and body) on replay.

---

**Q5. When is a 409 `Conflict` the right response?**
- A) Any validation failure
- B) State conflicts that are semantic, not syntactic: a duplicate resource, a version/state mismatch, or an operation illegal in the current state (`status != CANCELLED`) — a 422 covers well-formedness-semantic failures
- C) Missing request body
- D) Rate limiting

**Answer: B** — 409 means "your request is valid but conflicts with current state, and *you* could resolve it by re-reading." Rate limiting is 429, not 409.

---

**Q6. Why is offset/limit pagination the wrong default for a large dataset?**
- A) It is slower than keyset
- B) The database must count/skip N rows per page, so deep pages get linearly slower and the total count is O(n); meanwhile concurrent inserts shift rows so items get skipped or duplicated. Keyset (`?after=cursor`) is O(log n) per page and stable under writes
- C) It cannot be used with JSON
- D) It requires a transaction

**Answer: B** — Cursor pagination trades arbitrary jumping for correctness and speed. Give up "jump to page 500" if you need that.

---

**Q7. How do you design a keyset cursor so it does not become an injection vector?**
- A) Base64-encode it — that makes it safe
- B) Sign and encode an opaque token containing the sort-key values, so the client cannot tamper with the sort field; base64 is encoding, not integrity
- C) Encrypt with AES
- D) Include a checksum

**Answer: B** — Opaque signed cursors prevent clients from reordering the sort or smuggling a different column. A checksum is forgeable if the algorithm is known; a signature is not.

---

**Q8. What is the practical rule for `429` vs `503` on rate limiting?**
- A) Always 429
- B) `429 Too Many Requests` when the client is the problem (with `Retry-After`), `503` when your capacity is the problem (you are shedding) — clients and monitoring treat them differently
- C) Always 503
- D) 429 means the database is busy

**Answer: B** — Also always send `Retry-After` on a 429; a client that retries immediately is how a rate limit becomes an outage.

---

**Q9. How should a bulk operation behave, and why is 207-style or per-item status important?**
- A) Fail the whole request on the first error
- B) Return per-item results with individual status/error, because a 1,000-item batch will always contain a few invalid items and failing the whole thing makes partial success impossible for the client
- C) Return 200 with no body
- D) Retry the batch

**Answer: B** — Also cap batch size (e.g. 100) so a single request cannot become a denial-of-service, and require the client to handle partial results explicitly.

---

**Q10. Deprecation: what must you actually do, beyond a header?**
- A) Add `Deprecation: true`
- B) Send `Deprecation` + `Sunset` headers with a real date, log usage of the deprecated endpoint per client so you know who still depends on it, publish the replacement, and refuse new clients while serving existing ones
- C) Change the URL
- D) Return 410

**Answer: B** — `410 Gone` communicates permanence; `404` hides the problem; and without per-client usage logging, a deprecation date is a guess.

---

**Q11. Why is URI versioning (`/v2/orders`) often the wrong default for a mature API?**
- A) It is always wrong
- B) It forks the whole resource space, doubles maintenance, invites clients to stay on v1 forever, and makes non-breaking fixes impossible on the older version. Content negotiation or header versioning expresses the same transition without duplicating every unrelated endpoint
- C) URIs cannot be versioned
- D) It breaks caching

**Answer: B** — URI versioning's cost is the duplicated surface. Choose it when the change is genuinely a new contract, not for additive changes.

---

**Q12. What is an OpenAPI contract test, and why is it higher value than a schema lint?**
- A) It validates the OpenAPI file's syntax
- B) It runs real requests/responses between provider and consumer (or against recorded consumer expectations) so both sides prove compatibility; a lint only proves the document is internally consistent
- C) It generates documentation
- D) It measures latency

**Answer: B** — Schemas drift from implementations constantly. Provider-side tests catch it before the consumer does.

---

**Q13. What does `AsyncAPI` add over `OpenAPI`?**
- A) Faster generation
- B) A specification for event-driven/message-driven APIs — channels, message schemas, publish/subscribe bindings, and acknowledgement semantics — which OpenAPI does not model
- C) Database schemas
- D) Rate-limit definitions

**Answer: B** — Asynchronous contracts fail differently (schema drift, ordering, redelivery), so they need their own contract surface and their own compatibility tests.

---

**Q14. Why must error responses be structured, not a message string?**
- A) Styling
- B) Clients need to branch on a stable machine-readable `type`/`code`, plus which field is invalid and why; a human-readable message forces clients to string-match, which breaks the moment you reword it
- C) Strings are not supported in JSON
- D) It reduces payload size

**Answer: B** — Use RFC 9457 (`application/problem+json`) with a stable `type` URI and a `code` enum. Message text is for humans and may change without notice.

---

**Q15. The single most common cause of a breaking API change reaching production is?**
- A) A bad developer
- B) No contract enforcement in CI — the schema changed and merged because nothing compared the new contract against the consumers' expectations or against a recorded fixture set
- C) A missing version bump
- D) A caching bug

**Answer: B** — Every other failure mode is downstream of "the contract was not checked." Contract tests in CI are the control; versioning is only the consequence.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and build an evolved API.
- 12–10: revisit compatibility rules, cursor pagination, and error design; redo EXERCISES 2–5.
- <10: re-read THEORY + ARCHITECTURE_DECISIONS cold and retake in 48 hours.
