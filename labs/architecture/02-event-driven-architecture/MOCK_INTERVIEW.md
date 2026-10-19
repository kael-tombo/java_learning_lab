# Mock Interview: The Outbox Decision

> Question-bank format: a grounded scenario, then the probe list a panellist would run.

---

## Scenario

A ticket-resale marketplace. When a buyer checks out, the order service must insert the order row, then tell billing to move money, notify the seller, and feed the fraud scorers. Today the team commits, then calls `publisher.publish(...)` outside that transaction. After every deploy restart, a handful of orders silently reach nobody — billing sees no instruction, and the buyer hears nothing.

---

## Question Bank

1. "How would you prove that publish-after-commit is really the bug?"
   The sequence is two independent actions: commit, then a network call. A crash in the gap loses the announcement while the money row persists. Tests rarely trip it — the window is milliseconds — but restarts and deploys stretch it to a minute or more. The observable is silence on the consumer sum metric with orders still increasing.

2. "Fix it."
   An `outbox` record is written inside the same commit as the order row; a relay polls pending rows, ships them to the broker, marks them sent. Writing state and announcing it become one atomic action, and delivery becomes at-least-once by construction.

3. "Consumers now see duplicates. Handle it."
   Each handler maintains a `consumed_events` table with a uniqueness constraint over the message id, committed together with its own state change. A redelivered message hits that constraint and is skipped. The dedupe lives where the state lives.

4. "Why not demand exactly-once from the broker?"
   A broker can only guarantee what one hop sees; this flow spans several systems, and consumer restarts reorder work regardless. Delivery labels are guidance — the real guarantee is built in the handler: state change and seen-marker recorded in one local commit.

5. "Under what conditions does the email run late?"
   When consumer throughput drops below producer rate, backlog accumulates. Keep in-flight work bounded — a prefetch cap, a bulkhead around the mail provider — and alert on lag minutes rather than queue depth, so somebody pages before a shopper waits an hour.

6. "Should events carry the buyer's address or just identifiers?"
   Minimal notice: order id and buyer id. Consumers fetch detail on demand. Full state transfer weds every consumer to every upstream schema change; small payloads keep the contract narrow and the blast radius small.

7. "Who owns the relay, and what does its failure look like?"
   The order service does. Its failure mode is age: pending rows sit unsent. The alarm watches the oldest unsent row, not CPU — a stopped relay is otherwise invisible, since checkout itself still completes without a whisper.

---

## Panel Follow-Ups

- "The broker is dark for an hour — what does the outbox feel like?" — the relay stalls, the table grows on disk, and an alarm watches outbox age; producers never stop, because the order path must not stall behind a dependency that isn't the order path.
- "When do schemas roll forward safely?" — consumers accept old and new field sets for a release cycle; producers never drop a required field in the same window where consumers still expect it.
- "Poison messages?" — bounded retries, then a parking-lot topic carrying the payload plus failure context, so the consuming team triages with everything needed on the row.
- "Relay throughput when the broker comes back?" — it drains oldest-first at whatever rate the broker tolerates; recovery is deliberately unheroic, since purchases never paused to wait for it.

---

## Red Flag

Treating "at least once" as a knob on the broker while locating dedupe "somewhere downstream". If a candidate cannot point to the row and index that make replay harmless, the guarantee does not exist.
