# 54 — Production Java on AWS

## Overview

Ship the lab-53 cloud-native service to AWS production: EKS (or ECS) +
ALB, RDS Aurora PostgreSQL, ElastiCache Redis, MSK (or SQS/SNS),
CloudWatch + X-Ray, IAM IRSA, ECR + CDK. Graviton sizing, rolling
deploys, PITR-tested restores.

## Learning Objectives

- [ ] Deploy containerized Java to EKS with ALB health-gated rollout + HPA on latency
- [ ] Wire RDS Aurora (Multi-AZ), ElastiCache, and MSK/SQS with IAM roles for service accounts (no static keys)
- [ ] Observe via CloudWatch (RED) + X-Ray traces + JFR-on-demand; alert on deltas
- [ ] Restore-test PITR backup; cost-attribute per service; execute written rollback

## Topics Covered

### 1. Compute + ingress (EKS/ECS, ALB, HPA)
Target-group health checks against actuator readiness; rolling update
gates; HPA on p99/latency + CPU; Graviton (ARM) node sizing for JVMs.
ARCHITECTURE.md.

### 2. Data + messaging (Aurora, ElastiCache, MSK/SQS/SNS)
Aurora Multi-AZ + PITR; Redis for session/cache with TLS + AUTH token
from Secrets Manager; MSK for event streams (or SQS/SNS for queues);
Flyway migrations as init/separate job. CODE_DEEP_DIVE.md.

### 3. Identity + config (IRSA, Secrets Manager, Parameter Store)
Pod-named IAM roles (IRSA) — zero static AWS keys; secrets injected as
env/files; DB credentials rotated. THEORY.md.

### 4. Ops proof (X-Ray, alarms, rollback, cost)
Trace sampling to X-Ray; CloudWatch alarms (5xx, p99, CPU, DB
connections); deploy/rollback runbook; Cost Explorer tags per service.
MINI_PROJECT.md + REAL_WORLD_PROJECT.md + MATH_FOUNDATION.md.

## Prerequisites

- Lab 53 (container, probes, env config); AWS account + VPC basics; kubectl/CDK basics

## Further Reading

- EKS + ALB Controller docs; RDS Aurora PITR; MSK sizing guide
- Labs 53 (vision), 55/56 (same service, other clouds)
