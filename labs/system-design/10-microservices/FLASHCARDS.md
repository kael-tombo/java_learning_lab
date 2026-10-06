# Microservices - Flashcards

60 review cards.

## Front: What problem do microservices genuinely solve?
**Back:** Independent deployment, independent scaling, fault isolation, limited technology autonomy — all organisational benefits.

## Front: What do microservices make worse?
**Back:** Code complexity, testing, debugging, transactions, operations. Runtime complexity is traded for change-time autonomy.

## Front: When are microservices not worth it?
**Back:** Few teams, little change concurrency, small codebase. One deployable has all the benefits and none of the distributed-systems costs.

## Front: What is a distributed monolith?
**Back:** Microservices' costs with a monolith's coupling: multi-service changes, cascading outages, shared data, assumed cross-service transactions.

## Front: Name three distributed-monolith symptoms.
**Back:** A change needs several services deployed; one outage cascades; cross-service joins are normal.

## Front: Where should service boundaries come from?
**Back:** Business capability and bounded context — where the business changes. Not from technical layering or table counts.

## Front: What is the data ownership rule?
**Back:** A service owns its data exclusively. If two services read the same tables, they are one service with network latency.

## Front: Why is a shared database the worst microservices mistake?
**Back:** Every schema change becomes a coordinated release, so neither service can deploy independently and the boundary is fictional.

## Front: How do you get cross-service data without sharing a database?
**Back:** Replicate it — event-driven projection, or a read-only copy owned by the consumer. Accept eventual consistency and state the staleness bound.

## Front: When should a call be synchronous?
**Back:** When you need the answer to decide the next step. A timeout otherwise has no meaning.

## Front: When should a call be asynchronous?
**Back:** When the caller does not need the result: notifications, index updates, analytics fan-out.

## Front: What is temporal coupling?
**Back:** Both services must be up at the same moment for a sync call. It is the real cost of synchronous communication.

## Front: A 4-service sync chain at 99.9% each. What is the chain availability?
**Back:** 0.999^4 = 99.6%. Availability multiplies and erodes fast — cap chains at 2-3 hops.

## Front: What is the p99 of a 5-service sync chain?
**Back:** Far worse than 5x a single p99. P(all under p99) = 0.99^5 = 0.951, so the chain p95 is one service's p99.

## Front: Why parallel fan-out helps and what it costs.
**Back:** Reduces latency from sum to max, but multiplies concurrent connections by the fan-out factor.

## Front: What is a saga?
**Back:** A distributed transaction with no rollback, only compensating actions. Each step is a local transaction plus a compensation.

## Front: Why must every saga step be idempotent?
**Back:** Delivery is at-least-once, so every step will eventually be retried. A non-idempotent step double-applies.

## Front: Why is compensation not rollback?
**Back:** Refunding is a NEW business action. The money moved and the customer sees both transactions. Never name it "undo".

## Front: What must you do if a saga step is not compensatable?
**Back:** Add an approval gate before it, or a human-in-the-loop fallback. Email sent cannot be unsent.

## Front: Choreography vs orchestration in sagas.
**Back:** Choreography = event-driven, no coordinator, hard to reason past ~5 steps. Orchestration = central coordinator, explicit, one place to see in-flight state.

## Front: What is the transactional outbox for?
**Back:** The dual-write problem. Business write + publish is two writes with a loss window. The outbox makes them one transaction, then publishes async.

## Front: Does the outbox give exactly-once?
**Back:** No. It guarantees at-least-once delivery. Combined with an idempotent consumer, the effect is effectively-once.

## Front: What is the biggest outbox mistake?
**Back:** An unbounded table with a DELETE cleanup job. Partition by time and drop partitions, or the cleanup itself becomes an outage.

## Front: Name the four failure-isolation tools.
**Back:** Timeouts, circuit breakers, bulkheads, graceful degradation. Plus deadline propagation and load shedding.

## Front: What does a circuit breaker protect?
**Back:** The failing dependency, from your load. It does NOT protect your own capacity.

## Front: What protects your own capacity?
**Back:** Concurrency limits and bulkheads. Breakers react to errors; capacity is consumed by waiting.

## Front: Why does a breaker need a minimum-request threshold?
**Back:** So low traffic or a partial window cannot open it on a single failure. Without it, a 1 rps service never trips.

## Front: Why must downstream timeouts be shorter than the caller's?
**Back:** Otherwise you consume capacity doing work nobody is waiting for, and under load that becomes queueing, which becomes more timeout. A spiral.

## Front: Why propagate an absolute deadline instead of a duration?
**Back:** A duration restarts at each hop and never terminates. An absolute timestamp is inherited and decremented, bounding the total.

## Front: What is a bulkhead?
**Back:** A dedicated resource pool per dependency, so one slow service cannot starve the others. Sized by Little's Law, not guessed.

## Front: Size a bulkhead for 100 rps with 120 ms p50.
**Back:** 100 * 0.12 = 12 permits; use 12-24 with a safety factor. Exactly p50-sized pools queue on every p95 request.

## Front: What is graceful degradation?
**Back:** Returning partial or cached results instead of failing. It is the strongest isolation: the request succeeds with less data.

## Front: What is load shedding?
**Back:** Rejecting fast with a clear signal instead of queueing. Queues convert a dependency problem into a memory problem.

## Front: Why must you monitor request queue wait separately from service time?
**Back:** Because queue wait is the term that grows without bound under load, and it is invisible in service-time metrics.

## Front: What is the Strangler Fig pattern?
**Back:** Incrementally replacing a system by routing traffic through a facade and peeling capabilities off, keeping the monolith running throughout.

## Front: Why never rewrite from scratch?
**Back:** Rewrites fail because the old system keeps changing while you rewrite. Strangler Fig is reversible at every step; a rewrite is not.

## Front: Name the Strangler Fig phases.
**Back:** Facade, extract, dual write, verify, switch, shrink, repeat. Each step independently reversible.

## Front: Which phase of Strangler Fig matters most, and why?
**Back:** Verification. Without continuous comparison of old vs new, you switch on hope, and the failure modes are silent.

## Front: Order table-extraction difficulty.
**Back:** Read-only (1x), single-writer (3x), dual-write plus backfill plus verify (6x), shared-table split (10x+).

## Front: What must you identify before extracting a table?
**Back:** Its writer. Triggers and ETL are easy to miss, and missing one silently loses data during the migration.

## Front: What is the distributed monolith cost?
**Back:** N services in a critical chain multiply deploy coupling. If a typical change touches 3+ services, independence is not achieved.

## Front: What is consumer-driven contract testing for?
**Back:** Catching the failure microservices introduce: one team changing an interface and breaking a team that has not deployed. In a monolith the compiler catches this.

## Front: What is the shared-table-pair test?
**Back:** Count shared tables per service pair. Target zero. Anything above zero means a distributed monolith.

## Front: Why do independent scaling savings often not materialise?
**Back:** If service traffic shares are proportional, splitting costs the same total capacity. Savings come from different scaling curves, not from splitting.

## Front: What is the most important observability requirement?
**Back:** Trace context propagated on every call, so one request can be followed across all services. Without it you cannot answer "why is checkout slow".

## Front: Which trace context standard should you use?
**Back:** W3C trace context. Not a custom header, which some proxy will drop and which you will have to debug forever.

## Front: Why is a span duration different from a reported service duration useful?
**Back:** A gap means queueing. The span shows real elapsed time; the service reports only its own work.

## Front: What is the metric cardinality rule for services?
**Back:** service + operation + status is bounded. Request id or user id as a label is not — it can kill the metrics backend for every service.

## Front: What must every service have for operations?
**Back:** Liveness (shallow) and readiness (deep, dependency-aware) probes, graceful shutdown with draining, resource limits, autoscaling.

## Front: Why does a schema change become a service-to-service interaction?
**Back:** Every other service's deployed version reads that schema. The migration must be backward compatible with all of them.

## Front: Why can you not have N services and many environments?
**Back:** The combinations explode. Prefer contract tests plus production-like canaries over N-way integration environments.

## Front: What is the correct order for splitting a table and a service?
**Back:** Split the schema first, then the service. Reversed, other capabilities still write to the monolith's copy and you end up with two writers.

## Front: What must a service do on graceful shutdown?
**Back:** Fail readiness first (stop receiving new traffic), drain in-flight work, then exit. Skipping this causes 502s on every deploy.

## Front: What is a data ownership test result of zero good, and what is a bad value?
**Back:** Zero shared tables per pair is the goal. Any non-zero value means schema coupling and coordinated releases.

## Front: How do you verify independent deployability?
**Back:** Pick 20 recent changes and count how many services each needed. Over 2-3 per change means the decomposition is not delivering.

## Front: What does event-driven replication buy over a sync call for cross-service data?
**Back:** Availability isolation and independent deployment. It costs freshness, which must be bounded and stated.

## Front: When is a synchronous cross-service call acceptable?
**Back:** When the answer determines the next step, the chain is short, and the dependency is effectively required. Otherwise prefer a copy.

## Front: Why is an event a poor fit for a request that needs a verdict?
**Back:** The caller needs the answer to proceed. Async converts a deterministic answer into a poll, a webhook, or a timeout, all of which are worse.

## Front: What is the retry budget?
**Back:** Retries must stay at or below 10% of total requests. It is the control that stops a cascading failure from becoming a retry storm.

## Front: Why full jitter on retries?
**Back:** Synchronised retries produce a thundering herd. Randomised delay across the full backoff range smooths the retry rate.

## Front: What is the retry amplification formula?
**Back:** client_retries x gateway_retries x service_retries. 3x2x3 = 18x load reaching the database from one user request.

## Front: Why is a saga's compensation queue capacity worth projecting?
**Back:** Roughly 0.4% of sagas will need human intervention. At volume that is a real daily queue requiring a named owner.

## Front: What is the cheapest first step toward microservices for a monolith?
**Back:** A modular monolith: enforce module boundaries inside the codebase, each owning its tables. It captures most of the benefit at a fraction of the cost.

## Front: What is the single most important property of a service boundary?
**Back:** A single business change should require a change in exactly one service. If not, the boundary is in the wrong place.

## Front: What must every remote call have, without exception?
**Back:** An explicit timeout, shorter than the caller's remaining budget. No defaults — an explicit wrong timeout is fixable; an implicit infinite one is not.

## Front: What is the availability formula for a platform with optional dependencies?
**Back:** Required dependencies multiply. Making a dependency optional means it stops multiplying, which is often the largest available improvement.

## Front: What is the single best diagnostic for a cascading outage?
**Back:** Per-dependency latency and error rate, not the aggregate. The aggregate tells you something is wrong; the breakdown tells you where.