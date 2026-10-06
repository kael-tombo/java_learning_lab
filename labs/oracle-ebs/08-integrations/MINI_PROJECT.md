# Lab 08: Integrations — Mini Project

## Goal
Build a bi-directional Salesforce-to-EBS integration with idempotency, bounded
retry, and a replayable DLQ in 90 minutes.

## Requirements
- R1: Ownership table naming system of record per entity.
- R2: Idempotency table keyed on the external ID, with payload hash.
- R3: Processing procedure that claims the key and replays stored results.
- R4: Transformation from Salesforce JSON to EBS order records.
- R5: Validation step that runs before the API call.
- R6: Error classifier mapping ten cases to retryable or terminal.
- R7: Bounded backoff retry with DLQ entry on exhaustion.
- R8: DLQ replay procedure and a volume-agreement query.

## Steps
1. Write the ownership and direction table.
2. Create idempotency, DLQ, audit, and field mapping tables.
3. Implement the transformation from a sample Salesforce payload.
4. Implement validation rejecting a missing customer or closed order book.
5. Implement the idempotent processing procedure.
6. Process the same payload twice; confirm the second returns the stored result.
7. Simulate a timeout; confirm retry then DLQ with the full payload.
8. Simulate a validation error; confirm no retry occurs.
9. Fix the data and replay from the DLQ; confirm success.
10. Delete one message from the audit trail and run the agreement query.

## Acceptance criteria
- Processing the same payload twice creates exactly one order.
- A changed payload with the same external ID is flagged, not silently applied.
- A validation error goes to the DLQ after one attempt, not five.
- A transient error retries with increasing delays, then enters the DLQ.
- The DLQ retains the complete payload and replay succeeds after the fix.
- The agreement query exposes the deliberately deleted message.

## Stretch
- Add a new field to the mapping table and process it with no code change.
- Measure end-to-end latency and state which stage is not worth optimising.