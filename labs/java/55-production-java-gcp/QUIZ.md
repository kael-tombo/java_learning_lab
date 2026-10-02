# QUIZ — GCP

## 1. Autopilot vs Standard vs Cloud Run?
<details><summary>Answer</summary>Autopilot: managed nodes, per-pod billing. Standard: own pools, cheaper steady + Spot/ARM. Run: request-driven scale-to-zero, concurrency-tuned.</details>

## 2. Workload Identity in one line + classic mistake?
<details><summary>Answer</summary>KSA→GSA federation, zero exported keys. Mistake: code demanding a JSON key file — binding broken, not code.</details>

## 3. Concurrency 10→80 effect on instances?
<details><summary>Answer</summary>~8× fewer instances at fixed RPS — virtual threads make high concurrency safe headroom.</details>

## 4. DLQ-less subscription + poison message: outcome?
<details><summary>Answer</summary>Infinite redelivery stalling the subscription. DLQ + max attempts quarantines for autopsy.</details>

## 5. Ordering keys cost what?
<details><summary>Answer</summary>Per-key serialization ceiling — hot keys throttle. Shard or drop ordering where order is irrelevant.</details>

## 6. Auth Proxy sidecar buys what?
<details><summary>Answer</summary>App connects to localhost; proxy holds IAM auth — credentials never in app config.</details>

## 7. Burn-rate vs threshold alerts?
<details><summary>Answer</summary>Burn-rate fires on SLO-consumption speed (user pain early); thresholds fire on raw metrics (late or noisy).</details>

## 8. Push vs pull subscriptions?
<details><summary>Answer</summary>Push: HTTP endpoints (OIDC-authenticated). Pull: workers leasing/acking at their pace.</details>

## 9. minScale 0 trade?
<details><summary>Answer</summary>Zero idle cost vs cold starts — pair with native/CRaC for latency paths.</details>

## 10. Same deploy-safety rules as AWS?
<details><summary>Answer</summary>Yes: readiness gating, backward-compatible migrations (Flyway Job), previous-revision rollback, PITR drill proof.</details>
