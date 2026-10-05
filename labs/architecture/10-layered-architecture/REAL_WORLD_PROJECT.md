# Real-World Project — Layered Architecture

## Scenario

A hospital management system handles patient registration, appointments,
medical records, billing, and reporting. The system must support multiple
user roles (doctors, nurses, administrators, patients), integrate with
medical devices and lab systems, and maintain strict data privacy. The
development team is large and distributed, requiring clear structure and
separation of concerns.

## System Overview

The system uses a four-layer architecture:

| Layer | Components | Responsibility |
|-------|-----------|---------------|
| Presentation | Web portal, mobile app, device interfaces | User interaction |
| Application | API controllers, use case orchestration | Request handling |
| Domain | Entities, value objects, domain services | Business rules |
| Infrastructure | Database, external systems, messaging | Technical concerns |

## Architecture Decisions

### Layer Responsibilities
- **Presentation Layer**: Web portal for staff, mobile app for patients,
  integration interfaces for medical devices
- **Application Layer**: API controllers, authentication, authorization,
  request validation, use case orchestration
- **Domain Layer**: Patient, Appointment, MedicalRecord, Invoice entities;
  business rules for scheduling, treatment protocols, billing
- **Infrastructure Layer**: PostgreSQL database, HL7/FHIR integrations,
  message queue, file storage

### Communication Patterns
- **Strict downward communication**: each layer calls only the layer below
- **DTOs between layers**: prevent domain entities from leaking upward
- **Dependency injection**: infrastructure implementations injected into domain
- **Interface segregation**: domain defines interfaces, infrastructure implements

### Data Flow
1. Request arrives at Presentation layer
2. Presentation delegates to Application layer
3. Application coordinates Domain layer use cases
4. Domain enforces business rules
5. Infrastructure handles persistence and external calls
6. Response flows back up through layers

## Implementation Phases

### Phase 1: Foundation
1. Set up project structure with four layers
2. Implement domain model with business rules
3. Build infrastructure layer (database, integrations)
4. Create application layer services

### Phase 2: User Interfaces
5. Build web portal for hospital staff
6. Develop mobile app for patients
7. Implement device integration interfaces
8. Add authentication and authorization

### Phase 3: Integration
9. Integrate with lab systems (HL7/FHIR)
10. Add medical device data ingestion
11. Implement billing system integration
12. Add reporting and analytics interfaces

### Phase 4: Scale
13. Optimize database queries and caching
14. Add message queue for async processing
15. Implement audit logging across layers
16. Add monitoring and health checks

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Microsoft — Layered Architecture**: https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/layered
  Microsoft's Azure architecture guide on layered architecture,
  including layer responsibilities, communication patterns, and best practices.

- **Oracle — Core J2EE Patterns**: https://www.oracle.com/java/technologies/core-j2ee-patterns.html
  Oracle's documentation on J2EE patterns including layered architecture,
  separating presentation, business, and data access concerns.

## Success Metrics

- Layer dependency violations: zero (enforced by architecture tests)
- Domain layer test coverage: over 90%
- New feature implementation: changes localized to appropriate layers
- Developer onboarding time: under 1 week
- System uptime: 99.9%

## Lessons from Production

1. **Enforce layer boundaries** — without automated checks, developers
   will take shortcuts; use architecture tests to prevent violations.

2. **Avoid anemic domain models** — business logic in services with
  entities as data bags leads to transaction scripts; push logic into
   entities where possible.

3. **DTOs are essential** — exposing domain entities through layers
   creates coupling; use DTOs to maintain layer independence.

4. **Layered architecture scales teams** — clear boundaries allow
   multiple teams to work on different layers simultaneously.
