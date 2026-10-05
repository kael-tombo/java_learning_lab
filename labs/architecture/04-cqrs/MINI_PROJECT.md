# Mini Project — CQRS

## Goal

Build a task management application using CQRS to separate command
(write) and query (read) responsibilities. The write side enforces
business rules; the read side provides fast, denormalized views.

## Requirements

### Command Side (Write Model)

**Commands:**
- `CreateTask` — title, description, assignee, due date
- `AssignTask` — reassign to another user
- `CompleteTask` — mark as completed
- `DeleteTask` — remove a task

**Write Model:**
- `Task` aggregate with business rules:
  - Title is required and max 200 chars
  - Cannot complete an already completed task
  - Cannot assign a completed task
  - Due date must be in the future

### Query Side (Read Model)

**Queries:**
- `GetAllTasks` — list all tasks with filters (status, assignee)
- `GetTaskById` — single task with full details
- `GetTasksByAssignee` — tasks grouped by assignee
- `GetOverdueTasks` — tasks past due date

**Read Model:**
- Denormalized tables optimized for queries
- No joins needed for common queries
- Updated asynchronously from domain events

## Technical Specifications

1. **Command handling**
   - Commands are simple DTOs with intent
   - Command handlers validate and execute against write model
   - Commands emit domain events on success

2. **Query handling**
   - Queries return DTOs, not domain entities
   - Read model is a separate data store
   - Queries never modify state

3. **Read model updates**
   - Domain events trigger read model updates
   - Read model is eventually consistent
   - Multiple read models can exist for different queries

4. **Separation**
   - Different packages/modules for command and query sides
   - Different database schemas or tables
   - Clear interfaces between sides

## Steps

1. Define commands and command handlers
2. Implement write model (Task aggregate)
3. Define queries and query handlers
4. Implement read model (denormalized tables)
5. Connect domain events to read model updates
6. Add validation to commands
7. Write tests for command side (business rules)
8. Write tests for query side (read model accuracy)
9. Test eventual consistency behavior

## Acceptance Criteria

- [ ] Commands enforce all business rules
- [ ] Queries return denormalized data without joins
- [ ] Read model updates after commands complete
- [ ] Command and query sides are in separate modules
- [ ] Read model can be rebuilt from event log
- [ ] Queries never modify state

## Stretch Goals

- Implement event sourcing as the write model
- Add multiple read models for different query patterns
- Implement read model rebuild from scratch
- Add caching layer for frequently accessed queries
