# Theory — Architecture Deep Dive

## Fundamental Concepts

### What is Software Architecture?

Software architecture is the fundamental organization of a system,
embodied in its components, their relationships to each other and
the environment, and the principles governing its design and evolution.

### Key Architectural Principles

1. **Separation of Concerns** — Divide a system into distinct sections,
   each addressing a separate concern.

2. **Single Responsibility** — Each component should have one reason to change.

3. **Dependency Inversion** — Depend on abstractions, not concretions.

4. **Interface Segregation** — Many specific interfaces are better than
   one general-purpose interface.

5. **Don't Repeat Yourself (DRY)** — Every piece of knowledge must have
   a single, unambiguous representation.

### Architectural Patterns vs Design Patterns

| Aspect | Architectural Patterns | Design Patterns |
|--------|----------------------|-----------------|
| Scope | System-level | Component-level |
| Abstraction | High | Medium |
| Examples | Microservices, CQRS, EDA | Factory, Observer, Strategy |
| Impact | System-wide | Localized |

### Quality Attributes

- **Performance** — Response time, throughput, resource utilization
- **Scalability** — Ability to handle growth in load
- **Availability** — Uptime and reliability
- **Maintainability** — Ease of modification and extension
- **Testability** — Ease of testing
- **Security** — Protection against threats
- **Modifiability** — Ease of making changes

### Distributed Systems Challenges

1. **Network latency** — Communication takes time
2. **Partial failures** — Some components may fail
3. **Consistency** — Data may be inconsistent across nodes
4. **Concurrency** — Multiple operations simultaneously
5. **Security** — Network communication must be secured
6. **Observability** — Understanding system behavior

### CAP Theorem

The CAP theorem states that a distributed system can provide at most
two of three guarantees:

- **Consistency** — Every read receives the most recent write
- **Availability** — Every request receives a response
- **Partition tolerance** — System continues despite network partitions

In practice, partition tolerance is mandatory, so systems choose
between consistency (CP) and availability (AP).

### Consistency Models

1. **Strong consistency** — All nodes see the same data simultaneously
2. **Eventual consistency** — All nodes eventually see the same data
3. **Causal consistency** — Causally related operations are seen in order
4. **Read-your-writes** — A client always sees its own writes
5. **Monotonic reads** — A client never sees older data after seeing newer

### Architectural Decision Records (ADRs)

ADRs capture architectural decisions, including:
- **Context** — The situation requiring a decision
- **Decision** — The chosen approach
- **Consequences** — The results of the decision
- **Status** — Proposed, accepted, deprecated, superseded

### Evolutionary Architecture

Evolutionary architecture supports incremental change across multiple
dimensions:
- **Fitness functions** — Objective measures of architectural characteristics
- **Guided change** — Architecture evolves toward desired characteristics
- **Incremental change** — Small, frequent changes rather than big rewrites
