# Lab 08: Integrations (SOAP / Business Events) — Theory

## The Scenario

Sales reps create Opportunities in Salesforce that must become quotes in EBS.
After quoting, the order flows back to Salesforce. Manual double entry causes a
2-day quote delay and 15% of orders have data entry errors. The client wants
real-time sync.

## Principle 1: Integration architecture is a boundary decision first

The hardest question is not "SOAP or REST" but **who owns what**.

```
Salesforce owns:  Opportunity, Account, Contact, pipeline
EBS owns:         Quote, Order, fulfilment, pricing
Neither owns:     the mapping between them
```

That third line is the integration. It must have:

1. **A system of record per entity.** Opportunity value lives in Salesforce;
   quote total lives in EBS. Neither is a mirror of the other.
2. **An authoritative direction per field.** Salesforce owns *what was
   negotiated*; EBS owns *what it costs*. Both flow to the report.
3. **An owner for the mapping table.** Unowned mapping tables become stale and
   silently wrong.

The 2-day delay and 15% error rate are both symptoms of a missing boundary
definition. Double entry exists precisely because nobody decided which system
owns the customer record.

## Principle 2: Business events decouple production from consumption

**Push coupling** (the trap):

```
Salesforce creates Opportunity
   → synchronously call EBS
   → EBS is down / slow / mid-upgrade
   → the Salesforce transaction fails or times out
   → the rep's work is lost or blocked
```

The rep's work in Salesforce now depends on EBS availability. That is
architecturally wrong — they are different systems of record with different
availability requirements.

**Event coupling**:

```
Salesforce creates Opportunity
   → save locally (always succeeds)
   → publish event to a queue
   → an EBS-side consumer picks it up and processes it
   → failures retry independently
```

In EBS, the native mechanism is the **Workflow Business Event System**. An
event is raised when domain state changes; subscribers receive it.

| Event | Raised when |
|-------|-------------|
| Quote Created | `OE_QUOTE_PUB` completes |
| Order Booked | `OE_ORDER_PUB` completes |
| Order Shipped | Shipment confirmed |
| Order Cancelled | Cancellation processed |

### Why events rather than a polling integration

- No polling load on either system.
- The producer does not know or care who consumes.
- Adding a consumer does not change the producer.
- Failures are isolated per subscriber.

## Principle 3: Synchronous SOAP for actions, asynchronous for state

Two different needs:

```
INBOUND (Salesforce → EBS):
  "Create this quote"   → needs a response: quote number, or an error
                          → SYNCHRONOUS

OUTBOUND (EBS → Salesforce):
  "Order 12345 shipped" → no response needed; Salesforce records it
                          → ASYNCHRONOUS (outbound message / event subscriber)
```

Applying synchronous calls everywhere means an EBS outage breaks Salesforce
order entry. Applying asynchronous everywhere means the rep sees "submitted"
and then a failure an hour later with no clear cause.

**Match the mechanism to the need**: actions that must report an outcome are
synchronous; state notifications are asynchronous.

## Principle 4: Idempotency is the property that makes retry safe

Without idempotency, a retry creates duplicate orders. This is not a rare
concern — it is the normal case, because network timeouts are ambiguous:

```
Client sends create order → server processes it → response lost in transit
Client cannot tell: did it succeed or fail?
Client retries → DUPLICATE ORDER
```

**The response was lost, but the side effect happened.** Only the server knows
which. So the server must deduplicate.

### The pattern

```sql
-- Client sends a stable external reference
-- Server checks it before doing anything

CREATE TABLE xx_int_idempotency (
  source_system  VARCHAR2(20) NOT NULL,
  external_id    VARCHAR2(100) NOT NULL,
  payload_hash   VARCHAR2(64),          -- detects changed payloads
  status         VARCHAR2(15) NOT NULL, -- IN_PROGRESS / SUCCESS / FAILED
  ebs_object_id  VARCHAR2(40),
  created_at     TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  completed_at   TIMESTAMP,
  CONSTRAINT xx_idem_pk PRIMARY KEY (source_system, external_id)
);
```

```sql
-- Insert first: the PK is the lock
BEGIN
  INSERT INTO xx_int_idempotency (source_system, external_id, payload_hash, status)
  VALUES ('SALESFORCE', p_opportunity_id, p_hash, 'IN_PROGRESS');
  COMMIT;                       -- claim it
EXCEPTION WHEN DUP_VAL_ON_INDEX THEN
  -- already processed; return the existing result, do not duplicate
  SELECT status, ebs_object_id INTO l_status, l_obj FROM xx_int_idempotency
   WHERE source_system='SALESFORCE' AND external_id = p_opportunity_id;
  IF l_status = 'SUCCESS' THEN RETURN l_obj;  -- replay the answer
  ELSE RAISE_APPLICATION_ERROR(-20090,'Already in progress'); END IF;
END;
```

**Without this, every retry policy is a duplicate-creation policy.**

## Principle 5: Retry needs bounds, backoff, and a terminal state

Naive retry:

```
Fail → retry immediately → fail → retry → ... forever
```

Three problems: it hammers a struggling service, it never stops, and it produces
an infinite loop in a scheduled job.

### Bounded exponential backoff

```
Attempt 1: immediate
Attempt 2: +2 seconds
Attempt 3: +4 seconds
Attempt 4: +8 seconds
Attempt 5: +16 seconds
  → give up: move to dead letter queue
```

Bounded because an unbounded retry is a denial-of-service tool aimed at your own
dependencies. Giving up because the DLQ is the terminal state, and someone must
decide what to do with it.

### What is retryable?

| Failure | Retryable? | Reason |
|---------|-----------|--------|
| Connection timeout | Yes | Transient |
| HTTP 503 | Yes | Service overloaded |
| HTTP 401 | **No** | Credential problem — retrying cannot fix it |
| Validation error | **No** | Data is wrong; retrying sends the same wrong data |
| Unique constraint on idempotency key | **No** | Already processed |

**Retrying a validation error is pointless** — the payload is wrong and will
remain wrong. Retrying an auth failure just burns attempts. Classify before
retrying.

## Principle 6: The dead letter queue is a product requirement

When retry is exhausted, the message must land somewhere queryable.

```
XX_INTEGRATION_DLQ
  message_id
  source_system
  message_type        -- OPPORTUNITY / QUOTE / ORDER_STATUS
  external_id
  payload             -- the full message, not a summary
  error_code
  error_message
  attempt_count
  first_failed_at
  last_failed_at
  status              -- OPEN / REPLAYED / DISCARDED
  resolved_by
  resolved_at
```

Three properties:

1. **Full payload retained.** Without it, replay requires reconstructing the
   message from an audit trail that may have been purged.
2. **Error classification stored.** So DLQ triage can be aggregated: 90% auth
   failures points at one fix.
3. **Replayable.** A DLQ you cannot replay is a message graveyard.

```
DLQ entries:              0    → healthy
DLQ entries per day:      2    → normal for a high-volume integration
DLQ entries per day:      40   → investigate
DLQ entries per day:      200  → the integration is broken
```

## Principle 7: Transformation is a translation problem, not a copy

Salesforce Account → EBS `HZ_CUST_ACCOUNTS` is not field copying.

| Concept | Salesforce | EBS |
|---------|-----------|-----|
| Customer | Account | `HZ_PARTIES` / `HZ_CUST_ACCOUNTS` |
| Contact | Contact | `HZ_CONTACT_POINTS` |
| Address | BillingAddress | `HZ_LOCATIONS` |
| Opportunity | Opportunity | `OE_QUOTES` header |
| OpportunityLineItem | Product2 | `OE_PRICE_LIST_LINES` |

Mapping tables, not hardcoded field lists:

```sql
CREATE TABLE xx_field_mapping (
  source_system VARCHAR2(20),
  entity_name   VARCHAR2(50),      -- ACCOUNT / CONTACT / OPPORTUNITY
  source_field  VARCHAR2(60),
  target_table  VARCHAR2(30),
  target_column VARCHAR2(30),
  transform_rule VARCHAR2(50) DEFAULT 'DIRECT', -- DIRECT/UPPER/DEFAULT/DATE_FMT
  mandatory_flag CHAR(1) DEFAULT 'N',
  active_flag   CHAR(1) DEFAULT 'Y',
  CONSTRAINT xx_fm_pk PRIMARY KEY (source_system, entity_name, source_field)
);
```

**Why a table, not code**: when the client adds a required field in Salesforce,
the change is a row insert, not a code deployment. In a consulting engagement
that is the difference between hours and a week.

## Principle 8: Validation belongs before the API call

Validate against EBS before calling `OE_QUOTE_PUB`:

```
✓ Customer exists and is active
✓ Ship-to site is valid for the customer
✓ Requested date is open in the order book
✓ Items exist and are orderable
✓ Currency matches the site's currency
```

Each failure produces a specific message. Discovering "customer 12345 does not
exist" after the API call wastes a round trip and produces a generic SOAP fault.

**The API is the last step, not the validation step.** Its errors are structural
(formatted message strings), not diagnostic.

## Principle 9: Authentication is the integration's attack surface

OAuth2 client credentials for machine-to-machine:

```
Client → token endpoint: grant_type=client_credentials
       ← access_token (short-lived)
Client → resource: Bearer <token>
```

Security requirements:

| Control | Requirement |
|---------|-------------|
| Secrets | Not in source, not in APPL_TOP plaintext |
| Storage | Credential store / wallet / encrypted table |
| Token lifetime | Short (30–60 min) |
| TLS | Certificate validation on both endpoints |
| Least privilege | Integration user has only what it needs |
| Audit | Token issuance and use logged |

**A client secret in a shell script on the app tier is a credential compromise
waiting to be found.** On EBS, use the credential store framework or a wallet —
never a plaintext file in `APPL_TOP`.

## Principle 10: Monitoring is the difference between an integration and a hope

Four metrics matter:

```
1. Throughput     — messages processed per hour
2. Latency        — event raised to object created
3. Error rate     — failures / total
4. DLQ depth      — unprocessed failures
```

Plus business-level agreement, which catches what error rates miss:

```
Salesforce Opportunity count  vs  EBS Quote count, per day
```

```
Opportunities created: 400
Quotes created:         396
Gap:                     4
```

A 1% business-level gap with a 0% error rate means messages are being **dropped
silently** — the worst failure mode, because no error appears anywhere.

## Design Order

1. Define ownership per entity and authoritative direction per field.
2. Choose synchronous for actions, asynchronous for state.
3. Publish business events for everything EBS-side.
4. Implement idempotency keyed on the external ID.
5. Classify errors into retryable and terminal.
6. Add bounded backoff and a replayable DLQ.
7. Externalise field mappings into configuration.
8. Validate before calling APIs.
9. Store credentials in the credential store.
10. Monitor throughput, latency, error rate, DLQ depth, and volume agreement.

## Anti-Patterns

- Synchronous calls in the direction that must not fail on the other side's outage.
- Retrying without an idempotency key, creating duplicates.
- Retrying validation errors and auth failures.
- Unbounded retry loops in a scheduled job.
- A DLQ without the payload, or without replay capability.
- Hardcoded field mappings requiring a code deployment to add a field.
- Client secrets in plaintext on the app tier.
- Monitoring only error rate, not volume agreement.
- Calling the API first and validating from its error messages.

## Summary

The 2-day delay and 15% error rate came from missing architectural decisions
rather than missing code. Defining ownership per entity removed double entry.
Business events decoupled the producer so an EBS outage cannot break Salesforce.
Idempotency made retry safe instead of duplicating orders. Error classification
meant validation failures were not retried pointlessly. A replayable DLQ gave
failed messages somewhere to go. And monitoring volume agreement — not just
error rate — caught the failure mode where messages disappear silently.