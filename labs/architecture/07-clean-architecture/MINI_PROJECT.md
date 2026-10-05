# Mini Project — Clean Architecture

## Goal

Build an employee management system following Clean Architecture layers:
Entities, Use Cases, Interface Adapters, and Frameworks & Drivers.
Demonstrate that inner layers have zero dependencies on outer layers.

## Requirements

### Layer 1: Entities (Enterprise Business Rules)

**Entities:**
- `Employee` — id, name, email, department, salary, hireDate
- `Department` — id, name, budget
- Business rules:
  - Salary must be positive
  - Email must be unique
  - Department budget cannot be exceeded by total salaries

### Layer 2: Use Cases (Application Business Rules)

**Use Cases:**
- `HireEmployee` — create new employee, assign to department
- `TransferEmployee` — move employee between departments
- `GiveRaise` — increase salary with approval workflow
- `TerminateEmployee` — remove employee, update department budget
- `GetDepartmentReport` — generate department summary

**Use Case Interfaces:**
- Input ports (called by interface adapters)
- Output ports (implemented by interface adapters)

### Layer 3: Interface Adapters

**Controllers:**
- `EmployeeController` — REST API endpoints
- `DepartmentController` — REST API endpoints

**Presenters:**
- `EmployeePresenter` — formats employee data for API response
- `DepartmentReportPresenter` — formats report data

**Gateways:**
- `EmployeeRepository` — persistence interface
- `DepartmentRepository` — persistence interface
- `EmailService` — notification interface

### Layer 4: Frameworks & Drivers

**Frameworks:**
- Spring Boot application
- PostgreSQL database
- REST API with JSON

## Technical Specifications

1. **Dependency rule enforcement**
   - Entities have zero imports from outer layers
   - Use cases import only entities
   - Interface adapters import use cases
   - Frameworks import interface adapters

2. **Data transfer**
   - Use cases receive and return simple data structures
   - Presenters convert use case output to API format
   - Controllers convert API input to use case input

3. **Database independence**
   - Repository interfaces defined in use case layer
   - Implementations in framework layer
   - Easy to swap database implementations

## Steps

1. Implement entities with business rules
2. Define use case input/output ports
3. Implement use cases with business logic
4. Implement controllers and presenters
5. Implement repository interfaces and implementations
6. Wire everything together in the framework layer
7. Write unit tests for entities and use cases
8. Write integration tests for the full stack
9. Verify dependency rule with architecture tests

## Acceptance Criteria

- [ ] Entities have zero framework imports
- [ ] Use cases are testable without Spring or database
- [ ] Controllers delegate to use cases
- [ ] Repositories implement use case-defined interfaces
- [ ] Swapping database requires changes only in framework layer
- [ ] Architecture tests verify dependency rule

## Stretch Goals

- Add multiple presenters for different output formats (JSON, XML, CSV)
- Implement CQRS within the use case layer
- Add event-driven use case triggers
- Implement transaction management at the use case level
