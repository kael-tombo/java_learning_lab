# Lab 08: Integrations — Real World Project

## Scenario
A manufacturing client's sales reps create Opportunities in Salesforce that must
become quotes in EBS. After quoting, order status flows back to Salesforce. Today
the process is manual double entry: quotes arrive two days late and 15% of orders
contain data entry errors. The client wants real-time sync, with error handling,
retry logic, and a dead letter queue so nothing is silently lost across 400
opportunities and 2,600 integration messages a day.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS Order Management)
- https://docs.oracle.com/database/121/OEAPI/ (Order Management API)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/

## Architecture
```
Salesforce (system of record: Opportunity, Account, Contact, pipeline)
   │  Opportunity saved → event published locally (ALWAYS succeeds)
   ▼
Event queue ──► EBS consumer (Workflow Business Event subscription)
                  │
                  ├─► Idempotency claim (PK on external_id)  ── replay?
                  │        └─ yes → return stored result, no duplicate
                  ├─► Fetch SF payload via REST + OAuth2 client credentials
                  ├─► Transform: SF Account/Contact → HZ_CUST_ACCOUNTS
                  ├─► Validate BEFORE the API (customer, site, order book, items)
                  ├─► OE_ORDER_PUB.create_order   ← last step, not first
                  └─► Audit + outcome

EBS (system of record: Quote, Order, fulfilment, pricing)
   │  Business events: ORDER_BOOKED / SHIPPED / CANCELLED
   ▼
Outbound message ──► Salesforce REST  (asynchronous; no response needed)

Failure handling:
  classify → RETRYABLE → bounded backoff (2,4,8,16s, 5 attempts) ──► DLQ
           → TERMINAL  → DLQ immediately (retry cannot help)
DLQ: full payload + error class + attempts ──► manual replay (idempotency protects)
```

## Implementation sketch
```sql
-- The PK insert IS the lock. This is what makes retry safe.
BEGIN
  INSERT INTO xx_int_idempotency (source_system, external_id, payload_hash, status)
  VALUES ('SALESFORCE', p_sf_opportunity_id, l_hash, 'IN_PROGRESS');
  COMMIT;
EXCEPTION WHEN DUP_VAL_ON_INDEX THEN
  SELECT status, ebs_object_id INTO l_status, l_obj FROM xx_int_idempotency
   WHERE source_system='SALESFORCE' AND external_id = p_sf_opportunity_id;
  IF l_status = 'SUCCESS' THEN
    p_x_quote_id := TO_NUMBER(l_obj);
    RETURN;   -- REPLAY the answer; do not create a second order
  END IF;
END;

-- Volume agreement catches what error rate cannot see
SELECT TO_CHAR(TRUNC(a.created_at),'YYYY-MM-DD') day,
       (SELECT COUNT(*) FROM sf_opportunity_log
         WHERE created_at BETWEEN TRUNC(a.created_at) AND TRUNC(a.created_at)+1) sf_opps,
       COUNT(a.audit_id) ebs_orders,
       COUNT(a.audit_id) - (SELECT COUNT(*) FROM sf_opportunity_log
         WHERE created_at BETWEEN TRUNC(a.created_at) AND TRUNC(a.created_at)+1) gap
  FROM xx_int_audit a
 WHERE a.message_type='OPPORTUNITY' AND a.operation='CREATE_ORDER'
 GROUP BY TO_CHAR(TRUNC(a.created_at),'YYYY-MM-DD'), TRUNC(a.created_at);
```

## Requirements
- F1: Documented ownership per entity and authoritative direction per field.
- F2: Salesforce event decoupling so an EBS outage cannot block order entry.
- F3: Idempotency keyed on the Salesforce Opportunity ID with payload hash.
- F4: OAuth2 client credentials with secrets in the EBS credential store.
- F5: Transformation Salesforce Account/Contact → `HZ_CUST_ACCOUNTS` via a
      configuration-driven mapping table.
- F6: Pre-API validation for customer, ship-to site, order book, and items.
- F7: Order creation through `OE_ORDER_PUB`.
- F8: Asynchronous order status push to Salesforce via outbound message.
- F9: Error classification, bounded backoff, and a replayable DLQ.
- F10: Monitoring covering throughput, latency, error rate, DLQ depth and
      age, and volume agreement.
- NF1: Quote latency under 60 seconds (from 2 days).
- NF2: Data entry error rate under 1% (from 15%).
- NF3: Zero duplicate orders from retries.
- NF4: DLQ depth under 10/day with oldest entry under 24 hours.
- NF5: Security baseline — dedicated least-privilege integration user, no
      plaintext secrets.
- NF6: Documented rollback for every message type and configuration change.

## Milestones
- Week 1: Ownership decisions agreed with sales and order management.
- Week 2: Salesforce credentials, event subscription, and payload contract.
- Week 3: Idempotency, transformation, and validation implemented.
- Week 4: Order creation and status push end to end.
- Week 5: Classification, backoff, DLQ, and replay procedure.
- Week 6: Monitoring, backfill plan, and pilot with one sales region.

## Verification
- Process the same payload twice; confirm exactly one order exists.
- Fault injection: Salesforce timeout, 401, validation failure, EBS mid-upgrade.
- Confirm terminal errors are not retried and land in the DLQ immediately.
- Volume agreement across a full week with zero unexplained gaps.
- Security review of the integration user's privileges and secret storage.

## Rollback
Integration users can be disabled to halt all inbound flow without affecting
either business system; DLQ retains every unprocessed message for later replay;
field mappings are configuration. Document rollback steps for every change.