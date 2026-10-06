# Lab 08: Integrations — VISION

## Where this lab takes you
From 2-day manual quote delay and 15% data entry errors to a bi-directional
integration that cannot create duplicates, cannot loop forever, and cannot lose a
message silently.

## The Arc
1. **Boundaries** — who owns what, per entity and per field.
2. **Decoupling** — business events so an outage cannot break the other system.
3. **Mechanism choice** — synchronous for actions, asynchronous for state.
4. **Idempotency** — the property that makes retry safe.
5. **Classification** — retry only what a retry could fix.
6. **Bounded backoff** — with a terminal state, not an infinite loop.
7. **Dead letter queue** — full payload, replayable, monitored.
8. **Agreement monitoring** — catch silent drops, not just errors.

## Milestones (checkable)
- [ ] M1: Write the ownership table: system of record per entity, direction per field.
- [ ] M2: Design the event flow so a Salesforce save never depends on EBS uptime.
- [ ] M3: Implement the idempotency claim and prove a replay returns the original result.
- [ ] M4: Classify ten error cases into retryable and terminal, with reasons.
- [ ] M5: Implement bounded backoff and prove a terminal error is not retried.
- [ ] M6: Build a DLQ with full payload and write a working replay procedure.
- [ ] M7: Move field mappings into configuration and add a field without code.
- [ ] M8: Write the volume-agreement query and demonstrate a silent drop.

## Anti-Goals
- Calling EBS synchronously from the Salesforce save path.
- Retrying without an idempotency key, creating duplicate orders.
- Retrying validation errors and 401s.
- Unbounded retry loops in a scheduled job.
- A DLQ that stores only an error summary, or cannot be replayed.
- Hardcoded field mappings that require a deployment to add a field.
- Client secrets in plaintext on the app tier.
- Monitoring only error rate and missing silent drops.
- Validating only from the API's error messages.

## The one-sentence thesis
An integration is trustworthy when failure is expected — decide ownership first,
make retry idempotent, classify errors before retrying, and monitor volume
agreement so nothing disappears quietly.