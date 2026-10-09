# Mock Interview: Sidecar / Ambassador / Adapter Patterns

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Adding observability and resilience to legacy services

**Interviewer**: "We have legacy Java services that lack observability and resilience. We can't modify the application code. How do we add these capabilities?"

**Candidate**: "I'd use the sidecar pattern. Deploy a sidecar process alongside each service instance that handles cross-cutting concerns — logging, metrics, service discovery, circuit breaking — without modifying the application code."

**Interviewer**: "How does the sidecar intercept traffic?"

**Candidate**: "The sidecar runs in the same pod/deployment unit. All incoming traffic goes through the sidecar (which proxies to the application on localhost), and all outgoing traffic goes through the sidecar. The application is configured to connect to localhost — it doesn't know about the sidecar. This is how service meshes like Istio work."

**Interviewer**: "What about the ambassador pattern?"

**Candidate**: "The ambassador pattern is a specific type of sidecar focused on external communication. For the legacy services, I'd use an ambassador sidecar that handles: connection pooling, retry with exponential backoff, circuit breaking when calling downstream services, and service discovery. The ambassador knows about the infrastructure; the legacy application doesn't."

**Interviewer**: "And the adapter pattern?"

**Candidate**: "The adapter pattern transforms interfaces. For a legacy service that emits logs in an old format, an adapter sidecar can: consume the old-format logs (via file tail, shared volume, or stdout capture), transform them to structured JSON, and forward to the centralized logging system. The legacy service doesn't change; the adapter translates its output."

**Interviewer**: "Walk me through a concrete implementation."

**Candidate**: "For a legacy order-processing service: (1) Deploy an Envoy sidecar that handles all inbound HTTP traffic — adds distributed tracing headers, enforces rate limits, collects metrics. (2) Deploy an ambassador that handles all outbound calls to the payment service — implements retries, circuit breaking, timeout configuration. (3) Deploy an adapter that consumes the service's flat-file access logs and forwards structured events to Kafka."

**Interviewer**: "How do you manage the sidecar lifecycle?"

**Candidate**: "In Kubernetes, the sidecar runs in the same pod as the application. When the pod starts, the sidecar starts first. When the pod stops, the sidecar handles graceful shutdown — draining connections, flushing logs. I'd use init containers to configure the sidecar before the application starts, and preStop hooks for graceful shutdown."

**Interviewer**: "What are the downsides of sidecar patterns?"

**Candidate**: "Sidecars add latency — every request goes through an additional proxy hop. They consume resources — each sidecar uses CPU and memory, multiplied by every service instance. They add complexity — more processes to debug, more configuration to manage. For some use cases, a library-based approach (Resilience4J, OpenTelemetry SDK) is simpler and more efficient."

---

## Key Takeaways

- Sidecar adds cross-cutting capabilities without modifying app code
- Ambassador pattern focuses on external communication
- Adapter pattern translates interfaces and formats
- Kubernetes enables sidecar lifecycle management
- Sidecars add latency and resource overhead — evaluate trade-offs

---

## Evaluation Criteria

The interviewer assesses:
- **Architecture thinking**: Clear decomposition into meaningful boundaries
- **Trade-off awareness**: Understanding of when this pattern helps vs hurts
- **Failure handling**: Proactive identification of failure modes
- **Operational maturity**: Discussion of monitoring, deployment, and operations
- **Communication**: Ability to explain complex concepts clearly


## Staff+ Level Expectations

At the staff+ level, the interviewer expects you to:
- Challenge their assumptions and ask clarifying questions
- Discuss organizational implications (team boundaries, Conway's Law)
- Address data consistency challenges proactively
- Consider migration and evolution strategy
- Discuss cost and operational trade-offs
- Connect technical decisions to business outcomes

## Common Follow-Up Questions

1. ""How would this design change at 100x scale?"" — Discuss partitioning, caching, read replicas
2. ""How do you handle schema evolution?"" — Backward compatibility, versioning, migration strategies
3. ""Whats the biggest risk in this architecture?"" — Identify the weakest link and mitigation
4. ""How would you migrate from the current system?"" — Strangler Fig, feature toggles, parallel run
5. ""How do you test this system?"" — Unit, integration, contract, and end-to-end testing strategies

## Key Takeaways

This mock interview demonstrates the depth of discussion expected at staff+ level. The interviewer is not looking for a single ""correct"" answer but rather evaluating your thought process, trade-off awareness, and ability to communicate complex architectural decisions clearly.

