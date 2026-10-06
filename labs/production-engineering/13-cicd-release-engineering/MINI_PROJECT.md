# Lab 13: CI/CD Pipelines & Release Engineering — Mini Project

## Project: `PipelineLab` — Build Once, Promote, Canary With Automated Analysis, Survive a Schema Change

**Time**: 12–16 hours | **Difficulty**: Advanced | **Stack**: Java 21, Spring Boot 3, Maven/Gradle, Docker + BuildKit, GitHub Actions, Argo Rollouts (or Flagger), Argo CD, Helm, PostgreSQL 16, kind, k6

Take one Spring Boot service through a complete release-engineering lifecycle: reproducible build, quality gates, a migration that would have caused an outage, a canary with machine analysis, and a GitOps promotion — measuring blast radius and rollback time at each step.

---

## Part 1 — The service

A Spring Boot 3 `payments-api` with:
- `POST /api/v1/payments` (money-moving → needs idempotency)
- `GET /api/v1/payments/{id}`
- `GET /api/v1/payments?customerId=&limit=` (list; the canary's load generator target)
- PostgreSQL for payments and customers

Two tables, and one deliberate design flaw in the schema:

```sql
CREATE TABLE payments (
  id            UUID PRIMARY KEY,
  customer_id   UUID NOT NULL,
  amount_cents  BIGINT NOT NULL,          -- in cents
  currency      CHAR(3) NOT NULL,
  status        VARCHAR(16) NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- 40M rows, created over a year. This is your migration target.
```

The next release needs `amount_minor` + `currency_code` instead of `amount_cents` + `currency`. Your job is to make that change with zero downtime and a working rollback.

---

## Part 2 — Reproducible build and promotion

### 2.1 Multi-stage, digest-pinned Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.7
FROM eclipse-temurin:21.0.2_13-jdk@sha256:<PINNED_DIGEST> AS build
WORKDIR /src
COPY pom.xml .
RUN --mount=type=cache,target=/root/.m2 mvn -B -q dependency:go-offline
COPY src src
RUN --mount=type=cache,target=/root/.m2 mvn -B -q -DskipTests package \
 && cp target/payments-api-*.jar /out/app.jar

FROM eclipse-temurin:21.0.2_13-jre@sha256:<PINNED_DIGEST> AS runtime
RUN useradd -r -u 10001 app
WORKDIR /app
COPY --from=build --chown=app:app /out/app.jar app.jar
USER 10001
# No configuration, no secrets, no environment baked in. Runtime only.
ENTRYPOINT ["java","-jar","/app/app.jar"]
```

### 2.2 Prove reproducibility

```bash
docker build -t lab/payments:local-a --build-arg SOURCE_DATE_EPOCH=1700000000 .
docker build -t lab/payments:local-b --build-arg SOURCE_DATE_EPOCH=1700000000 .
sha256sum local-a local-b        # images may differ in metadata; the JAR must not
unzip -p local-a app.jar > a.jar; unzip -p local-b app.jar > b.jar
sha256sum a.jar b.jar            # must be identical
```

Then verify the artifact promoted through environments is the same one the tests ran against — the pipeline prints the digest and the deploy asserts it:

```bash
test "$TESTED_DIGEST" = "$PROMOTED_DIGEST" || exit 1
```

**Deliverable**: `REPRODUCIBILITY.md` with the digests, the differences you found (timestamps, layer ordering, JDK build), and how you removed each.

---

## Part 3 — The pipeline with honest feedback latency

```yaml
name: payments-api
on:
  pull_request: { branches: [main] }
  push:        { branches: [main] }

concurrency:
  group: payments-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '21', cache: maven }
      - run: mvn -B -q verify            # unit + integration + security regression
      - id: build
        run: |
          mvn -B -q -DskipTests package
          echo "digest=$(sha256sum target/payments-api-*.jar | cut -d' ' -f1)" >> "$GITHUB_OUTPUT"

  fast-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: mvn -B -q dependency:go-offline
      - run: trivy fs --scanners vuln,secret --exit-code 1 --severity HIGH,CRITICAL .
      - run: semgrep ci --config=p/java --config=p/spring --error
      - run: mvn -B -q spotless:check

  post-merge:                 # NOT developer-blocking
    runs-on: ubuntu-latest
    needs: [build, fast-gates]
    steps:
      - run: mvn -B -q verify -Pload-test        # k6 against a stub
      - uses: aquasecurity/trivy-action
        with: { image-ref: 'lab/payments', severity: 'CRITICAL,HIGH', ignore-unfixed: true }
      - run: oasdiff breaking origin/main:openapi.yaml openapi.yaml --fail-on-ERR
```

Measure every stage:

```bash
# per-stage wall time and queue wait
gh run list --json databaseId,conclusion,createdAt,updatedAt | jq -r '.[] | "\(.databaseId) \(.updatedAt)"'
# then per-job timings from the API
gh api /repos/$REPO/actions/runs/$ID/jobs --jq '.jobs[] | "\(.name) \(.started_at) \(.completed_at)"'
```

Record a table of pre-merge feedback vs total pipeline time, before and after your change. Note how many PRs bypassed CI before (ask).

**Deliverable**: `PIPELINE_TIMING.md` — stage durations, queue waits, the reordering, and the resulting feedback latency with the calculation.

---

## Part 4 — The migration (Part 4 is where the outage would have happened)

### 4.1 The naive migration (do this first, to see it break)

```sql
ALTER TABLE payments RENAME COLUMN amount_cents TO amount_minor;
ALTER TABLE payments RENAME COLUMN currency TO currency_code;
```

Deploy and watch: the previous version (still serving on some pods) fails with `column "amount_cents" does not exist`. Rollback is impossible without reverting the migration, which races with traffic.

### 4.2 Expand-contract, done properly

**Release A** — expand only, both code paths work:

```sql
-- migration V1__expand.sql   (every statement carries a lock_timeout)
SET lock_timeout = '2s';
SET statement_timeout = '30s';

ALTER TABLE payments ADD COLUMN amount_minor BIGINT;        -- nullable, metadata-only
ALTER TABLE payments ADD COLUMN currency_code CHAR(3);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_amount_minor ON payments (amount_minor);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_customer_created
  ON payments (customer_id, created_at DESC);
```

```java
// Dual-write. Reads still use the OLD columns so rollback stays valid.
@Modifying
@Query(value = """
    INSERT INTO payments (id, customer_id, amount_cents, amount_minor, currency, currency_code, status)
    VALUES (:id, :customerId, :cents, :minor, :currency, :currencyCode, :status)
    """, nativeQuery = true)
int insertDual(@Param("id") UUID id, @Param("customerId") UUID customerId,
               @Param("cents") long cents, @Param("minor") long minor,
               @Param("currency") String currency, @Param("currencyCode") String code,
               @Param("status") String status);
```

**Backfill**, batched, outside the release:

```java
@Scheduled(fixedDelayString = "${backfill.delay-ms:500}")
@Transactional
public void backfillBatch() {
    List<UUID> ids = jdbc.queryForList(
        "SELECT id FROM payments WHERE amount_minor IS NULL AND id > :last ORDER BY id LIMIT 1000",
        UUID.class, Map.of("last", lastId));
    if (ids.isEmpty()) { done = true; return; }
    jdbc.update("UPDATE payments SET amount_minor = amount_cents, currency_code = currency " +
                "WHERE id = ANY(?) AND amount_minor IS NULL", ids.toArray(new UUID[0]));
    lastId = ids.getLast();
}
```

**Release B** — switch reads:

```java
@Query("select new PaymentView(p.id, p.amountMinor, p.currencyCode) from Payment p where p.customerId = :cid")
```
Keep the dual-write for one more release so rollback to Release A is still valid.

**Release C** — drop (only after the rollback window, ≥ 30 days later):

```sql
SET lock_timeout = '2s';
ALTER TABLE payments DROP COLUMN amount_cents;      -- instant metadata-only drop
ALTER TABLE payments DROP COLUMN currency;
DROP INDEX CONCURRENTLY IF EXISTS idx_payments_status;
```

### 4.3 Verify under load

```bash
k6 run -e DURATION=10m -e RATE=4000 list.js &     # sustained write+read load
psql -c "SET lock_timeout='2s'; ALTER TABLE payments ADD COLUMN scratch text;"
# observe: fails in 2s, or queues behind your lock and stalls the app
```

Measure lock hold time for every statement, and the p99 impact during each migration step.

**Deliverable**: `MIGRATION_REPORT.md` with the full expand-contract timeline (days), the lock measurements, the backfill rate and duration, the rollback-validity table (which release can be redeployed when), and the naive-migration failure reproduction.

---

## Part 5 — Canary with machine analysis

Argo Rollouts (`rollout.yaml`):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata: { name: payments-api }
spec:
  replicas: 20
  strategy:
    canary:
      canaryService: payments-api-canary
      stableService: payments-api-stable
      trafficRouting:
        istio: { virtualService: { name: payments-api, routes: [ { primaryService: payments-api-stable, canaryService: payments-api-canary, trafficRouting: istio } ] } }
      analysis:
        templates:
        - templateName: slo-gate
        startingStep: 2
        args:
        - name: service-name
          value: payments-api
      steps:
      - setWeight: 1
      - pause: { duration: 60s }
      - setWeight: 5
      - pause: { duration: 300s }          # sized by the sample-size calculation
      - setWeight: 25
      - pause: { duration: 300s }
      - setWeight: 50
      - pause: { duration: 180s }
      - setWeight: 100
  template:
    spec:
      containers:
      - name: payments-api
        image: lab/payments@sha256:<DIGEST>     # digest, never a tag
        resources: { requests: { cpu: "1", memory: "1Gi" }, limits: { cpu: "1", memory: "1Gi" } }
```

The analysis template is the part that matters — it is a *pre-declared* decision rule:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata: { name: slo-gate }
spec:
  args: [{ name: service-name }]
  metrics:
  - name: error-rate
    interval: 30s
    count: 4
    failureLimit: 1
    successCondition: result[0] >= 0
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(http_server_requests_seconds_count{job="{{args.service-name}}-canary",status=~"5.."}[2m]))
          / sum(rate(http_server_requests_seconds_count{job="{{args.service-name}}-canary"}[2m]))
  - name: latency-p99
    interval: 30s
    count: 4
    failureLimit: 1
    successCondition: result[0] < 0.35
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          histogram_quantile(0.99,
            sum by (le) (rate(http_server_duration_seconds_bucket{job="{{args.service-name}}-canary"}[2m])))
  - name: saturation
    interval: 30s
    count: 2
    failureLimit: 1
    successCondition: result[0] < 0.2
    provider:
      prometheus:
        address: http://prometheus:30900
        query: |
          rate(container_cpu_cfs_throttled_seconds_total{container="payments-api-canary"}[2m])
```

Then run three experiments:

| Experiment | Change | Expected |
|---|---|---|
| Good release | bug fix | promotes 1 → 5 → 25 → 50 → 100% |
| Error regression | throw on 3% of requests | error-rate metric fails; automatic rollback at 5% |
| Latency regression | add a 300 ms `Thread.sleep` | p99 metric fails; automatic rollback at 25% |
| Saturation regression | set `-Xmx64m` | throttling metric fails |

Record, for each: time to first failure detection, the weight at which it was caught, total traffic affected, and the rollback duration.

**Deliverable**: `CANARY_REPORT.md` with the four experiment tables and the statement of which metric caught which class of regression.

---

## Part 6 — GitOps promotion and drift

```yaml
# ApplicationSet: promotes a promoted tag to a digest-pinned manifest
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: { name: payments }
spec:
  generators:
  - git:
      repoURL: https://github.com/acme/gitops
      revision: main
      files: [{ path: 'apps/payments/env/prod/release.yaml' }]   # written by the promotion job
  template:
    metadata: { name: payments-prod }
    spec:
      project: prod
      source:
        repoURL: https://github.com/acme/gitops
        targetRevision: main
        path: apps/payments/env/prod
        helm: { valuesFiles: [values-prod.yaml] }
      destination: { server: https://kubernetes.default.svc, namespace: prod }
      syncPolicy:
        automated: { prune: true, selfHeal: true }
        syncOptions: [CreateNamespace=true]
```

```yaml
# apps/payments/env/prod/release.yaml — written by CI after promotion
image:
  repository: registry.example.com/payments-api
  digest: sha256:9f2c...          # digest, so Git is the record of exactly what runs
```

Secrets by reference, never by value:

```yaml
# ExternalSecret
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: payments-db }
spec:
  refreshInterval: 1h
  secretStoreRef: { name: vault, kind: ClusterSecretStore }
  target: { name: payments-db, creationPolicy: Owner }
  data:
  - secretKey: password
    remoteRef: { key: prod/payments/db, property: password }
```

Now demonstrate drift detection:

```bash
kubectl -n prod scale deploy payments-api --replicas=3      # manual change
kubectl -n prod set image deploy/payments-api payments-api=somebody/debug:latest
kubectl -n prod get deploy payments-api -w                  # selfHeal reverts within syncInterval
```

**Deliverable**: `GITOPS_REPORT.md` — the promotion flow, the drift detection demonstration with timings, the secret reference design, and the audit trail (who changed what, and Git as the record).

---

## Part 7 — CI gates for release safety

```bash
#!/usr/bin/env bash
# ./check-release-safety.sh values-prod.yaml Dockerfile
set -euo pipefail
V=$1; D=$2; fail=0
check() { if eval "$2"; then echo "FAIL: $1"; fail=1; else echo "ok:   $1"; fi; }

# 1. Image pinned by digest, not tag
grep -qE 'image:.*:[0-9]+\.[0-9]+' "$V" && check "image uses a mutable tag" true || echo "ok:   image uses a digest"

# 2. No configuration or secrets baked into the image
grep -qE '^ENV (SPRING_|DB_|API_KEY)' "$D" && check "ENV config baked into image" true

# 3. Every migration sets a lock_timeout
grep -rL 'lock_timeout' db/migration/*.sql | while read -r f; do echo "FAIL: $f has no lock_timeout"; fail=1; done

# 4. No destructive DDL in a release that still reads the column
grep -rE 'DROP COLUMN' db/migration/*.sql && \
  grep -rqE 'amount_cents' src/main/java && \
  check "DROP COLUMN while code still references the old column" true

# 5. A canary analysis template exists and gates on error rate AND latency
test -f analysis/slo-gate.yaml && \
  grep -q 'status=~"5\.\."' analysis/slo-gate.yaml && \
  grep -q 'histogram_quantile(0.99' analysis/slo-gate.yaml

exit $fail
```

**Acceptance**: five deliberately bad PRs (mutable tag, `ENV SPRING_DATASOURCE_PASSWORD` in the Dockerfile, a migration without `lock_timeout`, a `DROP COLUMN` alongside old code, a canary that only checks error rate) each fail with a specific message.

---

## Acceptance Criteria

- [ ] `REPRODUCIBILITY.md` proves two clean builds yield the same artifact digest, with each removed source of nondeterminism named.
- [ ] `PIPELINE_TIMING.md` shows pre-merge feedback under 10 minutes with stage and queue timings, and no CI bypasses.
- [ ] `MIGRATION_REPORT.md`: the naive rename fails and is documented; expand-contract succeeds; lock hold times measured under load; `lock_timeout` demonstrated to fail fast; backfill rate and duration computed.
- [ ] A rollback-validity table proving every release in the migration sequence can be redeployed until the drop.
- [ ] `CANARY_REPORT.md`: four experiments (good, error, latency, saturation) with detection time, caught weight, traffic affected, and rollback duration.
- [ ] `GITOPS_REPORT.md`: promotion by digest, secret references, drift detection demonstrated with timing, and Git as the audit record.
- [ ] CI release-safety gates block all five bad PRs.

---

## Stretch

- Implement a Flagger/Argo analysis that also gates on a *business* SLI (payment success rate), not just HTTP metrics.
- Add automatic pipeline generation for a new service from a platform template and measure time-to-first-deploy.
- Build a "release risk score" that combines blast radius, detection window, rollback availability, and migration safety into a single gate.
- Run a game day: deploy a deliberately bad release during business hours with the on-call watching, and measure their actual time-to-detect versus the machine's.
