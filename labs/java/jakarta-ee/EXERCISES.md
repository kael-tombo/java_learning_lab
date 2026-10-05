# Exercises — Jakarta EE (9 hands-on)

## E1 — JAX-RS CRUD
```java
@Path("/orders") @Produces(APPLICATION_JSON)
public class OrderResource {
  @GET @Path("/{id}") public Order get(@PathParam("id") long id) { ... }
}
```
Tasks: GET/POST/PUT/DELETE + ExceptionMapper; test with curl.

## E2 — CDI Scopes
Tasks: @ApplicationScoped vs @RequestScoped counter demo; @Inject constructor.

## E3 — Bean Validation
Tasks: @NotNull @Size on DTO; violations → 400 mapping.

## E4 — JPA Entity + Query
Tasks: @Entity Order, Panache/JPQL分页 query, N+1 fix with JOIN FETCH.

## E5 — Transactions
Tasks: @Transactional rollback on RuntimeException; REQUIRES_NEW audit demo.

## E6 — MicroProfile Health/Metrics
Tasks: @Liveness/@Readiness checks; Counter/Timer metrics endpoint.

## E7 — Messaging (JMS/Kafka)
Tasks: @Incoming/@Outgoing channel; poison message → DLQ.

## E8 — Security (JWT/OIDC)
Tasks: @RolesAllowed admin endpoint; MP-JWT public-key verify.

## E9 — Capstone: Orders API
Tasks: resource+service+repo+validation+health+metrics.
Flags: `-Xmx512m -Dquarkus.http.port=8080`. Checklist: tests green, native optional.
