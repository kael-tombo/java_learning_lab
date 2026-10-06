# VISION — Lab 10: API Design & Evolution at Scale

> From "here are the endpoints" to "this API will still work in five years, and I can prove it."

---

## The Arc

1. **Resource modelling** — nouns, hierarchy, methods with real semantics, and why verbs-in-URL is a decision.
2. **Contracts as the unit of design** — status codes, problem details, and machine-readable errors.
3. **Idempotency and retries** — what makes a client safe to retry, and how the server supports it.
4. **Pagination and limits** — offset vs keyset, signed cursors, and why every `limit` is a cost control.
5. **Bulk and async operations** — partial-success semantics, size caps as lock-duration controls, 202 + job resources.
6. **Evolution rules** — what breaks clients, tolerant readers/writers, additive change, when v2 is genuinely warranted.
7. **Deprecation that works** — usage logging, `Deprecation`/`Sunset`, per-client outreach, feasibility arithmetic.
8. **Contract enforcement** — OpenAPI/AsyncAPI as generated artefacts, provider/consumer tests, breaking-change detection.
9. **Governance** — rate limits, quota, and what a platform team should standardise centrally.

---

## Why this lab exists

An API is the only part of a system you cannot refactor freely, because other people's code depends on its exact shape. Most breaking changes are not deliberate redesigns; they are careless additions plus a client that was stricter than you assumed.

The specific goal here: **you can design an API that can absorb three years of additive change without a version bump, and you can prove compatibility in CI rather than discovering it in production.**

---

## Milestones (checkable)

- [ ] M1: Design a resource model for a real domain with methods, status codes, and a per-endpoint problem-details catalogue.
- [ ] M2: Implement cursor pagination with a signed opaque cursor and prove a client cannot reorder or forge it.
- [ ] M3: Implement `Idempotency-Key` with verbatim replay, TTL pruning, and a test for a mismatched-payload reuse.
- [ ] M4: Add a breaking-change detector (`oasdiff`) to CI and demonstrate it blocking a rename.
- [ ] M5: Define a deprecation policy with `Deprecation`/`Sunset` headers and per-client usage logging, and compute the required migration rate.
- [ ] M6: Build provider + consumer contract tests with recorded fixtures, and show they fail on an unintended nullability change.
- [ ] M7: Write the platform API standard (naming, error catalogue, limits, versioning stance) and get two teams to adopt it.

---

## Anti-Goals

- `200 OK` with `{"success": false}` in the body.
- Error strings that clients string-match.
- Uncapped `pageSize`, `limit`, or batch size.
- Offset pagination on a large, concurrently-written collection.
- Renaming or retyping a field without a version bump.
- Setting a sunset date without per-client usage data.
- Hand-written documentation that drifts from the implementation.
- Publishing a schema nobody tests against.

---

## Interview Lens

- "How do you evolve an API without breaking clients?"
- "Why keyset pagination, and what is the cursor?"
- "How do you make a payment `POST` safe to retry?"
- "When is a v2 justified?"
- "How do you know a change is breaking?"

---

## 30-Day Plan

- **Week 1** — THEORY + ARCHITECTURE_DECISIONS: resource modelling, status codes, error format, compatibility rules; hands-on: publish an OpenAPI spec and diff it. M1–M2.
- **Week 2** — EXERCISES: pagination, idempotency, batch, deprecation arithmetic; QUIZ to 13/15; FLASHCARDS daily. M3.
- **Week 3** — MINI_PROJECT: implement the full API surface with contract tests, breaking-change CI, and a deprecation workflow. M4–M6.
- **Week 4** — REAL_WORLD_PROJECT war story; write the platform API standard; teach-back: "our compatibility contract and how we enforce it" in 10 minutes.

---

## Artifacts you should be able to show

1. An OpenAPI + AsyncAPI specification generated from validated types, with examples.
2. A problem-details error catalogue with stable `type` URIs.
3. A breaking-change CI report blocking a rename, plus recorded-fixture replay tests.
4. A deprecation plan with measured per-client usage and a feasible sunset date.
5. A platform API standard adopted by at least two teams.

---

## Done = You Can

- Justify a status code, a limit, and a versioning choice numerically.
- Prove a change is non-breaking before merging it.
- Design deprecation with a migration rate you have actually computed.
- Say "this is a v2" and defend it, or "this does not need a v2" and defend that instead.
