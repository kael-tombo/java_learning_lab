# INTERVIEW — 12 GCP-Java Q&A (answers hidden)

Twelve questions in interview order (warmup → deep). Click to reveal.
Each answer ends with the follow-up a strong interviewer asks next.

---

## 1. When do you pick GKE Autopilot, Standard, or Cloud Run for a Java service?

<details><summary>Answer</summary>
Autopilot: managed nodes, per-pod billing — default for steady services
where you don't want binpacking duty. Standard: you own node pools,
cheaper past ~60–70% sustained binpack, with Spot/ARM mixing — pick at
proven steady scale. Run: request-driven scale-to-zero with
concurrency tuning — pick for spiky slices (webhooks, sale bursts).
This lab runs both: Autopilot for the steady API, Run for the spiky
webhook (MINI_PROJECT).<br><em>Follow-up: show me the break-even math
from your last bill.</em>
</details>

## 2. Explain Workload Identity like I'm a security auditor. What's the classic mistake?

<details><summary>Answer</summary>
KSA→GSA federation: the GKE metadata server mints short-lived tokens
for the pod's Kubernetes identity — no exported JSON keys exist to
steal, rotate, or leak. The classic mistake is app code demanding a key
file (<code>GOOGLE_APPLICATION_CREDENTIALS</code>); when calls 403, the
IAM binding (<code>workloadIdentityUser</code> on exact
project-number/namespace/name) is broken, not the code. After any
project migration, re-verify both binding sides
(PRODUCTION_SCENARIOS.md §4).<br><em>Follow-up: your deploy suddenly
403s on Secret Manager — rollback or rebind?</em>
</details>

## 3. How do you tune Cloud Run concurrency for a virtual-thread Java service?

<details><summary>Answer</summary>
Instances ≈ RPS × latency / concurrency, so raising concurrency 10→80
cuts instances ~8× at fixed RPS. Virtual threads make high concurrency
safe headroom (blocking is cheap), but the sweep (EXERCISES.md §2) must
measure p99, instance count, cost, and the cold-start column at each
setting — the knee where p99 degrades is the production value, and the
cold column sets the warm floor (minScale) for events.<br><em>Follow-up:
minScale 0 vs 8 for a sale — price both sides.</em>
</details>

## 4. Design the Pub/Sub DLQ for checkout events. What attempts number, and why?

<details><summary>Answer</summary>
Dead-letter topic + <code>maxDeliveryAttempts: 5</code> as the default:
attempts 1–2 absorb transient blips, 3–5 confirm persistence, then
quarantine for autopsy instead of stalling the subscription forever
(the DLQ-less poison drill, EXERCISES.md §4). During throttling
incidents raise attempts temporarily so slow-but-healthy messages aren't
mis-quarantined; alert on DLQ arrival rate, and document the replay
procedure with ordering-key affinity.<br><em>Follow-up: poison message
vs hotspot — how do you tell from metrics?</em>
</details>

## 5. Burn-rate alerts vs threshold alerts — which pages you, and why?

<details><summary>Answer</summary>
Burn-rate pages me: it fires on SLO-budget consumption speed
(fast-burn 1h window → page, slow-burn 6h → ticket), catching user pain
early with context. Raw thresholds (<code>5xx &gt; N/min</code>) page on
harmless deploys and sleep through slow regressions. Every service ships
both burn windows from day one, proven by the synthetic-burn drill
(BIG_TECH_FEEDBACK.md §1).<br><em>Follow-up: design both windows for a
99.9% monthly SLO.</em>
</details>

## 6. One ordering key carries 60% of Pub/Sub volume and latency explodes. Diagnose and fix.

<details><summary>Answer</summary>
Diagnosis: per-key serialization ceiling — one hot key flows through a
single sequencer (~low-K msgs/s) regardless of subscriber parallelism;
ack expiries then redeliver and amplify. Check
<code>oldest_unacked_message_age by key</code>: one key old, rest fresh.
Fix: shard the key (<code>merchant#hash%16</code>), extend the ack
deadline to real handler time, drain and replay the DLQ with shard
affinity; long-term, order per-user/cart, never per-merchant-global
(EXERCISES.md §5).<br><em>Follow-up: when would you drop ordering
entirely?</em>
</details>

## 7. Cloud SQL fails over and your HikariCP fleet stays broken after the DB recovers. Why?

<details><summary>Answer</summary>
Pool stampede: pods × pool-size simultaneous reconnects overwhelm the
just-recovered writer, timeouts fire fleet-wide, readiness fails, and
restarts re-stampede. Virtual threads worsen queueing (unbounded cheap
queue instead of fast failure). Fix: smaller pools (pods × pool ≤ half
of <code>max_connections</code>), staggered restarts, bulkhead +
timeout + circuit breaker around DB calls so HTTP sheds load as 503
(PRODUCTION_SCENARIOS.md §3).<br><em>Follow-up: size the pool for 12
pods on a 100-connection writer.</em>
</details>

## 8. New Autopilot pods OOMKill during warmup while steady state fits fine. Root cause?

<details><summary>Answer</summary>
Requests sized from steady state, not the warmup peak (cache fill +
deferred first GC + off-heap). Standard's burstable limits forgave it;
Autopilot pins usage to request, so the peak dies with exit 137 and HPA
adds more dying pods. Fix: requests from measured warmup-peak +
<code>MaxRAMPercentage≈60</code> headroom, startup memory soak as merge
gate, working-set/request-ratio alert (PRODUCTION_SCENARIOS.md
§1).<br><em>Follow-up: CRaC snapshot vs bigger requests — decide with
numbers.</em>
</details>

## 9. AlloyDB or Spanner for a single-region catalog with read replicas?

<details><summary>Answer</summary>
AlloyDB (or Cloud SQL PG): Postgres-compatible, columnar acceleration,
HA + PITR, Flyway and JDBC unchanged — the lab default. Spanner only
when multi-region writes need external consistency, accepting
query-shape discipline and higher write cost. The choice comes from the
write topology (single-region RPS? cross-region requirement?), written
down before building (BIG_TECH_FEEDBACK.md §4).<br><em>Follow-up: what
breaks in your transactions if you migrate later?</em>
</details>

## 10. Walk me through a safe production deploy and rollback on GKE.

<details><summary>Answer</summary>
Cloud Deploy canary (e.g. 5% → 50% → stable) behind Gateway readiness
gates; Flyway as pre-deploy Job with backward-compatible
expand-then-contract migrations; burn-rate alerts as automatic
promotion/rollback signals; rollback = previous revision + reversibility
proof, rehearsed in the rollback drill (THEORY.md §4, MINI_PROJECT).
The Gateway split is what kept the OOMKill and cold-cascade incidents to
partial blast radius.<br><em>Follow-up: the migration isn't reversible —
what now?</em>
</details>

## 11. Your Cloud Trace bill tripled after enabling the Java OTel agent. What do you do?

<details><summary>Answer</summary>
Cut ingest, not visibility: head-based sampling 5–10% plus tail-based
capture of errors/slow traces, drop health-check spans at the
collector, keep Profiler always-on (cheap) for the hot-method view.
Budget observability at ~5–8% of compute; sampling policy lives in the
repo (COST_REALITY.md §3).<br><em>Follow-up: which spans must never be
sampled out?</em>
</details>

## 12. Sketch the monthly cost review you'd run for this platform.

<details><summary>Answer</summary>
Export the labeled bill; recompute Autopilot-vs-Standard from 30 days
of pod-request hours; verify committed-use covers only the proven-steady
floor (CUDs first, sustained-use on the remainder); check Pub/Sub
redelivery &lt; 1% and Trace within 5–8% of compute; confirm PITR/backup
retention matches the RPO claim being paid for (COST_REALITY.md
§4).<br><em>Follow-up: Autopilot data shows 80% steady binpack —
what do you propose?</em>
</details>
