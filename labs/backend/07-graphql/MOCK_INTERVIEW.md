# Mock Interview: GraphQL Federation / Schema Stitching (Lab 07)

**Role:** Senior Backend Engineer
**Duration:** 55 minutes
**Difficulty:** Easy to Medium to Hard

---

## Round 1: Easy Problem Understanding (5 min)

**Interviewer:** Design a GraphQL federation resolver. What problem does federation solve?

**Candidate:** Federation solves the problem of having multiple GraphQL microservices that each own a subset of the graph. For example, User Service owns the User type and its fields. Order Service owns the Order type and extends User with an orders field. Federation merges these into a single unified schema. Clients query the unified graph without knowing which service owns which field. The gateway handles delegation to the correct sub-service.

**Interviewer:** How is federation different from schema stitching?

**Candidate:** Schema stitching is the older approach that merges schemas at the gateway by combining type definitions and manually configuring resolvers. Federation (Apollo Federation) is more standardized where each sub-service declares what types and fields it provides. The gateway handles delegation and entity resolution automatically using __resolveReference. My design follows the federation entity resolution pattern with explicit resolver registration.

**Interviewer:** What is the entity resolution pattern in federation?

**Candidate:** When a query crosses service boundaries (e.g., querying User.orders where User is from User Service and orders is from Order Service), the gateway needs to extend the User type. It calls __resolveReference on the Order Service with the user ID and __typename. The Order Service returns enough of a User object to resolve the extended fields. This allows each service to own its data while contributing to a shared graph.

---

## Round 2: Medium Entity Resolution (10 min)

**Interviewer:** Explain __resolveReference in detail. When is it called?

**Candidate:** __resolveReference is called whenever the gateway encounters an entity that was defined in one service but extended by another. For example, in the query { user(id: "1") { name orders { total } } }, User.name is from User Service, but User.orders is from Order Service. The gateway first fetches the User from User Service, then for each User in the result, calls __resolveReference on Order Service with {"__typename": "User", "id": "1"}. The Order Service uses the reference to fetch and return the extended fields.

**Interviewer:** How does the gateway know which service to call for which field?

**Candidate:** Each registered service provides a ServiceSchema that declares its types and field resolvers. The gateway maintains a mapping of type names to services. When resolving a query, the gateway walks the field selection tree, checks which service owns each field, and delegates accordingly. Extension fields are registered separately via extendType which maps a base type to the extending service field resolvers.

**Interviewer:** How do you handle cross-service arguments in fields?

**Candidate:** Arguments are passed through the field resolution chain. When the gateway calls a field resolver it passes the parent object and the field arguments from the query. The resolver implementation uses these arguments to filter or parameterize the data. For example orders(limit: 5) passes the limit argument to the Order Service resolver which applies it to the database query.

---

## Round 3: Medium-Hard DataLoader and N+1 Problem (10 min)

**Interviewer:** How do you prevent the N+1 problem in GraphQL resolvers?

**Candidate:** The N+1 problem occurs when resolving a list of parent objects triggers one database query per parent. Resolving orders for 10 users fires 10 separate queries. I use a DataLoader pattern that batches related data requests into a single query. The DataLoader collects keys during a tick of the event loop then fires a single batch query.

**Interviewer:** Explain your DataLoader implementation.

**Candidate:** DataLoader K V has a load(K key) method returning CompletableFuture V. Keys are accumulated in a map. A scheduled task fires after 1ms to execute the BatchLoader which receives all accumulated keys and returns a Map K V. Each CompletableFuture is completed with the corresponding value. This reduces N+1 to O(1) batch calls.

**Interviewer:** What happens if the same entity appears at multiple levels in a query?

**Candidate:** DataLoader also caches results by key within a single request context. If User(id=1) is referenced both in a top-level field and in a nested field the DataLoader returns the cached result. The cache is cleared between requests. This deduplication reduces downstream service load.

---

## Round 4: Hard Error Handling and Production (15 min)

**Interviewer:** How do you handle partial failures when one sub-service is down?

**Candidate:** The gateway catches exceptions from each resolver, adds a GraphQLError to the errors list with path information, and sets the field to null. The rest of the query still resolves. This follows the GraphQL spec partial results with errors are preferred over total failure. The client checks the errors array in the response to see which fields failed.

**Interviewer:** How would you extend this to support subscriptions spanning multiple services?

**Candidate:** Each sub-service exposes its own WebSocket endpoint. The gateway multiplexes subscriptions from all services into a single client connection. When a message arrives from any sub-service, the gateway wraps it with the correct type information and forwards it to the client. The gateway maintains a map of subscription IDs to client connections.

**Interviewer:** How do you manage schema changes across services?

**Candidate:** Schema registry with versioning. Each service publishes its schema on deployment. The gateway validates that the merged schema is valid with no conflicting types and fields have matching return types. Breaking changes require coordination. I use contract testing and a CI pipeline that validates the federation against all registered schemas before deployment. Adding a new field is always backward compatible.

**Interviewer:** How does your gateway handle authentication and authorization across services?

**Candidate:** The gateway authenticates the request and extracts user claims. These claims are passed to each sub-service via headers (X-User-Id, X-User-Roles). Each sub-service enforces its own authorization rules based on the claims. For cross-service authorization, I use a distributed authorization system like OPA (Open Policy Agent) where the gateway includes the full user context and each sub-service evaluates policies against it.

**Interviewer:** How do you handle schema validation at the gateway level?

**Candidate:** On startup the gateway fetches the schema from each registered service. It validates: (1) No duplicate type definitions. (2) Extended types (using extends keyword) correspond to existing types. (3) Field return types are compatible (e.g., both return String or both return Int). (4) No conflicting directives. If validation fails the gateway refuses to start preventing broken federations from reaching production.

---

## Round 5: Summary (5 min)

**Interviewer:** What are the key trade-offs in your federation design?

**Candidate:** (1) Gateway complexity vs client simplicity clients get a unified graph but the gateway is a single point of failure that must be highly available. (2) N+1 elimination via DataLoader adds latency batching delay vs the cost of individual requests. (3) Schema ownership clarity vs coordination overhead each service owns its types but changes require cross-team communication. (4) Partial failure handling provides resilience but clients must handle null fields gracefully. The biggest advantage is that each team can develop and deploy their GraphQL service independently.
