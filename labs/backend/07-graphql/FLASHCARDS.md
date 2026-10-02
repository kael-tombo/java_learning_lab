# Flashcards: GraphQL Federation Gateway (Lab 07)

> **Instructions:** Cover the answer side, recall from memory, then reveal. Shuffle periodically.

---

## Core Concepts

| # | Question | Answer |
|---|----------|--------|
| 1 | What is GraphQL Federation? | Composing multiple GraphQL services (subgraphs) into a single unified graph (supergraph) that clients query. |
| 2 | What are the key components? | Gateway (router), Subgraphs (services), Schema Registry, Entity Resolution (`__resolveReference`). |
| 3 | How does federation differ from schema stitching? | Federation is declarative (services define their part + extensions), stitching is imperative (gateway merges programmatically). |
| 4 | What is a subgraph? | A GraphQL service that owns a subset of types and can extend types from other subgraphs. |
| 5 | What is the supergraph? | The composed schema that the gateway exposes to clients — union of all subgraph schemas. |

---

## Entity Resolution

| # | Question | Answer |
|---|----------|--------|
| 6 | What is an entity? | A type that can be resolved by key across subgraphs (e.g., `User @key(fields: "id")`). |
| 7 | What is `__resolveReference`? | A special resolver that fetches an entity by its key representation (e.g., `{__typename: "User", id: "1"}`). |
| 8 | How does the gateway resolve cross-service references? | 1. Query asks for `User.orders` 2. Gateway calls `User` service's `__resolveReference` 3. Gets User with `id` 4. Calls `Order` service for orders. |
| 9 | What is the `_entities` query? | Federation spec query: `_entities(representations: [_Any!]!): [_Entity]!` — batch resolves multiple entities. |
| 10 | What is the `_service` query? | Returns the subgraph's SDL for schema composition: `_service { sdl }`. |

---

## Type Extensions

| # | Question | Answer |
|---|----------|--------|
| 11 | How does service A extend service B's type? | Service A defines `extend type User { orders: [Order] }` with resolver. |
| 12 | What is the `@key` directive? | Defines the unique key for an entity: `@key(fields: "id")` or `@key(fields: "id organizationId")`. |
| 13 | What is `@external`? | Marks a field as owned by another subgraph (reference only). |
| 14 | What is `@requires`? | Specifies fields needed from base type to resolve extension: `@requires(fields: "id")`. |
| 15 | What is `@provides`? | Optimizes by returning additional fields from the extending service. |

---

## DataLoader & Batching

| # | Question | Answer |
|---|----------|--------|
| 16 | What is the N+1 problem? | Resolving a list of N items triggers N separate resolver calls for a nested field. |
| 17 | How does DataLoader solve it? | Collects all keys during same tick, calls `loadAll(keys)` once, returns map of results. |
| 18 | What is the batch window? | Typically 1-10ms (configurable) to collect keys before dispatching batch. |
| 19 | How does DataLoader cache? | Per-request cache: `load(key)` returns same promise for duplicate keys in same request. |
| 20 | What is `DataLoaderRegistry`? | Manages multiple DataLoader instances by name, shared across resolvers. |

---

## Gateway Implementation

| # | Question | Answer |
|---|----------|--------|
| 21 | How does `executeQuery` work? | Iterates root fields, finds owning service, delegates resolution, merges results. |
| 22 | How are nested fields resolved? | Recursively: if parent is Map, resolve child fields against that parent object. |
| 23 | What is `ServiceSchema.resolve()`? | Looks up field resolver for type+field, or extension field, or parent map value. |
| 24 | How are variables handled? | Passed through to field resolvers via `field.arguments()`. |
| 25 | What is `Field` record? | Represents a GraphQL selection: name, alias, typeName, parentType, arguments, selections. |

---

## Error Handling

| # | Question | Answer |
|---|----------|--------|
| 26 | How are resolver errors handled? | Caught, wrapped in `GraphQLError`, added to errors list, field returns `null`. |
| 27 | What is partial response? | Successful fields return data, failed fields return null + error in `errors` array. |
| 28 | How does this differ from REST? | REST typically fails entire request; GraphQL returns what it can. |
| 29 | What errors are NOT caught? | Schema validation errors (caught before execution), transport errors. |

---

## Federation Patterns

| # | Question | Answer |
|---|----------|--------|
| 30 | How to share a type across subgraphs? | Use `@key` on entity, implement `__resolveReference` in owning service. |
| 31 | How to add computed field from another service? | Extend type in extending service: `extend type User { posts: [Post] @requires(fields: "id") }`. |
| 32 | How to handle authentication context? | Pass headers through gateway to subgraphs via context. |
| 33 | How to do distributed tracing? | Propagate trace headers (W3C traceparent) through gateway to all subgraphs. |
| 34 | What is managed federation? | Apollo Studio hosts schema registry, handles composition, provides analytics. |

---

## Performance & Scaling

| # | Question | Answer |
|---|----------|--------|
| 35 | How to optimize query planning? | Gateway creates query plan: sequence of subgraph fetches, parallel where possible. |
| 36 | What is query complexity analysis? | Assign cost to fields, reject queries exceeding threshold (prevent DoS). |
| 37 | How to cache at gateway level? | Cache query plans, cache entity resolution results (with TTL). |
| 38 | How to handle subgraph failures? | Circuit breaker, fallback data, degrade gracefully (partial responses). |

---

## Quick Reference: Key Classes

| Class | Responsibility |
|-------|----------------|
| `FederationGateway` | Main entry point: registers services, executes queries, resolves references |
| `ServiceSchema` | Holds one subgraph's types, resolvers, entity resolvers, extensions |
| `DataLoaderRegistry` | Manages DataLoader instances for batching |
| `DataLoader<K,V>` | Batches `load(key)` calls into `loadAll(keys)` |
| `EntityResolver<T>` | Resolves entity by reference map |
| `FieldResolver` | Resolves a single field given parent + args |

---

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| No DataLoader | N+1 kills performance | Always use DataLoader for list fields |
| Circular references | Infinite recursion | Track visited entities, limit depth |
| Missing `@key` | Can't resolve across services | Add `@key` to all entities |
| Schema conflicts | Composition fails | Use schema registry, validate on deploy |
| No timeout | Hanging requests | Set per-subgraph timeouts |

---

## Related Technologies

| Tool | Role |
|------|------|
| **Apollo Gateway** | Production federation gateway (Node.js) |
| **Apollo Subgraph** | Libraries for building subgraphs (Java, Node, Go, etc.) |
| **GraphQL Java** | JVM GraphQL implementation |
| **DGS Framework** | Netflix's GraphQL for Spring Boot |
| **Schema Registry** | Stores and composes subgraph schemas (Apollo Studio) |