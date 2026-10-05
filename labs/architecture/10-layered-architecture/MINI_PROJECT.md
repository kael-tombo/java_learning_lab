# Mini Project — Layered Architecture

## Goal

Build a customer relationship management (CRM) system using a classic
three-layer architecture: Presentation Layer, Business Logic Layer, and
Data Access Layer. Demonstrate clear separation and downward-only
communication.

## Requirements

### Layer 1: Presentation Layer

**Components:**
- `CustomerController` — REST API for customer CRUD operations
- `OrderController` — REST API for order management
- `ReportController` — REST API for generating reports

**Responsibilities:**
- Handle HTTP requests and responses
- Input validation (format, required fields)
- Format output for clients
- No business logic

### Layer 2: Business Logic Layer

**Components:**
- `CustomerService` — customer business rules
- `OrderService` — order processing logic
- `ReportService` — report generation logic

**Business Rules:**
- Customer email must be unique
- Order total must match sum of line items
- Cannot delete customer with active orders
- Discounts apply only to customers with loyalty status

**Responsibilities:**
- Enforce business rules
- Coordinate transactions
- No knowledge of HTTP or database details

### Layer 3: Data Access Layer

**Components:**
- `CustomerRepository` — customer persistence
- `OrderRepository` — order persistence
- `ReportRepository` — report data queries

**Responsibilities:**
- Database CRUD operations
- Query optimization
- No business logic

## Technical Specifications

1. **Layer communication**
   - Presentation calls Business Logic only
   - Business Logic calls Data Access only
   - No upward or skip-layer calls

2. **Data transfer**
   - DTOs between Presentation and Business Logic
   - Entities between Business Logic and Data Access
   - No database entities in Presentation layer

3. **Error handling**
   - Data Access throws data exceptions
   - Business Logic throws business exceptions
   - Presentation handles and formats errors

## Steps

1. Create project structure with three layers
2. Implement Data Access layer (repositories)
3. Implement Business Logic layer (services)
4. Implement Presentation layer (controllers)
5. Add DTOs for inter-layer communication
6. Write unit tests for each layer independently
7. Write integration tests for the full stack
8. Verify no upward dependencies exist

## Acceptance Criteria

- [ ] Presentation layer has no business logic
- [ ] Business logic layer has no HTTP or database code
- [ ] Data access layer has no business rules
- [ ] Layers communicate only downward
- [ ] Each layer is testable independently
- [ ] DTOs are used between layers

## Stretch Goals

- Add a service layer between presentation and business logic
- Implement cross-cutting concerns (logging, security) as aspects
- Add caching layer between business logic and data access
- Implement layer-specific exception handling
