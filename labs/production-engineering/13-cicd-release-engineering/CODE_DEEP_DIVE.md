# CODE DEEP DIVE: Release Engineering Patterns
## Lab 13 | Production Engineering Academy

---

## Pattern 1: Production Argo Rollouts Automated Canary with Prometheus Analysis

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: payment-service-rollout
spec:
  replicas: 20
  strategy:
    canary:
      # Automatically evaluate Prometheus metrics at each step
      analysis:
        templates:
          - templateName: success-rate-and-latency-analysis
        args:
          - name: service-name
            value: payment-service
      steps:
        # Step 1: Route 5% traffic to Canary pods; pause 10 minutes for metric evaluation
        - setWeight: 5
        - pause: { duration: 10m }
        # Step 2: Route 20% traffic to Canary; pause 15 minutes
        - setWeight: 20
        - pause: { duration: 15m }
        # Step 3: Route 50% traffic
        - setWeight: 50
        - pause: { duration: 10m }
        # Step 4: Promote to 100%
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate-and-latency-analysis
spec:
  metrics:
    - name: success-rate
      interval: 1m
      # Abort deployment and trigger automated rollback if error rate > 0.5%
      failureLimit: 2
      successCondition: result[0] >= 0.995
      provider:
        prometheus:
          address: http://prometheus-k8s.monitoring:9090
          query: |
            sum(rate(http_server_requests_seconds_count{app="payment-service",status!~"5..",rollout_type="canary"}[2m]))
            /
            sum(rate(http_server_requests_seconds_count{app="payment-service",rollout_type="canary"}[2m]))
    - name: p99-latency
      interval: 1m
      failureLimit: 2
      successCondition: result[0] <= 0.200 # Max 200ms p99 latency
      provider:
        prometheus:
          address: http://prometheus-k8s.monitoring:9090
          query: |
            histogram_quantile(0.99, sum(rate(http_server_requests_seconds_bucket{app="payment-service",rollout_type="canary"}[2m])) by (le))
```

---

## Pattern 2: Zero-Downtime Multi-Phase Liquibase Migration

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
    http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd">

    <!-- Phase 1: EXPAND (Add new column as nullable - Safe for running v1 code) -->
    <changeSet id="2026-09-30-01-add-contact-number" author="architect">
        <addColumn tableName="users">
            <column name="contact_number" type="VARCHAR(32)">
                <constraints nullable="true" />
            </column>
        </addColumn>
    </changeSet>

    <!-- Phase 2: Add non-blocking index in PostgreSQL -->
    <changeSet id="2026-09-30-02-index-contact-number" author="architect">
        <sql dbms="postgresql">
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_contact_number ON users(contact_number);
        </sql>
    </changeSet>

    <!-- Phase 3 (Run after code v2 is reading new column): CONTRACT / DROP OLD COLUMN -->
    <!-- This changeset is deployed in a separate release 2 weeks later -->
    <!--
    <changeSet id="2026-10-15-01-drop-legacy-phone" author="architect">
        <dropColumn tableName="users" columnName="phone_number" />
    </changeSet>
    -->
</databaseChangeLog>
```
