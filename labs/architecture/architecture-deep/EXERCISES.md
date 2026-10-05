# Exercises — Architecture Deep Dive

## Exercise 1: Pattern Identification

Given the following scenarios, identify the most appropriate architectural
pattern and justify your choice:

1. A system needs to process millions of events per minute with real-time
   analytics and pattern detection.
2. A legacy monolith needs to be migrated to microservices without downtime.
3. A system must maintain a complete audit trail of all state changes.
4. Multiple frontend clients (web, mobile, TV) need different data shapes
   from the same backend services.
5. A distributed transaction must coordinate across five services with
   compensation on failure.

## Exercise 2: Trade-off Analysis

For each pattern below, analyze the trade-offs and explain when the
pattern is appropriate vs when it adds unnecessary complexity:

1. **CQRS** — When does separating reads and writes justify the complexity?
2. **Event Sourcing** — When is the audit trail worth the storage and
   complexity overhead?
3. **Microservices** — When does service decomposition outweigh the
   operational complexity?
4. **Saga Pattern** — When is eventual consistency acceptable vs when is
   strong consistency required?

## Exercise 3: Architecture Evaluation

Evaluate the following architecture decisions:

1. A team wants to implement event sourcing for a simple CRUD application.
   What advice would you give?

2. A system uses synchronous REST calls between all services. What
   problems might arise, and how would you address them?

3. A company wants to adopt microservices but has a team of 5 developers.
   What factors should they consider?

## Exercise 4: Design Exercise

Design an architecture for the following system:

**Requirements:**
- E-commerce platform with 1M+ daily users
- Product catalog with 100K+ products
- Order processing with payment integration
- Real-time inventory tracking
- Personalized recommendations
- Multi-region deployment

**Deliverables:**
1. High-level architecture diagram (describe in text)
2. Service decomposition with responsibilities
3. Data management strategy
4. Communication patterns between services
5. Resilience and failure handling approach

## Exercise 5: CAP Theorem Application

For each system, choose between consistency and availability, and
justify your choice:

1. **Banking system** — Account balance updates
2. **Social media** — Like counts on posts
3. **E-commerce** — Product inventory levels
4. **Collaborative document editing** — Real-time text changes
5. **IoT sensor network** — Temperature readings

## Exercise 6: Pattern Composition

Explain how the following patterns work together in a microservices
architecture:

1. **API Gateway + BFF + Microservices** — How do they complement each other?
2. **CQRS + Event Sourcing + Saga** — How do they address different concerns?
3. **Service Mesh + Circuit Breaker + Retry** — How do they provide resilience?

## Exercise 7: Failure Scenario Analysis

Analyze the following failure scenarios and propose solutions:

1. A payment service becomes slow (10s response times) during peak hours.
2. A database primary fails and failover takes 30 seconds.
3. A message broker loses messages due to a bug.
4. A deployment introduces a bug that causes memory leaks.
5. A third-party API changes its response format without notice.

## Exercise 8: Architecture Decision Records

Write ADRs for the following decisions:

1. **Decision**: Use Apache Kafka as the event backbone
   - Context: Need for event-driven architecture with replay capability
   - Alternatives: RabbitMQ, AWS SQS, Google Pub/Sub

2. **Decision**: Adopt microservices architecture
   - Context: Monolith has become a bottleneck
   - Alternatives: Modular monolith, service-oriented architecture

3. **Decision**: Implement CQRS for the order management system
   - Context: Read and write workloads have very different characteristics
   - Alternatives: Single model with optimizations, read replicas
