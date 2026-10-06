# Lab 08: Integrations — Quiz

**1.** What is the first design question for an integration?

A. SOAP or REST
B. Who owns what — system of record per entity, authoritative direction per field
C. Which scheduler to use
D. How many retries

<details><summary>Answer</summary><b>B</b> — The 2-day delay and 15% errors are symptoms of a missing boundary decision. Double entry exists precisely because ownership was never assigned.</details>

---

**2.** Why publish an event rather than call EBS synchronously from Salesforce?

A. Events are faster
B. A synchronous call makes the rep's work depend on EBS availability; an EBS
   outage would break Salesforce order entry
C. SOAP cannot be synchronous
D. Events use less bandwidth

<details><summary>Answer</summary><b>B</b> — Two systems of record have different availability requirements and must not share a failure domain.</details>

---

**3.** When should a call be synchronous?

A. Always
B. Never
C. For actions that must report an outcome; state notifications are asynchronous
D. Only for writes

<details><summary>Answer</summary><b>C</b> — Synchronous everywhere means an outage on one side blocks the other. Asynchronous everywhere means reps see "submitted" then a silent failure an hour later.</details>

---

**4.** Why is idempotency required for retry?

A. It improves throughput
B. A lost response leaves the outcome ambiguous — the server did the work but the
   client cannot tell, so retrying duplicates the order
C. Oracle requires unique keys
D. It reduces error messages

<details><summary>Answer</summary><b>B</b> — A lost response leaves the outcome ambiguous: the server did the work but the client cannot tell, so retrying duplicates the order. ~110 duplicates/year at $1,200 each = ~$132K/year, removed by one PK insert.</details>

---

**5.** How is the idempotency key claimed?

A. `SELECT` then `INSERT`
B. `INSERT` first — the primary key violation is the lock
C. An application-level mutex
D. A named lock

<details><summary>Answer</summary><b>B</b> — Claiming before any side effect means two concurrent deliveries cannot both proceed.</details>

---

**6:** Same external ID, different payload hash. What should happen?

A. Update the existing record
B. Process again and overwrite
C. Flag for review; do not silently update a transmitted object
D. Ignore the new payload

<details><summary>Answer</summary><b>C</b> — Silently updating after downstream transmission creates an inconsistency that is very hard to trace.</details>

---

**7.** Which errors should NOT be retried?

A. Timeouts and 503
B. Validation failures and 401s — the data is wrong or the credential is bad
C. ORA- errors
D. Connection resets

<details><summary>Answer</summary><b>B</b> — Retrying a validation error sends the same wrong data five times. Retrying a 401 burns attempts on a credential that will not fix itself.</details>

---

**8.** Why is unbounded retry harmful?

A. It uses memory
B. It is a denial-of-service pattern against your own dependency — ~3,600
   requests/hour per stuck message, and the DLQ is never created
C. Oracle limits it
D. It is slow

<details><summary>Answer</summary><b>B</b> — Bounded backoff drops it to ~120/hour, then to 6 total attempts.</details>

---

**9.** What makes a DLQ useful rather than a graveyard?

A. Row count
B. Full payload retained, error class stored, and a working replay procedure
C. Automatic deletion
D. Email alerts

<details><summary>Answer</summary><b>B</b> — Without the payload, replay requires reconstructing a message from a possibly purged audit trail.</details>

---

**10:** Error rate is 0% and 4 of 400 opportunities produced no order. What is wrong?

A. Nothing — 0% error rate is correct
B. Messages are being dropped silently; only volume agreement catches this
C. The report is wrong
D. The DLQ is empty

<details><summary>Answer</summary><b>B</b> — No error is recorded anywhere. Comparing source volume against target volume is the only check that detects it.</details>

---

## Scoring
- **9–10**: Ready to design production integrations.
- **7–8**: Solid; revisit idempotency and error classification.
- **5–6**: Re-read THEORY on decoupling and the DLQ.
- **<5**: Work through EXERCISES 3, 4, and 8 again.