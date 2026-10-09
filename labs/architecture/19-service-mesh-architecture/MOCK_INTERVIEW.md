# Mock Interview: Service Mesh Architecture

> Architecture-focused interview dialogue for staff-level system design.

---

## Scenario: Implementing a service mesh for microservice communication

**Interviewer**: "We have 50+ microservices and are struggling with service-to-service communication — implementing retries, timeouts, mTLS, and tracing in every service is inconsistent. How do you solve this?"

**Candidate**: "I'd implement a service mesh. The service mesh offloads communication concerns — traffic management, security, observability — from application code to a proxy layer. Envoy sidecars intercept all traffic, and a control plane manages the configuration."

**Interviewer**: "Walk me through the mesh architecture."

**Candidate**: "Two planes: Data plane and Control plane. The data plane consists of Envoy proxies deployed as sidecars alongside each service. All inbound and outbound traffic routes through the proxy. The control plane (Istio's istiod, or Linkerd's controller) manages configuration — routing rules, retry policies, mTLS certificates, and observability configuration."

**Interviewer**: "What problems does the mesh solve immediately?"

**Candidate**: "Three categories instantly: (1) Traffic management — canary deployments, traffic splitting, circuit breaking (configured centrally, not per-service). (2) Security — mTLS between all services transparently, no application code changes. (3) Observability — distributed tracing, metrics, and access logs for all service-to-service communication."

**Interviewer**: "How does the mesh handle mTLS?"

**Candidate**: "The control plane issues certificates to each sidecar proxy using SPIFFE identities. Service A's sidecar and Service B's sidecar establish mTLS automatically. The application code sends plain HTTP to localhost; the sidecars handle encryption. This means no code changes for encryption — every service gets encrypted communication without knowing about it."

**Interviewer**: "How do you implement canary deployments with the mesh?"

**Certificate**: "Without mesh: complex load balancer configuration or application-level routing. With mesh: define a VirtualService and DestinationRule in Istio. Route 90% traffic to v1, 10% to v2. Add request headers for canary identification. The mesh handles the routing transparently — services don't know about canary logic."

**Interviewer**: "What are the drawbacks of service mesh?"

**Candidate**: "Complexity is the biggest cost. Running a mesh requires: (1) Managing the control plane infrastructure. (2) Debugging becomes harder — requests go through more hops (client → sidecar → sidecar → server). (3) Resource overhead — each sidecar uses 50-200MB RAM and CPU. (4) Latency — 1-3ms added per hop from the proxy. (5) Learning curve — teams need to understand mesh concepts."

**Interviewer**: "When is service mesh NOT appropriate?"

**Candidate**: "For small deployments (under 10 services) where the complexity of the mesh exceeds the benefits. For latency-sensitive systems where the 1-3ms proxy overhead is unacceptable — though this is rare. For teams without the operational maturity to manage the mesh. Start without a mesh and introduce it when the pain of manual cross-cutting concerns becomes greater than the pain of managing the mesh."

**Interviewer**: "How do you handle a sidecar failure?"

**Candidate**: "The sidecar being unavailable means the service is unreachable. Mitigations: (1) Use Kubernetes liveness probes on the sidecar. (2) Consider 'fail open' or 'fail closed' policies — if the sidecar fails, should traffic bypass it or fail? Usually fail closed is safer for security. (3) Health checks at the service level (readiness probe) depend on both the app and sidecar being healthy."

---

## Key Takeaways

- Service mesh offloads communication concerns from application code
- Data plane (Envoy sidecars) handles traffic; control plane manages config
- mTLS, traffic splitting, and observability come without code changes
- Complexity and resource overhead are the main trade-offs
- Sidecar health must be managed as part of pod lifecycle

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

