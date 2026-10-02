# BIG_TECH_FEEDBACK — What Amazon, Netflix, Uber, and Stripe would red-pen in this lab

Quotable principles with the reasoning behind each. Treat every quote as a review comment on the catalog API in this lab (EKS + ALB → Aurora + ElastiCache + MSK/SQS, IRSA, HPA on p99 + CPU, Flyway Job, PITR drills). Adopt the ones your on-call story needs first.

---

## Amazon — "Everything fails, all the time; design the cell so the blast radius is a fraction."

**Principle:** *Cell-based architecture: partition the fleet so no single control-plane, AZ, or downstream can take more than one cell.*

**Reasoning:** Amazon's AZ evacuation and shuffle-sharding practice exists because Multi-AZ alone is not isolation — a bad deploy, a hot partition, or an Aurora failover storm (PRODUCTION_SCENARIOS §2) still hits 100% of pods if they share one cluster, one target group, one consumer group. Cells (separate EKS node groups / target groups / Aurora reader splits per cell, sticky routing by customer shard) turn a full outage into a fractional one. This lab's `minReplicas: 3` across 3 AZs is the embryo of a cell: same idea, smallest viable form. Scale it by sharding the catalog by tenant/region before you need it — retrofitting cells during an incident is the incident.

**Apply here:** Start with AZ-spread + PodDisruptionBudget (`minAvailable: 2`), then add a second ALB target group per AZ-weighted split; measure "fraction of traffic lost when one cell drains" as an SLO input.

## Amazon — "Deployability is the feature. Every deploy must be reversible in minutes by someone half-asleep."

**Principle:** *Deployment safety: automated rollback on canary alarms, backward-compatible everything, one-button revert.*

**Reasoning:** Amazon's Apollo/pipeline culture gates every stage on metrics and keeps the previous known-good artifact hot. This lab already encodes half of it: `maxUnavailable: 0, maxSurge: 1` + readiness gating + Flyway expand-then-contract (old + new code coexist). The missing half most teams skip: the rollback is *timed and rehearsed* (REAL_WORLD_PROJECT exit drill), not documented-and-hoped. The ALB-drains-pods incident (PRODUCTION_SCENARIOS §1) is what "rollback exists but takes 25 minutes to figure out" costs.

**Apply here:** Every deploy records previous image tag + migration reversibility verdict in the release note; CloudWatch 5xx/p99 alarms auto-pause the rollout (`kubectl rollout pause` via pipeline); quarterly rollback drill timed with a stopwatch.

## Netflix — "HPA on CPU is astrology. Scale on the thing users feel, and chaos-test the scaler."

**Principle:** *Latency-and-queue-driven autoscaling, proven by deliberately breaking it (Chaos Monkey / FIT for autoscalers).*

**Reasoning:** Netflix scales on request concurrency, queue depth, and streaming-experience signals — CPU is an input, never the decision — because the failures that matter are queue-bound (threads parked, CPU idle, users timing out). This lab's HPA on p99 + CPU and KEDA-on-consumer-lag (PRODUCTION_SCENARIOS §3) are the same lesson at smaller scale. Netflix's corollary: if you haven't chaos-tested the scaler, you don't have a scaler — you have a YAML file. Kill pods mid-scale-up, black-hole the downstream, expire all DB connections at once, and watch whether HPA/KEDA does the right thing before production teaches you.

**Apply here:** Keep the HPA math (`peak RPS × p99 / (concurrency × util)`, MATH_FOUNDATION §4) recomputed quarterly; run EXERCISES §4 (slow-downstream load test) as the chaos case that proves latency-HPA fires while CPU-HPA sleeps.

## Netflix / Uber — "JVM flags are production code. Review them, version them, and benchmark them per workload."

**Principle:** *Standardize the JVM flag set per service class; no ad-hoc `-Xmx` in manifests; every flag change is a canaried deploy.*

**Reasoning:** At Netflix/Uber scale, a single GC or heap flag ships to thousands of JVMs — a wrong `MaxRAMPercentage`, a missing `UseZGC`/`UseG1GC` choice, or an unpinned micro JDK (see the Graviton crypto regression, PRODUCTION_SCENARIOS §5) becomes a fleet-wide latency shift. Their practice: flags live in versioned config (Helm values / CDK), sized from measured heap profiles (JFR old-gen growth, not guesses), with container-awareness (`-XX:MaxRAMPercentage=75.0`, `-XX:+UseContainerSupport`) and DNS TTL flags (`networkaddress.cache.ttl=5`) as mandatory defaults for AWS-backed services. "It worked on my node family" is not a benchmark.

**Apply here:** This lab's flag baseline — container support + `MaxRAMPercentage` per node size + G1/ZGC chosen by pause measurements + DNS TTL 5 s + explicit AES/SHA intrinsics on Graviton — goes in one reviewed file; any PR touching it re-runs the lab-53 benchmark matrix (throughput + p99 + $/M-req, both archs).

## Uber / Stripe — "DynamoDB-vs-RDS is not a religion; it is an access-pattern decision. Write the query list first."

**Principle:** *Choose DynamoDB when access patterns are known, key-shaped, and need single-digit-ms at any scale; choose Aurora/RDS when queries are relational, ad-hoc, or transactional across entities. Decide from the query list, not the logo.*

**Reasoning:** Uber (schemaless/MySQL layers) and Stripe (relational discipline with radical query ownership) converge on the same rule: the data model follows the questions you ask. Catalog API reads (`GET /products/{id}`, `GET /category/{c}?page=`) are key-shaped and cache-friendly → DynamoDB + DAX or Aurora reader + ElastiCache both work. But admin search ("products with margin < X in categories updated last week"), financial reconciliation, and Flyway-managed schema evolution are relational workloads — forcing them into single-table DynamoDB design buys operational pain for no latency gain. Conversely, the price-update event stream at 10k writes/s with replay needs is a streams problem (MSK/Kinesis), not a relational one. This lab picks Aurora + Redis + MSK/SQS because the catalog's query mix is relational-reads + cache + events — the ARCHITECTURE.md decision table is the artifact; "we use Postgres because we know Postgres" is not an architecture.

**Apply here:** Before adding DynamoDB (or any store), list every query with its rate, latency budget, and consistency need; only a store that answers all rows wins. Revisit when the list changes — scale changes the answer (see COST_REALITY.md: at 100× scale, the key-value slice often migrates first).

## Stripe — "Chaos practice is a calendar invite, not a value statement. Game-day quarterly or it didn't happen."

**Principle:** *Scheduled, scripted failure drills (AZ loss, Aurora failover, bad deploy, region evacuation) with written outcomes — the same cadence as financial close.*

**Reasoning:** Stripe's chaos/game-day discipline treats operational proof like accounting: periodic, evidenced, auditable. Every drill in this lab maps to it — PITR restore with canary diff (RPO proof), Aurora failover timing (RTO proof), readiness-gated rollout with black-holed DB (deploy proof), IRSA trust re-verification after upgrades (identity proof), consumer-lag recovery (streaming proof). The principle that bites: a drill without a recorded number (RTO seconds, RPO rows, rollback minutes) is theater. REAL_WORLD_PROJECT's "demonstrated, not claimed" SLOs are this idea in one line.

**Apply here:** Quarterly game-day covering exactly four events (AZ loss, DB failover, bad deploy, MSK lag spike); each produces one number + one runbook edit. Monthly cost review alongside (Graviton mix + Aurora I/O watch) so efficiency gets the same cadence as resilience.

---

## The five-line synthesis

1. Blast radius is a design input (cells), not an apology after.
2. Rollback is part of the deploy, timed with a stopwatch.
3. Scale on user pain (latency/lag), and break the scaler on purpose.
4. JVM flags and IAM bindings are code — review and canary them.
5. Data-store choice comes from the query list; chaos cadence turns all of the above from docs into proof.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Atlassian, "Migrating the Jira and Confluence applications to AWS
  Graviton" (Nov 2025, 3000+ EC2 instances): prior G2/G3 attempts failed
  on *unexplained* slowness (L3-miss suspicion, `synchronized` folklore)
  until the team banned micro- and passive-benchmarking and defined one
  metric — **throughput at breaking latency**. PMU data then showed ~25%
  higher L3-mpki on G3 (cache thrashing) → fix was *smaller* JIT code
  cache (64–128 MB via `InitialCodeCacheSize`/`ReservedCodeCacheSize`) +
  `TieredCompilation` + Transparent Huge Pages for TLB pressure. Outcome
  on G4 (c8g): ~30% fewer instances, P90 down >12%, pilot throughput
  +20–30%, fleet savings ~9.8% (25% on hot shards). Confluence *regressed*
  on c7g in prod (p50 19→22 ms, p99 262→347 ms) after passing tests —
  same-binary-different-workload lesson. Capacity: 10–15k ICE errors/hour
  at their scale; mitigation = sync/async workload split (async on older
  Gravitons) + mixed-instance ASGs with x86 fallback.
  <https://www.atlassian.com/blog/how-we-build/migrating-the-jira-and-confluence-applications-to-aws-graviton>
  Lab actions: cap code cache + tiered compilation in the lab-53
  Dockerfile JAVA_OPTS variant; add an ICE/fallback exercise (mixed
  instances policy) to EXERCISES.md §5; treat any Graviton claim as
  guilty-until-PMU-proven.
- Netflix virtual-threads incident via InfoQ summary of the Netflix JVM
  Ecosystem TechBlog post (Aug 2024): Java 21 + Spring Boot 3 + embedded
  Tomcat hung with `closeWait` socket pile-up; `jcmd Thread.dump_to_file`
  showed thousands of *blank* (never-scheduled) virtual threads — Tomcat
  minted per-request virtual threads that pinned on `synchronized` blocks
  while all ForkJoinPool carriers were held: classic deadlock shape with
  no lock owner in the heap dump. Fix path: reproducible test case
  (gist by Daniel Thomas, linked in article) + JDK-side pinning fixes in
  later releases; same fleet also adopted generational ZGC (JEP 439) for
  pause control with Atlas Streaming Eval alerting catching the bad
  instances.
  <https://www.infoq.com/news/2024/08/netflix-performance-case-study/>
  (primary: `netflixtechblog.com/java-21-virtual-threads-dude-wheres-my-lock-…`)
  Lab actions: the lab's pinning exercise (53/EXERCISES) and ReentrantLock
  rule now have a named production casualty; add `jcmd` dump reading to
  the virtual-threads deep-dive follow-up.
