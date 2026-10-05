# Quiz — Architecture Deep Dive

## Section 1: Fundamental Concepts

**Q1:** What is the primary goal of the Dependency Inversion Principle?

A) Reduce the number of dependencies in a system
B) Make high-level modules depend on low-level modules
C) Make both high-level and low-level modules depend on abstractions
D) Eliminate all dependencies between modules

**Answer:** C — Both high-level and low-level modules should depend on
abstractions, not on each other directly.

---

**Q2:** According to the CAP theorem, which two guarantees can a
distributed system provide simultaneously during a network partition?

A) Consistency and Availability
B) Consistency and Partition Tolerance
C) Availability and Partition Tolerance
D) All three can be provided simultaneously

**Answer:** C — During a network partition, a system must choose between
consistency and availability; partition tolerance is mandatory.

---

**Q3:** What is the main difference between architectural patterns and
design patterns?

A) There is no difference; they are the same
B) Architectural patterns operate at system level; design patterns at component level
C) Design patterns are more important than architectural patterns
D) Architectural patterns are only used in distributed systems

**Answer:** B — Architectural patterns address system-level organization,
while design patterns address component-level solutions.

## Section 2: Architectural Patterns

**Q4:** In CQRS, what does the "command" side typically handle?

A) Read operations and queries
B) Write operations that change state
C) Caching and performance optimization
D) User interface rendering

**Answer:** B — Commands represent intent to change state and are handled
by the write model in CQRS.

---

**Q5:** What is the primary purpose of the Saga pattern?

A) To improve query performance
B) To manage distributed transactions without distributed locks
C) To synchronize data across multiple databases
D) To provide real-time analytics

**Answer:** B — Sagas manage distributed transactions through a sequence
of local transactions with compensating actions.

---

**Q6:** In Event Sourcing, how is current state determined?

A) By reading the latest database record
B) By replaying all events from the beginning
C) By querying a materialized view
D) By checking the cache

**Answer:** B — Current state is derived by replaying the sequence of
immutable events.

## Section 3: Resilience Patterns

**Q7:** What does a circuit breaker do when it is in the "open" state?

A) Allows all requests to pass through
B) Blocks all requests and fails fast
C) Allows a limited number of test requests
D) Retries failed requests automatically

**Answer:** B — In the open state, the circuit breaker blocks all requests
and fails fast without calling the failing service.

---

**Q8:** What is the purpose of the Strangler Fig pattern?

A) To improve application performance
B) To gradually migrate a legacy system to a new architecture
C) To handle high traffic loads
D) To provide failover capabilities

**Answer:** B — The Strangler Fig pattern gradually replaces a legacy system
by building a new system around its edges.

## Section 4: Advanced Concepts

**Q9:** What is the main advantage of a service mesh over implementing
cross-cutting concerns in each service?

A) Better performance
B) Consistent behavior without application code changes
C) Simpler debugging
D) Lower resource consumption

**Answer:** B — Service mesh provides consistent cross-cutting behavior
(security, observability, traffic management) without requiring changes
to application code.

---

**Q10:** In Platform Engineering, what is a "golden path"?

A) The most expensive infrastructure option
B) A paved road for common workflows with built-in best practices
C) A path that only senior engineers can use
D) A deprecated approach to development

**Answer:** B — Golden paths are standardized, self-service workflows
that incorporate best practices and reduce cognitive load on developers.

## Section 5: Scenario-Based

**Q11:** A system needs to support multiple consistency models for
different use cases (strong consistency for financial transactions,
eventual consistency for analytics). Which pattern best supports this?

A) Circuit Breaker
B) CQRS
C) Saga
D) Strangler Fig

**Answer:** B — CQRS allows different consistency models for read and
write sides, supporting multiple consistency requirements.

---

**Q12:** A company wants to migrate from a monolith to microservices
but cannot afford downtime or a big-bang rewrite. Which approach should
they use?

A) Blue-green deployment
B) Strangler Fig pattern
C) Canary releases
D) Feature flags

**Answer:** B — The Strangler Fig pattern enables gradual migration
without downtime or big-bang rewrites.

---

**Q13:** Which pattern would you use to prevent cascading failures
when a downstream service becomes unavailable?

A) API Composition
B) Circuit Breaker
C) Event Sourcing
D) BFF Pattern

**Answer:** B — Circuit breakers prevent cascading failures by failing
fast when a downstream service is unavailable.

---

**Q14:** What is the primary benefit of using a BFF (Backend for Frontend)
pattern?

A) Reduced database load
B) Client-specific API optimization
C) Improved security
D) Simplified deployment

**Answer:** B — BFFs provide client-specific API optimization, tailoring
responses to each frontend's needs.

---

**Q15:** In a microservices architecture, what is the main challenge
that the Saga pattern addresses?

A) Service discovery
B) Distributed transactions
C) Load balancing
D) API versioning

**Answer:** B — The Saga pattern addresses the challenge of managing
distributed transactions across multiple services.
