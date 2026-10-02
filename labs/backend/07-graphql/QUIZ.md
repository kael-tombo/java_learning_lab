# Quiz: GraphQL Federation Gateway (Lab 07)

**Topic:** GraphQL Schema Stitching / Federation Resolver  
**Difficulty:** Medium  
**Time Limit:** 15 minutes

---

## Questions

### 1. Core Concept
What is GraphQL Federation?
- A) A single GraphQL schema for all services
- B) Composing multiple GraphQL schemas into a unified graph
- C) A REST-to-GraphQL adapter
- D) A GraphQL caching layer

### 2. Architecture
In the `FederationGateway` implementation, what is the role of `ServiceSchema`?
- A) Represents a downstream GraphQL service and its type/resolver mappings
- B) Defines the gateway's unified schema
- C) Handles HTTP routing to services
- D) Manages DataLoader instances

### 3. Entity Resolution
What is the purpose of `__resolveReference` in federation?
- A) Resolve a field within the same service
- B) Fetch an entity by its key from the owning service
- C) Resolve schema conflicts
- D) Validate query syntax

### 4. DataLoader
What problem does the `DataLoader` pattern solve?
- A) N+1 query problem when resolving lists of entities
- B) Schema stitching conflicts
- C) Authentication
- D) Query complexity analysis

### 5. Type Extension
How does the `extendType` method work?
- A) Modifies the original service's schema
- B) Adds fields to a base type from another service's resolvers
- C) Creates a new merged type
- D) Overrides existing field resolvers

### 6. Query Execution
In `executeQuery()`, how are errors handled?
- A) Entire query fails on first error
- B) Errors are collected, partial data returned
- C) Errors are logged and ignored
- D) Only field-level errors are captured

### 7. Field Resolution
When resolving a field, what is checked first?
- A) Base type resolvers
- B) Extension fields (from other services)
- C) Entity resolvers
- D) Parent map values

### 8. Batching
How does `DataLoader.batchLoad()` work?
- A) Immediately executes batch for each key
- B) Collects keys for 1ms, then executes single batch load
- C) Waits for all keys before loading
- D) Loads keys one at a time

### 9. Service Registration
What happens when `registerService()` is called?
- A) Only schema is stored
- B) Schema + entity resolvers are merged into gateway
- C) HTTP health check is performed
- D) Schema is validated against federation spec

### 10. Error Handling
What does `GraphQLError` contain?
- A) Error code and path only
- B) Message and optional exception
- C) Full stack trace
- D) HTTP status code

---

## Answers

| # | Answer | Explanation |
|---|--------|-------------|
| 1 | **B** | Federation composes multiple subgraph schemas into a single supergraph. |
| 2 | **A** | `ServiceSchema` holds a service's types, field resolvers, and entity resolvers. |
| 3 | **B** | `__resolveReference` allows the gateway to fetch an entity (e.g., User) by its key (`{id: "1"}`) from the service that owns it. |
| 4 | **A** | DataLoader batches multiple `load(key)` calls into a single `loadAll(keys)` request, eliminating N+1. |
| 5 | **B** | `extendType("User", "order-service", ...)` adds `orders` field to User type, resolved by order-service. |
| 6 | **B** | Errors are collected in a list; successfully resolved fields still return data (partial results). |
| 7 | **B** | Extension fields are checked first (line 253-260), then base type resolvers. |
| 8 | **B** | `scheduler.schedule(() -> batchLoad(), 1, TimeUnit.MILLISECONDS)` — brief window to collect keys. |
| 9 | **B** | Schema types and entity resolvers are added to gateway's maps for cross-service resolution. |
| 10 | **B** | `GraphQLError` record: `message` and `exception` (nullable). |

---

## Scoring

| Score | Level |
|-------|-------|
| 9-10 | Expert — Federation architecture master |
| 7-8 | Proficient — Understands stitching, DataLoader, entities |
| 5-6 | Developing — Review entity resolution and extensions |
| <5 | Beginner — Re-read LEETCODE_SOLUTION and test cases |

---

## Further Study

- Read `MOCK_INTERVIEW.md` (if exists) or study Apollo Federation spec
- Explore `@apollo/gateway` and `@apollo/subgraph` implementations
- Practice: Add subscription support, query complexity limiting