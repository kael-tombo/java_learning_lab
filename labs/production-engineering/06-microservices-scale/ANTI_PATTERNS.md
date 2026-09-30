# ANTI-PATTERNS: Microservices Architecture at Scale
## Lab 06 | Production Engineering Academy

---

## Anti-Pattern 1: The Distributed Monolith (Chatty Synchronous Cascades)

### The Mistake
Splitting a monolith into 20 microservices where a single user action triggers a chain of 15 synchronous REST calls across services.

### Why It Fails
1. Latency is additive: If each service takes 30ms, total latency is $15 \times 30\text{ms} = 450\text{ms}$.
2. Availability is multiplicative: If each service has 99.9% availability, total system availability is:
   $$A = 0.999^{15} \approx 98.51\%$$
   The system experiences downtime of over 130 hours per year!
3. Deployment coupling: Any change requires orchestrated deployments across 5 services simultaneously.

### The Correct Production Fix
1. Redefine bounded contexts using Domain-Driven Design (DDD).
2. Transition synchronous chains to **asynchronous event-driven choreography** via Kafka.
3. Use data replication (CQRS / materialized views) so services can query data locally rather than making remote cross-service calls.

---

## Anti-Pattern 2: Missing gRPC `maxConnectionAge` (The Forever TCP Trap)

### The Mistake
Running gRPC servers with default infinite connection lifetimes behind Kubernetes services.

### Why It Fails
HTTP/2 connections never terminate. When autoscaling adds 10 new pods to handle a traffic surge, existing clients keep sending all traffic over existing TCP sockets to the original 2 pods. The new pods receive 0 traffic while the original 2 pods crash from overload.

### The Correct Production Fix
Always configure `maxConnectionAge` (e.g. 5–10 minutes) with a grace period on gRPC servers.
