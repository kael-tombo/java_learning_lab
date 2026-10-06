# Lab 08: Integrations — Flashcards

## Boundaries

---
**Q**: First design question?
**A**: Who owns what — system of record per entity, authoritative direction per field.

---
**Q**: Who owns what in this lab?
**A**: Salesforce: Opportunity, Account, Contact, pipeline. EBS: Quote, Order, pricing, fulfilment. Neither: the mapping.

---
**Q**: Why do 2-day delays and 15% errors persist in a "working" integration?
**A**: Missing boundary definitions. Double entry exists because nobody decided who owns the customer record.

---
**Q**: Why synchronous everywhere is wrong?
**A**: An EBS outage would break Salesforce order entry. Two systems of record, two availability requirements.

---

## Mechanisms

---
**Q**: What does a business event give you?
**A**: The Salesforce save always succeeds. The producer does not know or care who consumes. Failures isolate per subscriber.

---
**Q**: Synchronous vs asynchronous — which for what?
**A**: Actions needing an outcome → synchronous. State notifications → asynchronous.

---
**Q**: EBS business events in this lab?
**A**: Order Booked, Order Shipped, Order Cancelled, Quote Created.

---
**Q**: Why not polling?
**A**: No polling load, no producer changes when a consumer is added, per-subscriber failure isolation.

---

## Idempotency

---
**Q**: The ambiguity problem?
**A**: A lost response means the client cannot tell if the server succeeded. Retry then duplicates the order.

---
**Q**: How is the key claimed?
**A**: `INSERT` first. The primary key violation IS the lock. Claim before any side effect.

---
**Q**: Second delivery behaviour?
**A**: `DUP_VAL_ON_INDEX` → look up the stored result → replay the answer. Do not create a second order.

---
**Q**: Same ID, different payload hash?
**A**: Flag for review. Do not silently update an object already transmitted downstream.

---
**Q**: Cost of duplicates without idempotency?
**A**: ~110/year at $1,200 each ≈ **$132K/year**, prevented by one PK insert.

---

## Error Handling

---
**Q**: Retryable?
**A**: Timeouts, 503, connection reset, transient ORA errors.

---
**Q**: Terminal?
**A**: Validation failures, API rejects, 401 auth, malformed payloads, unknown (default).

---
**Q**: Why classify before retrying?
**A**: Retrying a validation error sends the same wrong data five times. Retrying a 401 burns attempts on a credential that will not self-heal.

---
**Q**: Misclassifying RETRYABLE as TERMINAL — cost?
**A**: Premature DLQ. ~1,000 messages/year × 15 min triage = **250 hours/year** of manual work.

---
**Q**: Default classification for unknown errors?
**A**: TERMINAL. Surface to a human rather than looping.

---

## Retry

---
**Q**: Backoff schedule (base 2s, 5 attempts)?
**A**: 0s, 2s, 6s, 14s, 30s → DLQ at ~30 seconds.

---
**Q**: Unbounded retry requests/hour per stuck message?
**A**: ~3,600 immediate. Bounded exponential ≈ 120. Bounded 5-attempt = 6 total.

---
**Q**: Why bounded?
**A**: Unbounded is a denial-of-service pattern against your own dependency, and the DLQ never gets created.

---
**Q**: Transient vs terminal retry — different mechanisms?
**A**: Yes. Transient: more attempts, longer horizon. Terminal: few attempts, then DLQ for a human.

---

## DLQ

---
**Q**: What must a DLQ store?
**A**: Full payload (not a summary), error class, error code, attempt count, first/last failed timestamps, status.

---
**Q**: Why the full payload?
**A**: Without it, replay requires reconstructing the message from a possibly purged audit trail.

---
**Q**: Alert thresholds?
**A**: Depth > 10/day (2,600 daily volume = 0.4%), plus oldest entry age > 24h.

---
**Q**: Why alert on age, not just depth?
**A**: Old entries mean nobody is triaging. The DLQ has become a graveyard rather than a recovery mechanism.

---
**Q**: What makes a replay safe?
**A**: Idempotency. Replaying an already-SUCCESS message returns the stored result instead of duplicating.

---

## Transformation and Validation

---
**Q**: Why a field mapping table?
**A**: Adding a Salesforce field becomes an INSERT (minutes) not a code deployment (4 hours + regression). In the lab: 48 hours/year saved.

---
**Q**: Unmapped field behaviour?
**A**: Must be explicit. Silently dropping fields produces records missing data discovered only when a report is wrong.

---
**Q**: Validate before or after the API call?
**A**: Before. API errors are formatted strings, not diagnostics. "Customer 12345 does not exist" discovered after a round trip wastes it.

---
**Q**: Validation checks for orders?
**A**: Customer exists and active · ship-to site valid · order book open · items orderable · currency matches site.

---

## Security

---
**Q**: OAuth flow for machine-to-machine?
**A**: Client credentials. Short-lived token (30–60 min), refreshed by the client.

---
**Q**: Where do secrets live?
**A**: EBS credential store / wallet. **Never** plaintext in `APPL_TOP`.

---
**Q**: Why does that matter?
**A**: Plaintext is readable by every OS user on a shared 20-admin app tier.

---
**Q**: Integration user privileges?
**A**: Quote creation only. Least privilege limits a credential compromise to one operation instead of all AP functions.

---

## Monitoring

---
**Q**: Four metrics?
**A**: Throughput, latency, error rate, DLQ depth. **Plus** volume agreement.

---
**Q**: What does volume agreement catch that error rate cannot?
**A**: Silent drops. 400 opportunities, 396 orders, **0% error rate** — nothing appears in any error report.

---
**Q**: Scheduler interval trade-off?
**A**: 30s → 15s average latency, 2,880 polls/day. Beyond 60s users believe it's broken.

---
**Q**: End-to-end latency budget vs manual?
**A**: ~25s automated vs 48 hours manual (2,160×). The integration is not latency-constrained — reliability is where the value is.

---

## Business Case

| Metric | Manual | Automated |
|--------|--------|-----------|
| Quote latency | 48 hours | ~25 seconds |
| Error rate | 15% | ~1% |
| Errors/month | 270 | 18 |
| Error correction cost | ~$630K/yr | ~$42K/yr |
| **Annual saving** | | **~$588K** |

**Latency is the headline; the $588K in error correction is what funds it.**

---

## Quick Reference

| Task | Object / Call |
|------|---------------|
| Order API | `OE_ORDER_PUB.create_order` |
| Order header rec | `oe_order_pub.order_rec_type` |
| Auth token | OAuth2 `/services/oauth2/token` |
| SF REST version | `v59.0` |
| Secrets | Credential store (`xx_sec_pvt.get`) |
| HTTP call | `UTL_HTTP` with Bearer token |
| Request record | `FND_CONCURRENT_REQUESTS` |

---

## Anti-Patterns

1. Synchronous call in the direction that must survive an outage.
2. Retry without an idempotency key.
3. Retrying validation or auth errors.
4. Unbounded retry in a scheduled job.
5. DLQ without payload or without replay.
6. Hardcoded field mappings.
7. Plaintext secrets in `APPL_TOP`.
8. Monitoring error rate only.
9. Validating from the API's error messages.

---

## Study Tips
1. Write the ownership table from memory.
2. Explain the ambiguous-response problem in one sentence with a number.
3. State the backoff schedule and total elapsed before DLQ.
4. Describe a failure with 0% error rate that still loses data.