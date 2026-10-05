# Multi-Cloud - Mini Project

## Project: A Provider-Neutral Application Core

### Objective
Take an application that calls three provider services and separate the portable business
logic from the provider-specific integration, then measure what portability actually costs.

### Requirements
1. `ProviderAdapter` interface with AWS, Azure, and GCP implementations
2. Portable domain logic that never imports a provider SDK
3. A conformance test suite every adapter must pass
4. `PortabilityReport` enumerating what is portable, what is not, and the estimated cost
5. A test that fails if provider SDK types leak into the domain layer

### Steps

**Step 1: Decide the strategy and write it down**
| Strategy | Meaning | Cost | Use when |
|---|---|---|---|
| Single cloud, well-architected | one provider, deep integration | lowest | default for most teams |
| Portable core, single deploy | portable code, one provider | low | you want exit optionality |
| Active-active across providers | two live deployments | high | regulatory or outage exposure |
| Cloud-agnostic by platform | Kubernetes + object storage | medium | you already run Kubernetes |

Pick one. "All three at once" is not a strategy, it is three projects.

**Step 2: Find the seam in real code**
```java
// BEFORE — domain logic entangled with the SDK
public class OrderService {
    private final DynamoDbClient dynamo;              // provider type in the domain

    public Order place(OrderRequest req) {
        var item = Item.builder().content(req.toString()).build();   // provider type
        dynamo.putItem(PutItemRequest.builder().tableName("orders").item(item).build());
        return Order.from(req);
    }
}
```
```java
// AFTER — the seam is "store an order", not "put a Dynamo item"
public interface OrderStore {
    void save(Order order);
    Optional<Order> find(String id);
}

public class OrderService {                 // pure domain, no SDK imports
    private final OrderStore store;
    public Order place(OrderRequest req) { var o = Order.from(req); store.save(o); return o; }
}
```
The refactor is not glamorous and it is the whole job. The SDK stays in the adapter.

**Step 3: The adapters carry the real differences**
```java
public final class DynamoOrderStore implements OrderStore {
    private static final Map<String, AttributeValue> toItem(Order o) { /* provider-native */ }
    private static Order fromItem(Map<String, AttributeValue> m) { /* provider-native */ }

    public void save(Order o) {
        table.putItem(PutItemRequest.builder()
            .tableName("orders")
            .item(toItem(o))
            .conditionExpression("attribute_not_exists(orderId)")   // idempotent insert
            .build());
    }
}
```
Now the interesting work is visible: DynamoDB gives you a conditional put, Azure Table gives
you an ETag, and a relational implementation gives you an upsert. **Those are different
capabilities, not different syntaxes.** Write them down.

**Step 4: Conformance tests, run against every adapter**
```java
interface OrderStoreConformance {
    @Test default void saveThenFindReturnsTheOrder() { ... }
    @Test default void duplicateSaveIsRejected() { ... }
    @Test default void findMissingReturnsEmpty() { ... }
    @Test default void partialWriteIsNotVisible() { ... }
}
```
Each adapter's test class implements the suite. If an adapter cannot satisfy a test, that is
a **portability finding**, not a test to delete.

**Step 5: Enforce the boundary in CI**
```java
@Test
void domainLayerHasNoProviderImports() {
    var violations = Files.walk(Path.of("src/main/java/com/example/domain"))
        .filter(p -> p.toString().endsWith(".java"))
        .filter(p -> containsProviderImport(p))
        .toList();
    assertThat(violations).as("provider SDK leaked into the domain layer").isEmpty();
}
```
This is the test that keeps the abstraction honest. Without it, one convenient SDK call and
six months later the domain layer is not portable.

**Step 6: Write the honest report**
```
Portable:     domain logic, HTTP APIs, PostgreSQL-compatible SQL, containers, OpenTelemetry
Semi-portable: object storage (different consistency and IAM models), queues, serverless
Not portable: managed identity flows, IAM semantics, VPC constructs, managed Kubernetes add-ons
Cost of keeping it this way: N engineer-days per release for the adapter layer
```
If the semi-portable list is where your application actually lives, say so. That is the finding
that changes the strategy.

### Deliverables
1. `ProviderAdapter` interface plus AWS, Azure, and GCP implementations
2. Pure domain layer with a CI-enforced no-provider-imports test
3. Conformance suite run against all three adapters, with failures documented as findings
4. `PortabilityReport` naming the carrying cost and the honest non-portable list

### Extension (CHALLENGE)
Implement the same order service on a managed serverless platform in each cloud and measure
cold start, cost per request, and the operator effort to keep all three working.

### Estimated Time
5-6 hours