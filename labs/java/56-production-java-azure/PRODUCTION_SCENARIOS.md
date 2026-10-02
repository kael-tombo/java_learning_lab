# PRODUCTION_SCENARIOS — Azure Java incidents

Five incidents drawn from real Azure failure modes for the lab-53 catalog service running on AKS + Application Gateway, Flexible Server PostgreSQL, Service Bus, and Entra workload identity federation. Each follows timeline → root cause → fix → prevention.

---

## 1. App Gateway probe misconfiguration drains a zone

**Setup:** AKS across 3 zones in `westeurope`-equivalent region, Application Gateway v2 with AGIC managing backend pool, readiness probe pointed at `/actuator/health/readiness`.

**Timeline:**

- T+0: Team ships a "faster startup" change: readiness probe path changed in Bicep from `/actuator/health/readiness` to `/actuator/health` to "simplify", interval 30s → 5s, unhealthy threshold left at default 3, timeout 5s.
- T+10 min: Rolling deploy starts. New pods take ~25s before HikariCP + Flyway-validate + first Redis ping complete, but the liveness-style `/actuator/health` endpoint returns UP only after all groups pass — meanwhile DB connection warmup under load pushes first-probe latency to 6–8s, exceeding the 5s timeout.
- T+12 min: App Gateway marks every new pod Unhealthy (3 consecutive timeouts). AGIC removes them from the backend pool. Old ReplicaSet already scaled down by the rolling update (`maxUnavailable: 1`, `maxSurge: 1`).
- T+15 min: All traffic concentrates on the few remaining old pods in one zone. Those pods saturate (Hikari pool + CPU), their probe responses slow past 5s too, and App Gateway drains them as well. Effectively one zone serves everything, then nothing.
- T+22 min: 5xx spike → Azure Monitor burn-rate alert fires. On-call sees "Backend health: 0 healthy hosts" on the App Gateway backend-health blade.

**Root cause:** Two compounding misconfigurations: (a) probe timeout (5s) shorter than realistic cold-readiness latency under load (DB pool fill + Redis TLS handshake), and (b) readiness semantics conflated with liveness — the probe gated *routing* but was tuned like a *restart* check. The rolling strategy allowed the old generation to disappear before the new generation ever passed health gates. This is the Azure-specific paragraph from EXERCISES.md §2 made real: App Gateway probes gate both routing *and* AGIC backend membership.

**Fix:**

1. Halt rollout (`kubectl rollout pause`), restore previous ReplicaSet; backend health recovers as old pods re-register.
2. Separate probes properly:
   - Readiness: `/actuator/health/readiness`, `periodSeconds: 15`, `timeoutSeconds: 10`, `failureThreshold: 3`, `initialDelaySeconds: 30` — generous enough for pool warmup.
   - Liveness: `/actuator/health/liveness`, tuned to restart only on deadlock, never on downstream slowness.
3. Mirror the same path/timeout in the App Gateway health-probe resource in Bicep — AGIC-managed probes must match the pod semantics, including host override (`pickHostNameFromBackendHttpSettings: true`) so TLS SNI matches.
4. Re-run rollout with `maxUnavailable: 0` for the serving Deployment.

**Prevention:**

- Single-source the probe definition: Bicep module exports `probePath`, `probeInterval`, `probeTimeout`; both the K8s manifest and the App Gateway probe reference it. CI diff fails if they diverge.
- Load-tested readiness budget: the KEDA-vs-HPA shootout harness (EXERCISES.md §5) runs at 5× baseline and records p99 readiness latency; probe timeout must exceed p99 + 50% margin.
- Deployment Stacks deny-rule: block `maxUnavailable > 0` on serving Deployments.
- Dashboard: App Gateway "healthy host count by zone" as a deployment-gating signal — auto-pause rollout if healthy hosts drop below N−1.

---

## 2. Flexible Server failover + PgBouncer pool exhaustion

**Setup:** Azure Database for PostgreSQL Flexible Server, zone-redundant HA (standby in another zone), Java (HikariCP per pod) behind PgBouncer in transaction-pooling mode as a sidecar-per-node. `statement_timeout` and PgBouncer `server_lifetime` at defaults.

**Timeline:**

- T+0: Azure initiates a planned failover (or a zonal fault triggers automatic failover). Primary → standby promotion takes ~90–120s (documented RTO in minutes).
- T+0–2 min: All server-side connections on the old primary are killed. Every Hikari pool sees a burst of `PSQLException: connection reset / server closed the connection unexpectedly`.
- T+2 min: New primary accepts connections. 40 pods × 20 Hikari connections each = 800 simultaneous reconnects slam PgBouncer, which fans out to Postgres. Postgres `max_connections` (e.g., 200 on a mid SKU) is protected by PgBouncer — but PgBouncer's own `default_pool_size` (20) and `max_client_conn` saturate, so most Java threads block in `getConnection()` and request latency explodes.
- T+5 min: Failover itself succeeded (RPO ~0, data intact), but p99 latency stays at 10–30s for 15 minutes because each pod's Hikari pool refills slowly and PgBouncer queues behind a few long-running Flyway-validate / analytics queries holding server connections in transaction mode.
- T+20 min: Latency recovers only after on-call kills the long runners via `pg_terminate_backend` and restarts the worker Deployment to reset pools.

**Root cause:** Failover was tested for *data* (PITR drill, canary diff) but never for *connection-storm* behavior. Three gaps: (a) no reconnect backoff/jitter in the DataSource config, so all pods retried in lockstep; (b) PgBouncer `default_pool_size` sized for steady state, not for 40× simultaneous pool refill; (c) long-running transactions held pooled server connections, serializing everyone else behind them in transaction-pooling mode.

**Fix:**

1. Immediate: `SELECT pg_terminate_backend(pid)` for the blocking analytics PIDs; rolling restart of API pods to rebuild Hikari pools against the new primary.
2. DataSource hardening (`application-azure.yml`):
   - `hikari.connection-timeout: 5000`, `validation-timeout: 2000`, `max-lifetime: 300000` (< PgBouncer `server_lifetime`), `keepalive-time: 30000`.
   - `socket-connect-timeout` + retry with exponential backoff + jitter on startup (Spring Retry around Flyway + pool warmup).
3. PgBouncer tuning: raise `default_pool_size` to cover `(pods × minIdle)` steady state, set `reserve_pool_size` + `reserve_pool_timeout` for burst refill, enable `server_fast_close` so dead servers are evicted fast.
4. Move analytics/reporting reads to the Flexible Server **read replica** so they never hold primary pool slots.

**Prevention:**

- Quarterly **failover game-day**: trigger manual failover (`az postgres flexible-server restart --failover`), measure reconnect-storm p99 and time-to-drain, assert against RTO ≤ 30 min / p99 recovery ≤ 5 min. Record in the ops report.
- Connection budget math in MATH_FOUNDATION style: `pods × hikariMaximumPoolSize ≤ pgbouncer max_client_conn`, and `pgbouncer default_pool_size + reserve ≤ postgres max_connections × 0.8`. CI check on the Helm values.
- `statement_timeout = 30s` on the OLTP role; separate role with longer timeout only on the replica.
- Alert on PgBouncer `cl_waiting` (clients waiting for a server connection) — symptom-based, fires before p99 does.

---

## 3. Service Bus session hotspot blocks an entire tenant

**Setup:** `orders` queue is session-enabled (`requiresSession: true`), session-id = `tenantId`. `maxDeliveryCount: 5` with DLQ configured. One enterprise tenant suddenly emits 50× its normal volume during a flash sale.

**Timeline:**

- T+0: Hot tenant floods its session with 200k messages. All other tenants' sessions are quiet.
- T+5 min: KEDA scales workers from 2 → 30 replicas (messageCount backlog trigger). But session receivers are **sticky per session**: each session can only be processed by one receiver at a time. 29 of 30 pods idle-spin or churn session-accept calls while one pod grinds through the hot session serially.
- T+15 min: A poison message (schema v3 payload on a v2 consumer) sits at the head of the hot session. Without per-message parallelism inside a session, every delivery attempt fails, `deliveryCount` climbs to 5, but the session lock is held throughout redelivery backoff — **head-of-line blocking** stalls the tenant's entire order flow.
- T+20 min: `deliveryCount` exceeds `maxDeliveryCount` and the message finally dead-letters — but the *next* poison message (same bad publisher deploy) is immediately head-of-line. Throughput for the hot tenant ≈ 0; other tenants unaffected but the team pages on "orders backlog not draining despite 30 replicas".
- T+40 min: On-call identifies `sessionId = hot-tenant` dominating `ActiveMessages` + `DeadLetterMessageCount` climbing in lockstep.

**Root cause:** Session-id cardinality mistake: `tenantId` has unbounded per-key volume skew, and sessions serialize *all* work per key. This is the exact hotspot math from MATH_FOUNDATION.md §3 — the Pub/Sub ordering-key lesson in Service Bus dress. KEDA scaled *replicas* but sessions cap *parallelism per key at 1*, so scaling could not help. The poison payload turned a slow drain into a full stall.

**Fix:**

1. Stop the bleeding: pause the bad publisher (roll back the v3 schema deploy), purge or DLQ-forward the poison batch.
2. Re-key sessions: session-id becomes `tenantId#orderDay#shard` (e.g., 16 shards per tenant) so a hot tenant fans out across up to 16 concurrent receivers. Ordering guarantee narrows from "per tenant" to "per tenant-day-shard" — confirm with product that this is acceptable (it was: orders are independent aggregates).
3. Set `maxConcurrentSessions` per pod (e.g., 8) and `maxAutoLockRenewalDuration` bounded; add `maxDeliveryCount: 5` + `forwardDeadLetteredMessagesToError` already present — verify replay runbook (EXERCISES.md §4) actually works against the DLQ.
4. Add a non-sessioned overflow path: messages over a per-session backlog threshold route to a plain queue consumed with full parallelism (ordering dropped for the overflow slice by design).

**Prevention:**

- Session-cardinality review in every topology PR: estimate p99-per-key rate vs single-receiver throughput; if `perKeyRate > singleReceiverRate`, shard the key or drop sessions.
- Dashboard per `sessionId`: active messages + delivery-count histogram. Alert on "one session > 50% of namespace backlog for > 10 min".
- Poison-drill (EXERCISES.md §4) runs in CI weekly: publish 10 schema-invalid messages to a canary session, assert DLQ quarantine + flow resume within N minutes.
- Publisher contract tests: schema-registry compatibility check gates deploy — v3 payloads never reach v2 consumers.

---

## 4. Federated-credential expiry breaks deploys

**Setup:** AKS workload identity federation: each ServiceAccount bound to a user-assigned managed identity via a federated credential trusting the cluster OIDC issuer (`iss` + `sub` = `system:serviceaccount:<ns>:<sa>`). No client secrets anywhere — the lab's headline posture.

**Timeline:**

- Day −90: Platform team rotates AKS clusters (new OIDC issuer URL after cluster recreation in a new Bicep Deployment Stack). Federated credentials were created once, manually, in the portal — nobody recorded them as code.
- Day 0, 09:00: CI builds images fine (ACR push works — different identity). Deploy stage applies manifests, then the Flyway pre-deploy Job fails: `DefaultAzureCredential: ManagedIdentityCredential authentication failed; federated token exchange rejected (invalid issuer)`.
- 09:15: Team assumes app bug, re-runs pipeline three times. Same failure. API pods crash-loop on Key Vault CSI mount for the same reason — nothing that needs Entra works, including App Insights token auth and Service Bus data-plane RBAC.
- 09:45: Someone checks Entra → managed identity → federated credentials: issuer still points at the *old* (deleted) cluster URL. Subject matches, issuer doesn't.
- 10:30: Fix applied, deploys unblocked. Total: 90 minutes of failed deploys during a release window; no data loss (old pods kept serving) but the release train slipped a day.

**Root cause:** The trust binding — the one failure mode CODE_DEEP_DIVE.md §1 warns is "always the trust binding, never application code" — was managed out-of-band (portal clickops) instead of in Bicep alongside the cluster. Cluster recreation changed the OIDC issuer; nothing updated the federated credential. Blast radius was total for deploys because *every* secret and data-plane access flows through federation.

**Fix:**

1. Update the federated credential issuer to the live cluster OIDC URL (`az aks show --query oidcIssuerProfile.issuerUrl`), verify subject string exactly.
2. Re-run Flyway Job, then rollout. Verify from a debug pod with zero credential env vars (EXERCISES.md §1) that Key Vault read works.
3. Rotate nothing else — that is the point of federation: no secrets to rotate, only the trust pointer to repair.

**Prevention:**

- Federated credentials **in Bicep** (`Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials`), deployed in the same Deployment Stack as the AKS cluster, with issuer wired as `aks.properties.oidcIssuerProfile.issuerUrl`. Portal-created credentials are banned by policy (Azure Policy deny + CI grep).
- Deploy-pipeline preflight: `az rest` check that every expected federated credential's issuer matches the live cluster before Flyway runs; fail fast with "issuer mismatch" instead of a cryptic token error.
- Alert on `AADSTS700016`-family / `invalid issuer` exchange failures in Activity Log + CSI driver events — pages platform, not app on-call.
- Document the cluster-recreation runbook: "recreating AKS rotates the OIDC issuer; federated credentials redeploy automatically via the stack" — then test it on a throwaway cluster.

---

## 5. KEDA scaler misfire from wrong messageCount threshold

**Setup:** `catalog-worker` ScaledObject, `azure-servicebus` trigger, `queueName: orders`, `messageCount: "50"` (copied from CODE_DEEP_DIVE.md §4 example verbatim into production), `minReplicaCount: 2`, `maxReplicaCount: 30`, polling interval default 30s. Each message takes ~2s single-threaded; each pod runs 8 concurrent message pumps.

**Timeline:**

- T+0: Steady state ~40 msgs/s in, 2 pods × 8 pumps × 0.5 msg/s = 8 msg/s out. Backlog grows even on a normal day — the threshold math was never done, so nobody notices the slow drift (backlog is "normally" ~200).
- T+1h: Promo push doubles ingress to 80 msgs/s. KEDA sees messageCount 200 > 50 and scales to 30 replicas within minutes. Drain capacity becomes 30 × 8 × 0.5 = 120 msg/s — overshoot. Backlog drains in ~2 minutes, then KEDA cool-down (default 5 min) keeps 30 pods burning while the queue sits empty.
- T+1h15: Ingress drops to 5 msgs/s overnight. KEDA scales back to 2 — but polling interval + stabilization delay means each small burst (a 300-message batch from a cron publisher) triggers a full 2→30→2 oscillation: scale-up latency (~90s for node scale + image pull) exceeds burst duration, so every burst pays for 30 pods and uses 3.
- End of week: Cost review shows worker spend 4× the HPA-only baseline from the shootout (EXERCISES.md §5) with *worse* p99 during bursts (cold pods + session affinity churn).

**Root cause:** `messageCount: "50"` was a doc-example placeholder treated as a tuned value. Correct threshold derives from the drain-time SLO: `threshold ≈ perReplicaDrainRate × targetLatencyBudget`, and the trigger must account for per-pod concurrency (8 pumps), message cost (2s), polling interval, and cooldown. A raw queue-length number with no per-replica-rate reasoning guarantees either chronic under-provision (drift) or sawtooth overshoot (this incident — both, at different hours).

**Fix:**

1. Derive the threshold properly: per-pod drain = 8 pumps / 2s = 4 msg/s. SLO: drain any burst within 120s without exceeding 12 replicas. Threshold per replica ≈ 4 × 120 / 12 ≈ 40… but KEDA divides backlog across desired replicas, so set `messageCount: "40"` **and** `maxReplicaCount: 12`, `cooldownPeriod: 120`, `pollingInterval: 15`.
2. Add `activationMessageCount: "10"` so tiny batches don't wake extra replicas at all.
3. Split the worker pool: session-ordered consumers (bounded parallelism, per §3 sharding) separate from the plain-queue overflow consumers (aggressive KEDA scaling) — one ScaledObject per workload shape.
4. Re-run the EXERCISES.md §5 shootout to confirm: backlog drain time ≤ SLO with cost ≤ 1.3× steady baseline.

**Prevention:**

- No magic scaler numbers: every KEDA `metadata` value links to the drain-time derivation in the PR description (formula + measured per-message cost from App Insights traces).
- Weekly scaler review: plot desired-replicas vs backlog; sawtooth with empty-queue plateaus = threshold/cooldown wrong.
- Cost guardrail: Azure Monitor alert on worker replica-hours > 1.5× trailing-4-week steady baseline — pages with "check scaler tuning", not "check app".
- Load-test the scaler, not just the app: burst harness (300/3k/30k messages) in staging asserts drain-time SLO *and* replica ceiling before any threshold change ships.
