# Mini Project — Domain-Driven Design

## Goal

Model a library management system using DDD tactical patterns: entities,
value objects, aggregates, repositories, domain services, and domain events.
The focus is on creating a rich domain model that captures business rules.

## Requirements

### Core Domain: Library Management

**Aggregates:**
- `Book` (aggregate root) — has ISBN, title, author, status
- `Member` (aggregate root) — has name, membership status, borrowed books
- `Loan` (aggregate root) — connects Member to Book, tracks dates

**Value Objects:**
- `ISBN` — validates format
- `Money` — for late fees
- `DateRange` — for loan periods

**Domain Events:**
- `BookBorrowed` — emitted when a loan is created
- `BookReturned` — emitted when a book is returned
- `LoanOverdue` — emitted when a loan passes its due date

**Repositories:**
- `BookRepository` — persistence for Book aggregate
- `MemberRepository` — persistence for Member aggregate
- `LoanRepository` — persistence for Loan aggregate

**Domain Services:**
- `LoanService` — handles borrowing logic across aggregates
- `FineCalculationService` — calculates late fees

## Technical Specifications

1. **Aggregate design**
   - Enforce invariants within aggregate boundaries
   - Only aggregate roots are accessible from outside
   - Use aggregate ID references between aggregates

2. **Value objects**
   - Immutable with value-based equality
   - Self-validating on construction

3. **Repositories**
   - One repository per aggregate root
   - Interface defined in domain layer
   - Implementation in infrastructure layer

4. **Domain events**
   - Emitted by aggregates when state changes
   - Handled by application layer

5. **Ubiquitous language**
   - Name classes and methods using business terms
   - Avoid technical names in domain layer

## Steps

1. Identify aggregates, entities, and value objects
2. Implement value objects with validation
3. Implement aggregates with invariant enforcement
4. Define repository interfaces
5. Implement domain services
6. Add domain events
7. Implement application services coordinating the flow
8. Write unit tests for domain logic
9. Write integration tests for repositories

## Acceptance Criteria

- [ ] Aggregates enforce invariants (e.g., can't borrow a borrowed book)
- [ ] Value objects validate on construction
- [ ] Repositories persist and retrieve aggregates correctly
- [ ] Domain events are emitted on state changes
- [ ] Domain layer has no infrastructure dependencies
- [ ] Business rules are expressed in ubiquitous language

## Stretch Goals

- Implement specification pattern for complex queries
- Add anti-corruption layer for external system integration
- Implement domain event handlers for side effects
- Add unit of work pattern for transaction management
