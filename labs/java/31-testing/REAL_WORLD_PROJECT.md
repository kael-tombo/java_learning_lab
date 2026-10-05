# REAL-WORLD PROJECT — Testing: Flaky Suite Hides a Double-Charge Bug

## Incident Scenario
Billing deploys on green CI, then double-charges 3,200 customers: the suite
is 40% E2E, retries flakes, and mocks the payment gateway so the
exactly-once rule was never tested against a real fault.

## Symptoms
- CI passes after 2–3 retries; `附` flaky list grows weekly, owned by nobody.
- Unit tests mock `InvoiceRepository` AND `Money` — logic untested.
- No Testcontainers; H2 masks a Postgres `ON CONFLICT` idempotency bug.
- Webhook handler untested under timeout → duplicate charge on retry.
- Coverage 82% but PIT would show survivors on the charge path.

## Investigation Tasks
1. Triage: `jcmd <pid> Thread.print` on stuck E2E (Selenium/grid waits);
   `jcmd <pid> GC.heap_dump` only if CI OOM — else focus on test forensics.
2. JFR on the service (not tests): `jcmd <pid> JFR.start duration=120s
   filename=billing.jfr`; confirm duplicate `charge` calls via
   `jdk.JavaMonitorEnter` / custom JFR event or log trace IDs.
3. DB forensics: `SELECT idempotency_key, COUNT(*) ... HAVING COUNT(*)>1`;
   diff H2 vs Postgres DDL (case, upsert semantics).
4. Repro: WireMock timeout on first `charge`, immediate retry — show second
   charge fires (missing `idempotency_key` guard); run 20x to prove flake.
5. Suite audit: classify tests (unit/slice/E2E), time each, list retries in
   CI config; run PIT on `billing/` to expose survivors.
6. Clock/random audit: `grep -rn "Instant.now\|Random\|Thread.sleep" src/ test/`.
7. Log diff: `grep "charge.*orderId" app.log | sort | uniq -d` for dupes.

## Root Cause
Ice-cream-cone suite + over-mocking + H2-only persistence + retry-masked
flakes + no idempotency contract test; timeout-retry path charges twice.

## Resolution
- Immediate: halt billing deploy; backfill refunds; add DB unique constraint
  on `idempotency_key`; hotfix exactly-once guard in charge path.
- Short-term: pyramid rebuild (parametrized units, slices, one Testcontainers
  IT), WireMock fault tests, fake clock, quarantine+fix flakes, PIT gate.
- Long-term: fast/slow CI split, flake SLO + ownership, contract tests with
  gateway, chaos on webhook path.

## Runbook
```
1. Freeze deploys; JFR + dup-key query + charge-log diff.
2. Land idempotency guard + unique constraint (backfill first).
3. Rebuild pyramid tip-down; WireMock timeout test must pass 20/20.
4. PIT >= 85% on billing/; flake-quarantine lane in CI.
5. Postmortem: refund report + exactly-once runbook.
```

## Metrics
- Duplicate charges = 0 over 30d; idempotency test 20/20 green.
- Fast ring < 3 min; flake rate < 1%; PIT >= 85% on charge path.
- E2E share < 10% of suite; retries removed from CI config.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Spring testing reference: https://docs.spring.io/spring-framework/reference/testing.html
- Spring Boot testing: https://docs.spring.io/spring-boot/reference/testing/index.html
