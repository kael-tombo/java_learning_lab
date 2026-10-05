# Code Deep Dive — Jakarta EE

## 1. Source Tour
- JAX-RS: `jakarta.ws.rs.*`; impl RESTEasy/Jersey scanning `@Path`.
- CDI: Weld `BeanManager`, contexts per scope; proxies for normal scopes.
- JPA: Hibernate `SessionImpl`, dirty checking, lazy proxies.

## 2. Bytecode: Annotations
```java
@Path("/o") class R {}
```
`javap -v` → `RuntimeVisibleAnnotations: @Path("/o")`. Runtimes scan at boot.
Native: Quarkus records annotations at build (no runtime scan).

## 3. CDI Proxy
`@ApplicationScoped` injects proxy subclass; `javap -c` shows delegate + context lookup.
Request scope: proxy → `ThreadLocal` context map; wrong thread → ContextNotActive.

## 4. JAX-RS Dispatch
`UriRoutingContext` matches path regex → resource method; `@Produces` negotiates.
Filter chain: `ContainerRequestFilter` → method → `ContainerResponseFilter`.

## 5. JPA N+1 Path
Lazy `PersistentBag` triggers SELECT per access; `JOIN FETCH` single query.
Verify: `hibernate.show_sql` + `format_sql`, counter assert in test.

## 6. Tx Interceptor
`@Transactional` → JTA interceptor begin/commit; RuntimeException → rollback.
Check: `TransactionSynchronizationRegistry` status in test.

## 7. Profiling EE
```bash
curl localhost:8080/q/health; curl localhost:8080/q/metrics
jfr: jdk.SocketRead + JPA query events; slow = top stack
```

## 8. Flags/Configs
`-Xmx512m -Dquarkus.datasource.jdbc.max-size=20 -Dquarkus.http.limits.max-body-size=1M`.

## 9. Refs
Jakarta EE specs (REST/CDI/Persistence), Weld/Hibernate sources, MicroProfile docs.
