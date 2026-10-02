# INTERVIEW — 12 AWS-Java questions (answers hidden)

Twelve questions an interviewer uses to separate "deployed a tutorial" from "ran it at 2 a.m." Each answer is collapsed — attempt the question, then open it. Covers IRSA, HPA signals, Flyway placement, PITR proof, and MSK vs SQS, plus the failure modes in PRODUCTION_SCENARIOS.md.

---

## 1. Explain IRSA end to end. A pod gets 403 from SQS after a cluster upgrade — walk me through your diagnosis.

<details><summary>Answer</summary>
IRSA = EKS OIDC provider ↔ IAM role trust policy (issuer + <code>sub</code> = serviceaccount) ↔ pod ServiceAccount annotation (<code>eks.amazonaws.com/role-arn</code>). Kubelet projects a web-identity token; AWS SDKs call <code>AssumeRoleWithWebIdentity</code> for short-lived creds — zero static keys. Post-upgrade 403: (1) <code>eks describe-cluster</code> → current OIDC issuer; (2) <code>iam get-role</code> → trust policy issuer — upgrades rotate the issuer while IaC pins the old one (PRODUCTION_SCENARIOS §4); (3) run the lab proof — debug pod <code>sts get-caller-identity</code> must show the app role, not the node role (node-role fallback masks the break); (4) fix CDK OIDC provider + trust in the same stack, redeploy, restart pods. Prevention: OIDC provider managed with the cluster, CI issuer-equality check after version bumps.
</details>

## 2. Your HPA targets 70% CPU. Traffic doubles, CPU sits at 45%, p99 explodes. What happened, and what is the correct HPA design?

<details><summary>Answer</summary>
Queue-bound saturation: threads parked on a slow downstream (DB pool, Redis, enrichment call), CPU idle while latency explodes — CPU-only HPA sleeps through it (PRODUCTION_SCENARIOS §1/§3, EXERCISES §4). Correct design per CODE_DEEP_DIVE §3: HPA on <b>p99 latency AND CPU</b> (Micrometer → CloudWatch custom metric + resource metric), min 3 (one per AZ), max sized for 10× spikes; consumer workloads scale separately on lag (KEDA kafka scaler). Prove it with the slow-downstream load test: CPU-HPA flat, latency-HPA scales — and recompute the arithmetic (<code>peak RPS × p99 / (concurrency × util)</code>) quarterly.
</details>

## 3. Where do Flyway migrations run — app startup or a separate Job — and why does it matter during a rolling deploy?

<details><summary>Answer</summary>
Pre-deploy <b>Job, never app startup</b>. Concurrent pod starts race migrations (double-applied or half-applied schema); a Job migrates exactly once, then the rollout proceeds. During rolling updates old + new code coexist, so migrations must be <b>backward-compatible, expand-then-contract</b> (add column → dual-write → migrate → drop), verified by <code>flyway validate</code>. Rollback ships with the migration reversibility verdict — a non-reversible migration means the previous image tag alone cannot save you.
</details>

## 4. "Aurora has PITR enabled with 35-day retention." Prove the RPO ≤ 5 min claim. What exactly do you do?

<details><summary>Answer</summary>
Console-green-checkmark proves nothing. The drill (EXERCISES §3, MINI_PROJECT): (1) note timestamp T; (2) write canary rows; (3) delete them; (4) <b>restore-to-point-in-time (T+5 min) into a NEW cluster</b>; (5) diff canaries — record achieved RPO vs the ≤ 5 min claim and every step for the runbook. PITR bounds RPO only if transaction-log retention covers the window — verify by restoring, not by reading the retention setting. Separate drill, separate number: Aurora <b>failover timing</b> (DNS TTL + pool settings) proves RTO ~30–60 s; passing one proves nothing about the other.
</details>

## 5. MSK vs SQS for the catalog's price-update stream — state your decision rule and apply it at 1,200 msg/s.

<details><summary>Answer</summary>
<b>Replay/compaction/event-sourcing → MSK. Task distribution without broker ops → SQS/SNS</b> (QUIZ §7, ARCHITECTURE.md table). Price updates need replay (rehydrate projections, new consumer from history) → MSK earns its broker ops at 1,200 msg/s (~$750/mo flat vs ~$1,350 SQS usage — COST_REALITY.md breakeven). If the workload were fire-and-forget notifications, SQS wins (no partitions to size, no rebalance storms, lag-native scaling, DLQ built in). At dev scale (10 msg/s) SQS wins regardless — MSK is half the bill. Revisit when the query list changes, not on ideology.
</details>

## 6. The ALB target group health-checks `/actuator/health/liveness`. Deploys cause 5xx spikes. Explain the bug and the correct setup.

<details><summary>Answer</summary>
Liveness = "JVM alive" (true seconds after start, cold pools); <b>readiness = "can serve"</b> (pools warm, schema validated, Redis reachable). Routing on liveness sends traffic to cold pods while killing the warm ones — every batch is a mini-outage (PRODUCTION_SCENARIOS §1). Correct: target group → <code>GET /actuator/health/readiness</code> (healthy 2×15 s, unhealthy 2×5 s), pod <code>readinessProbe</code> on the same path with custom indicators (Hikari validation query, Redis ping), rolling <code>maxUnavailable: 0, maxSurge: 1</code>, <code>preStop: sleep 30</code> ≥ deregistration delay ≤ grace period. Liveness stays — for restarts only, never routing.
</details>

## 7. Aurora fails over. Your JVMs keep hitting the old writer for 4 minutes. Name the three layers and the fix for each.

<details><summary>Answer</summary>
(1) <b>JVM DNS cache</b> defeats Aurora's DNS-based endpoint flip → set <code>-Dnetworkaddress.cache.ttl=5 -Dnetworkaddress.cache.negative.ttl=5</code>. (2) <b>Stale pooled sockets</b> (Hikari <code>maxLifetime</code> longer than failover) → <code>maxLifetime</code> ≤ 5 min, <code>connectionTimeout</code> 3 s, validation + 30 s keepalive; readiness must open a fresh validation query. (3) <b>Thundering-herd reconnect</b> (all pods refill full pools on a cold writer → <code>Too many connections</code>) → staggered rolling restart, reader-endpoint splits for reads, CloudWatch <code>DatabaseConnections</code> alarm at 70% of max. Prove with a quarterly <code>failover-db-cluster</code> game-day measuring true RTO (PRODUCTION_SCENARIOS §2).
</details>

## 8. Consumer lag grows linearly after a deploy and never recovers, with frequent rebalances. Diagnose and sequence your response.

<details><summary>Answer</summary>
Per-record cost rose past group capacity (e.g., 8 ms → 45 ms synchronous enrichment; need 54 threads, have 24) while <code>max.poll.records: 500</code> × slow processing exceeds <code>max.poll.interval.ms</code> → members look dead → rebalance storms pause everything (PRODUCTION_SCENARIOS §3). Sequence: <b>(1)</b> stop the storm — raise interval (~300 s), lower records (50–100), restart one at a time; <b>(2)</b> scale to the math (<code>threads ≥ rate × per_record_s / 0.7</code>, capped by partition count); <b>(3)</b> revert/async the enrichment or move work off the poll thread. Prevention: lag-based autoscaling (KEDA), per-record timer in every consumer-path PR, rebalance-rate + lag alarms.
</details>

## 9. You migrate EKS nodes to Graviton and p99 triples under TLS-heavy load while CPU drops. Is Graviton slower for Java? What do you check?

<details><summary>Answer</summary>
No — allocation/GC are arch-neutral; <b>crypto intrinsics and native bindings are not</b> (PRODUCTION_SCENARIOS §5). Check: (1) JDK micro version — old 17.0.x lacks ARM AES/SHA intrinsics, x86 AES-NI fast path becomes pure-Java on ARM; upgrade to latest 17/21 and verify with <code>-XX:+PrintIntrinsics</code>/JFR; (2) native deps (tcnative/BouncyCastle/Conscrypt) missing <code>linux-aarch64</code> classifiers → portable fallback; (3) rerun the EXERCISES §5 matrix (throughput + p99 + $/M-req, peak TLS mix, both archs) — fixed result here was ~−8% p99 and ~−19% $/M-req on m7g. Keep mixed-arch node groups during validation; pin JDK + flags in versioned config.
</details>

## 10. Egress is your largest bill line. Name four concrete reductions for this API, in leverage order.

<details><summary>Answer</summary>
Per COST_REALITY.md: (1) <b>Edge caching</b> — CloudFront + ElastiCache for <code>GET /products/*</code>; each 10% hit-rate shift ≈ $180/mo baseline, $4,500 event-scale. (2) <b>Payload discipline</b> — pagination, <code>?fields=</code>, gzip/Brotli, image bytes via S3/CloudFront never through pods (1 MB → 200 KB halves transfer). (3) <b>Regional affinity</b> — same-region EKS/Aurora/Redis/MSK, AZ-aware routing; cross-AZ ($0.01/GB) and fanout multiply silently. (4) <b>LCU hygiene + sampling</b> — keep-alive, fewer listener rules, drain tuning; X-Ray 1–5% sampling at peak (unsampled spans cost more than MSK), no DEBUG logs to CloudWatch. Guardrail: cost tags + WoW > 15% alert; review transfer first, compute second, datastores third.
</details>

## 11. "No static AWS keys" — how is that actually enforced for pods, DB passwords, and Redis AUTH tokens?

<details><summary>Answer</summary>
Pods: <b>IRSA</b> — ServiceAccount annotation → IAM role via OIDC, SDKs assume short-lived creds automatically (CODE_DEEP_DIVE §1); verified by <code>sts get-caller-identity</code> showing the app role. DB: Secrets Manager (or IAM DB auth) injected as env/mounted files with scheduled rotation — never ConfigMap/env-baked; JDBC URL + user + password resolved from <code>application-aws.yml</code> placeholders. Redis: TLS + AUTH token from Secrets Manager (<code>REDIS_AUTH</code>), rotation without restart via file mounts. CI/IaC enforcement: no <code>AWS_ACCESS_KEY_ID</code> in manifests, least-privilege Security Groups, GuardDuty + CloudTrail + ECR scanning (REAL_WORLD_PROJECT).
</details>

## 12. Design the rollback for tonight's catalog deploy in 60 seconds: what ships with the release, and what do you do when p99 alarms fire mid-rollout?

<details><summary>Answer</summary>
Ships with it: <b>previous image tag + migration reversibility verdict</b> (expand-then-contract only — else rollback is unsafe) <b>+ written runbook entry</b> (FLASHCARDS §15). Rollout is readiness-gated (<code>maxUnavailable: 0</code>) with 5xx/p99 alarms wired to auto-pause. Alarms fire: (1) <code>kubectl rollout pause</code> (or pipeline auto-pause); (2) confirm old pods still <code>HealthyHostCount</code> in ALB — readiness gating should have held them; (3) <code>kubectl rollout undo</code> to previous tag; (4) if migration already applied, execute the pre-planned compatible-forward fix (never downgrade-migrate under traffic); (5) record rollback minutes for the quarterly drill. Amazon's rule (BIG_TECH_FEEDBACK): reversibility by someone half-asleep, or it isn't a rollback plan.
</details>
