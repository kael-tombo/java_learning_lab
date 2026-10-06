# Microservices - Exercises

Twelve exercises ordered by difficulty. Solutions follow.

---

## Exercise 1: Availability Compounding (Easy)

Three services, each 99.9% available, in a serial chain. What is the chain's availability? Three of the three?

<details>
<summary>Solution</summary>

`0.999^3 = 0.997` = **99.7%**, not 99.9%.

Three: `0.999^3 * 0.999^3 = 0.994` = **99.4%**.

Every additional *required* synchronous dependency multiplies availability down.
This is why chain depth is capped at 2-3 and why optional dependencies are
reclassified as optional wherever product will tolerate degradation.
</details>

---

## Exercise 2: Tail Latency (Easy)

A chain of 5 services, each with p50 = 60 ms and p99 = 100 ms. Estimate the chain's p50 and p99.

<details>
<summary>Solution</summary>

p50: roughly `5 * 60 = 300 ms`.

p99: **not** `5 * 100 = 500 ms`. `P(all five under 100 ms) = 0.99^5 = 0.951`, so
the chain's p95 is already a single service's p99. The chain's p99 corresponds to
the ~99.9th percentile of one service's distribution — realistically
**700-1,200 ms**, i.e. 2-3x worse than the naive sum.

This is why you budget explicitly and shed load, rather than assuming a chain's
latency is additive.
</details>

---

## Exercise 3: Bulkhead Sizing (Medium)

Checkout calls payment at 100 rps; payment's p50 is 120 ms. There are 8 services
on the critical path. Size the payment bulkhead and explain what happens without it.

<details>
<summary>Solution</summary>

Little's Law: `concurrency = 100 * 0.12 = 12`. Use **12-24** (safety factor 1-2x),
because a pool sized exactly at p50 will queue on every p95 request.

Without bulkheads: payment's 12 threads block, and since all services share one
100-thread pool, **all** checkout traffic dies because of a 10%-of-traffic
dependency. With bulkheads, 12 permits are affected, 88 keep serving, and the
failure is bounded and visible as a payment-specific metric.
</details>

---

## Exercise 4: Distributed Monolith Detection (Medium)

Your "microservices" are: `user-service`, `order-service`, `payment-service`.
`user-service` and `order-service` both read the `users` table directly, and a
typical "place order" change touches all three. Diagnose.

<details>
<summary>Solution</summary>

**Distributed monolith.** Two independent signals:

1. **Shared data.** Reading the same tables makes every schema change a
   coordinated release. The boundary exists only in a diagram.
2. **Coupled change.** If a typical change spans 3+ services, you have not
   achieved independent deployability — the main benefit.

Fix: replicate the needed user data into `order-service` via an event-driven
projection (accepting staleness), so neither service reads the other's tables.
Then re-measure change coupling.
</details>

---

## Exercise 5: Timeout Coordination (Medium)

Client timeout 1,000 ms. Five services. Database query p99 is 600 ms. Where do
timeouts go?

<details>
<summary>Solution</summary>

Budget from the inside out, reserving response-shaping time:

```
client                 1,000 ms
  - all services' own cost
  - final shaping reserve            50 ms
  -> 950 ms available for the chain

gateway self budget      30 ms  -> passes 920
checkout self budget     60 ms  -> passes 860
order self budget        60 ms  -> passes 800
inventory self budget    40 ms  -> passes 760
payment self budget      60 ms  -> passes 700
  -> database timeout should be ~600 ms, inside 700
```

Key errors: a single global default timeout (either useless or harmful), and
any downstream timeout that **exceeds** the caller's remaining budget — which
wastes capacity on work nobody is waiting for.
</details>

---

## Exercise 6: Circuit Breaker Minimum Requests (Hard)

Dependency `payments` fails 60% of requests with a 2 s timeout. Breaker:
50% threshold, 20-request minimum, 30 s open. Traffic to payments: 1 rps.

Does the breaker open? Should it?

<details>
<summary>Solution</summary>

**No.** At 1 rps with a 20-request minimum, the window takes 20 s of *volume* to
fill. If the window is time-based at 20 s, only ~20 requests arrive — right at
the threshold. But the real point: a *count-based* window at 1 rps accumulates
over minutes, so the failure ratio is eventually computed on stale data.

The deeper issue: the breaker will not open, so requests keep queueing and
holding resources for a dependency that is 60% broken. **Breakers protect
correctness of dependency state; concurrency limits protect your capacity.**
Here you need a concurrency limit sized for payment, so 60% failure cannot
consume the whole pool.

Also: a dependency failing with *timeouts* rather than errors is a case where
errors-based breaking may not trigger promptly — count timeouts as failures.
</details>

---

## Exercise 7: Saga Compensatability (Medium)

Checkout saga: reserve inventory → charge card → create shipping label → send
confirmation email. Which steps are compensatable? What happens if label creation
succeeds and email fails?

<details>
<summary>Solution</summary>

| Step | Compensatable? | Compensation |
|------|---------------|-------------|
| Reserve inventory | yes (compensatable) | release reservation |
| Charge card | yes (**repeatable**) | refund — repeatable N times |
| Create label | awkward | void the label (may incur a fee) |
| Send email | **no** | nothing — send a correction |

If the label succeeds and email fails: there is **no valid compensation** for the
email. The design must therefore place an **approval gate** before any
irreversible step, or convert email into a delayed/outbox action whose failure is
detectable and retryable rather than "already sent, cannot undo".

The deeper lesson: classify every step's compensatability when designing the saga.
If any step is irreversible, the saga needs a human-in-the-loop fallback.
</details>

---

## Exercise 8: Idempotency Key Derivation (Hard)

Your payment service dedups on a `requestId` the client generates **per HTTP
request**. A client times out and retries. What happens? Why does this pass all
your tests?

<details>
<summary>Solution</summary>

The retry has a **different** `requestId`, so the dedup store sees a brand-new
request and executes again → **duplicate charge**. The `ON CONFLICT` / unique
constraint never fires because the key is new every time.

It passes tests because **tests do not retry**. A test that sends the request
once gets a unique key, and the dedup path is never exercised.

Fix: derive the key from stable business identity —
`merchant_id : checkout_order_id : operation` — so every retry of the same
logical operation produces the same key. Then a test *with* retries passes.
</details>

---

## Exercise 9: Data Ownership Test (Medium)

Two services both need `customer_email`. Service A reads it from its own database
(the customer is its aggregate). Service B needs it for a shipping label. Options?

<details>
<summary>Solution</summary>

Options and their costs:

1. **B reads A's database** — breaks data ownership. A's schema change breaks B;
   neither can deploy independently. Not acceptable.
2. **B calls A synchronously** — adds a required dependency: `A_b = A_b * A_a`,
   a new failure mode, and a latency hop on the shipping path.
3. **B stores its own copy, updated by event** — correct. Customer email is
   eventually consistent in B (acceptable: it is a label, and a day-old email
   address rarely blocks a shipment). B is insulated from A's availability and
   schema.
4. **B fetches once and stores** — also fine, but do it at order time, not at
   label time.

The general rule: cross-service data is **copied**, never shared, and the
staleness bound is written down.
</details>

---

## Exercise 10: Retry Amplification (Hard)

Client retries 3x, checkout retries 2x, order retries 3x. A `POST /orders`
request times out. How many requests reach the database? What's the fix?

<details>
<summary>Solution</summary>

`3 * 2 * 3 = 18x`. One user-visible request can become 18 database operations.

Fixes:

1. Retry at **exactly one layer** — normally the client.
2. Retry **only idempotent** requests or those carrying an idempotency key.
3. Cap retries at 2-3 with **full jitter**, and enforce a **retry budget**
   (retries ≤ 10% of total requests). A retry budget is the control that stops a
   cascading failure from becoming a retry storm.
4. Never retry on a timeout for a non-idempotent request — the operation may have
   succeeded.
</details>

---

## Exercise 11: Migration Sequencing (Hard)

The monolith has tables: `users`, `products`, `orders`, `order_items`, `audit_log`.
You are extracting an `order` service. Order the steps and justify.

<details>
<summary>Solution</summary>

Order by **data dependency**, not by business importance:

1. **`order_items`** first — child of `orders`, no independent consumers, and it
   is pure insert-only data. Lowest risk.
2. **`orders`** second, with dual write: the monolith writes both, then a
   continuous verification job diffs old vs new.
3. **`audit_log`** — write path unknown (triggers? ETL? app code?). **Identify
   the writer first** or you will silently lose rows. This is the step most
   migrations skip.
4. Switch reads, then shrink the monolith.
5. `products` and `users` last — they are read by many capabilities, so they
   need a projection/event model rather than a copy.

Rule: reverse this order (split tables before splitting services) and the
migration becomes painful, because other capabilities still read the monolith's
copies of data that now has two writers.
</details>

---

## Exercise 12: Design Review (Hard)

A team proposes 30 services, one per database table. Give the review.

<details>
<summary>Solution</summary>

**Reject.** Table-per-service inverts the correct direction.

1. **Boundaries come from business capability, not tables.** "order" owns orders
   *and* order_items *and* the order state machine — splitting them means a
   single business change spans two services, and the state machine is split
   across a network.
2. **Every service adds a network call to a previously atomic operation.**
   Placing an order goes from one transaction to a saga.
3. **30 services is 30 deployables.** Coordination cost grows faster than
   independence, and shared infrastructure (CI, secrets, observability, on-call)
   dominates.
4. **Availability collapses.** A place-order chain of 5-6 required services at
   99.9% is 99.4%.
5. **Most tables change together.** Table-per-service means those changes become
   multi-service releases — the exact problem microservices were supposed to
   solve.

Correct decomposition: order, catalog, customer, fulfilment, payment — 5-8
services on business boundaries, each owning multiple tables.
</details>