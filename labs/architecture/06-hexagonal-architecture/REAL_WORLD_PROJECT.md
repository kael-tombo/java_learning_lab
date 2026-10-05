# Real-World Project — Hexagonal Architecture

## Scenario

A payment processing platform handles transactions for multiple payment
methods (credit cards, bank transfers, digital wallets) across different
regions with varying regulatory requirements. The platform must integrate
with dozens of external payment providers, fraud detection services, and
regulatory reporting systems while keeping the core payment logic stable
and testable.

## System Overview

The platform is structured with a pure core surrounded by adapters:

| Layer | Components |
|-------|-----------|
| Core Domain | Payment, Refund, Settlement, Compliance rules |
| Driving Ports | Payment API, Refund API, Admin API, Webhook Receiver |
| Driving Adapters | REST controllers, gRPC services, CLI tools |
| Driven Ports | PaymentProvider, FraudService, ComplianceService, NotificationService |
| Driven Adapters | Stripe, PayPal, Adyen adapters; AWS SQS, SNS adapters |

## Architecture Decisions

### Core Design
- **Pure domain logic** — no framework annotations, no database dependencies
- **Rich domain model** — payments, refunds, and settlements as aggregates
- **Domain events** — emitted by core, handled by adapters
- **Ports as interfaces** — defined in core, implemented by adapters

### Adapter Strategy
- **One adapter per external system** — Stripe adapter, PayPal adapter, etc.
- **Adapter isolation** — changes to Stripe API don't affect core or other adapters
- **Testing adapters separately** — integration tests with real or sandbox APIs
- **In-memory adapters for development** — fast local development without external dependencies

### Dependency Management
- **Compile-time enforcement** — core module has no dependencies on adapter modules
- **Dependency injection at composition root** — adapters wired together in main application
- **ArchUnit tests** — automated tests enforce architectural boundaries

## Implementation Phases

### Phase 1: Core Foundation
1. Design domain model (Payment, Refund, Settlement aggregates)
2. Define ports for all external interactions
3. Implement core business logic with comprehensive unit tests
4. Set up project structure enforcing dependency rules

### Phase 2: Primary Adapters
5. Implement REST API adapters (driving)
6. Implement database adapters (driven)
7. Implement primary payment provider adapter
8. Implement notification adapters

### Phase 3: Scale
9. Add additional payment provider adapters
10. Implement fraud detection adapter
11. Add compliance reporting adapters
12. Implement webhook receiver adapters

### Phase 4: Operations
13. Add monitoring and logging adapters
14. Implement feature flag adapters
15. Add metrics and tracing adapters
16. Build adapter health check system

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Alistair Cockburn — Hexagonal Architecture**: https://alistair.cockburn.us/hexagonal-architecture/
  The original article by Alistair Cockburn introducing the hexagonal
  architecture pattern, explaining ports and adapters and the rationale
  behind the approach.

- **Baeldung — Hexagonal Architecture in Java**: https://www.baeldung.com/hexagonal-architecture-ddd-spring
  Practical guide to implementing hexagonal architecture with Java and Spring,
  including code examples and testing strategies.

## Success Metrics

- Core domain test coverage: over 95%
- Core test execution time: under 10 seconds
- New payment provider integration: under 2 weeks
- Zero framework dependencies in core
- Architecture boundary violations: zero (enforced by automated tests)

## Lessons from Production

1. **Enforce boundaries with tooling** — architectural boundaries that
   aren't enforced by tests or build rules will erode over time.

2. **Start with in-memory adapters** — they make development fast and
   testing easy; add real adapters when the core is stable.

3. **Don't over-abstract** — not every external call needs a port/adapter;
   reserve the pattern for things that actually change or need testing.

4. **Core events are powerful** — domain events emitted by the core enable
   loose coupling with adapters and make the system more extensible.
