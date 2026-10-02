# EXERCISES — Azure

## 1. Federated proof (beginner)
From a debug pod with zero credential env vars, read one Key Vault secret
via DefaultAzureCredential. Break the federated trust (wrong subject),
record the exact error, restore. *Why is this safer than a stored client
secret in two concrete scenarios?*

## 2. Probe-gated rollout (beginner)
Black-hole the DB readiness dependency; roll; show App Gateway keeping old
pods + new pods Unhealthy. Fix; watch the batch flip. Same lesson as
AWS/GCP — write the one paragraph that is Azure-specific (probe config).

## 3. PITR drill (intermediate)
Canary rows → delete → point-in-time restore to a *new* Flexible Server →
diff. Record RPO vs ≤5 min claim. Document runbook steps verbatim.

## 4. DLQ + sessions drill (intermediate)
Publish 10 poison messages to a session-enabled queue (no DLQ first):
watch head-of-line blocking stall the session. Add DLQ +
maxDeliveryCount=5, replay, confirm quarantine + flow resume. Then measure
per-session throughput ceiling with one hot session vs sharded sessions.

## 5. KEDA vs HPA shootout (advanced)
Backlog-spike the worker queue under (a) CPU-HPA only, (b) KEDA queue-
length scaling. Plot backlog drain time + cost for both. Derive the
messageCount threshold from your drain-time SLO.
