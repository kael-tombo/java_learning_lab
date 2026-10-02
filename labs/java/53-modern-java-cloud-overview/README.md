# 53 — Modern Java in the Cloud: Overview & Vision

## Overview

Where Java meets the cloud: why Java 21+ (virtual threads, GraalVM
native, CRaC) changed the economics of running Java on AWS/GCP/Azure,
what "cloud-native Java" demands (containers, 12-factor, observability,
elasticity), and how to choose among the three clouds. Gateway to labs
54 (AWS), 55 (GCP), 56 (Azure).

## Learning Objectives

- [ ] Explain the vision: one portable Java artifact, three clouds, zero lock-in by design
- [ ] Apply 12-factor + cloud-native principles to a Spring Boot / Quarkus / Micronaut service
- [ ] Compare JVM-on-container economics (memory, startup, Graviton/ARM) and the native-image alternative
- [ ] Choose AWS vs GCP vs Azure per workload using the decision framework

## Topics Covered

### 1. Vision & philosophy (`VISION.md`)
Cloud-native Java thesis; portability vs managed-service gravity; Java's
late-bloomer advantages (mature observability, virtual threads erasing the
async tax). → Labs 54–56 are the three implementations of this vision.

### 2. The container contract (THEORY + CODE_DEEP_DIVE)
`Dockerfile` (JRE-slim, non-root, layered jars); JVM container awareness
(`-XX:MaxRAMPercentage`, cgroupv2); health probes (`/actuator/health`);
externalized config (env > files); stateless processes; logs-to-stdout.

### 3. Runtime economics (MATH_FOUNDATION)
Memory math (heap vs container limit), startup budgets (JVM vs native vs
CRaC), per-request cost models,文件中 scale-to-zero trade-offs.

### 4. Choosing a cloud (MINI_PROJECT + REAL_WORLD_PROJECT)
Scorecard across compute/container/serverless/data/messaging/observability
/identity/IaC for AWS/GCP/Azure; migrate one service across two clouds.

## Prerequisites

- Java 21+, Spring Boot or Quarkus basics; Docker fundamentals

## Further Reading

- Labs 54/55/56 (AWS/GCP/Azure production paths); `labs/cloud/` academy
