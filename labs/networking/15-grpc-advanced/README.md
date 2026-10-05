# gRPC Advanced - README

## Overview
This lab covers the parts of gRPC that only matter in production: how channels and
load balancing actually behave, how to order an interceptor chain, how deadlines and
retries compose into a real reliability story, and how to govern a schema that 200
services depend on. The recurring theme is that the local happy path and the production
behaviour differ in specific, diagnosable ways.

## Learning Objectives
- Explain channel/subchannel architecture and why a single-address resolver defeats
  round-robin load balancing
- Order an interceptor chain deliberately and justify the ordering
- Propagate deadlines as absolute timestamps and never extend a caller's budget
- Design retry and hedging policy with a safety analysis for non-idempotent operations
- Enforce idempotency with server-side deduplication rather than hoping
- Build a CI gate that rejects client-breaking proto changes and generates the migration
- Size a gRPC server thread pool against downstream concurrency, not CPU count
- Derive SLOs from a caller graph so a dependency cannot consume its callers' budgets

## Prerequisites
- Java 21+
- Completed lab 04 (gRPC) or equivalent working knowledge of proto, stubs, and streaming
- Familiarity with load balancers and service meshes

## Lab Structure

| Directory/File | Description |
|----------------|-------------|
| `src/main/java/` | Channel config, interceptors, retry policy, schema gate |
| `src/test/java/` | Distribution, deadline, retry-safety, and CI gate tests |
| `MINI_PROJECT/` | GridRPC: load-balanced channel, interceptor chain, contract gate |
| `REAL_WORLD_PROJECT/` | MeshContract: governed gRPC platform for 200 services |
| `SOLUTION/` | Solutions to exercises |

## Quick Start

```java
// The failure mode this lab exists to prevent: a "round-robin" that talks to one backend.
var channel = Grpc.newChannelBuilderForAddress("inventory", 9090, creds)
        .defaultLoadBalancingPolicy("round_robin")   // explicit; default is pick_first
        .intercept(CorrelationId, Deadline, Auth, Retry, Metrics, Logging)
        .build();
for (int i = 0; i < 300; i++) stub.getStock(request("SKU-1"));
assertThat(backendMetrics.requestsPerBackend()).hasSize(3);   // fails if only one address resolved
```

## Topics Covered
1. Channel and subchannel architecture; name resolution; LB policies and their defaults
2. Interceptor ordering as a correctness property; context propagation
3. Deadlines: absolute propagation, the never-extend rule, budget sharing with retries
4. Retries: retryable codes, idempotency requirements, hedging and its double-write risk
5. Idempotency: schema declaration, server-side dedupe, enforcement at the mesh
6. Schema governance: breaking-change detection, versioned packages, deprecation by usage
7. Server capacity: thread pool sizing, bounded queues, load shedding, keepalive
8. Observability: per-method metrics, dependency graph, SLO budgets and burn-rate alerts
9. Migration: shadow mode, automatic new-package generation, multi-language stubs

## Assessment
- Complete the coding exercises in `EXERCISES.md`
- Pass the quiz in `QUIZ.md`
- Submit the mini project
- Complete the real-world project

## Estimated Time
5-6 hours

## References
- gRPC core concepts, deadlines, retry, status codes
- Protobuf encoding and compatibility guarantees
- gRPC Java API docs - ServerBuilder, ClientInterceptor
- Envoy retry and outlier detection documentation
- SRE Workbook - implementing SLOs
