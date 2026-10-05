# Code Deep Dive — Architecture Deep Dive

## Circuit Breaker Implementation

```java
public class CircuitBreaker {
    private enum State { CLOSED, OPEN, HALF_OPEN }
    
    private State state = State.CLOSED;
    private int failureCount = 0;
    private final int failureThreshold;
    private final long timeout;
    private long lastFailureTime;
    
    public CircuitBreaker(int failureThreshold, long timeout) {
        this.failureThreshold = failureThreshold;
        this.timeout = timeout;
    }
    
    public <T> T execute(Callable<T> action) throws Exception {
        if (state == State.OPEN) {
            if (System.currentTimeMillis() - lastFailureTime > timeout) {
                state = State.HALF_OPEN;
            } else {
                throw new CircuitBreakerOpenException();
            }
        }
        
        try {
            T result = action.call();
            onSuccess();
            return result;
        } catch (Exception e) {
            onFailure();
            throw e;
        }
    }
    
    private void onSuccess() {
        failureCount = 0;
        state = State.CLOSED;
    }
    
    private void onFailure() {
        failureCount++;
        lastFailureTime = System.currentTimeMillis();
        if (failureCount >= failureThreshold) {
            state = State.OPEN;
        }
    }
}
```

## Event Store Implementation

```java
public class EventStore {
    private final List<Event> events = new ArrayList<>();
    private final Map<String, Integer> aggregateVersions = new HashMap<>();
    
    public synchronized void append(String aggregateId, Event event) {
        int currentVersion = aggregateVersions.getOrDefault(aggregateId, 0);
        event.setAggregateId(aggregateId);
        event.setVersion(currentVersion + 1);
        events.add(event);
        aggregateVersions.put(aggregateId, currentVersion + 1);
    }
    
    public List<Event> getEvents(String aggregateId) {
        return events.stream()
            .filter(e -> e.getAggregateId().equals(aggregateId))
            .sorted(Comparator.comparingInt(Event::getVersion))
            .collect(Collectors.toList());
    }
    
    public <T> T rebuildAggregate(String aggregateId, Supplier<T> factory) {
        T aggregate = factory.get();
        for (Event event : getEvents(aggregateId)) {
            aggregate.apply(event);
        }
        return aggregate;
    }
}
```

## Saga Orchestrator Implementation

```java
public class SagaOrchestrator {
    private final SagaStateRepository stateRepository;
    private final Map<String, SagaStep> steps;
    
    public void executeSaga(String sagaId, SagaDefinition definition) {
        SagaState state = new SagaState(sagaId, definition.getSteps());
        stateRepository.save(state);
        
        List<SagaStep> executedSteps = new ArrayList<>();
        
        for (SagaStep step : definition.getSteps()) {
            try {
                step.execute();
                state.markStepCompleted(step.getName());
                executedSteps.add(step);
            } catch (Exception e) {
                state.markStepFailed(step.getName());
                compensate(executedSteps);
                state.markCompensated();
                return;
            }
        }
        
        state.markCompleted();
    }
    
    private void compensate(List<SagaStep> executedSteps) {
        List<SagaStep> reverse = new ArrayList<>(executedSteps);
        Collections.reverse(reverse);
        
        for (SagaStep step : reverse) {
            try {
                step.compensate();
            } catch (Exception e) {
                // Log and alert — manual intervention may be needed
                alertCompensationFailure(step, e);
            }
        }
    }
}
```

## CQRS Command Handler

```java
public class CommandHandler<C extends Command, R> {
    private final Class<C> commandType;
    private final Function<C, R> handler;
    private final List<CommandInterceptor> interceptors;
    
    public R handle(C command) {
        CommandContext context = new CommandContext(command);
        
        for (CommandInterceptor interceptor : interceptors) {
            interceptor.beforeHandle(context);
        }
        
        R result = handler.apply(command);
        
        for (CommandInterceptor interceptor : interceptors) {
            interceptor.afterHandle(context, result);
        }
        
        return result;
    }
}
```

## Event-Driven Consumer with Idempotency

```java
public class IdempotentEventConsumer {
    private final Set<String> processedEventIds = new HashSet<>();
    private final EventHandler handler;
    
    public void consume(Event event) {
        if (processedEventIds.contains(event.getId())) {
            return; // Already processed
        }
        
        try {
            handler.handle(event);
            processedEventIds.add(event.getId());
        } catch (Exception e) {
            // Retry or dead letter
            throw e;
        }
    }
}
```

## API Composition with Parallel Fetching

```java
public class DashboardComposer {
    private final UserService userService;
    private final OrderService orderService;
    private final ProductService productService;
    
    public Dashboard compose(String userId) {
        CompletableFuture<User> userFuture = 
            CompletableFuture.supplyAsync(() -> userService.getUser(userId));
        CompletableFuture<List<Order>> ordersFuture = 
            CompletableFuture.supplyAsync(() -> orderService.getOrders(userId));
        CompletableFuture<List<Product>> productsFuture = 
            CompletableFuture.supplyAsync(() -> productService.getRecommendations(userId));
        
        return CompletableFuture.allOf(userFuture, ordersFuture, productsFuture)
            .thenApply(v -> new Dashboard(
                userFuture.join(),
                ordersFuture.join(),
                productsFuture.join()
            ))
            .exceptionally(ex -> {
                // Partial failure handling
                return createPartialDashboard(userFuture, ordersFuture, productsFuture);
            })
            .join();
    }
}
```

## Hexagonal Architecture Port Definition

```java
// Core defines the port
public interface NotificationPort {
    void sendNotification(String recipient, String message);
}

// Core uses the port
public class OrderService {
    private final NotificationPort notificationPort;
    
    public OrderService(NotificationPort notificationPort) {
        this.notificationPort = notificationPort;
    }
    
    public void placeOrder(Order order) {
        // Business logic
        notificationPort.sendNotification(
            order.getCustomerEmail(),
            "Order confirmed: " + order.getId()
        );
    }
}

// Adapter implements the port
public class EmailNotificationAdapter implements NotificationPort {
    private final EmailClient emailClient;
    
    @Override
    public void sendNotification(String recipient, String message) {
        emailClient.send(recipient, "Order Confirmation", message);
    }
}
```

## Service Mesh Traffic Splitting

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-service
spec:
  hosts:
  - order-service
  http:
  - route:
    - destination:
        host: order-service
        subset: v1
      weight: 90
    - destination:
        host: order-service
        subset: v2
      weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: order-service
spec:
  host: order-service
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```
