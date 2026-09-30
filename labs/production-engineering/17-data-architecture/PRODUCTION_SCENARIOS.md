# PRODUCTION SCENARIOS: Data Architecture & Distributed State Failures
## Lab 17 | Production Engineering Academy

---

## Scenario 1: The Zombie Compensating Transaction in E-Commerce Saga

### Context
A travel booking platform handling flights, hotels, and car rentals. Bookings were orchestrated via a Saga.

### The Disaster
- Step 1: Flight booked and credit card charged ($850).
- Step 2: Hotel booking failed because rooms sold out during checkout.
- Saga orchestrator initiated compensating transaction: `RefundCreditCard($850)`.
- The payment gateway API was experiencing a network partition and timed out during the refund call.
- The Saga orchestrator had a naive exception handler that treated the timeout as a permanent failure and aborted the workflow!
- Result: The customer was charged $850 for a vacation package that was never booked. 1,400 customers experienced this during a holiday weekend, resulting in severe brand damage and regulatory fines.

### The Fix
Compensating transactions **must be idempotent and guaranteed to eventually succeed**:
1. Persist Saga state transitions in an append-only Saga log table.
2. If a compensating transaction times out, transition to `COMPENSATION_RETRYING` state.
3. A background reconciler daemon continuously retries compensating actions with exponential backoff until acknowledged by the payment gateway, never abandoning money in an inconsistent state.

---

## Scenario 2: CQRS Replication Lag & "Read-Your-Own-Writes" Violation

### Context
A social media platform implemented CQRS: writes went to PostgreSQL, while user feeds were read from an Elasticsearch read model synchronized via Kafka.

### The Failure Mode
- User updated their profile name and profile picture.
- The frontend immediately redirected the user back to `/profile`.
- The read request queried Elasticsearch, where replication lag was currently running at 1,500ms due to Kafka consumer lag.
- The user saw their old profile name and photo!
- Confused, the user repeatedly clicked "Save Changes", generating dozens of duplicate write requests and overwhelming customer support with "Profile update is broken" tickets.

### The Solution: Read-Your-Own-Writes Consistency
1. In the write response, return the write transaction version or timestamp: `etag: v1042`.
2. The client passes `If-None-Match` or includes `min_version=v1042` on subsequent GET requests.
3. If the read replica has not caught up to `v1042`, the gateway routes the read directly to the primary database for that specific user for the next 5 seconds.
