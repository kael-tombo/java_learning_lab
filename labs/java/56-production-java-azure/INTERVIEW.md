# INTERVIEW — 12 Azure-Java Q&A

Questions first; answers hidden in `<details>` blocks. Covers federation, KEDA vs HPA, sessions/DLQ, and AGIC probes. Say the answer aloud before opening.

---

## 1. How does Entra workload identity federation remove secrets from a Java pod, and what is the single most common failure mode?

<details><summary>Answer</summary>The AKS cluster exposes an OIDC issuer; a federated credential on the user-assigned managed identity trusts a specific <code>subject</code> (<code>system:serviceaccount:&lt;ns&gt;:&lt;sa&gt;</code>) from that issuer. The workload-identity webhook injects a projected service-account token; <code>DefaultAzureCredential</code> exchanges it for short-lived Entra tokens — no client secret or connection string is ever stored. The classic failure is the <b>trust binding</b> (wrong issuer URL after cluster recreation, or subject typo), which surfaces as token-exchange rejection blamed on application code. Fix and prevention: manage federated credentials in Bicep alongside the cluster (issuer by reference), preflight-check issuer match before Flyway, and drill per EXERCISES.md §1.</details>

## 2. When is a federated credential preferable to a Key Vault-stored client secret, and what still belongs in Key Vault?

<details><summary>Answer</summary>Federation is preferable for <b>Azure control/data-plane access from the workload itself</b> (Key Vault reads, Service Bus/Event Hubs RBAC, Flexible Server Entra auth, ACR pull, App Insights ingestion): short-lived tokens, no rotation burden, blast radius bounded by RBAC. Key Vault still carries <b>third-party and non-federatable material</b>: Redis access keys, external API keys, webhook signing secrets, and any password for systems without Entra auth. References flow via CSI driver or env with scheduled rotation; the Java app never sees the vault mechanics, only mounted values.</details>

## 3. KEDA vs HPA on AKS: which signal does each scale on, and why do queue-bound workers need KEDA?

<details><summary>Answer</summary>HPA scales on <b>compute-native signals</b> (CPU, memory, or custom latency/concurrency metrics): it answers "pods are hot." KEDA (<code>ScaledObject</code> with e.g. <code>azure-servicebus</code> trigger) scales on <b>work-native signals</b> (queue messageCount, Event Hubs lag): it answers "work is waiting." A queue-bound worker can sit at 10% CPU while backlog grows unboundedly — HPA sees nothing wrong; only KEDA's backlog trigger adds replicas. Production pattern: KEDA on workers (drain-time SLO math sets <code>messageCount</code>/<code>cooldownPeriod</code>), latency-HPA on the API tier. Never copy the doc-example <code>messageCount: "50"</code> untuned (PRODUCTION_SCENARIOS.md §5).</details>

## 4. Derive a KEDA `messageCount` threshold from first principles.

<details><summary>Answer</summary>Measure per-pod drain rate: <code>pumpsPerPod / secondsPerMessage</code> (e.g., 8 pumps ÷ 2 s = 4 msg/s). Choose a drain-time SLO (e.g., any burst drains within 120 s) and a replica ceiling (e.g., 12). Then <code>messageCount ≈ drainRate × SLO / maxReplicas</code> (≈ 40 here), plus <code>activationMessageCount</code> so trivia doesn't scale, <code>pollingInterval</code> (15 s) for responsiveness, and <code>cooldownPeriod</code> (≥ drain SLO) to prevent sawtooth. Validate with the EXERCISES.md §5 shootout: burst harness asserts drain time <b>and</b> replica-hours. Re-derive whenever message cost or pump concurrency changes.</details>

## 5. Service Bus sessions: what ordering guarantee do they buy, what throughput ceiling do they impose, and how do you fix a hot session?

<details><summary>Answer</summary>Sessions guarantee <b>FIFO per session-id with a single exclusive receiver</b> — ordering scoped to the key. The ceiling: <b>one receiver's throughput per session</b>, no matter how many replicas KEDA adds. A hot key (e.g., session-id = tenantId with a 50× tenant) serializes all its work through one pod. Fixes, in order: shard the session key (<code>tenant+day+shard</code>, narrowing the ordering scope with product sign-off), bound <code>maxConcurrentSessions</code> per pod, and add a non-sessioned overflow queue (ordering dropped by design) for backlog beyond a threshold. Review per-key rate vs single-receiver rate in every topology PR.</details>

## 6. A session-enabled queue with no DLQ receives a poison message. Walk through the failure.

<details><summary>Answer</summary>The poison message reaches the head of its session and every delivery attempt fails; with no DLQ/<code>maxDeliveryCount</code>, redelivery loops forever while the session lock is held — <b>head-of-line blocking</b> stalls the entire session's flow (all subsequent messages for that key wait behind the poison one). Other sessions proceed, masking the outage in aggregate dashboards. Fix: <code>maxDeliveryCount: 5</code> + <code>forwardDeadLetteredMessagesToError</code> quarantines the poison message for autopsy and unblocks the session; publisher contract tests (schema-registry compatibility gate) stop the next one. Drill per EXERCISES.md §4.</details>

## 7. What does App Gateway health-probe configuration gate during an AKS rollout, and what are the two classic probe mistakes?

<details><summary>Answer</summary>AGIC-managed App Gateway probes gate <b>both routing and backend-pool membership</b>: Unhealthy pods are removed from the pool, and during a rolling update that can concentrate traffic onto surviving pods until none are healthy (PRODUCTION_SCENARIOS.md §1). Classic mistakes: (a) <b>timeout shorter than cold-readiness latency</b> (pool fill + Redis TLS + Flyway-validate under load exceeds a 5 s timeout → every new pod marked Unhealthy), and (b) <b>conflating readiness with liveness</b> (one endpoint/threshold for "route to me" and "restart me"). Fix: separate readiness (<code>/actuator/health/readiness</code>, generous timeout, <code>maxUnavailable: 0</code>) from liveness, single-source probe path/timeout in Bicep for pods and gateway alike, and budget timeout from measured p99 readiness + 50%.</details>

## 8. Flexible Server failover succeeded but p99 stayed red for 15 minutes. Why?

<details><summary>Answer</summary>Failover restores the <b>data plane</b> in minutes, but the <b>connection plane</b> storms: all Hikari pools reconnect in lockstep against PgBouncer, whose <code>default_pool_size</code>/<code>reserve_pool</code> were sized for steady state, while long-running transactions hold pooled server connections in transaction-pooling mode. Everyone queues in <code>getConnection()</code>. Remedies: staggered reconnect with backoff+jitter, <code>max-lifetime</code> below PgBouncer <code>server_lifetime</code>, <code>reserve_pool_size</code> for refill bursts, <code>statement_timeout</code> on OLTP roles, analytics on the read replica — and a quarterly failover game-day measuring <b>time-to-p99-recovery</b>, not just RPO. See PRODUCTION_SCENARIOS.md §2.</details>

## 9. Service Bus vs Event Hubs for a Java estate: which carries commands and which carries telemetry, and why?

<details><summary>Answer</summary><b>Service Bus carries commands</b> (queues/topics, sessions, transactions, duplicate detection, DLQ): enterprise messaging with per-message settlement and dead-lettering — exactly what order/payment flows need. <b>Event Hubs carries telemetry/streams</b> (Kafka protocol, partitions, replay, Capture): high-throughput append-only log for events, metrics, and audit trails. Same broker-vs-log split as lab 14: commands need settlement semantics; telemetry needs replay and throughput units. Mixing them up (commands on a replay log with no DLQ, or telemetry on transacted queues) is the design smell.</details>

## 10. How do Flexible Server Entra auth and Key Vault references combine, and where does Flyway fit in the deploy?

<details><summary>Answer</summary>Flexible Server <b>Entra auth</b> lets the pod authenticate as its managed identity (token-as-password via the <code>DefaultAzureCredential</code> chain) — no DB password exists to leak or rotate. Everything else secret-like (Redis keys, third-party credentials) arrives as <b>Key Vault references</b> (CSI volume or env). <b>Flyway runs as a pre-deploy Kubernetes Job</b> with the same federated identity — before the new ReplicaSet admits traffic — so migrations complete exactly once and never race the rollout. The Job's failure blocks promotion, which is the point.</details>

## 11. AKS vs Container Apps for the lab-53 service: state the split rule and the cost crossover.

<details><summary>Answer</summary><b>AKS for the steady API</b> (24/7, zone-spread, custom CNI/networking, full KEDA+AGIC control — node-hour economics win above ~60% utilization, deepened by RIs on the proven-steady slice); <b>Container Apps for spiky slices</b> (webhooks, fan-out, cold-tolerant endpoints — scale-to-near-zero, per-second billing, native/CRaC images for cold starts, Dapr building blocks). Crossover heuristic: a slice averaging &lt; 25% replica utilization belongs on Container Apps; above ~60% it belongs on reserved AKS nodes. Prove with the 7-day tagged bill (MINI_PROJECT) and re-check quarterly — see COST_REALITY.md.</details>

## 12. Design the Azure Monitor alert set for this estate. Which alerts are symptom-based, and what is each one's runbook first step?

<details><summary>Answer</summary>Symptom-first set: (a) <b>burn-rate alert</b> on availability/p99 (first step: pause rollout via Deployment Stack gate, check App Gateway backend health); (b) <b>App Gateway healthy-host count by zone</b> (first step: <code>kubectl rollout pause</code>, compare probe config vs pod readiness); (c) <b>PgBouncer <code>cl_waiting</code></b> (first step: check for failover/long runners, terminate blockers); (d) <b>per-session backlog skew</b> (first step: identify hot session-id, check DLQ growth for poison); (e) <b>scaler replica-hour anomaly</b> (first step: review KEDA desired-vs-backlog plot, not the app). Cause-metrics (CPU, pod restarts) are diagnostic context, never paging triggers. Every alert links to the REAL_WORLD_PROJECT.md runbook; unactionable or twice-firing-known-condition pages are filed as monitoring bugs per BIG_TECH_FEEDBACK.md §5.</details>
