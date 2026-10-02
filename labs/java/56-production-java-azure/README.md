# 56 — Production Java on Microsoft Azure

## Overview

Same lab-53 service, Microsoft path: AKS (or Container Apps for spiky
slices) + Application Gateway, Azure Database for PostgreSQL Flexible
Server, Azure Cache for Redis, Service Bus / Event Hubs, Azure Monitor +
Application Insights, Microsoft Entra ID (workload identity federation),
ACR + Deployment Stacks/Bicep.

## Learning Objectives

- [ ] Deploy to AKS with App Gateway health-gated rollout + HPA/KEDA, or Container Apps with scale rules
- [ ] Wire Flexible Server PostgreSQL (HA + PITR), Redis Cache, Service Bus/Event Hubs with managed identity (no connection strings in config)
- [ ] Observe via Azure Monitor (SLO burn) + Application Insights (distributed traces); alert on symptoms
- [ ] Restore-test backups; attribute cost per service (tags); execute rollback

## Topics Covered

### 1. Compute + ingress (AKS, Container Apps, App Gateway)
Probe-gated rolling updates; HPA + KEDA event-driven scaling; Container
Apps scale rules + min/max replicas. ARCHITECTURE.md.

### 2. Data + messaging (Flexible Server PG, Redis Cache, Service Bus/Event Hubs)
Zone-redundant HA + PITR + tested restore; Redis TLS + access keys via
Key Vault; Service Bus queues/topics + DLQ vs Event Hubs streams.
CODE_DEEP_DIVE.md.

### 3. Identity + config (Entra workload identity federation, Key Vault)
Pod↔managed-identity federation — no client secrets; Key Vault references
(CSI driver or env); Flexible Server Microsoft Entra auth. THEORY.md.

### 4. Ops proof (App Insights, alerts, rollback, cost)
Availability + failure + performance blades; action groups; deploy/
rollback; reservation + saving-plan math on proven baseline.
MINI_PROJECT + REAL_WORLD + MATH_FOUNDATION.

## Prerequisites

- Lab 53; Azure subscription + VNet basics; kubectl/Bicep basics

## Further Reading

- AKS + App Gateway (AGIC), Flexible Server PITR, Service Bus DLQ docs
- Labs 53 (vision), 54/55 (same service, other clouds)
