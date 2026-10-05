# Real-World Project — Clean Architecture

## Scenario

An insurance claims processing system must handle complex business rules
that change frequently due to regulatory requirements, integrate with
multiple external systems (medical providers, vehicle assessment services,
fraud detection), and support multiple channels (web portal, mobile app,
partner APIs, agent workstations). The system must remain maintainable
as technologies and regulations evolve over decades.

## System Overview

The system follows Clean Architecture with clear layer separation:

| Layer | Components |
|-------|-----------|
| Entities | Claim, Policy, Coverage, Beneficiary, business rules |
| Use Cases | SubmitClaim, ApproveClaim, RejectClaim, InvestigateClaim, SettleClaim |
| Interface Adapters | REST controllers, gRPC services, message consumers, presenters |
| Frameworks & Drivers | Spring Boot, PostgreSQL, Kafka, external API clients |

## Architecture Decisions

### Entity Design
- **Rich domain model** — claims and policies as aggregates with behavior
- **Enterprise business rules** — coverage limits, eligibility checks, fraud indicators
- **Framework-free entities** — pure Java/Kotlin with no annotations

### Use Case Design
- **One class per use case** — SubmitClaim, ApproveClaim, etc.
- **Input/output ports** — interfaces for repositories and services
- **Application-specific rules** — claim routing, approval workflows, SLA tracking
- **Transaction boundaries** — each use case is a transaction

### Interface Adapters
- **Multiple controllers** — REST for web, gRPC for internal services, Kafka consumers for events
- **Presenters per view** — different formats for web, mobile, and partner APIs
- **Gateway implementations** — database repositories, external service clients

### Framework Independence
- **Spring only in outer layer** — use cases and entities have zero Spring dependencies
- **Database abstraction** — repository interfaces in use case layer
- **Configuration in framework layer** — all wiring in the outermost layer

## Implementation Phases

### Phase 1: Core Foundation
1. Design entity model (Claim, Policy, Coverage)
2. Implement enterprise business rules
3. Define use case ports and interfaces
4. Build use case implementations with comprehensive tests

### Phase 2: Primary Flows
5. Implement SubmitClaim use case with all adapters
6. Build REST API controllers and presenters
7. Implement database repositories
8. Add external service integrations

### Phase 3: Multi-Channel
9. Add gRPC service for internal consumers
10. Implement Kafka event consumers and producers
11. Build mobile-optimized presenters
12. Add partner API adapters

### Phase 4: Evolution
13. Implement new regulations as use case changes
14. Swap database technology without core changes
15. Add new external service integrations
16. Build new UI without touching business logic

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Robert C. Martin — Clean Architecture**: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
  Uncle Bob's original article on Clean Architecture, explaining the
  dependency rule, the layers, and the philosophy behind the approach.

- **Clean Architecture Example**: https://github.com/mattia-battiston/clean-architecture-sandbox
  Practical implementation examples of Clean Architecture with multiple
  use cases, demonstrating layer separation and dependency management.

## Success Metrics

- Entity and use case test coverage: over 90%
- Core test execution time: under 30 seconds
- Zero framework dependencies in inner layers
- New channel integration: under 1 week
- Regulation change implementation: use cases only, no entity changes

## Lessons from Production

1. **The dependency rule is everything** — if inner layers leak to outer
   layers, the architecture degrades; enforce it with automated tests.

2. **Use cases are the most valuable code** — they encode business processes;
   invest in their design and testing.

3. **Don't start with full Clean Architecture** — for simple CRUD apps,
   the overhead isn't justified; introduce layers as complexity grows.

4. **Presenters solve the impedance mismatch** — different views need
   different data shapes; presenters handle this without polluting use cases.
