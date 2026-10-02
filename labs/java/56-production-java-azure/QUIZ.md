# QUIZ — Azure

## 1. AKS vs Container Apps vs Functions?
<details><summary>Answer</summary>AKS (full K8s, KEDA, AGIC) / Container Apps (serverless K8s + Dapr + scale rules) / Functions (tariff-shaped events only).</details>

## 2. Federation in one line + classic mistake?
<details><summary>Answer</summary>SA↔managed-identity via cluster OIDC; short-lived tokens, nothing stored. Mistake: broken trust binding (issuer/subject), blamed on code.</details>

## 3. Sessions cost what?
<details><summary>Answer</summary>Per-session serialization ceiling — hot sessions throttle. Shard or drop sessions where order is irrelevant.</details>

## 4. DLQ-less session queue + poison message: outcome?
<details><summary>Answer</summary>Head-of-line block stalls the whole session forever. DLQ + maxDeliveryCount quarantines for autopsy.</details>

## 5. KEDA vs HPA signals?
<details><summary>Answer</summary>KEDA: event backlog (work-native). HPA: CPU/latency (compute-native). Queue-bound saturation needs KEDA.</details>

## 6. Entra DB auth buys what?
<details><summary>Answer</summary>No DB passwords at all — token-as-password via identity chain (plus Key Vault for the rest).</details>

## 7. Service Bus vs Event Hubs?
<details><summary>Answer</summary>Commands (queues/topics/sessions/DLQ/transactions) vs streams (Kafka protocol, replay, capture).</details>

## 8. Probe gates what, exactly?
<details><summary>Answer</summary>Rolling batches + App Gateway routing (readiness); restarts only (liveness). Same split, Azure tooling.</details>

## 9. Spot pools: serving path?
<details><summary>Answer</summary>Never — batch/fault-tolerant workers only. Eviction during peak erases the savings.</details>

## 10. Reservations on what baseline?
<details><summary>Answer</summary>Measured-steady only (proven utilization) — buying down hoped-for load is a donation.</details>
