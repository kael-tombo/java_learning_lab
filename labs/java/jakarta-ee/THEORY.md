# THEORY — Jakarta EE

## Overview

Jakarta EE (formerly Java EE) provides enterprise APIs for building scalable, secure, transactional applications. It's now under the Eclipse Foundation.

## Core Specifications

| Spec | API Package | Purpose |
|------|-------------|---------|
| Servlet | `jakarta.servlet` | HTTP request/response handling |
| JPA | `jakarta.persistence` | Object-relational mapping |
| CDI | `jakarta.inject` | Dependency injection |
| EJB | `jakarta.ejb` | Enterprise beans (transactions, security) |
| JAX-RS | `jakarta.ws.rs` | RESTful web services |
| JSON-P/B | `jakarta.json` | JSON processing/binding |
| Bean Validation | `jakarta.validation` | Declarative validation |
| Security | `jakarta.security` | Authentication/authorization |

## Dependency Injection (CDI)

```java
@ApplicationScoped
public class OrderService {
    @Inject PaymentProcessor processor;
    
    public void process(Order order) {
        processor.charge(order.getPayment());
    }
}

@Qualifier @Retention(RUNTIME) @Target({FIELD, PARAMETER})
@interface PayPal {}

@Inject @PayPal PaymentProcessor processor;
```

## JPA Entities

```java
@Entity @Table(name = "orders")
public class Order {
    @Id @GeneratedValue(strategy = IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = LAZY)
    @JoinColumn(name = "customer_id")
    private Customer customer;
    
    @OneToMany(mappedBy = "order", cascade = ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();
}
```

## JAX-RS REST Endpoints

```java
@Path("/orders")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class OrderResource {
    
    @GET @Path("/{id}")
    public Response getOrder(@PathParam("id") Long id) {
        return orderService.find(id)
            .map(Response::ok)
            .orElse(Response.status(NOT_FOUND))
            .build();
    }
    
    @POST
    public Response createOrder(OrderDTO dto) {
        Order order = orderService.create(dto);
        return Response.created(URI.create("/orders/" + order.getId())).build();
    }
}
```

## Transaction Management

```java
@Stateless
public class OrderBean {
    @PersistenceContext EntityManager em;
    
    @TransactionAttribute(REQUIRED)
    public void placeOrder(Order order) {
        em.persist(order);
        inventory.reserve(order.getItems());
        // Auto-commit or rollback on exception
    }
}
```

## Configuration & Profiles

```properties
# MicroProfile Config
app.datasource.url=jdbc:postgresql://localhost:5432/app
app.datasource.username=${env.DB_USER}
app.datasource.password=${env.DB_PASS}
```

## Modern Jakarta EE 10+

- **Servlet 6.0**: HTTP/2, WebSocket, async I/O
- **JPA 3.1**: New query hints, enhanced locking
- **CDI 4.0**: Build-time processing, interceptors
- **JSON-B 3.0**: Improved serialization

## Key Servers

| Server | Version | Notes |
|--------|---------|-------|
| WildFly | 32+ | Full Jakarta EE 10 |
| Open Liberty | 23+ | Lightweight, cloud-native |
| Payara | 6+ | GlassFish derivative |
| TomEE | 9+ | Tomcat + EE |