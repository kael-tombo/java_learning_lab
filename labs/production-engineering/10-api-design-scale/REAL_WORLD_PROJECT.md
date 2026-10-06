# Lab 10: API Design & Evolution at Scale — Real World Project

## Scenario: "The Field We Renamed"

You are an architect on a fintech platform: 9 Spring Boot 3 services behind an API gateway, 11 internal consumers plus 3 external partner integrations, roughly 60 team members across 6 squads.

**The incident** — Monday 09:14, start of the European business day. Three of your partner integrations fail simultaneously with `400 Unprocessable Entity`.

**What happened over 4 days**:

1. **Friday 16:40** — Squad Payments ships `POST /v1/payouts` 4.7 → 5.0 to production as part of a routine release. The change renames `beneficiaryAccount` → `beneficiaryAccountIban` in the response and tightens validation so `reference` is now required on create.
2. **Friday 16:40–Monday 09:14** — Nothing fails immediately: two consumers use the request side, one reads the response via a generated client with `FAIL_ON_UNKNOWN_PROPERTIES` disabled, so the rename is silent.
3. **Monday 09:14** — Partner `clearbank-eu` sends a payout create with no `reference`. It is rejected with 400. Partner `nordic-pay` fails at 09:22 when its strict parser sees the unknown `beneficiaryAccountIban` and `beneficiaryAccount` is missing.
4. **Rollback is attempted 09:31** and fails: the payout batch job that ran over the weekend persisted 41,000 payouts whose `reference` values are now in a column the old code ignores. Rolling back re-enables duplicate payout attempts. Roll-forward takes 6 hours of data repair.
5. **Total impact**: 3 partners down for 4 hours 10 minutes; 12,800 payouts queued; one partner's reconciliation SLA missed; a contractual notification issued. Cost: $340K plus trust.

**Postmortem finding**: there is no contract enforcement anywhere in the delivery path. The OpenAPI document is generated at deploy time and thrown away, no one diffs it, and the change was merged because "it's just a response field rename."

**Your job over 4 weeks**: make the API contract a first-class, enforced artifact. Introduce contract tests, breaking-change detection, deprecation practice, and the API standards that would have blocked Friday's release — and prove that the same change now fails in CI in under 5 minutes.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Establish the current contract reality (Day 1–4)

### 1.1 Inventory the surface

For all 9 services: endpoints, methods, request/response schemas (as deployed, not as documented), error shapes, status codes actually returned, auth requirements, and rate limits. Note where the deployed behaviour differs from any written spec.

**Deliverable 1 — API inventory** with a per-endpoint table and a "documented vs actual" delta column. Expect several dozen undocumented behaviours.

### 1.2 Client inventory

Identify every consumer of every endpoint: 11 internal services, 3 partners, 4 scripts/batch jobs, plus anything discovered from gateway access logs. For each: does it use a generated client? Is its JSON parser strict? Does it do exhaustive enum matching? Does it construct URIs by hand?

**Deliverable 2 — Client matrix**: endpoint × consumer × client type × strictness × owner. This table is the basis of every compatibility decision that follows.

### 1.3 Reconstruct the Friday failure

Rebuild the causal chain: the change, which consumer would break, why nothing failed for 65 hours, why rollback was unsafe, and which control would have caught it.

**Deliverable 3 — Causal analysis** with the timeline, the per-consumer prediction, and the rollback-safety analysis.

### 1.4 Compatibility audit

Scan the git history of each service's controllers and DTOs for the last 12 months. Classify each deployed change as breaking, risky, or safe, and count how many breaking changes reached production.

**Deliverable 4 — Breaking-change audit**: total changes, breaking count, and the list — this is your business case.

---

## Phase 2 — Design the standard (Day 4–8)

### 2.1 Resource and error standard

One platform-wide convention, adopted everywhere:

- Plural resource nouns, max two levels of nesting, verbs only as actions on sub-resources (`/orders/{id}/cancel`) with `POST`.
- Status code catalogue: which codes mean what, and the rule that errors are status codes plus `application/problem+json` with an append-only `type` URI and a `code` enum.
- Limits: `pageSize` ≤ 100, bulk ≤ 100 items, `reference` length ≤ 64, all client-supplied collections capped.
- Server-capped, never client-trusted.

**Deliverable 5 — API standard v1** (naming, errors, limits, idempotency, pagination, deprecation, versioning stance), with a migration path per existing service.

### 2.2 Idempotency standard

`Idempotency-Key` required on every money-moving `POST`; key scope = caller + endpoint + key; store first response verbatim; TTL = 24 h for payouts, 10 min for low-risk creates; mismatch → 409; concurrent same-key → single create.

**Deliverable 6 — Idempotency spec** plus the implementation plan for the 9 money-moving endpoints.

### 2.3 Deprecation policy

- `Deprecation` + `Sunset` + `Link rel="successor-version"` from day one of deprecation.
- Per-client usage logging on every deprecated endpoint, for the full sunset window.
- No sunset date until usage data shows a feasible migration rate.
- `410 Gone` at sunset with the successor link.

**Deliverable 7 — Deprecation policy** with the migration-rate formula and a worked example.

---

## Phase 3 — Make contracts enforced (Week 2)

### 3.1 Specs as committed artifacts

Generate OpenAPI from validated types; commit it; CI regenerates and fails on drift. AsyncAPI for the event-driven endpoints (7 exist across 3 services).

**Deliverable 8 — Committed specs** for all 9 services, with the drift check running in CI and the delta list from Phase 1 reconciled.

### 3.2 Breaking-change detection

```yaml
- name: Breaking change detection
  run: |
    oasdiff breaking origin/main:openapi.yaml openapi.yaml --fail-on-ERR --format text
```

Escape hatch: an intentional break requires an ADR file and an owner approval, leaving a permanent record.

**Deliverable 9 — Breaking-change gate** with the audit result: re-run it over the last 12 months of history and report how many of the Phase 1 breaking changes it would have caught.

### 3.3 Consumer contract tests

Two layers:
1. **Provider tests** — generated from the spec; every status code, header, and content type the service claims to return is asserted, including error bodies.
2. **Consumer-driven tests** — for each of the 11 internal consumers, record its actual requests/expectations (Pact or Spring Cloud Contract) and run them against the provider in CI.

**Deliverable 10 — Contract test suite** running in CI for all 9 providers × 11 consumers, with a coverage table showing which consumer expectations are asserted.

### 3.4 Replay fixtures

Record 24 hours of production traffic (sanitized), store as request/response fixtures, replay on every build. Any change to status code, headers, or nullability shows up as a diff.

**Deliverable 11 — Recorded-fixture replay** with the diff report for one release.

---

## Phase 4 — Retrofit the highest-risk endpoints (Week 2–3)

Priority order, driven by the Phase 1 audit:

1. `POST /v1/payouts` — idempotency, validation, error catalogue.
2. `GET /v1/payouts/{id}` — typed DTO, PII removed, no response rename without deprecation.
3. `GET /v1/payouts` — cursor pagination, capped page size, no client-controlled sort.
4. `POST /v1/refunds` — idempotency.
5. Bulk payout endpoints — partial-success semantics.

For each: implement, deploy behind a version or additive change, and prove with contract tests that no consumer breaks.

**Deliverable 12 — Retrofit report** per endpoint: what changed, which consumers were affected, and the evidence that nothing broke.

---

## Phase 5 — Prove it (Week 3)

Replay the Friday release shape in staging, with the real consumers attached:

| Scenario | Change | Expected outcome |
|---|---|---|
| S1 | Add optional `updatedAt` to a response | merges clean; no client failure |
| S2 | Add a new enum value to `status` | merges, but the strict consumer fails its test → forced tolerance fix first |
| S3 | Rename `beneficiaryAccount` → `beneficiaryAccountIban` | **blocked in CI in < 5 min** with the exact breaking diff |
| S4 | Make `totalAmountMinor` nullable | blocked; requires an ADR |
| S5 | Tighten validation (`reference` required) | blocked as a breaking change |
| S6 | Uncapped `pageSize` | blocked by the limits lint |
| S7 | New endpoint added without a spec entry | blocked by the drift check |
| S8 | Same rename, but with `Deprecation` on the old field and `ALLOW_BREAKING` + ADR | merges, emits the deprecation headers, and the per-client usage dashboard shows who still reads it |
| S9 | Replay of the 24 h fixture set against the retrofitted payout endpoints | zero unintended diffs |
| S10 | Third party retries a timed-out payout create with the same key | single payout created; identical response replayed |

**Deliverable 13 — Contract enforcement test report** with all ten scenarios, the time each took to detect, and the fixes for anything missed.

---

## Phase 6 — Roll out the standard (Week 3–4)

- **Linting**: a shared OpenAPI lint profile (operation ids, examples, documented status codes, no untyped objects) in every service's CI.
- **Design review**: API changes reviewed by the owning squad plus one platform reviewer when the client matrix shows external or cross-squad consumers.
- **Generators**: client SDK generation from the committed spec, so consumers stop hand-writing models.
- **Default templates**: Spring Boot starter that ships the error handler, cursor pagination, idempotency filter, rate-limit filter, security headers, and the CI contract job.
- **Documentation**: generated from the spec, hosted, with deprecations visible.
- **Partner communication**: a partner-facing changelog with the deprecation policy and notice periods.

**Deliverable 14 — Rollout package**: lint profile, review process, generator setup, starter template, partner changelog.

---

## Phase 7 — Quantify and institutionalize (Week 4)

| Metric | Before | After |
|---|---|---|
| Breaking changes reaching production (12 mo) | 14 | 0 |
| Mean time from merge to production partner failure | 65 h | 0 (blocked in CI, < 5 min) |
| Endpoints with a committed, drift-checked spec | 0 / ~120 | 120 / 120 |
| Consumers with contract tests | 0 / 11 | 11 / 11 |
| Money-moving endpoints with idempotency | 0 / 9 | 9 / 9 |
| Uncapped `pageSize`/bulk endpoints | 23 | 0 |
| Deprecations with per-client usage data | n/a (no practice) | 100% |
| Client-driven rollback safety | unknown | rollback script verified for all 9 services |
| Mean detection time for a contract break | hours-to-days (partner) | < 5 min in CI |

Institutionalize: the API standard becomes part of the service template and the production readiness review; every new endpoint requires a spec entry in the same PR; the breaking-change gate is mandatory for merge; partner-facing deprecation notice is a contractual commitment with a minimum window defined.

**Deliverable 15 — Business case + institutionalization**, including the contractual deprecation window you commit to partners and the review at which it is approved.

---

## Deliverables checklist

- [ ] Phase 1 API inventory, client matrix, causal analysis, breaking-change audit.
- [ ] Phase 2 API standard, idempotency spec, deprecation policy.
- [ ] Phase 3 committed specs, breaking gate (with historical replay), contract tests, fixtures.
- [ ] Phase 4 retrofit of the five highest-risk endpoints.
- [ ] Phase 5 ten-scenario enforcement test report.
- [ ] Phase 6 lint profile, review process, generators, starter template, partner changelog.
- [ ] Phase 7 before/after business case + institutionalization.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Discovery | "We have OpenAPI" | Deployed-behaviour inventory, client strictness matrix, 12-month breaking-change audit |
| Diagnosis | "We renamed a field" | Causal chain, 65-hour silent window explained, rollback-safety analysis |
| Standard | "Use REST" | Naming, error catalogue, limits, idempotency, pagination, deprecation, versioning stance — with migration path |
| Enforcement | "We review the spec" | Committed specs + drift check + breaking gate + consumer contract tests + fixtures |
| Escape hatch | "We just skip the check" | ADR-gated intentional break leaving a permanent trail |
| Deprecation | "We send a header" | Per-client usage data, migration-rate feasibility, outreach, 410 + successor link |
| Proof | "Schema lints clean" | Replays the actual Friday change; blocked in < 5 min; partner retry idempotency proven |
| Rollout | "New teams should follow it" | Lint profile, generated SDKs, starter template, review process, partner contract |
| Economics | Technical only | Before/after numbers + contractual notice window approved at a named review |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Martin Fowler — "Microservices" (with the linked "MicroservicePremium"/API-evolution material)** — https://martinfowler.com/articles/microservices.html — the reference for API-evolution principles in a microservice estate: published contracts, decentralized monoliths, and the argument for evolutionary design and consumer-driven contracts. Use it to justify why the client matrix (not the provider's intent) determines compatibility, and why a spec nobody tests against is not a contract.
2. **Kubernetes API conventions — resource naming, paths, verbs, and how a large API evolves** — https://kubernetes.io/docs/concepts/overview/api-resources/ — a stable, authoritative worked example of a large API's compatibility discipline: plural noun resources, `path`/`verb` conventions, and the additive-evolution policy ("all additions to existing objects are backwards compatible"). The authoritative anchors for your own standard are the OpenAPI Specification's schema-evolution/compatibility rules and RFC 9457 `application/problem+json` for the error contract — verify the current OpenAPI version's compatibility clauses and the IANA HTTP Status Code Registry before writing either into a platform standard.

Additional anchors worth verifying: `oasdiff`'s current breaking-change rule set and `--fail-on-ERR` behaviour for your version (rule sets change between releases), the AsyncAPI specification version and its compatibility model for event contracts, and the IANA `Deprecation`/`Sunset`/`Link rel="successor-version"` header registrations — these were relatively recent and clients may not yet implement them.

---

## Reflection questions

1. The rename shipped on Friday and nothing failed for 65 hours. Which is the more serious problem — the breaking change, or the fact that your observability could not see a client silently degrading?
2. Rollback was unsafe because the batch job wrote data the old code ignored. What release discipline would have made rollback safe, and who has to enforce it?
3. Nine money-moving endpoints had no idempotency. How many duplicate payouts would you expect to have occurred before Monday, and why did nobody notice?
4. Contract tests take CI time. How would you measure the break-even point between the cost of running them and the cost of the next partner incident?
5. You cannot force partners to upgrade. What contractual notice period are you willing to commit to, and what happens on day 1 of the sunset?
