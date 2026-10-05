# Mini Project — Orders API (Quarkus or Bare EE)

## Goal
CRUD orders with validation, health, metrics. 30-min demoable.

## Endpoints
`POST /orders` `GET /orders/{id}` `GET /orders` `DELETE /orders/{id}`.

## Steps
1. `Order` entity/record + `OrderResource` (E1 template).
2. Service with `@Transactional` + repo (Panache or JPA).
3. Bean Validation + ExceptionMapper → 400 JSON.
4. Health check (DB ping) + `@Counted` order-created metric.
5. Tests: RestAssured/RestClient happy + 400 + 404 paths.

## Skeleton
```java
@Path("/orders") public class OrderResource {
  @Inject OrderService svc;
  @POST public Response create(@Valid OrderDto d) { ... }
}
```

## Acceptance
- All endpoints 200/201/400/404 correct; `/q/health` UP.
- N+1-free list (single query logged).

## Stretch
- JWT admin delete; Kafka `orders-created` event.

## Demo (2 min)
curl create→get→list→metrics increment.
