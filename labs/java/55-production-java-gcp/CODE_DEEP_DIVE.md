# CODE_DEEP_DIVE — GCP wiring

## 1. Workload Identity binding (no JSON keys)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: catalog-api
  annotations:
    iam.gke.io/gcp-service-account: catalog-api@PROJECT.iam.gserviceaccount.com
```

GSA needs `roles/iam.workloadIdentityUser` bound to the KSA. Verify from a
debug pod: GCP SDK calls succeed with *no* `GOOGLE_APPLICATION_CREDENTIALS`
set — if code demands a key file, the binding (not the code) is broken
(the GCP twin of the AWS OIDC bug).

## 2. DataSource + Redis via Secret Manager

```yaml
# application-gcp.yml
spring:
  datasource:
    url: ${DB_URL}        # AlloyDB/Cloud SQL via Auth Proxy: jdbc:postgresql://localhost:5432/catalog
    username: ${DB_USER}
    password: ${DB_PASSWORD}   # Secret Manager → env/volume
  data:
    redis:
      host: ${REDIS_HOST}
      password: ${REDIS_AUTH}
      ssl:
        enabled: true
```

Auth Proxy sidecar pattern: app connects to localhost, proxy holds IAM
auth to the instance — credentials never touch app config. Flyway as a
pre-deploy Job (same race argument as AWS).

## 3. Pub/Sub subscription shapes

```java
// Pull (workers): lease + ack deadline; ordering key per aggregate
// Push (HTTP endpoints): OIDC-token authenticated push to readiness-gated service
// DLQ: deadLetterPolicy { deadLetterTopic, maxDeliveryAttempts: 5 }
```

Ordering keys serialize per key (throughput cap per key — shard hot keys
or drop ordering). DLQ topics are mandatory in production configs —
without one, poison messages retry forever and stall partitions.

## 4. Cloud Run concurrency (spiky slice)

```yaml
# service.yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "50"
    spec:
      containerConcurrency: 80   # virtual threads love high concurrency
      containers:
      - image: REGION-docker.pkg.dev/PROJECT/catalog/api:TAG
```

Concurrency ≈ per-instance in-flight requests; virtual threads push it
high safely. minScale 0 = scale-to-zero savings *and* cold starts —
pair with native/CRaC artifacts for latency-sensitive paths.
