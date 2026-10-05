# AWS Serverless - Real World Project

## Project: Migrating a Monolith Endpoint Family to Serverless

### Objective
Move a group of related endpoints from a container service to Lambda behind API Gateway and
Step Functions, with the operational changes that migration actually requires — observability,
cold-start budgets, failure semantics, and a rollback plan.

### Why This Matters
Serverless migrations fail on the non-code parts: no long-lived connections, no shared memory,
different observability, different cost shape at scale, and no "scale the container up" as an
escape hatch. Those are the things this project plans for.

### Architecture Overview
```
  Client ─▶ API Gateway (HTTP API) ─▶ Lambda (sync, thin: validate + enqueue)
                                        │
                              SQS queue (ordering per tenant, DLQ)
                                        │
                              Lambda (async, idempotent processor)
                                        │
                    ┌───────────────────┼───────────────────┐
              DynamoDB (conditional)  Step Functions   EventBridge
                                                          │
                                                  downstream service
```

### Phase 1: Decide What Actually Moves (Week 1)
1. Inventory endpoints by profile: latency requirement, throughput, statefulness, dependencies
2. Good candidates: spiky, low-latency tolerance, stateless, event-driven triggers
3. Poor candidates: steady high throughput with predictable load, stateful sessions, anything
   needing persistent connections
4. Be honest about cost: at sustained high request rates, containers usually win per request.
   Compute the break-even for your traffic shape and put it in the ADR

### Phase 2: Build the Skeleton (Week 2)
1. API Gateway HTTP API with authorizer and throttling per route
2. Thin synchronous Lambda: validate, authorise, enqueue, return 202. **No business logic** —
   this keeps the user-facing latency inside the cold-start budget
3. Asynchronous processor Lambda with idempotency and a DLQ
4. Step Functions for multi-step flows with per-state failure policy
5. Infrastructure as code, so the environment is reproducible

### Phase 3: Cold-Start Budget and Mitigation (Week 3)
1. Measure cold start p50/p99 in the deployed environment, per memory size
2. Reduce init cost: minimal dependencies, no heavy framework, lazy initialisation of clients
3. Move expensive client creation outside the handler where possible, or accept its cost once
   per container
4. Decide on provisioned concurrency for the latency-critical routes; price it against the
   latency it buys
5. Set a real SLO: p99 under 300ms at the edge. If the cold start makes it unachievable,
   say so and change the architecture rather than hiding it

### Phase 4: Observability and Cost (Week 4)
1. X-Ray tracing enabled end to end; verify trace continuity across API Gateway, Lambda, and
   the downstream service
2. Metrics that matter per stage: API Gateway latency and errors, Lambda duration and
   concurrent executions, queue age and depth, DLQ depth, Step Functions execution outcomes
3. Cost dashboard per stage with the three biggest contributors named
4. Alerts: queue age above threshold, DLQ non-empty, error rate above SLO, concurrency
   throttling at the account level

### Phase 5: Cut Over and Verify (Week 5+)
1. Shadow traffic: run both paths, compare responses, log differences
2. Route 1% → 10% → 50% → 100% with a soak at each stage
3. Automatic rollback on error-rate or latency SLO breach
4. Keep the container path deployable until two full business cycles pass
5. Post-migration report: latency change, cost change, and what surprised you

### Deliverables
1. Endpoint inventory with the keep/move decision and cost break-even per endpoint
2. Reproducible infrastructure and the two-Lambda + Step Functions pipeline
3. Cold-start measurements, mitigations, and the provisioned-concurrency decision
4. Dashboards, rollback plan, and the post-migration comparison report

### Success Criteria
- p99 latency at the edge meets the declared SLO under peak traffic
- Zero duplicate effects, verified by idempotency key across 30 days
- DLQ depth is alerted and driven to zero within one business day
- Cost per request documented and compared against the container baseline

### Sourced field notes (fetched Oct 2026 — verify before citing)
- AWS Lambda Developer Guide —
  https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
  Use for: the maintained model of execution environments, cold starts, timeouts, and
  concurrency. Verify current memory/CPU relationship and timeout limits before relying on
  specific numbers in an SLO.
- Amazon EventBridge event patterns —
  https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html
  Use for: routing rules and the filter semantics used to decouple producers from consumers
  in the event-driven portion of this architecture.

### Estimated Time
7-8 weeks part-time