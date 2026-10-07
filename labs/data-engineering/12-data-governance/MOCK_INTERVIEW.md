# Mock Interview: Data Governance (12-data-governance)

## Scenario: Implement data governance for a data mesh
Your large enterprise is adopting a data mesh architecture. 5 domain teams (marketing, finance, product, sales, engineering) own their data products. You need governance.

### Time: 45 minutes | Difficulty: Hard

---

## Part 1: Governance Model (15 min)

**Federated governance model:**

```
Data Governance Council (Central)
├── Data standards: naming conventions, data types, format standards
├── Security policies: access control framework, encryption requirements
├── Compliance: GDPR/CCPA/SOX policies, audit requirements
├── Data catalog: metadata schema, quality standards
└── Tooling: shared catalog, lineage, quality platform

Domain Teams (Federated)
├── Marketing domain: customer 360, campaign analytics, lead scoring
├── Finance domain: revenue, expenses, budgets, forecasts
├── Product domain: feature usage, A/B tests, product metrics
├── Sales domain: pipeline, deals, forecasts, territories
└── Engineering domain: infrastructure metrics, logs, deployments
```

**Key principles:**
1. Domains own their data (create, maintain, govern)
2. Domain publishes data products (not raw tables)
3. Central team provides shared platform and standards
4. Cross-domain data access via data contracts
5. Global policies (PII, retention) enforced by platform, implemented by domains

**Roles and responsibilities:**
| Role | Responsibility | Central or Domain |
|------|---------------|-------------------|
| Data Product Owner | Defines data product, SLA, quality | Domain |
| Data Steward | Day-to-day data quality, metadata, access | Domain |
| Data Engineer | Builds and maintains data pipelines | Domain |
| Data Architect | Cross-domain schema design, integration | Central |
| Governance Lead | Policy, compliance, audit | Central |
| Platform Engineer | Shared tools (catalog, lineage, quality) | Central |

---

## Part 2: Data Catalog (10 min)

**Metadata schema for the catalog:**

```yaml
data_product:
  id: marketing.customer_360_v2
  display_name: "Customer 360 (Marketing)"
  domain: marketing
  owner: marketing-data-team@company.com
  version: 2.1.0
  description: "Unified customer profile from CRM, web, and support data"
  
  schema:
    tables:
      - name: dim_customer
        columns:
          - name: customer_id
            type: STRING
            description: "Unique customer identifier"
            pii: true
            classification: "direct_identifier"
          - name: email
            type: STRING
            pii: true
            classification: "direct_identifier"
            masked: true
          - name: segment
            type: STRING
            description: "Marketing segment (e.g., 'premium', 'standard')"
            pii: false
    
  lineage:
    sources:
      - type: postgres
        table: sales.customers
      - type: s3
        path: s3://raw-web/events/dt=2024-01-01/
    transforms:
      - tool: dbt
        model: dim_customer
        code: (link removed)
    destinations:
      - type: snowflake
        table: marketing_analytics.dim_customer
      - type: kafka
        topic: marketing.customer_updated
  
  quality:
    freshness_sla_hours: 4
    row_count_range: [1000000, 1500000]
    tests:
      - name: not_null_customer_id
        type: not_null
        pass_rate: 99.9%
      - name: unique_customer_id
        type: unique
        pass_rate: 99.99%
  
  sla:
    availability: "99.5%"
    max_lag_hours: 4
    support_hours: "9 AM - 6 PM EST"
    escalation: "marketing-data-oncall@company.com"
  
  access:
    owner: "marketing-data-team"
    readers:
      - team: analytics
        access: read
      - team: datascience
        access: read
      - team: sales
        access: read_columns: [customer_id, segment]
          masked_columns: [email]
```

---

## Part 3: Data Contracts & Access Control (10 min)

**Data contract template:**

```yaml
data_contract:
  version: 1.0.0
  contract_id: "DC-2024-015"
  status: ACTIVE  # ACTIVE, DEPRECATED, ARCHIVED
  
  provider:
    domain: marketing
    team: marketing-data-team
    contact: marketing-data@company.com
  
  consumer:
    domain: sales
    team: sales-analytics
    contact: sales-analytics@company.com
  
  dataset: marketing.customer_360_v2.dim_customer
  
  schema:
    version: 2.1.0
    compatibility: BACKWARD
    columns:
      - name: customer_id
        type: STRING
        nullable: false
        description: "Customer ID (canonical from Salesforce)"
      - name: segment
        type: STRING
        nullable: true
      - name: lifetime_value
        type: DECIMAL(18,2)
        nullable: true
  
  slas:
    availability: 99.5%
    freshness: 4 hours
    max_lag: 6 hours
  
  quality:
    - metric: row_count
      min: 1000000
      max: 1500000
    - metric: null_rate
      column: segment
      max_pct: 5
  
  change_management:
    notification: "2 weeks before breaking changes"
    breaking_change_definition: "Column drop, type change, NULL to NOT NULL"
    approval: "Both parties must approve"
  
  termination:
    notice_period: "30 days"
    data_retention: "Provider retains data for 90 days after termination"
```

**RBAC model for data mesh:**
| Role | Access Level | Scope |
|------|-------------|-------|
| Data Product Owner | Full admin | Own domain only |
| Domain Engineer | Write, read own, read some cross-domain | Own domain |
| Domain Analyst | Read own domain data products | Own domain |
| Cross-domain Analyst | Read specific cross-domain data products | Authorized domains |
| Data Scientist | Read cross-domain (anonymized) | Authorized via contract |
| Auditor | Read-only metadata, lineage, access logs | All |
| External | No direct access | N/A |

---

## Part 4: Compliance & Measurement (10 min)

**GDPR/CCPA deletion workflow:**

```
User deletion request received → Data Governance team → Initiate deletion workflow

1. Find user data across all domains (data catalog search by user_id)
2. For each dataset containing user data:
   a. If direct identifier: delete row (hard delete)
   b. If indirect identifier: anonymize (hash user_id)
   c. If aggregate: no action (no individual data)
3. Verify deletion: query to confirm user_id returns 0 rows
4. Log deletion: deletion_id, user_id, timestamp, datasets affected
5. Notify user: confirmation within 30 days (GDPR) or 45 days (CCPA)

Deletion methods per storage:
- Snowflake: DELETE FROM table WHERE user_id = ?
- S3: Rewrite Parquet files excluding user data
- Kafka: Compact by user_id key, delete tombstone
- Redshift: DELETE (VACUUM later for space reclamation)
```

**PII auto-classification:**
```python
# Auto-classify columns using metadata + sampling
def classify_columns(table_schema, sample_data):
    classifications = []
    for column in table_schema.columns:
        score = 0
        # Name-based heuristic
        if any(kw in column.name.lower() for kw in ['email', 'ssn', 'phone', 'ssn']):
            score += 0.5
        # Value-based heuristic (sample 1000 rows)
        sample = sample_data[column.name]
        if column.name.lower() == 'email':
            if all('@' in str(v) for v in sample if v):
                score += 0.5
        if column.name.lower() in ['ssn', 'social_security']:
            if all(len(str(v)) == 11 for v in sample if v):
                score += 0.5
        # Classify
        if score >= 0.8:
            classifications.append((column.name, 'DIRECT_IDENTIFIER', 'HIGH'))
        elif score >= 0.3:
            classifications.append((column.name, 'QUASI_IDENTIFIER', 'MEDIUM'))
        else:
            classifications.append((column.name, 'NON_PII', 'LOW'))
    return classifications
```

**Measuring data trust and adoption:**
| Metric | How to Measure | Target |
|--------|---------------|--------|
| Data catalog coverage | % of datasets with complete metadata | > 90% |
| Data quality score | Average pass rate across all quality checks | > 95% |
| Data product adoption | % of domains publishing data products | > 80% |
| Cross-domain usage | % of datasets accessed by >1 domain | > 30% |
| Time to discovery | Average time to find a dataset | < 2 minutes |
| Data incidents/month | P1 + P2 data quality incidents | < 2 |
| Contract compliance | % of data contracts meeting SLAs | > 99% |

---

## Follow-up Questions

**Data lineage tracking with OpenLineage:**
```python
# OpenLineage integration
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState

client = OpenLineageClient(url="http://marquez:5000")

# Emit lineage event for dbt model
client.emit(RunEvent(
    eventType=RunState.COMPLETE,
    eventTime=datetime.now(),
    run=Run(runId="dbt-run-123"),
    job=Job(namespace="dbt", name="dim_customer"),
    inputs=[Dataset(namespace="postgres://source", name="public.customers")],
    outputs=[Dataset(namespace="snowflake://analytics", name="marketing.dim_customer")]
))
```

**Data product marketplace:**
- Searchable catalog with: domain, tags, description, quality score
- Usage metrics: # queries last 7 days, # consumers, freshness
- Self-service: Request access, subscribe to alerts, view samples
- Rating system: consumers rate data quality, documentation, freshness
- Integration: Slack bot for dataset search (e.g., `/find-data customer 360`)

**Data mesh anti-patterns to avoid:**
- Central team building all pipelines (defeats mesh purpose)
- No standards (every domain does their own thing)
- Over-governance (too slow, kills agility)
- Under-governance (no discoverability, data swamps)
- Ignoring cross-domain joins (mesh requires contracts)

