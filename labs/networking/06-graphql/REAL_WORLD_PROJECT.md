# GraphQL - REAL WORLD PROJECT

## Project: MeshQL — federated GraphQL across a polyglot service estate

A retail group with orders in Java, inventory in Go, pricing in Python, and customer data
in a legacy system. Each team owns and deploys its service independently. Clients need
product availability, price, stock, and delivery estimate in one round trip. REST would
mean the mobile client composing four calls; GraphQL gives one schema over four services.

### Architecture

```
  Mobile / web client
        │  one request, one schema, one round trip
        ▼
  ┌─────────────── Product Gateway (GraphQL) ───────────────┐
  │  schema: federated SDL, stitched from subgraph SDLs      │
  │  cost analysis │ depth limit │ persisted queries        │
  │  DataLoader per source │ query plan cache                 │
  └───┬────────────┬─────────────┬──────────────┬────────────┘
      ▼            ▼             ▼              ▼
  orders-svc   inventory-svc   pricing-svc   customer-legacy
  (Java)       (Go)           (Python)       (SOAP wrapper)
      │            │             │              │
      └────────────┴─────────────┴──────────────┘
                    Redis / Kafka / Postgres
```

### Implementation

The federation subgraph contract, owned by each team, is the integration boundary:

```graphql
# inventory-svc owns this subgraph. Other services EXTEND it; they do not redefine it.
type Product @key(fields: "sku") {
  sku: ID!
  name: String!
  availableQuantity: Int!            # owned by inventory, resolved locally
  warehouses: [Warehouse!]!
}

type Warehouse @key(fields: "id") {
  id: ID!
  city: String!
  leadTimeDays: Int!
}

extend type Product @key(fields: "sku") {
  # A reference, not an implementation: the gateway resolves it by fetching the entity
  # and delegating. The owning service never learns about the other fields.
  price: Money
  deliveryEstimate: DeliveryEstimate
  reviews: ReviewConnection
}
```

Cost control as production infrastructure, since a federated gateway is an amplification point:

```java
@Component
class FederatedCostPolicy {
    /**
     * In federation the cost is the SUM of subgraph costs, and a single field can fan out
     * to several services. So a naive cost model here under-counts by a large factor.
     * Cost is therefore computed per resolved field, with subgraph fan-out multipliers.
     */
    public ExecutionInput enforce(DocumentNode query, RequestContext ctx) {
        int cost = costAnalyzer.analyze(query);
        int limit = ctx.userTier().maxCostPerQuery();       // free tier: 1000, partner: 100_000
        if (cost > limit)
            throw new CostExceededException(cost, limit, topContributors(query));

        // Persisted queries: clients send a hash, not a query string. This removes the
        // attack surface of arbitrary query text AND a large amount of parse cost.
        if (!persistedQueries.enabledFor(ctx.clientId()))
            throw new FeatureDisabledException("persisted queries required");

        return ExecutionInput.newExecutionInput(query)
                .graphQLContext(b -> b.of("complexity", cost))
                .root(
                    // A global timeout is essential with federation: one slow subgraph
                    // must not hold the connection open indefinitely.
                    dataFetcherExceptionHandler(new TimeoutExceptionHandler(Duration.ofMillis(2500)))
                ).build();
    }
}

record CostExceededException(int cost, int limit, List<String> topContributors) {}
```

Resolving across services without a cross-service N+1, using a batch loader per subgraph:

```java
/**
 * The critical detail: one loader instance PER SUBGRAPH PER REQUEST. If a single loader
 * cached by a shared key across subgraphs, Product#sku=1 fetched from pricing and from
 * inventory would collide in the cache and return the wrong entity to one of them.
 */
class SubgraphLoaders {
    private final Map<String, DataLoader<String, Map<String,Object>>> perSubgraph = new HashMap<>();

    DataLoader<String, Map<String,Object>> forSubgraph(String subgraphName) {
        return perSubgraph.computeIfAbsent(subgraphName, name -> {
            var client = clients.forSubgraph(name);
            return DataLoader.newMappedDataLoader(keys ->
                    client.batchFetchByKeys(keys),      // each subgraph exposes a batch-by-keys endpoint
                    DataLoaderOptions.newOptions()
                            .setBatchingDelay(Duration.ofMillis(5))
                            .setMaxBatchSize(100)       // bounded: a huge key list would stall the subgraph
                            .build());
        });
    }
}
```

Circuit breaking and partial results, because four services means three ways to be down:

```java
@Component
class SubgraphResilience {
    /**
     * Federation's failure mode is partial data, which is easy to miss in a client that
     * only checks for a null field. Policy: hard-fail on money (price), degrade with an
     * explicit null + error entry on presentation data (reviews, images).
     */
    Price resolvePrice(Product product) {
        try {
            return pricingCircuitBreaker.execute(
                    () -> pricingClient.priceFor(product.sku()),
                    // Fallback is NOT a wrong price. A fallback that guesses a price is
                    // a financial incident; an explicit "price unavailable" is correct.
                    throwable -> Price.unavailable());
        } catch (CircuitBreakerOpenException e) {
            metrics.counter("graphql.subgraph.open", "subgraph", "pricing");
            return Price.unavailable();
        }
    }

    List<Review> resolveReviews(Product product) {
        return reviewsCircuitBreaker.execute(() -> reviewsClient.forProduct(product.sku()),
                throwable -> List.of());       // empty list is an acceptable degradation here
    }
}
```

Persisted queries and allow-listing, the production answer to arbitrary client queries:

```java
@Component
class PersistedQueryRegistry {
    /**
     * Registration is a deliberate act: a client submits a query once, it is reviewed,
     * reviewed cost recorded, and stored against a hash. Afterwards the client sends only
     * the hash. Consequences: no arbitrary query text reaches execution, the cost model
     * becomes exact, and parsing cost drops to a map lookup.
     */
    public String register(RegisterRequest req) {
        int cost = costAnalyzer.analyze(parse(req.query()));
        if (cost > MAX_REGISTRABLE_COST) throw new CostExceededException(cost, MAX_REGISTRABLE_COST);
        if (introspectionUsed(req.query()) && !req.client().trusted()) throw new FeatureDisabledException("introspection");
        if (!schemaDiff.isCompatible(parse(req.query()), currentSchema())) throw new IncompatibleQueryException();
        String hash = sha256(canonicalize(req.query()));
        store.put(hash, new RegisteredQuery(req.client().id(), req.query(), cost, Instant.now()));
        auditLog.registered(req.client().id(), hash, cost, reviewer());
        return hash;
    }

    /** Resolver: hash -> query. A hash that was never registered is a rejection, not a parse. */
    public String lookup(String hash) {
        return Optional.ofNullable(store.get(hash))
                .map(RegisteredQuery::query)
                .orElseThrow(() -> new UnknownPersistedQueryException(hash));
    }
}
```

Response shaping, because over-fetching is the client tax this architecture is meant to remove:

```java
/** Return only what was asked for. A gateway that returns full entities has not solved anything. */
record ProductCard(String sku, String name, Money price, int availableQuantity,
                   DeliveryEstimate delivery, List<String> imageUrls) {}

ProductCard toCard(Product p, Money price, int qty, DeliveryEstimate est, List<String> images) {
    return new ProductCard(p.sku(), p.name(), price, qty, est, images);
    // No internal IDs, no cost prices, no supplier fields. The card is the public shape.
}
```

### Non-functional requirements

- **Latency**: p95 under 350 ms for a product page query across four subgraphs, p99 under
  900 ms. Per-subgraph latency is broken out, since one slow subgraph dominates the p99.
- **Resilience**: independent circuit breakers per subgraph with explicit degradation
  semantics. Price degrades to "unavailable", never to a wrong number. Partial results
  carry an `errors` array so a client cannot mistake missing data for real absence.
- **Cost control**: persisted queries mandatory, per-tier cost limits, 2.5 s global
  timeout, and a per-subgraph batch size cap. These four controls are what keep the
  gateway from becoming the outage.
- **Caching**: per-subgraph response caching keyed by the hashed query plus a version tag,
  with explicit TTLs. A query-plan cache for parse overhead.
- **Rate limiting**: per client and per cost unit, so a cheap query and an expensive one
  consume budget proportionally.
- **Schema governance**: per-team subgraph SDL in one repo, a federated composition check in
  CI, and a rule that `extend type` never redefines an owned field.
- **Observability**: per-subgraph latency and error rate, resolver-level timing for the
  slowest fields, cost distribution per client, and the N+1 canary (a query whose subgraph
  call count grows with result size is an alert).
- **Rollout**: the gateway starts in shadow mode beside the existing mobile REST calls,
  comparing responses before serving traffic.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- GraphQL over HTTP and the GraphQL specification define the single-endpoint request model,
  the query language, and the execution semantics this gateway builds on.
  https://graphql.org/learn/
- Apollo Federation documentation describes subgraph schemas, entity references via `@key`,
  and the gateway composition model where owning services extend rather than redefine types.
  https://www.apollographql.com/docs/federation/

## Deliverables

- [x] Federated subgraph SDL per service team, with `@key` references and extension rules
- [x] Per-subgraph, per-request DataLoader instances to prevent cross-subgraph cache collisions
- [x] Persisted queries as a mandatory production control, with reviewed registration
- [x] Cost analysis with per-tier limits, per-subgraph fan-out multipliers, and a global timeout
- [x] Independent circuit breakers with explicit degradation semantics per field category
- [x] Partial-result handling where missing data is distinguishable from empty data
- [x] Resolver-level timing and a per-subgraph latency/error breakdown
- [x] N+1 canary alert on subgraph call count growing with result size
