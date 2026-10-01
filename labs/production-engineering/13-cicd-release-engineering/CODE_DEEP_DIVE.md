# CODE DEEP DIVE: Release Engineering, Canary & GitOps Patterns
## Lab 13 | Production Engineering Academy — Top 0.0001% Engineering

---

## Pattern 1: Argo Rollouts Canary with Prometheus Automated Metric Analysis

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: payment-service-rollout
  namespace: production
spec:
  replicas: 10
  strategy:
    canary:
      # Step-based progressive traffic routing via service meshes or ingress
      steps:
        - setWeight: 5
        - pause: { duration: 15m }  # Evaluate canary at 5% for 15 minutes
        - analysis:
            templates:
              - templateName: canary-health-metrics
        - setWeight: 25
        - pause: { duration: 15m }
        - analysis:
            templates:
              - templateName: canary-health-metrics
        - setWeight: 50
        - pause: { duration: 10m }
  template:
    metadata:
      labels:
        app: payment-service
    spec:
      containers:
        - name: payment-service
          image: registry.corp.internal/payments/service:3.4.0@sha256:7f9a8b1c4e2d3f...
          resources:
            requests:
              cpu: "1000m"
              memory: "4Gi"
            limits:
              memory: "4Gi"
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: canary-health-metrics
  namespace: production
spec:
  metrics:
    # Metric 1: HTTP 5xx Error Rate must remain < 0.2%
    - name: error-rate
      interval: 1m
      successCondition: result[0] <= 0.002
      failureLimit: 3 # Abort and roll back if condition fails 3 times
      provider:
        prometheus:
          address: http://prometheus-k8s.monitoring.svc:9090
          query: >-
            sum(rate(http_requests_total{app="payment-service", status=~"5.*", rollouts_pod_template_hash="canary"}[2m]))
            /
            sum(rate(http_requests_total{app="payment-service", rollouts_pod_template_hash="canary"}[2m]))

    # Metric 2: P99 Latency must remain < 50ms
    - name: p99-latency
      interval: 1m
      successCondition: result[0] <= 0.050
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus-k8s.monitoring.svc:9090
          query: >-
            histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{app="payment-service", rollouts_pod_template_hash="canary"}[2m])) by (le))
```

---

## Pattern 2: ArgoCD PreSync Database Migration Job Hook

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration-v3-4-0
  namespace: production
  annotations:
    # ArgoCD executes this Job BEFORE applying the updated Rollout manifest:
    argocd.argoproj.io/hook: PreSync
    # Automatically cleans up successful jobs to prevent clutter:
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  backoffLimit: 0 # Fail fast; do not retry failed migrations automatically!
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: flyway-migrator
          image: registry.corp.internal/platform/flyway-migrator:10.8.0
          env:
            - name: FLYWAY_URL
              value: "jdbc:postgresql://postgres-ha.database.svc:5432/payments"
            - name: FLYWAY_USER
              valueFrom:
                secretKeyRef:
                  name: db-migration-credentials
                  key: username
            - name: FLYWAY_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-migration-credentials
                  key: password
            - name: FLYWAY_LOCATIONS
              value: "classpath:db/migration"
          resources:
            requests:
              cpu: "500m"
              memory: "1Gi"
            limits:
              memory: "1Gi"
```

---

## Pattern 3: Hermetic Multi-Stage Dockerfile for Java 21 on Distroless

```dockerfile
# ------------------------------------------------------------------------------
# Stage 1: Hermetic Builder with Pinned Gradle/Maven Checksums
# ------------------------------------------------------------------------------
FROM eclipse-temurin:21-jdk-jammy AS builder
WORKDIR /workspace

# Cache dependencies hermetically
COPY pom.xml mvnw ./
COPY .mvn .mvn
RUN ./mvnw dependency:go-offline -B

# Compile and package application
COPY src src
RUN ./mvnw package -DskipTests -B

# Extract Spring Boot layered JAR for optimal Docker layer caching
RUN java -Djarmode=layertools -jar target/*.jar extract

# ------------------------------------------------------------------------------
# Stage 2: Hardened, Minimal Non-Root Runtime Container (Distroless)
# ------------------------------------------------------------------------------
FROM gcr.io/distroless/java21-debian12:nonroot
WORKDIR /app

# Run strictly as non-root user (UID 65532)
USER 65532:65532

# Copy layers in order of change frequency (dependencies change least often)
COPY --from=builder --chown=65532:65532 /workspace/dependencies/ ./
COPY --from=builder --chown=65532:65532 /workspace/spring-boot-loader/ ./
COPY --from=builder --chown=65532:65532 /workspace/snapshot-dependencies/ ./
COPY --from=builder --chown=65532:65532 /workspace/application/ ./

# High-Performance Containerized JVM Flags
ENV JAVA_TOOL_OPTIONS="\
  -XX:+UseContainerSupport \
  -XX:MaxRAMPercentage=75.0 \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=150 \
  -XX:+ExitOnOutOfMemoryError \
  -Dnetworkaddress.cache.ttl=5 \
  -Djava.security.egd=file:/dev/urandom"

EXPOSE 8080
ENTRYPOINT ["java", "org.springframework.boot.loader.launch.JarLauncher"]
```

---

## Pattern 4: Java Expand-Contract Dual-Write Repository Implementation

```java
package com.learning.production.lab13;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

/**
 * Implements Phase 2 (Dual-Write) and Phase 4 (Read New) of the Expand-Contract pattern.
 * Safely migrates schema from 'legacy_phone' to 'e164_mobile_number' with zero downtime.
 */
@Repository
public class ExpandContractUserRepository {

    private static final Logger log = LoggerFactory.getLogger(ExpandContractUserRepository.class);

    private final JdbcTemplate jdbcTemplate;
    private final FeatureFlagService featureFlagService;

    public ExpandContractUserRepository(JdbcTemplate jdbcTemplate, FeatureFlagService featureFlagService) {
        this.jdbcTemplate = jdbcTemplate;
        this.featureFlagService = featureFlagService;
    }

    /**
     * DUAL-WRITE: Always writes to BOTH columns during Phase 2, 3, and 4.
     */
    @Transactional
    public void updateUserPhone(long userId, String rawPhone, String formattedE164Phone) {
        // Writes to both legacy and new columns simultaneously:
        String sql = """
            UPDATE users 
            SET legacy_phone = ?, 
                e164_mobile_number = ?,
                updated_at = NOW() 
            WHERE id = ?
        """;
        jdbcTemplate.update(sql, rawPhone, formattedE164Phone, userId);
    }

    /**
     * DYNAMIC READ SWITCH: Controls whether reads come from legacy or new schema via Feature Flag.
     */
    public String getUserPhone(long userId) {
        if (featureFlagService.isEnabled("read-from-new-mobile-schema", userId)) {
            // Phase 4: Read from new schema
            String sql = "SELECT e164_mobile_number FROM users WHERE id = ?";
            String phone = jdbcTemplate.queryForObject(sql, String.class, userId);
            if (phone != null) return phone;
            log.warn("Fallback to legacy phone for user {}: new column was NULL", userId);
        }

        // Phase 1, 2, 3: Read from legacy schema
        String legacySql = "SELECT legacy_phone FROM users WHERE id = ?";
        return jdbcTemplate.queryForObject(legacySql, String.class, userId);
    }
}
```

---

## Pattern 5: GitHub Actions Multi-Arch CI Pipeline with Cosign Cryptographic Signing

```yaml
name: Production CI/CD Pipeline

on:
  push:
    branches: [main]

permissions:
  contents: read
  id-token: write # Required for keyless OIDC Cosign signing
  packages: write

jobs:
  build-and-sign:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: 'maven'

      - name: Verify Dependencies & Compile
        run: mvn clean verify -B

      - name: Install Cosign (Sigstore)
        uses: sigstore/cosign-installer@v3.5.0

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push Multi-Arch Image
        id: build-push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}

      - name: Cryptographically Sign Container Image via Cosign (Keyless)
        run: |
          cosign sign --yes \
            ghcr.io/${{ github.repository }}@${{ steps.build-push.outputs.digest }}
```
