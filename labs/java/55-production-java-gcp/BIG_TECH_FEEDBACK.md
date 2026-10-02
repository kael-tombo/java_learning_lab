# BIG_TECH_FEEDBACK — Google / Spotify / Shopify lessons for GCP Java

Quotable principles with the reasoning behind each. Use them in design
reviews; each ends with the concrete GCP/Java action this lab expects.

---

## 1. SRE burn-rate alerting (Google SRE book)

> "Alert on how fast you are eating the error budget, not on how many
> errors you saw in the last minute."

Raw thresholds (`5xx > 100/min`) page during harmless deploys and sleep
through slow-burn regressions. A 99.9% monthly SLO gives ~43 min of
budget; a burn-rate alert fires when the *consumption speed* predicts
exhaustion — fast-burn (1h window, page) vs slow-burn (6h window,
ticket). This lab's Cloud Monitoring SLO alerts (THEORY.md §4) are the
managed form of the SRE-book multiwindow pattern.

**Action:** Every service ships two burn alerts from day one; the
synthetic-burn drill (MINI_PROJECT step 3) must fire the fast-burn path
before prod traffic arrives.

## 2. Borg/K8s lessons: requests are contracts (Google)

> "The scheduler believes your resource requests. If you lie, the
> machine teaches you the truth at 3 AM."

Borg taught Google that declared requests drive placement and billing;
GKE Autopilot (PRODUCTION_SCENARIOS.md §1) makes the contract literal —
you pay per request and get killed past it. Java teams lie accidentally
by sizing from steady state and forgetting warmup, GC pacing, and
off-heap (Metaspace, direct buffers, thread stacks × virtual-thread
counts).

**Action:** Requests derive from measured warmup-peak + GC headroom;
the startup memory soak is a merge gate, not folklore.

## 3. Diplomacy of SLOs (Google / Spotify)

> "An SLO is a treaty between engineering and the business, not a
> technical metric. Renegotiate it before you violate it."

Spotify's squad model works because each squad's SLO states what users
tolerate (checkout p99 < 300 ms at 5× baseline — REAL_WORLD_PROJECT.md)
and what happens when budget runs out (feature freeze, not heroics).
Burn-rate pages carry weight only if product agreed the budget first.
Engineers who set 99.99% without business sign-off manufacture their
own pager fatigue.

**Action:** Write the 99.9% SLO + freeze policy into the ops report;
every burn-rate page links the treaty, not just the graph.

## 4. AlloyDB vs Spanner calls (Google Cloud teams)

> "AlloyDB is Postgres that scales up gracefully; Spanner is a global
> commit protocol that happens to speak SQL. Choose by write topology,
> not by marketing."

AlloyDB (columnar + PG compatibility) wins when the workload is
single-region relational with read replicas — this lab's default, with
Flyway and the Auth Proxy unchanged. Spanner wins for multi-region
writes with external consistency, at the price of query-shape
discipline and higher write latency/cost. Migrating later reshapes
transactions, not just the JDBC URL — decide from the lab-53 write
profile before building.

**Action:** Document the choice with numbers: single-region write RPS
and cross-region requirement; default AlloyDB/Cloud SQL unless global
writes are proven.

## 5. Progressive delivery (Google / Shopify flash-sale scars)

> "Nobody survives a 100% deploy on sale day. Ship in slices the
> Gateway can retract."

Shopify's flash-sale history and Google's deploy infrastructure agree:
canary → stable with readiness-gated traffic (Cloud Deploy +
Gateway, THEORY.md §4) turns bad revisions into 5%-blast-radius
non-events. The Autopilot OOMKill (§1) and cold-cascade (§5) scenarios
both stayed survivable *because* the Gateway held the split. Big-bang
`kubectl set image` on the whole fleet converts every sizing error into
a full outage.

**Action:** Every prod promotion is a Cloud Deploy canary with
automatic rollback on burn-rate; attach the rollback-bundle proof to
the MINI_PROJECT deliverable.

## 6. No keys in prod (Google Cloud security reviews)

> "Every exported service-account key is a future incident report with
> your name on it."

Google's breach reviews keep finding the same root cause: a JSON key
checked into CI, baked into an image, or emailed for debugging. The fix
is structural — Workload Identity (CODE_DEEP_DIVE.md §1) removes the
secret class entirely instead of rotating it better. The project-move
outage (PRODUCTION_SCENARIOS.md §4) proves the corollary: when auth
breaks, repair the federation; reaching for a key converts an outage
into a vulnerability.

**Action:** CI fails on any `*.json` key file in the repo or image;
the keyless-proof gate runs on every deploy.

## 7. Measure the cold path (Shopify / Cloud Run wisdom)

> "Your p99 is decided by your coldest instance, not your warmest
> benchmark."

Warm-load benchmarks flatter JIT images; production p99 during scale
events is set by startup time × queueing (PRODUCTION_SCENARIOS.md §5).
Shopify sizes warm floors around sale calendars; the equivalent here is
CRaC/native artifacts + scheduled minScale for the Run slice, priced
explicitly rather than discovered at noon on sale day.

**Action:** Publish cold-start latency beside every benchmark; the
concurrency sweep (EXERCISES.md §2) is invalid without the cold column.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)

- GoogleCloudPlatform `serverless-production-readiness-java-gcp` (living
  repo, 397 commits): production-ready = stable, reliable, scalable,
  performant, fault-tolerant, monitored, documented, secured — and
  optimization is always *for something* (startup, latency, memory/CPU,
  concurrency, image size, cost). The repo's framing matches this lab's
  THEORY split; use its `services/` multi-service sample (quotes/audit/
  reference/faulty/BFF on Cloud SQL + Firestore) as the reference
  implementation for the MINI_PROJECT dual-deploy.
  <https://github.com/GoogleCloudPlatform/serverless-production-readiness-java-gcp>
- Cloud Run Java tips (official docs): container-aware JVM (8u192+,
  11/17 GA), AppCDS/shared archives, smaller thread stacks (1 MB default
  × thread count adds up fast), reactive-or-bounded pools (blocking code
  on 2–4 event-loop threads tanks throughput; unbounded pools thrash),
  background tasks don't run under request-based billing (JDBC eviction,
  trace/metric batching, `@Scheduled`, Pub/Sub streaming pull all stall
  at zero QPS), lazy init + Spring AOT/GraalVM for startup, explicit GC
  choice (G1 default ≥ ~1.8 GB/2 CPU; Serial below — know which you got).
  <https://docs.cloud.google.com/run/docs/tips/java>
- Cloud Run concurrency (official docs): default max 80 (CLI/Terraform),
  cost ≈ billable instance-time — higher concurrency usually lowers cost
  *until* contention raises latency; match memory to concurrency; avoid
  mutable global state without locks; iterate 8 → up with load tests to
  maximum *stable* concurrency. Directly backs EXERCISES.md §2's sweep
  method and the COST_REALITY Run math.
  <https://docs.cloud.google.com/run/docs/about-concurrency>
