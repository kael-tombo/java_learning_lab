# Lab 08: Integrations — Exercises

## Exercise 1: Ownership Boundaries
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Define system of record per entity and direction per field.

### Steps
1. List the entities on both sides (Opportunity, Account, Quote, Order).
2. Assign a system of record to each.
3. For a shared concept, name the authoritative direction per field.
4. Name an owner for the mapping table.

### Verification
- [ ] Every entity has exactly one system of record
- [ ] Authoritative direction stated per contested field
- [ ] Mapping table owner named
- [ ] Double-entry scenario explained as a symptom of a missing decision

---

## Exercise 2: Decoupling With Business Events
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Ensure a Salesforce save never depends on EBS uptime.

### Steps
1. Draw the synchronous (coupled) design.
2. Identify what breaks when EBS is unavailable.
3. Redraw with an event queue between them.
4. Confirm the Salesforce transaction succeeds regardless.

### Verification
- [ ] Both designs drawn
- [ ] Failure impact of each stated
- [ ] Event version guarantees the save succeeds

---

## Exercise 3: Idempotency
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Make retry safe and prove it.

### Steps
1. Create the idempotency table with the composite primary key.
2. Implement the claim-first pattern with `DUP_VAL_ON_INDEX` handling.
3. Process the same payload twice.
4. Confirm one order exists and the second call replays the result.

### Verification
- [ ] Claim precedes any side effect
- [ ] Second call returns the stored object ID
- [ ] Exactly one order created
- [ ] Different payload with the same ID is flagged, not silently applied

---

## Exercise 4: Error Classification
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Classify ten failure modes as retryable or terminal.

### Steps
1. List ten failures: 401, 503, timeout, ORA error, validation failure,
   API reject, constraint violation, malformed payload, DLQ replay, unknown.
2. Classify each with a written reason.
3. Confirm retrying a classified terminal failure would be pointless.

### Verification
- [ ] All ten classified
- [ ] Reasons given for each, not just the label
- [ ] Unknown defaults to TERMINAL
- [ ] Auth and validation confirmed terminal

---

## Exercise 5: Bounded Backoff
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Implement bounded exponential backoff with a terminal state.

### Steps
1. Implement retry with delays 2, 4, 8, 16 seconds.
2. Cap at 5 attempts.
3. On exhaustion, write to the DLQ with the full payload.
4. Confirm total elapsed before DLQ is ~30 seconds.

### Verification
- [ ] Delays follow exponential growth
- [ ] Attempt count is bounded
- [ ] DLQ entry created with the complete payload
- [ ] No infinite loop under repeated failure

---

## Exercise 6: DLQ Replay
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Replay a failed message after fixing the cause.

### Steps
1. Fail a message deliberately and let it reach the DLQ.
2. Confirm the payload is complete and queryable.
3. Fix the underlying cause.
4. Replay and confirm success.
5. Replay a message that is already SUCCESS; confirm no duplicate.

### Verification
- [ ] DLQ retains the full payload
- [ ] Replay succeeds after the fix
- [ ] Idempotency protects against duplicate replay
- [ ] Resolved entries record who and when

---

## Exercise 7: Configuration-Driven Mapping
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Add a mapped field without a code change.

### Steps
1. Move three field mappings into `XX_FIELD_MAPPING`.
2. Add a fourth field by inserting a row only.
3. Process a payload containing the new field.
4. Confirm it is transformed without any deployment.

### Verification
- [ ] Mappings read from configuration
- [ ] New field added by INSERT only
- [ ] Transformation handles the new field
- [ ] Time-to-add recorded (target: minutes, not hours)

---

## Exercise 8: Volume Agreement
**Time**: 25 minutes | **Difficulty**: Advanced

### Objective
Detect silently dropped messages.

### Steps
1. Run the agreement query over several days.
2. Delete one audit row to simulate a silent drop.
3. Confirm the query shows a non-zero gap with a 0% error rate.
4. Add a DLQ depth and age alert alongside it.

### Verification
- [ ] Agreement query written
- [ ] Gap detected while error rate remains 0%
- [ ] Explanation given for why error rate alone misses this
- [ ] Alerts cover depth and age

---

## Exercise 9: Security Review
**Time**: 20 minutes | **Difficulty**: Intermediate

### Objective
Verify least privilege and secret handling.

### Steps
1. Inspect the integration user's privileges.
2. Confirm no plaintext secret exists in `APPL_TOP`.
3. Confirm token lifetime is short.
4. Quantify the blast radius of a leaked secret.

### Verification
- [ ] Integration user has quote creation only
- [ ] Secrets in the credential store
- [ ] Token lifetime under 60 minutes
- [ ] Blast radius described in terms of operations, not users