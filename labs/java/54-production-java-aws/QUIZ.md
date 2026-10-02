# QUIZ — AWS

## 1. EKS vs ECS vs Lambda for the steady catalog API?
<details><summary>Answer</summary>EKS (full K8s semantics, HPA, mesh path) or ECS (simpler). Lambda only for spiky slices — steady APIs hit cost + 15-min walls.</details>

## 2. IRSA in one sentence + the #1 misconfiguration?
<details><summary>Answer</summary>Pod ServiceAccount ↔ IAM role via OIDC, short-lived creds, zero static keys. #1 bug: broken OIDC trust (wrong issuer/audience).</details>

## 3. Readiness vs liveness on the ALB target group?
<details><summary>Answer</summary>Readiness gates routing/rollouts; liveness only restarts. Routing on liveness causes outage during slow-but-alive starts.</details>

## 4. Why HPA on latency AND CPU?
<details><summary>Answer</summary>Queue-bound saturation parks threads (CPU low, p99 exploding) — CPU-only HPA sleeps through it.</details>

## 5. Flyway as pre-deploy Job, not app-startup. Why?
<details><summary>Answer</summary>Concurrent pod starts race migrations; a Job migrates once, then the rollout proceeds.</details>

## 6. Aurora failover RTO + the test that proves RPO?
<details><summary>Answer</summary>~30–60 s; PITR restore drill into a new cluster with canary diff (not the console's green checkmark).</details>

## 7. MSK vs SQS/SNS decision rule?
<details><summary>Answer</summary>Replay/compaction/event-sourcing → MSK. Task distribution without broker ops → SQS/SNS.</details>

## 8. Redis AUTH token storage?
<details><summary>Answer</summary>Secrets Manager (rotatable), injected — never env-baked or in the image.</details>

## 9. Migrations must be… (deploy-safety adjective)?
<details><summary>Answer</summary>Backward-compatible, expand-then-contract — old + new code both run during rolling updates.</details>

## 10. Egress dominates API bills. Which knob matters most?
<details><summary>Answer</summary>Data-transfer architecture (caching, regional affinity, payload size) — compute is usually second.</details>
