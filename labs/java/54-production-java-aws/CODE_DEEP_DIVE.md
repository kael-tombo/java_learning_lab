# CODE_DEEP_DIVE — AWS wiring

## 1. IRSA ServiceAccount (no static keys)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: catalog-api
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/catalog-api
```

Pod env (`AWS_ROLE_ARN` + web-identity token) is injected automatically;
AWS SDKs assume the role with short-lived credentials. Verify with
`aws sts get-caller-identity` from a debug pod — if it shows the role,
IRSA works; if it shows a node role or fails, the OIDC binding is wrong
(the #1 EKS identity bug).

## 2. DataSource from Secrets Manager (rotation-safe)

```yaml
# application-aws.yml — values resolved at deploy from Secrets Manager
spring:
  datasource:
    url: ${DB_URL}          # jdbc:postgresql://<writer-endpoint>:5432/catalog
    username: ${DB_USER}
    password: ${DB_PASSWORD}
  data:
    redis:
      host: ${REDIS_HOST}
      password: ${REDIS_AUTH}
      ssl:
        enabled: true
```

Secrets land as env (or mounted files for rotation without restart).
Flyway runs as a pre-deploy Job (`migrate` then app rollout) — never
inside app startup (concurrent pod starts would race migrations).

## 3. HPA on latency + CPU (not CPU alone)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: catalog-api
spec:
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_server_requests_seconds  # Micrometer → CloudWatch
      target:
        type: AverageValue
        averageValue: 300m                  # p99 budget proxy
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

CPU-only HPA misses queue-bound saturation (threads parked, CPU low,
latency exploding) — the latency metric catches it. Three replicas
minimum spans three AZs.

## 4. ALB health gating (readiness, not liveness)

Target group health check: `GET /actuator/health/readiness`, healthy
threshold 2 × 15 s, unhealthy 2 × 5 s. Rolling update (maxUnavailable 0,
maxSurge 1) + readiness gate = zero-downtime deploys; liveness is for
restarts only, never routing.
