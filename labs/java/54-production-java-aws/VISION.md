# VISION — Production Java on AWS

## 1. Thesis

AWS rewards Java teams that treat the JVM as a sized machine, not a
black box: Graviton + right-sized heaps on EKS/ECS, Aurora doing the
durability work, ALB gating every rollout. Vision: **one Spring Boot
artifact, health-gated onto EKS, with cost per request falling as
traffic rises** — because virtual threads removed the thread-pool tax
and autoscaling follows latency, not superstition.

## 2. Reference shape

ALB → EKS (ARM nodes, HPA on p99/CPU) → Aurora PostgreSQL Multi-AZ +
ElastiCache Redis; MSK or SQS/SNS for events; IRSA for identity (no
static keys); ECR + CDK for build/ship; CloudWatch RED + X-Ray traces.

## 3. Cost / latency tradeoffs

| Choice | Latency effect | Cost effect |
|--------|---------------|-------------|
| Graviton (ARM) nodes | Neutral | −20–40% compute |
| Aurora Serverless v2 | Idle scale-to-low | Pay per ACU, watch floor |
| ElastiCache for sessions | −p99 on reads | Fixed node cost |
| MSK vs SQS | MSK: throughput; SQS: simplicity | SQS wins under ~100 M msgs/mo |
| ZGC on large heaps | Bounded pauses | +10–15% CPU |

Rule: cache only after X-Ray proves the DB is the bottleneck; scale
reads with replicas before upsizing the writer.

## 4. Career trajectory

Operator (kubectl + logs) → Tuner (HPA, JVM flags, PITR drills) →
Architect (multi-AZ, cost attribution, chaos) → Platform owner
(golden paths, CDK constructs, org-wide SLOs). AWS depth + JVM depth
is the rare, well-paid combo.

## 5. Six-month learning path

```
Month 1-2: EKS + ALB deploys, probes, HPA; IRSA + Secrets Manager.
Month 3-4: Aurora Multi-AZ + PITR restore drill; Redis caching; X-Ray tracing.
Month 5:   MSK/SQS events, Flyway jobs, CloudWatch alarms + runbooks.
Month 6:   Cost Explorer per-service tags, rollback + exit drill, present SLOs.
```

## 6. Success bar

99.9% availability design, p99 < 300 ms at 5x load, RPO ≤ 5 min /
RTO ≤ 30 min demonstrated, rollback written and rehearsed.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- https://aws.amazon.com/eks/
- https://aws.amazon.com/rds/
- https://kubernetes.io/docs/home/
