# Lab 15: Disaster Recovery Failover — Region Outage

## Situation Overview

**Scenario**: AWS us-east-1 region outage — failover to us-west-2 takes too long, data loss

**Severity**: P0 (Critical) / SEV1

**Impact Assessment**:
- AWS us-east-1 experiences a severe regional outage affecting EC2, RDS, and ElastiCache
- Primary production infrastructure in us-east-1 completely unavailable for 5 hours 23 minutes
- Failover to us-west-2 DR region took 1 hour 47 minutes (target RTO: 15 minutes)
- Data loss of 12 minutes of transactions (RPO target: 5 minutes, actual: 17 minutes)
- All customer-facing services down for 7 hours 10 minutes total
- 3.1 million daily active users unable to access the platform
- Revenue loss: $742,000 (peak holiday shopping period)
- Brand trust impact: trending on Twitter/X, multiple news articles
- Incident duration: 7 hours 10 minutes (09:47 UTC — 16:57 UTC)

**Affected Systems**:
- Primary Region: AWS us-east-1 (EC2, RDS MySQL, ElastiCache Redis, ALB, Route53)
- DR Region: AWS us-west-2 (standby infrastructure, never tested)
- Services: API Gateway, Order Service, Payment Service, User Service, Product Catalog
- Database: RDS MySQL Multi-AZ in us-east-1 (primary), read replica in us-west-2
- DNS: Route53 with health checks (TTL=86400 on production records)
- CDN: CloudFront distributions pointing to us-east-1 origins
- Monitoring: Prometheus/Grafana in us-east-1 (no cross-region DR for monitoring)

**Detection**: AWS Health Dashboard reports "Elevated Error Rates" in us-east-1 at 09:47 UTC. PagerDuty alert `AWSRegionDegraded` fires at 09:48 UTC. Full region failure confirmed at 09:52 UTC.

**Business Context**: The DR runbook was 14 months old and had never been tested. The last DR drill was scheduled but cancelled due to "critical business priorities." The RDS cross-region read replica had asynchronous replication lag of 12 minutes (configured for cost savings). Route53 DNS records had TTL=86400 (24 hours) preventing fast DNS cutover. CloudFormation DR templates had drifted from production configuration.

**Engineering Teams Involved**:
- SRE Team (incident command, failover execution)
- Cloud Infrastructure Team (AWS console, Route53, CloudFormation)
- Database Team (RDS promotion, replication lag, data integrity)
- Application Team (connection strings, cache warming, application startup)
- Network Team (DNS propagation, CloudFront, security groups)
- Security Team (cross-region access, encryption, compliance)
- Customer Support Team (user communication, status page)
- Executive Leadership (crisis management, regulatory reporting)

## References

1. AWS Well-Architected Framework — Reliability Pillar: https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/
2. Netflix Tech Blog — Chaos Monkey: https://netflixtechblog.com/chaos-monkey-the-netflix-way
3. Google SRE Book — Chapter 29: Disaster Recovery: (link removed)
4. AWS Disaster Recovery whitepaper: https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery.html
5. Azure Well-Architected Framework — Disaster Recovery: https://learn.microsoft.com/en-us/azure/well-architected/reliability/disaster-recovery
6. Google Cloud Disaster Recovery: https://cloud.google.com/architecture/disaster-recovery
7. Netflix Simian Army: https://netflixtechblog.com/the-netflix-simian-army
8. Route53 Application Recovery Controller: https://docs.aws.amazon.com/r53recovery/latest/dg/

## Key Metrics

| Metric | Target | Actual | Gap |
|--------|--------|--------|-----|
| RTO (Recovery Time Objective) | 15 minutes | 1h 47m | 7x target |
| RPO (Recovery Point Objective) | 5 minutes | 17 minutes | 3.4x target |
| Total outage duration | N/A | 7h 10m | N/A |
| Revenue loss | $0 | $742,000 | $742,000 |
| DR drill compliance | Quarterly | Never tested | 4+ quarters |
| DNS propagation time | < 5 minutes | 35 minutes | 7x target |
| Cross-region sync lag | < 5 seconds | 12 minutes | 144x target |
| Runbook age | < 3 months | 14 months | 11 months stale |

## Detailed Impact Analysis

### Service Status During Outage

| Service | us-east-1 Status | us-west-2 Status | Customer Impact |
|---------|-----------------|------------------|-----------------|
| API Gateway | DOWN (ALB unavailable) | Coming up (t+1h 47m) | All API calls failing |
| Order Service | DOWN (EC2 terminated) | Starting (t+2h 10m) | Cannot place orders |
| Payment Service | DOWN (RDS primary unreachable) | Starting (t+1h 47m) | Payment processing down |
| User Service | DOWN (EC2 terminated) | Starting (t+2h 05m) | Login/auth failing |
| Product Catalog | DOWN (EC2 + Elasticache down) | Starting (t+2h 30m) | Product listings down |
| Search Service | DOWN (Elasticsearch cluster failed) | Not restored (t+7h) | Search unavailable |
| Admin Dashboard | DOWN | Starting (t+3h) | Admin access down |
| Reporting | DOWN | Coming up (t+5h) | Analytics delayed |

### Failover Step Duration Breakdown

| Step | Duration | Cumulative | Target | Issue Encountered |
|------|----------|------------|--------|-------------------|
| Incident declaration | 5 min | 5 min | 2 min | — |
| Runbook retrieval | 8 min | 13 min | 2 min | Runbook stale, needed updates |
| CloudFormation template fix | 12 min | 25 min | 5 min | AMI, instance class, SG fixes |
| RDS promotion | 10 min | 35 min | 5 min | 12 min replication lag |
| Stack deployment | 25 min | 60 min | 5 min | SG dependency, missing ECR images |
| Application startup | 15 min | 75 min | 5 min | Container rebuild from source |
| Cache warming | 12 min | 87 min | 2 min | Empty Redis, no cross-region repl |
| DNS cutover | 10 min | 97 min | 2 min | TTL=86400 |
| CloudFront origin update | 10 min | 107 min | 2 min | Cache invalidation |
| **Total RTO** | **107 min** | **107 min** | **15 min** | **7.1x target** |

### Data Loss Gap Analysis

```
RDS replication check at 10:18 UTC:

Primary (us-east-1): Last committed transaction
  File: mysql-bin.001234
  Position: 847291234
  Timestamp: 2026-11-27T09:35:22Z
  GTID: 847291234-ae12-11ec-8ea0-0242ac130002

Replica (us-west-2): Last replicated transaction
  File: mysql-bin.001234  
  Position: 847123456
  Timestamp: 2026-11-27T09:23:14Z
  GTID: 847123456-ae12-11ec-8ea0-0242ac130002

Gap: 12 minutes 8 seconds of transactions

Estimated lost transactions:
  Order volume at 09:23-09:35: ~847 orders
  Average order value: $127
  Estimated lost revenue: $107,569
  Estimated lost transactions: 847
  Affected customers: ~780 unique users
```

### CloudFormation Drift Details

| Resource | Expected (DR Template) | Actual (us-east-1 Production) | Drift Impact |
|----------|----------------------|------------------------------|--------------|
| AMI ID | ami-0abcdef1234567890 | ami-9876543210fedcba | Template validation failure |
| RDS instance class | db.r5.large | db.r6g.large | Deprecated class warning |
| Security group 1 | 10.0.0.0/16 | 10.0.0.0/16 + 172.31.0.0/16 | Missing CIDR causes timeout |
| Security group 2 | sg-0123456789abcdef | sg-fedcba9876543210 | Wrong SG reference |
| Load balancer subnets | subnet-aaaa, subnet-bbbb | subnet-cccc, subnet-dddd | Wrong subnets |
| Instance count | 3 (min), 12 (max) | 5 (min), 20 (max) | Insufficient capacity |
| Instance type | t3.medium | t3.large | Wrong sizing |
| EBS volume size | 100 GB | 200 GB | Insufficient storage |
| Backup retention | 7 days | 35 days | Not critical |
| CloudWatch alarm thresholds | Various | Various | Different values |

### DNS Propagation Measurement

```
Route53 TTL: 86400 (24 hours)
DNS cutover initiated: 11:35 UTC

Propagation measurement from global resolvers:

Resolver Location | Before Cutover | t+5m | t+15m | t+30m | t+60m | t+2h | t+4h | t+8h | t+24h
------------------|---------------|------|-------|-------|-------|------|------|------|------
Google (8.8.8.8) | us-east-1 IP | us-east-1 | us-east-1 | us-east-1 | us-west-2 | us-west-2 | us-west-2 | us-west-2 | us-west-2
Cloudflare (1.1.1.1) | us-east-1 IP | us-east-1 | us-east-1 | us-west-2 | us-west-2 | us-west-2 | us-west-2 | us-west-2 | us-west-2
OpenDNS (208.67.222.222) | us-east-1 IP | us-east-1 | us-east-1 | us-east-1 | us-west-2 | us-west-2 | us-west-2 | us-west-2 | us-west-2
AWS Route53 | us-east-1 IP | us-west-2 | us-west-2 | us-west-2 | us-west-2 | us-west-2 | us-west-2 | us-west-2 | us-west-2
ISP (Comcast) | us-east-1 IP | us-east-1 | us-east-1 | us-east-1 | us-east-1 | us-west-2 | us-west-2 | us-west-2 | us-west-2

First propagation seen: 15 minutes (Cloudflare — low TTL standard)
Full propagation: ~24 hours (due to 86400 TTL)
```

### Failover Decision Tree

The team's decision tree during the incident:

```
09:47 — AWS us-east-1 degraded
  → Is it regional? YES (EC2 + RDS + ElastiCache all affected)
  → Is it recoverable within RTO? NO (AWS status: "Underlying cause being investigated")
  → Decision: DECLARE INCIDENT, INITIATE FAILOVER

10:02 — Runbook issues found
  → Can we fix the template? YES
  → Can we proceed with manual steps? YES
  → Decision: PROCEED WITH FIXING AND FAILOVER

10:18 — RDS replication lag = 12 minutes
  → Is data loss acceptable? YES (business decision)
  → Can we recover lost data later? PARTIALLY (need manual reconciliation)
  → Decision: PROCEED WITH PROMOTION

10:35 — ECR images not in us-west-2
  → Can we rebuild from source? YES
  → Is there a faster option? NO
  → Decision: REBUILD CONTAINER IMAGES

11:35 — DNS TTL = 86400
  → Can we reduce TTL now? YES (but propagation still slow)
  → Decision: REDUCE TTL AND CUTOVER (accept slow propagation)
```

### Cost Analysis

| Category | Amount | Per-Hour Cost During Outage |
|----------|--------|-----------------------------|
| Direct revenue loss | $390,000 | $54,545/hour |
| SLA penalties | $120,000 | $16,783/hour |
| Customer churn (estimated) | $150,000 | One-time |
| Engineering overtime | $32,000 | $4,475/hour |
| AWS DR infrastructure | $12,000 | New DR resources |
| Crisis PR | $25,000 | One-time |
| Compliance penalties | $13,000 | Estimated |
| **Total** | **$742,000** | **$103,636/hour** |

## Lessons Learned

1. **Untested DR plan**: The disaster recovery plan was never tested. The runbook was 14 months old and contained incorrect IP addresses, outdated AMI IDs, and stale connection strings.

2. **Cross-region replication lag**: RDS read replica lag was configured for cost optimization (async replication with 12-minute lag at time of failover). Target should be < 5 seconds.

3. **DNS TTL too high**: Route53 records had TTL=86400 (24 hours), meaning DNS propagation alone took 35+ minutes after cutover.

4. **Monitoring single-region**: Prometheus/Grafana stack was only deployed in us-east-1. During the outage, the team had no monitoring visibility in the DR region.

5. **CloudFormation drift**: DR CloudFormation templates had drifted significantly from production. Key differences: security group rules, instance types, auto-scaling group sizes.

6. **No automation**: Failover required manual execution of 47 steps across 8 different AWS services. No automated failover script existed.

7. **Chaos engineering absent**: No chaos experiments or game days had been conducted to validate DR procedures.

8. **No pre-warmed DR**: DR infrastructure was not kept running (cost saving), causing provision-from-scratch delays.

9. **Container images not replicated**: ECR was configured for single-region only, requiring image rebuilds.

10. **No cross-region cache replication**: ElastiCache Redis was not configured with Global Datastore, requiring cold cache startup.

### Appendix A: AWS Well-Architected Reliability Checklist

| Pillar | Question | Our Score | Target |
|--------|----------|-----------|--------|
| Foundations | Have you mitigated single-region failure? | 1/5 | 4/5 |
| Workload Architecture | Is workload deployed to multiple regions? | 1/5 | 4/5 |
| Change Management | Are changes monitored and tested? | 3/5 | 4/5 |
| Failure Management | Are backups tested regularly? | 1/5 | 4/5 |
| Failure Management | Is failover automated? | 1/5 | 4/5 |
| Failure Management | Do you perform game days? | 1/5 | 4/5 |
| **Overall** | | **1.3/5** | **4/5** |

### Appendix B: Pilot Light DR Strategy

```
Pilot Light Strategy (Recommended for us):

Primary Region (us-east-1):            DR Region (us-west-2):
  ┌──────────────────────┐              ┌──────────────────────┐
  │ Route53 DNS          │              │ Route53 Health Checks│
  │ (Active)             │              │ (Standby)            │
  ├──────────────────────┤              ├──────────────────────┤
  │ CloudFront           │              │ CloudFront           │
  │ (Primary Origin)     │              │ (Failover Origin)    │
  ├──────────────────────┤              ├──────────────────────┤
  │ ALB                  │              │ ALB (Powered Off)     │
  ├──────────────────────┤              ├──────────────────────┤
  │ ECS / EC2            │              │ ECS / EC2            │
  │ (Running)            │              │ (Stopped — snapshots) │
  ├──────────────────────┤              ├──────────────────────┤
  │ RDS Primary          │────async────→│ RDS Read Replica     │
  │ (Multi-AZ)           │              │ (Running, replicating)│
  ├──────────────────────┤              ├──────────────────────┤
  │ ElastiCache Redis    │              │ ElastiCache Redis    │
  │ (Primary)            │──────sync────→│ (Global Datastore)   │
  ├──────────────────────┤              ├──────────────────────┤
  │ ECR                  │──rep──→      │ ECR (Replicated)     │
  └──────────────────────┘              └──────────────────────┘

During failover:
  - RDS Read Replica promoted to primary (10s)
  - EC2 instances started from AMI snapshots (3-5 min)
  - ALB created/powered on (2 min)
  - Route53 health check fails → DNS cutover (30s)
  - CloudFront origin updated (5 min)
  - Cache warmed from database (5 min)
  
Estimated RTO with Pilot Light: 15-20 minutes
Estimated RPO with sync replication: < 5 seconds
```

### Appendix C: Multi-Region Architecture Comparison

| Strategy | RTO | RPO | Cost | Complexity | Our Status |
|----------|-----|-----|------|------------|------------|
| Backup & Restore | Hours | 24h | $ | Minimal | ✅ Current |
| Pilot Light | 15-20 min | < 5s | $$ | Medium | ⬜ Planned |
| Warm Standby | 5-10 min | < 1s | $$$ | High | ⬜ Future |
| Multi-Site Active-Active | < 1 min | < 1s | $$$$ | Very High | ⬜ Future |
| Multi-Region Active-Passive | 5-15 min | < 5s | $$$ | High | ⬜ Planned |

### Appendix D: Route53 Application Recovery Controller Configuration

```json
{
  "ControlPanel": {
    "Name": "acmecorp-production",
    "ClusterArn": "arn:aws:route53-recovery-control::123456789:cluster/acmecorp-dr"
  },
  "RoutingControls": [
    {
      "Name": "primary-us-east-1",
      "Status": "ON",
      "Region": "us-east-1"
    },
    {
      "Name": "dr-us-west-2",
      "Status": "OFF",
      "Region": "us-west-2"
    }
  ],
  "SafetyRules": [
    {
      "Name": "prevent-simultaneous-active",
      "AssertedControls": ["primary-us-east-1", "dr-us-west-2"],
      "Rule": "NOT (primary-us-east-1=ON AND dr-us-west-2=ON)"
    }
  ]
}
```

### Appendix E: Chaos Engineering Game Day Template

```yaml
game_day:
  title: "Region Outage Simulation — us-east-1"
  duration: 4 hours
  participants:
    - incident_commander
    - sre_engineer
    - db_engineer
    - network_engineer
    - app_developer
    - observer

  faults_to_inject:
    - name: "Block us-east-1 traffic"
      type: "network"
      duration: "30 minutes"
      expected_action: "Initiate failover to us-west-2"
      
    - name: "RDS primary failure"
      type: "database"
      duration: "15 minutes"
      expected_action: "Promote read replica"
      
    - name: "DNS resolution failure"
      type: "network"
      duration: "5 minutes"
      expected_action: "Verify Route53 health checks"
      
  success_criteria:
    - RTO <= 15 minutes
    - RPO <= 5 minutes
    - All critical services restored
    - No data loss > 5 minutes
    - Runbook followed without errors
```

### Appendix F: DR Runbook Template

```markdown
# Disaster Recovery Runbook — AWS Region Failover

## Pre-Failover Checklist
- [ ] Verify DR region health
- [ ] Verify RDS replication lag < 5s
- [ ] Verify ECR images in DR region
- [ ] Verify Route53 health checks configured
- [ ] Verify CloudFormation template in-sync
- [ ] Verify IAM roles and permissions

## Failover Steps (Automated via Route53 ARC)
1. Execute ARC failover: `aws route53-recovery-cluster update-routing-control-state`
2. Verify DNS cutover
3. Promote RDS read replica (if not auto-promoted)
4. Start EC2/ECS services in DR region
5. Verify application health
6. Update CloudFront origins
7. Monitor error rates and latency

## Failback Steps
1. Re-establish RDS replication from DR to primary
2. Sync data from DR to primary
3. Execute ARC failback to primary
4. Verify primary health
5. Restart cross-region replication
6. Document RTO and RPO achieved
```

### Appendix G: RTO/RPO Monitoring Dashboard

```sql
-- RTO tracking table
CREATE TABLE dr_rto_tracking (
    id SERIAL PRIMARY KEY,
    drill_date TIMESTAMP NOT NULL,
    scenario VARCHAR(255),
    target_rto_seconds INT NOT NULL DEFAULT 900,
    actual_rto_seconds INT,
    target_rpo_seconds INT NOT NULL DEFAULT 300,
    actual_rpo_seconds INT,
    issues_found TEXT[],
    passed BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quarterly drill results
SELECT 
    drill_date,
    scenario,
    actual_rto_seconds,
    target_rto_seconds,
    CASE WHEN actual_rto_seconds <= target_rto_seconds 
         THEN 'PASS' ELSE 'FAIL' END as rto_result,
    actual_rpo_seconds,
    target_rpo_seconds,
    CASE WHEN actual_rpo_seconds <= target_rpo_seconds 
         THEN 'PASS' ELSE 'FAIL' END as rpo_result
FROM dr_rto_tracking
ORDER BY drill_date DESC;
```
