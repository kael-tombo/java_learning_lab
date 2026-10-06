# Theory: GraphQL with Spring for GraphQL (DGS)

## The Query Model

GraphQL lets clients declare exactly which fields they need from a graph of
typed objects. A single endpoint accepts operations; a resolver function
computes each field of the response. The response shape mirrors the query —
which kills the REST problems of over-fetching and under-fetching, and
introduces its own.

## DGS vs Spring for GraphQL

Both are annotation programming models over the same `graphql-java` engine:

- **DGS (Netflix)**: schema-first, `@DgsComponent` resolvers, `@DgsQuery`,
  `@DgsData`, codegen from `.graphqls` files into interfaces.
- **Spring for GraphQL**: `@Controller` + `@QueryMapping`/`@SchemaMapping`,
  broader Spring ecosystem features (persisted queries, metrics via
  `ExecutionGraphAdapters`).

Either way: the `.graphqls` schema is the contract. Codegen turns the schema
into typed Java; hand-written DTOs drift from the schema and fail at runtime
with obscure `FieldResolver` errors.

## The N+1 Problem

The trap that defines GraphQL backend work: a resolver for `Book.author` runs
once per `Book`. A query fetching 50 books issues 50 author lookups. The fix
is `DataLoader` — batch each level of the field tree into one query: author
ids of the 50 books become one `SELECT ... WHERE id IN (...)`. Batched,
cached per-request, and ordered to match the input list. Every serious schema
needs loaders at each to-one/to-many boundary or it collapses under its own
elegance.

## Execution Semantics

- Fields of one object resolve in parallel by default; list children
  materialize lazily but loaders batch them.
- Errors are per-field: a failing resolver nullifies its subtree (or bubbles
  per nullability: non-null `!` fields propagate nulls upward). A partial
  data response with an `errors` array is normal; don't try to make GraphQL
  behave like HTTP status codes for domain errors — model them as union
  types (`union SearchResult = Book | NotFoundError`).
- Subscriptions stream over WebSocket; the same N+1/loader discipline
  applies per emission.

## Security and Abuse Controls

GraphQL's flexibility is attack surface:

- **Depth limiting**: `{user{friends{friends{...}}}}` bombs the server.
  Enforce max query depth and max aliases with `MaxQueryDepthInstrumentation`
  / `MaxQueryComplexityInstrumentation`.
- **Cost analysis**: charge a complexity budget per field and reject
  expensive queries before execution.
- **Persisted operations**: only allow client-supplied query strings in dev;
  in prod accept operation names and serve the document server-side — plus
  prevents ad-hoc exfiltration queries.
- **Batching/rate limits**: GraphQL's single endpoint concentrates traffic;
  express concurrency limits per tenant.

## Failure Modes in Production

- A missing loader turns the N+1 pattern into an outage when the schema
  gains one more nested field.
- A `null` from a non-null field triggers "Cannot return null for
  non-nullable field" at runtime and blanks the parent — schema tests that
  assert non-null contracts catch it.
- Resolvers doing their own authorization per field: one forgotten
  `@PreAuthorize` exposes an entire subtree. Centralize via a
  `FieldVisibility` interceptor or a schema-directive-driven check.
- Federation (Apollo Federation /DGS) with a gateway: subgraph schemas
  disagree on nullability of a shared field after a deploy; the gateway
  returns hard-to-debug merge errors. Validate composition in CI.

## References

- GraphQL.org — "October 2021" spec, lists/nullability
- Netflix DGS documentation; Spring for GraphQL reference
- graphql-java `DataLoader` batching docs
