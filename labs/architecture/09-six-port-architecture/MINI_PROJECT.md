# Mini Project — Six-Port Architecture

## Goal

Build a project management system using Six-Port Architecture with three
driving ports (REST API, CLI, Message Consumer) and three driven ports
(Database, Email Service, External API). The core logic is completely
isolated from all six adapters.

## Requirements

### Core (Application Logic)

**Domain Model:**
- `Project` — id, name, description, status, tasks
- `Task` — id, title, description, assignee, status, dueDate
- Business rules:
  - Cannot add tasks to completed projects
  - Cannot assign tasks to non-existent users
  - Task due date must be within project timeline

### Driving Ports (Input)

1. **REST API Port** — `ProjectApiPort`
   - Create project, add task, assign task, get project status

2. **CLI Port** — `ProjectCliPort`
   - Command-line interface for project operations

3. **Message Consumer Port** — `ProjectMessagePort`
   - Consume events from message queue (e.g., user created, deadline approaching)

### Driven Ports (Output)

1. **Database Port** — `ProjectRepository`
   - Save and retrieve projects and tasks

2. **Email Service Port** — `EmailPort`
   - Send notifications for task assignments and deadlines

3. **External API Port** — `UserApiPort`
   - Fetch user information from external user service

### Adapters

- `RestApiAdapter` — implements REST API port
- `CliAdapter` — implements CLI port
- `MessageConsumerAdapter` — implements message consumer port
- `PostgresRepositoryAdapter` — implements database port
- `SmtpEmailAdapter` — implements email port
- `HttpUserApiAdapter` — implements external API port

## Technical Specifications

1. **Port interfaces**
   - All six ports defined as interfaces in the core
   - Core depends only on these interfaces
   - Adapters implement the interfaces

2. **Symmetry**
   - Driving ports: core defines, adapters implement
   - Driven ports: core defines, adapters implement
   - Same design principles for both directions

3. **Testing**
   - Core tested with mock implementations of all six ports
   - Each adapter tested independently
   - Integration tests verify adapter-port contracts

## Steps

1. Define core domain model and business rules
2. Define all six port interfaces
3. Implement core application logic
4. Implement REST API adapter
5. Implement CLI adapter
6. Implement message consumer adapter
7. Implement database adapter
8. Implement email adapter
9. Implement external API adapter
10. Write tests for core with mock ports
11. Write tests for each adapter

## Acceptance Criteria

- [ ] All six ports are interfaces defined in core
- [ ] Core has zero dependencies on adapters
- [ ] Each adapter implements exactly one port
- [ ] Core tests run with mock ports (no infrastructure)
- [ ] Each adapter can be swapped independently
- [ ] All adapters are tested in isolation

## Stretch Goals

- Add a seventh port for caching
- Implement port for event publishing
- Add port for audit logging
- Create composite adapters that implement multiple ports
