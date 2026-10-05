# Flashcards — Architecture Deep Dive

## Architectural Patterns

### Microservices
**Q:** What is the primary characteristic of microservices architecture?
**A:** Small, independently deployable services that own their data and
communicate over the network.

---

### Event-Driven Architecture (EDA)
**Q:** What is the core concept of EDA?
**A:** Systems communicate through events — immutable facts that represent
something that happened — rather than direct calls.

---

### CQRS
**Q:** What does CQRS stand for and what does it separate?
**A:** Command Query Responsibility Segregation — it separates read (query)
operations from write (command) operations.

---

### Saga Pattern
**Q:** What problem does the Saga pattern solve?
**A:** Managing distributed transactions across multiple services without
distributed locks, using local transactions and compensating actions.

---

### Event Sourcing
**Q:** How does Event Sourcing store state?
**A:** As a sequence of immutable events; current state is derived by
replaying events.

---

### Hexagonal Architecture
**Q:** What are the core concepts of Hexagonal Architecture?
**A:** Ports (interfaces) and Adapters (implementations) — the core
application is isolated from external concerns.

---

### Clean Architecture
**Q:** What is the key rule of Clean Architecture?
**A:** The Dependency Rule — source code dependencies point inward only;
inner layers have no knowledge of outer layers.

---

### Strangler Fig Pattern
**Q:** What is the Strangler Fig pattern used for?
**A:** Gradually migrating a legacy system to a new architecture by
building around the edges of the old system.

---

### BFF Pattern
**Q:** What does BFF stand for and what is its purpose?
**A:** Backend for Frontend — dedicated backend services for each frontend
client, optimized for that client's specific needs.

---

### Circuit Breaker
**Q:** What are the three states of a circuit breaker?
**A:** Closed (normal operation), Open (fail fast), Half-Open (testing recovery).

---

### Service Mesh
**Q:** What are the two main components of a service mesh?
**A:** Data plane (sidecar proxies that handle traffic) and control plane
(centralized management and configuration).

---

### Platform Engineering
**Q:** What is the primary goal of Platform Engineering?
**A:** Building internal developer platforms that provide self-service
infrastructure, tooling, and automation to product teams.

## Key Principles

### Separation of Concerns
**Q:** What does Separation of Concerns mean?
**A:** Dividing a system into distinct sections, each addressing a separate
concern, to reduce complexity and improve maintainability.

---

### Single Responsibility Principle
**Q:** What does the Single Responsibility Principle state?
**A:** Each component should have one reason to change — it should have
only one responsibility.

---

### Dependency Inversion Principle
**Q:** What does the Dependency Inversion Principle state?
**A:** High-level modules should not depend on low-level modules; both
should depend on abstractions.

---

### CAP Theorem
**Q:** What does the CAP theorem state?
**A:** A distributed system can provide at most two of three guarantees:
Consistency, Availability, and Partition Tolerance.

---

### Ubiquitous Language
**Q:** What is Ubiquitous Language in DDD?
**A:** A shared vocabulary used by developers and domain experts, used
consistently in code, conversation, and documentation.

---

### Bounded Context
**Q:** What is a Bounded Context in DDD?
**A:** An explicit boundary within which a domain model is defined and
applicable, with its own ubiquitous language.

## Quality Attributes

### Scalability
**Q:** What is scalability?
**A:** The ability of a system to handle growth in load by adding resources.

---

### Availability
**Q:** What is availability?
**A:** The proportion of time a system is in a functioning condition,
often measured as uptime percentage.

---

### Maintainability
**Q:** What is maintainability?
**A:** The ease with which a system can be modified, extended, or fixed.

---

### Observability
**Q:** What is observability?
**A:** The ability to understand the internal state of a system by
examining its outputs (logs, metrics, traces).

## Distributed Systems

### Eventual Consistency
**Q:** What is eventual consistency?
**A:** A consistency model where, if no new updates are made, all accesses
will eventually return the last updated value.

---

### Idempotency
**Q:** What is idempotency?
**A:** The property of an operation that it can be applied multiple times
without changing the result beyond the initial application.

---

### Compensating Transaction
**Q:** What is a compensating transaction?
**A:** An operation that semantically undoes a previously committed
transaction when a subsequent step in a business process fails.

---

### Outbox Pattern
**Q:** What is the Outbox pattern?
**A:** A pattern where events are stored in the same database transaction
as the business data, then published to a message broker by a separate process.
