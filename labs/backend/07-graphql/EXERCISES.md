# Exercises: GraphQL Federation Gateway (Lab 07)

**Prerequisites:** Read `LEETCODE_SOLUTION.md`  
**Difficulty:** Progressive (Easy → Medium → Hard)

---

## Exercise 1: Scalar Type Support (Easy)

### Task
Add support for custom scalar types (DateTime, JSON, Email) in the gateway.

### Requirements
```java
// Extend FieldResolver to handle scalar coercion
public interface ScalarCoercer {
    Object serialize(Object value);   // For response
    Object parseValue(Object value);  // For input variables
    Object parseLiteral(Object ast);  // For inline query values
}

// Register scalars in ServiceSchema
public void addScalar(String typeName, ScalarCoercer coercer) { ... }

// Handle in resolve(): if type is scalar, apply coercion
```

### Test Case
```java
@Test
void testDateTimeScalar() {
    var svc = new ServiceSchema("test");
    svc.addType("Event");
    svc.addScalar("DateTime", new ScalarCoercer() {
        public Object serialize(Object v) { return ((Instant)v).toString(); }
        public Object parseValue(Object v) { return Instant.parse((String)v); }
    });
    svc.addFieldResolver("Event", "createdAt", (p, a) -> Instant.now());
    
    gateway.registerService("test", svc);
    // Query: { event { createdAt } }
    // Result should be ISO-8601 string
}
```

---

## Exercise 2: Interface & Union Types (Easy)

### Task
Add support for GraphQL interfaces and unions in the gateway.

### Requirements
```java
// In ServiceSchema
public void addInterface(String interfaceName, List<String> implementingTypes) { ... }
public void addUnion(String unionName, List<String> memberTypes) { ... }

// In resolve(): when field returns interface/union, include __typename
// Gateway must resolve to concrete type
```

### Test Case
```java
@Test
void testInterfaceResolution() {
    // User and Bot both implement Actor interface
    // Query: { actor { ... on User { name } ... on Bot { version } } }
    // Gateway should resolve correct type based on __typename
}
```

---

## Exercise 3: Subscription Support (Medium)

### Task
Add GraphQL subscription support via WebSocket.

### Requirements
```java
public class SubscriptionManager {
    private final Map<String, Set<Subscription>> subscriptions = new ConcurrentHashMap<>();
    
    public void subscribe(String eventType, Consumer<Object> handler) { ... }
    public void publish(String eventType, Object payload) { ... }
}

// WebSocket handler:
// - Parse connection_init, start, stop messages
// - Execute subscription operation
// - Stream results via async iterator
```

### Test Case
```java
@Test
void testSubscription() throws Exception {
    // Start WebSocket server
    // Client sends subscription: subscription { orderCreated { id total } }
    // Publish event
    // Verify client receives data
}
```

---

## Exercise 4: Query Complexity Analysis (Medium)

### Task
Implement query complexity scoring to prevent abusive queries.

### Requirements
```java
public class ComplexityAnalyzer {
    private final Map<String, Integer> fieldCosts = new HashMap<>(); // field -> cost
    private final int maxComplexity = 1000;
    
    public void analyze(Query query) {
        // Walk query tree, sum costs
        // Multiply by list size (arguments.first, arguments.last)
        // Throw if exceeds maxComplexity
    }
}

// Default costs: scalar=1, object=5, connection=10
// Configure per-field: fieldCosts.put("User.orders", 10);
```

### Test Case
```java
@Test
void testComplexityLimit() {
    // Deeply nested query should exceed limit
    // Query with large `first: 1000` should be rejected
    // Simple query should pass
}
```

---

## Exercise 5: Query Plan Caching (Medium)

### Task
Cache the query execution plan to avoid re-computing service resolution on each request.

### Requirements
```java
public class QueryPlanCache {
    private final Cache<String, QueryPlan> cache = Caffeine.newBuilder()
        .maximumSize(10_000)
        .expireAfterWrite(1, TimeUnit.HOURS)
        .build();
    
    public QueryPlan getOrCreate(String queryHash, Supplier<QueryPlan> creator) {
        return cache.get(queryHash, k -> creator.get());
    }
}

// QueryPlan: ordered list of fetches (service, fields, dependencies)
// Enables parallel execution of independent fetches
```

### Test Case
```java
@Test
void testPlanCaching() {
    // Execute same query twice
    // Second execution should use cached plan (measure time)
    // Modify query slightly -> new plan created
}
```

---

## Exercise 6: Directive Support (Medium)

### Task
Implement common GraphQL directives: `@skip`, `@include`, `@deprecated`, `@specifiedBy`.

### Requirements
```java
// In Field resolution:
public boolean shouldInclude(Field field, Map<String, Object> variables) {
    // @skip(if: Boolean) - skip if true
    // @include(if: Boolean) - include if true
    // Evaluate argument with variables
}

// @deprecated: add to field metadata, include in introspection
// @specifiedBy: for custom scalars, validate URL
```

### Test Case
```java
@Test
void testDirectives() {
    // Query: { user { name @skip(if: true) email @include(if: false) } }
    // Result should not include name or email
}
```

---

## Exercise 7: Distributed Tracing Integration (Hard)

### Task
Integrate OpenTelemetry / W3C Trace Context propagation across gateway and subgraphs.

### Requirements
```java
public class TracingGateway extends FederationGateway {
    private final Tracer tracer;
    
    @Override
    public ExecutionResult executeQuery(Query query) {
        return tracer.spanBuilder("graphql.execute")
            .setAttribute("graphql.operation", query.selections().get(0).name())
            .startScopedSpan(span -> {
                // Inject trace context into subgraph requests
                // Add span events for each subgraph call
                return super.executeQuery(query);
            });
    }
}

// Subgraph HTTP client: inject traceparent header
// Subgraph server: extract and continue trace
```

### Test Case
```java
@Test
void testTracePropagation() {
    // Execute query through gateway
    // Verify trace spans: gateway -> subgraph1, gateway -> subgraph2
    // Verify trace context propagated via headers
}
```

---

## Exercise 8: Schema Composition & Validation (Hard)

### Task
Implement schema composition logic (simplified Apollo Federation composition).

### Requirements
```java
public class SchemaComposer {
    public SupergraphSchema compose(List<SubgraphSchema> subgraphs) {
        // 1. Collect all type definitions
        // 2. Merge types with same name
        // 3. Resolve @key, @extends, @external, @requires, @provides
        // 4. Validate: no duplicate field definitions, valid references
        // 5. Generate query plan for each possible query shape
    }
}

// SubgraphSchema: serviceName + SDL string
// SupergraphSchema: composed SDL + query planner
```

### Test Case
```java
@Test
void testComposition() {
    // Subgraph A: type User @key(fields: "id") { id: ID! name: String }
    // Subgraph B: extend type User @key(fields: "id") { posts: [Post] }
    // Compose -> Supergraph with User { id, name, posts }
}
```

---

## Exercise 9: Persisted Queries / Automatic Persisted Queries (APQ) (Hard)

### Task
Implement APQ to reduce request size and enable query allow-listing.

### Requirements
```java
public class PersistedQueryRegistry {
    private final Map<String, String> queryMap = new ConcurrentHashMap<>(); // hash -> query
    
    public String register(String query) {
        String hash = sha256(query);
        queryMap.put(hash, query);
        return hash;
    }
    
    public String getQuery(String hash) { return queryMap.get(hash); }
}

// Gateway flow:
// 1. Client sends { extensions: { persistedQuery: { version: 1, sha256Hash: "..." } } }
// 2. Gateway looks up hash
// 3. If not found, client sends full query + hash for registration
// 4. Optionally: allow-list mode (reject unregistered queries)
```

### Test Case
```java
@Test
void testAPQ() {
    // Register query -> get hash
    // Execute with hash only
    // Verify execution works
    // Unknown hash -> error (or prompt for registration)
}
```

---

## Exercise 10: Federation Gateway with GraphQL Java + Spring Boot (Hard)

### Task
Build a production-ready federation gateway using GraphQL Java and Spring Boot.

### Requirements
```java
// Spring Boot 3.x + GraphQL Java 24.x + graphql-java-spring-boot
// Configuration:
@Configuration
public class FederationConfig {
    @Bean
    public GraphQLSchema supergraphSchema() { ... }
    
    @Bean
    public DataFetcherFactory dataFetcherFactory() { ... }
}

// Subgraph client: WebClient with circuit breaker (Resilience4j)
// Query execution: graphql-java execution engine
// Metrics: Micrometer + Prometheus
// Health: Spring Boot Actuator
```

### Test Case
```java
@SpringBootTest
class FederationGatewayIntegrationTest {
    @Autowired WebTestClient client;
    
    @Test
    void testFederatedQuery() {
        client.post().uri("/graphql")
            .bodyValue("{\"query\": \"{ user(id: \\\"1\\\") { name orders { id } } }\"}")
            .exchange()
            .expectStatus().isOk()
            .expectBody().jsonPath("$.data.user.name").isEqualTo("Alice");
    }
}
```

---

## Solutions

See `SOLUTIONS.md` for reference implementations.

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1 | 15 | Scalars serialize/parse correctly |
| 2 | 15 | Interface/union resolution works |
| 3 | 30 | WebSocket subscriptions functional |
| 4 | 20 | Complexity analysis blocks expensive queries |
| 5 | 20 | Plan caching reduces latency |
| 6 | 15 | All core directives implemented |
| 7 | 40 | Trace context propagates end-to-end |
| 8 | 50 | Schema composition validates & merges |
| 9 | 30 | APQ registration + execution works |
| 10 | 80 | Spring Boot app runs, federates real subgraphs |

**Total: 315 points**

---

## Next Steps

1. Run tests: `mvn test`
2. Study Apollo Federation spec v2.x
3. Explore GraphQL Java DataFetchingEnvironment
4. Practice: Add rate limiting, auth integration
5. Read about: GraphQL Gateway performance patterns