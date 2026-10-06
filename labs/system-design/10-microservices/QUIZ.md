# Microservices - Quiz

15 questions. Answer before checking the key.

---

## Section A: Foundations (Q1-5)

**Q1.** What problem do microservices genuinely solve, and what do they make worse?

**Q2.** What is a distributed monolith, and name three symptoms.

**Q3.** Two services read the same table. Why is this a boundary failure, not a convenience?

**Q4.** Your team has 5 engineers and one service. Should you decompose? Defend either answer.

**Q5.** What metric most reliably tells you your microservices decomposition succeeded?

---

## Section B: Communication (Q6-9)

**Q6.** When should a call be synchronous rather than asynchronous? Give the decision rule.

**Q7.** A 4-service synchronous chain, each 99.9% available. What is the chain's availability?

**Q8.** Why should cross-service data be copied rather than shared? What do you give up?

**Q9.** A service reads another service's table directly. Name two concrete production failures this causes.

---

## Section C: Failure Isolation (Q10-12)

**Q10.** What are the four isolation tools for a remote call, and what does each protect?

**Q11.** Why is a circuit breaker with only an error-ratio threshold insufficient to protect capacity?

**Q12.** What happens to capacity if a downstream timeout exceeds the caller's remaining budget?

---

## Section D: Transactions and Migration (Q13-15)

**Q13.** Why must every saga step be idempotent, and what breaks if it isn't?

**Q14.** Your payment service dedups on a per-request UUID. What is wrong, and why do tests pass?

**Q15.** In a Strangler Fig migration, why is the verification step the one that matters most?

---

## Answer Key

**A1.** **Genuinely solved:** independent deployment (teams ship without a
coordinated release), independent scaling (a hot service scales alone), fault
isolation, and limited technology autonomy. **Made worse:** code complexity,
testing (more integration, more flakiness), debugging (you need tracing),
transactions (you need sagas), and operations (more deployables, more failure
modes). The trade is runtime complexity for change-time autonomy.

**A2.** An architecture with microservices' costs and a monolith's coupling.
Symptoms: (1) a single change requires several services to deploy together;
(2) one team's outage cascades across services; (3) cross-service joins are
normal; (4) people assume cross-service transactions work as they did in the
monolith; (5) shared infrastructure is required for ordinary changes.

**A3.** Because sharing a database makes the split irreversible in neither
direction. Both services can break each other with a schema change, neither can
deploy without checking the other, and the "boundary" exists only in a diagram.
The rule is a service owns its data exclusively; cross-service data is
**replicated** (via events or a projection), accepting staleness.

**A4.** (Defensible either way, if argued.) **No:** one team does not have
change conflicts, so the primary benefit (change-time autonomy) does not exist,
while every cost still does. One deployable also means transactions, joins, and
transactions-in-context stay simple. **Yes:** if the codebase is large, the
domain has genuinely distinct bounded contexts, or the team is being asked to
scale beyond one deployable's limits — and then decompose into a **modular
monolith** first, which captures most of the benefit at a fraction of the cost.

**A5.** **Change coupling**: how many services a typical change requires to
deploy together. If it is more than 2-3, the decomposition is not delivering
independence. Supporting metrics: deployment frequency per team and change
failure rate — frequency alone is easy to improve while failure rate worsens.

**B6.** **Use sync when you need the answer to decide the next step** ("is this
item in stock?", "is this password correct?" — without an answer there is no
meaning). **Use async when the caller does not need the answer** (send an email,
update a search index, notify analytics). The real cost of sync is *temporal
coupling*: both services must be up at the same moment, and availability
multiplies along the chain.

**B7.** `0.999^4 = 0.996` = **99.6%**, not 99.9%. Availability is multiplied,
never added, and it erodes fast. This is why chains are capped at 2-3 hops and
why any dependency that can be made optional should be — an optional
dependency at 99% costs the platform nothing, whereas a required one at 99%
costs 1%.

**B8.** Sharing means every service's schema change is everyone's breaking
change, so no service can deploy independently — the boundary is fictional.
Copying gives up **freshness**: the copy is eventually consistent and needs a
stated staleness bound and an update mechanism. In exchange you get independent
deployment and, crucially, **availability isolation** — the copy survives the
source service being down.

**B9.** (1) **Schema coupling**: `order-service` changes `users` and breaks
`user-service` in production, despite neither team communicating. (2) **Query
plan and index ownership**: `user-service` cannot safely add an index for its own
query without contending with `order-service`'s access pattern, so performance
problems become unresolvable conflicts. (3) **Independent scaling is gone** —
one query on the shared table couples the load of both services, so one
service's traffic spike now affects the other's capacity. (4) Neither service can
run or be tested without the other's database.

**B10.** **Timeouts** — bound how long a call may occupy a resource.
**Circuit breakers** — stop calling a failing dependency so it can recover and
so you stop amplifying the failure. **Bulkheads** — isolate resource pools per
dependency so one slow service cannot starve the others. **Graceful
degradation** — return partial or cached results so the request succeeds with
less data. Add deadline propagation (stop work nobody is waiting for) and load
shedding (reject fast rather than queue).

**B11.** Because breakers react to **errors**, and capacity is consumed by
**waiting**. A dependency that is slow but not failing produces no errors, so
the breaker stays CLOSED while requests queue and hold connections until the
caller exhausts. Breakers protect the dependency from your load; **concurrency
limits** protect your capacity. You need both, and often a minimum-request
threshold as well so a low-traffic window cannot open a breaker on noise.

**B12.** **Wasted work, then a spiral.** The downstream service keeps working
after the caller has given up, so capacity is consumed producing nothing. Under
load, wasted work becomes queueing, queueing causes more timeouts, more timeouts
mean more wasted work — the positive feedback loop is why an unbounded chain
collapses rather than merely degrading. Propagating an absolute deadline
inherited and decremented per hop is the fix; a propagated *duration* restarts
at each hop and never terminates.

**B13.** Because delivery is at-least-once, so every saga step **will** be
retried at some point — after a network blip, a timeout, a consumer rebalance, or
a redeploy. A non-idempotent step (charge a card, add stock) applies twice on
retry, producing duplicate charges or oversold inventory. Therefore every step
needs an idempotency key derived from **stable business identity** (not a
per-attempt UUID), and every compensation must be idempotent too, since a
retried refund must not refund twice.

**B14.** The key is regenerated on every attempt, so the dedup store sees a new
key each time and **never deduplicates** — the unique constraint never fires and
retries execute the operation again. It passes tests because **tests do not
retry**: a single send gets a single unique key and the dedup path is never
exercised, so the code looks correct while being useless in production. Fix:
derive the key from stable business identity (`merchant : order : operation`) so
all attempts of the same logical operation collide, then add a test that
actually retries.

**B15.** Because every earlier phase is reversible only if you know the new
service is producing correct data. Without continuous verification you are
switching traffic on the basis of hope, and because the failure modes here are
*silent* — a missing backfilled row, a subtly different rounding rule, a filter
that quietly drops rows — they surface as customer reports rather than errors.
Verification turns a silent data discrepancy into an alert that fires while the
diff is still diagnosable, and it is the step teams skip when a migration is
late, which is exactly when it is most needed.