# CODE_DEEP_DIVE — Azure wiring

## 1. Workload identity federation (no secrets)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: catalog-api
  annotations:
    azure.workload.identity/client-id: <MANAGED-IDENTITY-CLIENT-ID>
  labels:
    azure.workload.identity/use: "true"
```

Federated credential on the managed identity trusts the cluster OIDC
issuer for this ServiceAccount. SDKs (DefaultAzureCredential chain)
pick up the token automatically — verify by listing Key Vault secrets
from a debug pod with *no* env credentials set. Failure mode is always
the trust binding (issuer/subject mismatch), never application code.

## 2. DataSource + Redis via Key Vault references

```yaml
# application-azure.yml
spring:
  datasource:
    url: ${DB_URL}        # flexibleserver.postgres.database.azure.com:5432/catalog?sslmode=require
    username: ${DB_USER}   # Entra principal or vaulted user
    password: ${DB_PASSWORD}  # Key Vault reference (CSI volume or env)
  data:
    redis:
      host: ${REDIS_HOST}
      password: ${REDIS_KEY}   # Key Vault; TLS enforced
      ssl:
        enabled: true
```

Entra-authenticated Postgres removes passwords entirely where supported
(token-as-password via the identity chain). Flyway as pre-deploy Job —
same anti-race argument as ever.

## 3. Service Bus topology (commands) + DLQ

```java
// Queue per command type; sessions where ordering per aggregate matters;
// duplicate detection window for at-least-once publishers;
// forwardDeadLetteredMessagesToError / maxDeliveryCount: 5 → DLQ
```

Sessions serialize per session-id (same hotspot math as Pub/Sub ordering
keys — shard or drop). DLQ + `maxDeliveryCount` is mandatory config, not
optional hygiene — review it in every PR touching topology.

## 4. KEDA event-driven scaling (beyond CPU)

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: catalog-worker
spec:
  minReplicaCount: 2
  maxReplicaCount: 30
  triggers:
  - type: azure-servicebus
    metadata:
      queueName: orders
      messageCount: "50"     # scale when backlog exceeds 50/consumer
```

Queue-length scaling reacts to *work*, not CPU — the backpressure-native
signal. Pair with the latency HPA on the API pods; the two cover
compute-bound and queue-bound saturation respectively.
