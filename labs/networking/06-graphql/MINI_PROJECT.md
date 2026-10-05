# GraphQL - MINI PROJECT

## Project: CatalogQL — a schema with nested resolvers, DataLoader, and cost limits

Build a product catalog GraphQL API where resolvers naively cause N+1 queries, then fix
that with batching, and add depth, complexity, and timeout controls. Include a query-count
test so the regression cannot come back.

### Architecture

```
  Schema (SDL is the contract)
    type Query { product(id: ID!): Product   products(filter: ProductFilter): [Product!]! }
    type Product { id, name, price, reviews(first: Int): [Review!]!, manufacturer: Manufacturer }
    type Manufacturer { id, name, country }

  Execution (per-parent field resolution)
    products ──▶ for EACH product: reviews resolver runs ──▶ 1 + N queries   <-- the problem
                  for EACH review:   author resolver runs  ──▶ N queries     <-- worse

  Fix
    DataLoader: batch reviews by productId into ONE query per level
    Query counter test asserts queries <= constant, independent of result size
```

### Implementation

The schema, where nullability choices are the contract:

```graphql
schema { query: Query }

type Query {
  product(id: ID!): Product
  products(filter: ProductFilter, first: Int = 20, after: String): ProductConnection!
}

# A product that exists always has a name and price. A review's author may have been
# deleted, so author is NULLABLE - and the client is forced by the schema to handle it.
# Making everything non-null turns a transient upstream failure into a total query failure.
type Product {
  id: ID!
  name: String!
  price: Money!
  reviews(first: Int = 10, after: String): ReviewConnection!
  manufacturer: Manufacturer            # nullable: may be unknown for legacy products
  createdAt: String!
}

type Money { amount: String! currency: String! }   # String, not Float: money is not a float

type Review {
  id: ID!
  rating: Int!
  title: String
  body: String
  author: User                          # nullable: deleted users
  createdAt: String!
}

type ProductConnection { nodes: [Product!]! pageInfo: PageInfo! totalCount: Int! }
type ReviewConnection  { nodes: [Review!]!  pageInfo: PageInfo!  totalCount: Int! }
type PageInfo { hasNextPage: Boolean! endCursor: String }
```

Naive resolvers, to establish the baseline the tests will prove we beat:

```java
@Component
class ProductResolver {
    private final ProductRepository products;
    private final ReviewRepository reviews;
    private final ManufacturerRepository manufacturers;
    private final QueryCounter counter;    // test-only instrumentation, always present

    public Product product(String id) { counter.record("product.findById"); return products.findById(id).orElse(null); }

    public List<Product> products(ProductFilter filter, int first, String after) {
        counter.record("products.list");
        return products.findAll(filter, first, after);
    }

    /** THE BUG: this runs ONCE PER PRODUCT in the response. 100 products = 101 queries. */
    public ReviewConnection reviews(Product parent, int first, String after) {
        counter.record("review.findByProductId");      // called N times
        var page = reviews.findByProductId(parent.id(), first, after);
        return ReviewConnection.of(page);
    }

    /** Worse: once per REVIEW. 100 products x 20 reviews = 2000+ queries. */
    public User author(Review parent) {
        counter.record("user.findById");
        return users.findById(parent.authorId()).orElse(null);
    }
}
```

DataLoader, which is the actual fix, with the request-scoped subtlety that matters:

```java
@Component
class Loaders {
    /**
     * ONE instance per request, not per application. A shared instance would cache a user
     * across requests and serve one tenant's data to another - a cross-tenant data leak.
     */
    @Bean
    @Scope("request", proxyMode = ScopedProxyMode.TARGET_CLASS)
    public DataLoader<String, List<Review>> reviewsByProduct(ReviewRepository repo) {
        return DataLoader.newMappedDataLoader(ids ->
            repo.findByProductIds(ids),                    // ONE query for all ids
            DataLoaderOptions.newOptions()
                // BatchingWindow exists for the rare high-fanout case; keep it small so
                // latency does not suffer while waiting for keys to accumulate.
                .setBatchingDelay(Duration.ofMillis(1))
                .setCachingEnabled(true)
                .build());
    }

    @Bean
    @Scope("request", proxyMode = ScopedProxyMode.TARGET_CLASS)
    public DataLoader<String, Manufacturer> manufacturerById(ManufacturerRepository repo) {
        return DataLoader.newLoader(id -> repo.findById(id), cachingEnabled(true));
    }
}
```

With loaders wired, the resolvers become cheap and declarative:

```java
@Component
class BatchedProductResolver {
    private final ProductRepository products;
    private final DataLoader<String, List<Review>> reviewsByProduct;
    private final DataLoader<String, Manufacturer> manufacturerById;

    /**
     * Returning CompletableFuture is the point: the resolver yields immediately, and
     * DataLoader dispatches the batched query once all sibling resolvers have returned.
     * The executor must be non-blocking or the batching window does nothing.
     */
    public CompletableFuture<ReviewConnection> reviews(Product parent, int first, String after) {
        return reviewsByProduct.load(parent.id()).thenApply(list ->
                ReviewConnection.of(list.stream().limit(first).toList()));
    }

    public CompletableFuture<Manufacturer> manufacturer(Product parent) {
        if (parent.manufacturerId() == null) return CompletableFuture.completedFuture(null);
        return manufacturerById.load(parent.manufacturerId());
    }
}
```

Cost control, because one endpoint plus arbitrary queries is an unbounded bill:

```java
@Component
class QueryCostGuard implements Instrumentation {
    // Cost is computed from the query AST: list fields have a multiplier (the number of
    // children each parent generates), nested fields add up. This is the only defence
    // against a client asking for 10,000 rows of a 12-field object in one request.
    static int estimateCost(OperationDefinition op, FieldSelectionSet parent, int multiplier) {
        int cost = 0;
        for (Field field : fieldsOf(parent)) {
            int childMultiplier = field.hasListType() ? multiplier * (int) field.listArg("first", 20) : multiplier;
            cost += field.hasChildren() ? estimateCost(op, field.selectionSet(), childMultiplier) : childMultiplier;
        }
        return op.operation() == MUTATION ? cost * MUTATION_MULTIPLIER : cost;   // mutations are expensive
    }

    void validate(DocumentNode query) {
        int depth = depthOf(query);
        if (depth > MAX_DEPTH)  throw new CostException("query depth " + depth + " exceeds " + MAX_DEPTH);
        int cost = estimateCost(query);
        if (cost > MAX_COST)   throw new CostException("estimated cost " + cost + " exceeds " + MAX_COST);
        if (containsIntrospection(query) && !introspectionAllowed())
            throw new CostException("introspection disabled");
    }

    /** A timeout is a last resort: it bounds damage but returns a partial error, so
     *  it must complement cost limits rather than replace them. */
    CompletableFuture<ExecutionResult> withTimeout(CompletableFuture<ExecutionResult> f) {
        return f.orTimeout(QUERY_TIMEOUT_MS, MILLISECONDS)
                .exceptionally(t -> errorResult("query exceeded " + QUERY_TIMEOUT_MS + "ms"));
    }
}
```

### Test It

```java
@Test void nestedQueryDoesNotScaleQueriesWithResultSize() {
    // The regression test that matters: query count must not grow with rows returned.
    var counter = new QueryCounter();
    var result = graphql.execute(productsWith(field("reviews", field("author"))), 100);
    assertThat(result.getErrors()).isEmpty();
    assertThat(counter.count("review.findByProductIds")).isEqualTo(1);   // ONE batched query
    assertThat(counter.count("user.findByIds")).isEqualTo(1);
    assertThat(counter.total()).isLessThanOrEqualTo(4);   // independent of 100 products
}

@Test void naiveResolverIsNPlusOne() {
    // Keep this test as documentation of the problem the loader solves.
    var counter = new QueryCounter();
    naiveResolvers().resolve(productsWith(field("reviews")), 100);
    assertThat(counter.count("review.findByProductId")).isEqualTo(100);
}

@Test void deepQueryIsRejected() {
    var deep = query("{ products { manufacturer { country { code { name } } } } }");
    assertThatThrownBy(() -> guard.validate(deep)).isInstanceOf(CostException.class)
        .hasMessageContaining("depth");
}

@Test void expensiveListQueryIsRejected() {
    // The classic abuse: a huge first: on a list field, multiplied by a nested list.
    var expensive = query("{ products(first: 1000) { reviews(first: 100) { body } } }");
    assertThatThrownBy(() -> guard.validate(expensive)).isInstanceOf(CostException.class)
        .hasMessageContaining("cost");
}

@Test void dataloaderCacheIsRequestScoped() {
    // Two separate requests must not share cached entities. This test would fail if the
    // DataLoader were a singleton - and that failure is a cross-tenant data leak.
    var loader = context.request(1).getBean(DataLoader.class);
    var other  = context.request(2).getBean(DataLoader.class);
    assertThat(loader).isNotSameAs(other);
}

@Test void nullableAuthorDegradesGracefully() {
    var result = graphql.execute(query("{ reviews { author { id } } }"));   // one author deleted
    assertThat(result.getErrors()).isEmpty();
    assertThat(result.getData().toString()).contains("author:null");        // not a total failure
}
```

## Deliverables

- [ ] SDL schema with documented nullability reasoning and `PageInfo` on every list
- [ ] Naive resolver implementation kept alongside the optimised one, as documentation
- [ ] `DataLoader` batching for every nested resolver, with request-scoped instances
- [ ] A query-count test proving query count is independent of result size
- [ ] Query depth limit with a rejection test
- [ ] Query cost analysis with list multipliers and a mutation penalty
- [ ] Introspection control, off by default for unauthenticated clients
- [ ] Query timeout complementing the cost limits
- [ ] A N+1 demonstration test that documents the problem being solved
