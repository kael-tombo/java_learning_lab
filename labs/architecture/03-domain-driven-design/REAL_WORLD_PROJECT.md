# Real-World Project — Domain-Driven Design

## Scenario

A healthcare platform manages patient records, appointments, billing,
and clinical workflows across multiple hospital departments. The domain
is highly complex with intricate business rules, regulatory requirements,
and the need for different departments to view the same data differently.

## System Overview

The platform is divided into bounded contexts:

| Bounded Context | Responsibility | Key Aggregates |
|-----------------|---------------|----------------|
| Patient Management | Demographics, insurance | Patient, InsurancePolicy |
| Scheduling | Appointments, resources | Appointment, Room, Schedule |
| Clinical | Diagnoses, treatments | PatientRecord, TreatmentPlan |
| Billing | Invoices, payments | Invoice, Payment, Claim |
| Pharmacy | Medications, prescriptions | Prescription, Medication |

## Architecture Decisions

### Strategic Design
- **Core Domain**: Clinical context — most business value, most complexity
- **Supporting Subdomain**: Scheduling — important but not differentiating
- **Generic Subdomain**: Billing — use existing solutions where possible
- **Context Relationships**: Customer/Supplier, Conformist, Anti-Corruption Layer

### Tactical Patterns
- **Aggregates** enforce consistency boundaries for business rules
- **Domain Events** integrate contexts without tight coupling
- **Repositories** abstract persistence from the domain model
- **Domain Services** handle operations spanning multiple aggregates
- **Specifications** encapsulate complex query logic

### Ubiquitous Language
- Each context has its own glossary
- Clinical terms differ from billing terms for the same concept
- Code uses context-specific language (e.g., `Patient` in clinical vs `Client` in billing)

## Implementation Phases

### Phase 1: Strategic Modeling
1. Event storming workshops with domain experts
2. Identify bounded contexts and context map
3. Define ubiquitous language per context
4. Establish context integration patterns

### Phase 2: Tactical Implementation
5. Implement core domain (Clinical) with full DDD patterns
6. Implement supporting contexts with appropriate patterns
7. Build anti-corruption layers for legacy system integration
8. Implement domain events for inter-context communication

### Phase 3: Evolution
9. Refine aggregates based on production usage
10. Extract new bounded contexts as understanding grows
11. Implement context map changes as relationships evolve
12. Add domain event sourcing for audit requirements

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Eric Evans — Domain-Driven Design**: https://domainlanguage.com/ddd/
  The foundational DDD resource by Eric Evans, covering strategic design,
  tactical patterns, and the philosophy of domain modeling.

- **Martin Fowler — Bounded Context**: https://martinfowler.com/bliki/BoundedContext.html
  Martin Fowler's explanation of bounded contexts and their role in
  managing complexity in large systems.

## Success Metrics

- Domain model accurately reflects business processes
- New features are implemented within appropriate bounded contexts
- Cross-context integration happens through well-defined interfaces
- Domain experts review and validate model changes
- Code changes are localized to single contexts

## Lessons from Production

1. **Invest in event storming** — the upfront modeling effort pays dividends
   in reduced miscommunication and clearer boundaries.

2. **Don't apply DDD everywhere** — generic subdomains (email, notifications)
   don't need full tactical patterns; use simpler approaches.

3. **Context maps are living documents** — relationships between contexts
   evolve; keep the map current or it becomes useless.

4. **Ubiquitous language takes discipline** — it's easy to slip back into
   technical jargon; code reviews should enforce language consistency.
