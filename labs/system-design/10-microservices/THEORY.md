# Microservices - Theory

## 1. What Microservices Actually Solve

Microservices are a **organisational** architecture adopted for a technical
reason. The problems they genuinely address:

- **Independent deployment** — teams ship without coordinating a release train.
- **Independent scaling** — one hot service scales without the other 200.
- **Fault isolation** — a memory leak in recommendations does not take down
  checkout.
- **Technology autonomy** — practical only at the edges.

The problems they do **not** solve, and make worse:

- Code complexity (now distributed, with network failure modes)
- Testing (more integration, more environments, more flakiness)
- Debugging (you now need distributed tracing to answer simple questions)
- Transactions (you now need sagas)
- Operations (more deployables, more failure modes)

So the honest framing: microservices trade **runtime complexity** for
**change-time autonomy**. That trade is worth it when you have many teams
changing the same code concurrently. With 5 engineers and 1 service, it is
almost never worth it.

## 2. Finding Boundaries

Boundaries come from **business capability**, not from technical layering or
table count.

```
  BAD (technical split):   user-service, order-service, utility-service
                           -> nothing owns a business capability

  BAD (table split):       users-db-service, orders-db-service
                           -> a change to "place order" now spans both

  GOOD (capability split): product-catalog, cart, order, payment, fulfilment
                           -> one team owns "order" end to end
```

Method: look at where the business changes. The place that changes most often,
for the most reasons, is a candidate boundary. Then check whether the data
needed for that capability can live behind it.

### Bounded Contexts and Shared Data

Two services sharing a database is the **most common microservices failure**,
because it makes the split reversible in neither direction:

- Both services can now break each other with a schema change.
- Neither can be deployed without checking the other.
- The boundary exists only in a diagram.

The rule: **a service owns its data exclusively**. If two services read the
same tables, they are one service with extra network latency. If you need
cross-service data, replicate it via events or build a read-only projection —
and accept the staleness.

### Distributed Monolith (the warning sign)

A "microservices" architecture where services are tightly coupled by
synchronous call chains and share a database is a **distributed monolith**: all
the costs of distribution, none of the benefits of autonomy. Symptoms:

- One service change requires three others to deploy.
- A single team's outage cascades to five services.
- Cross-service joins are normal.
- Transactional consistency is assumed across services.

If you have these, you have made things worse. The fix is to reduce the number
of services, or genuinely decouple them with events.

## 3. Communication: Sync vs Async

| Dimension | Synchronous | Asynchronous |
|-----------|-------------|--------------|
| Caller learns result | yes | no |
| Failure mode | cascading, immediate | delayed, partial |
| Consistency | read-your-writes possible | eventual |
| Coupling | temporal (both up) | looser |
| Best for | queries, commands needing a verdict | fan-out, notifications, integration |

The decision rule:

```
  Use SYNC when you need an answer to decide what to do next
    - "is this item in stock?" -> the answer determines the next step
    - "is this password correct?" -> no answer, no meaning

  Use ASYNC when the caller does not need the answer
    - "send an email" -> the user does not need to know if it succeeded now
    - "update the search index" -> nobody waits
    - "notify the analytics pipeline" -> by construction not a request path
```

The **temporal coupling** is the real cost of sync: both services must be up at
the same moment. That is why every sync chain multiplies availability:

```
  3 services in a chain, each 99.9%:
  A_chain = 0.999^3 = 0.997  -> 99.7%, not 99.9%
```
Async does not fix availability — it moves failure to *eventually* and makes it
harder to observe. It buys decoupling and load smoothing, not reliability.

### Choosing the Protocol
- **REST/gRPC** for request-response. gRPC for internal, high-volume, typed
  contracts; REST for external and debuggability.
- **Events** for fan-out and integration.
- Never build a synchronous chain more than 2-3 deep. Beyond that you have
  built a monolith with network latency.

## 4. Distributed Transactions: Sagas

A transaction cannot span services. Instead, break it into local transactions
with compensations:

```
  Saga: place order
    1. reserve inventory      -> compensate: release
    2. charge payment         -> compensate: refund
    3. create shipment        -> compensate: void label
    4. send confirmation      -> NOT COMPENSATABLE
```

Key points:
- **Every step must be idempotent.** Retries are guaranteed, so a
  non-idempotent step will double-apply.
- **Compensation is not rollback.** Refunding is not un-charging; the money
  moved. Say "refund" in your code, not "undo".
- **Some steps are not compensatable.** Anything irreversible (an email, a
  shipped parcel) needs an approval gate before it executes.
- **Choreography** (event-driven, no coordinator) is simple and hard to
  reason about past ~5 steps. **Orchestration** (central coordinator) is
  explicit and gives you one place to see in-flight state. Prefer orchestration
  beyond a handful of steps.

### The Transactional Outbox

The dual-write problem: writing to your database and publishing to a broker is
two writes with a failure window. The outbox makes them one transaction, then
publishes asynchronously, accepting duplicates and requiring idempotent
consumers. See lab `07-transactions`.

## 5. Failure Isolation

Distributed systems fail partially. Every design must answer: when service A
calls B and B is slow or down, what happens?

The four tools:

1. **Timeouts** — mandatory everywhere, always shorter than the caller's
   deadline. No default: make it explicit.
2. **Circuit breakers** — stop calling a failing dependency. Prevents
   resource exhaustion and lets the dependency recover.
3. **Bulkheads** — separate resource pools per dependency, so one slow service
   cannot starve the others. A thread pool per call site, a connection pool per
   dependency.
4. **Graceful degradation** — return partial or cached results instead of
   failing. The best isolation: the request succeeds with less data.

Plus:
5. **Deadline propagation** — stop downstream work nobody is waiting for.
6. **Load shedding** — reject fast with a clear signal instead of queueing.
   Queues convert a dependency problem into a memory problem.

The failure mode without these: A calls B, B hangs, A's threads block, A's pool
exhausts, A's inbound requests queue, A's memory grows, A dies. B recovers and
receives thousands of doomed requests. Both are down for a reason that has
nothing to do with the original fault.

## 6. Migration: Strangler Fig

Never rewrite. Incrementally replace, keeping the monolith running.

```
  1. FACADE      route all traffic through a gateway in front of the monolith
  2. EXTRACT     move ONE capability to a new service
  3. DUAL WRITE  monolith writes both, or replicates data to the new service
  4. VERIFY      compare old vs new continuously (shadow traffic)
  5. SWITCH      route reads to the new service
  6. SHRINK      remove the capability from the monolith
  7. REPEAT
```

Each step is independently reversible. The verification window in step 4 is
where the discipline lives: you do not switch until the diff is empty, and
"empty" is measured, not assumed.

Data extraction, in order of increasing difficulty:
- **Read-only tables** → easiest, export to the new service, verify, switch.
- **Tables also written by the monolith** → dual write, then backfill.
- **Tables written by triggers or ETL** → identify the writer first or you
  will silently lose data.
- **Shared tables used by other capabilities** → split the schema, then split
  the service. Reverse order causes pain.

## 7. Observability

With microservices, a request crosses 5+ services. Without tracing you cannot
answer "why is checkout slow" at all.

- **Trace context propagated on every call**, from the edge. W3C trace context
  is the standard; use it rather than a custom header.
- **Spans per call**, with the deadline and the actual duration. Compare them:
  a service reporting 10 ms while the span shows 400 ms means queueing.
- **Per-service SLOs and error budgets.** A platform SLO with no per-service
  budget has no owner when it burns.
- **Cardinality discipline**: service + operation + status is bounded. Request
  id as a metric label is not.

## 8. Testing a Distributed System

| Test type | What it catches | Cost |
|-----------|----------------|------|
| Unit | logic | cheap |
| Contract (consumer-driven) | incompatible interface changes | cheap, high value |
| Integration | wiring, serialisation | medium |
| Component (in-memory, real deps) | interaction bugs | medium |
| End-to-end | the whole path | expensive, flaky |

The most valuable addition to a monolith's test suite is **consumer-driven
contract tests**, because they catch the specific failure microservices
introduce: one team changes an interface and breaks a team that has not
deployed. In a monolith the compiler catches this. Across a network, nothing
does — unless you add Pact-style contract tests.

## 9. Deployment and Operational Reality

- **Independent deployment** is the point; independent *operability* is the cost.
- Every service needs: health checks (liveness shallow, readiness deep),
  graceful shutdown that stops accepting and drains, resource limits, and
  autoscaling on a metric that means something.
- **Schema changes are a service-to-service interaction.** A migration must be
  backward compatible with every other service's currently deployed version.
- **Environments**: you cannot have 200 services and 20 integration environment
  combinations. Prefer contract tests plus production-like canaries.

## Summary

Microservices are worth it when organisational coupling dominates technical
coupling. They are a way to let teams move independently, paid for with
runtime complexity. The three things that determine whether you got it right:
**does each service own its data**, **does every remote call have a timeout and
a breaker**, and **can you trace one request across the whole path**.