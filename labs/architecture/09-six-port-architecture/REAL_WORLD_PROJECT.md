# Real-World Project — Six-Port Architecture

## Scenario

A supply chain management system coordinates between manufacturers,
distributors, retailers, and logistics providers. The system must
integrate with dozens of external systems, support multiple user interfaces
(web, mobile, EDI), and handle real-time events from IoT sensors and
tracking systems. The core supply chain logic must remain stable while
external systems change frequently.

## System Overview

The system defines six ports for all external interactions:

| Port | Direction | Purpose | Adapters |
|------|-----------|---------|----------|
| WebApiPort | Driving | Web UI interactions | REST controller |
| MobileApiPort | Driving | Mobile app interactions | GraphQL resolver |
| EDIReceiverPort | Driving | EDI message ingestion | EDI parser |
| DatabasePort | Driven | Data persistence | PostgreSQL adapter |
| NotificationPort | Driven | Alerts and notifications | SMS/Email/Push adapters |
| PartnerApiPort | Driven | External partner systems | HTTP/SOAP adapters |

## Architecture Decisions

### Core Design
- **Pure domain logic** — supply chain rules, inventory optimization, order routing
- **Framework-free core** — no Spring, no database dependencies
- **Port interfaces** — all six ports defined as interfaces in the core
- **Domain events** — emitted by core, handled by adapters

### Adapter Strategy
- **One adapter per external system** — each partner has its own adapter
- **Adapter isolation** — changes to one partner don't affect others
- **Protocol adapters** — EDI, HTTP, SOAP, message queues
- **Testing adapters separately** — integration tests with real or mock external systems

### Symmetry
- **Driving ports** — core defines input interfaces, adapters implement them
- **Driven ports** — core defines output interfaces, adapters implement them
- **Same principles** — both directions follow identical design patterns

## Implementation Phases

### Phase 1: Core Foundation
1. Design supply chain domain model
2. Define all six port interfaces
3. Implement core business logic
4. Build comprehensive core test suite with mock ports

### Phase 2: Primary Adapters
5. Implement Web API adapter (REST)
6. Implement database adapter (PostgreSQL)
7. Implement notification adapter (email/SMS)
8. Implement primary partner API adapter

### Phase 3: Additional Interfaces
9. Implement Mobile API adapter (GraphQL)
10. Implement EDI receiver adapter
11. Add additional partner API adapters
12. Implement IoT event receiver adapter

### Phase 4: Operations
13. Add monitoring and logging adapters
14. Implement feature flag adapters
15. Add metrics and tracing adapters
16. Build adapter health check system

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Hexagonal Architecture**: https://alistair.cockburn.us/hexagonal-architecture/
  Alistair Cockburn's original article on hexagonal architecture,
  the foundation for six-port architecture, explaining ports and adapters.

- **Domain-Driven Design**: https://domainlanguage.com/ddd/
  Eric Evans' DDD resource, covering strategic and tactical patterns
  that complement six-port architecture in complex domains.

## Success Metrics

- Core domain test coverage: over 95%
- Core test execution time: under 15 seconds
- Zero framework dependencies in core
- New partner integration: under 1 week
- Adapter swap without core changes: 100% of the time

## Lessons from Production

1. **Six ports is a guideline, not a rule** — some systems need more or
   fewer ports; the principle of explicit ports matters more than the count.

2. **Adapters are where complexity lives** — external system integration
   is hard; isolate it in adapters so it doesn't infect the core.

3. **Test the core exhaustively** — the core is the most valuable code;
   comprehensive tests with mock ports ensure its correctness.

4. **Plan for adapter evolution** — external systems change; adapters
   must be designed for change without affecting the core.
