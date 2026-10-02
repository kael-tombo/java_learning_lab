# 55 — Production Java on GCP

## Overview

Same lab-53 service, Google path: GKE Autopilot (or Cloud Run for spiky
slices) + Global LB, AlloyDB (or Cloud SQL) PostgreSQL, Memorystore
Redis, Pub/Sub, Cloud Monitoring/Trace/Profiler, Workload Identity, Artifact
Registry + Cloud Deploy. Request-based autoscaling, VPC-native networking.

## Learning Objectives

- [ ] Deploy to GKE with Gateway/Ingress health-gated rollout + HPA, or Cloud Run with concurrency tuning
- [ ] Wire AlloyDB/Cloud SQL (HA + PITR), Memorystore, Pub/Sub with Workload Identity (no JSON keys)
- [ ] Observe via Cloud Monitoring (SLO burn), Cloud Trace, Profiler; alert on symptoms
- [ ] Restore-test backups; attribute cost per service (labels); execute rollback

## Topics Covered

### 1. Compute + ingress (GKE Autopilot/Standard, Cloud Run, GCLB)
Pod readiness gates; HPA; Cloud Run concurrency + min/max instances for
scale-to-zero slices. ARCHITECTURE.md.

### 2. Data + messaging (AlloyDB/Cloud SQL, Memorystore, Pub/Sub)
HA + PITR + tested restore; Redis TLS + AUTH; Pub/Sub topics/subscriptions
(push vs pull, ordering keys, dead-letter topics). CODE_DEEP_DIVE.md.

### 3. Identity + config (Workload Identity, Secret Manager)
KSA→GSA federation — no exported JSON keys; secrets mounted/env;
Cloud SQL Auth Proxy (or AlloyDB Omni connection) patterns. THEORY.md.

### 4. Ops proof (SLOs, traces, rollback, cost)
Burn-rate alerts; Trace sampling; deploy/rollback; committed-use +
sustained-use + labels math. MINI_PROJECT + REAL_WORLD + MATH_FOUNDATION.

## Prerequisites

- Lab 53; GCP project + VPC basics; kubectl/Terraform basics

## Further Reading

- GKE Autopilot + Gateway docs; AlloyDB PITR; Pub/Sub delivery semantics
- Labs 53 (vision), 54/56 (same service, other clouds)
