# Code Deep Dive: Multi-Tenancy in Spring

## Tenant context from JWT

```java
public final class TenantContext {
    private static final ThreadLocal<String> CURRENT = new ThreadLocal<>();
    public static void set(String t) { CURRENT.set(t); }
    public static String get()       { return CURRENT.get(); }
    public static void clear()       { CURRENT.remove(); }
}

@Component
public class TenantInterceptor implements HandlerInterceptor {
    @Override public boolean preHandle(HttpServletRequest req, HttpServletResponse res, Object h) {
        var auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth instanceof JwtAuthenticationToken jwt) {
            TenantContext.set(jwt.getToken().getClaimAsString("tenant_id"));
        }
        return true;
    }
    @Override public void afterCompletion(HttpServletRequest r, HttpServletResponse s, Object h, Exception e) {
        TenantContext.clear();                         // mandatory, or threads leak
    }
}
```

Pitfall: `afterCompletion` skipping `clear()` when an exception path is
taken — that is exactly when the leaked tenant id corrupts the next request.

## Hibernate filter for pool-model isolation

```java
@Entity
@FilterDef(name = "tenantFilter", parameters = @ParamDef(name = "tenantId", type = String.class))
@Filter(name = "tenantFilter", condition = "tenant_id = :tenantId")
public class Document { @Id Long id; String tenant_id; String title; }

@Component
public class TenantFilterAspect {
    @PersistenceContext EntityManager em;
    @Before("execution(* com.example..*Repository.*(..))")
    public void apply() {
        em.unwrap(Session.class).enableFilter("tenantFilter")
          .setParameter("tenantId", TenantContext.get());
    }
}
```

Pitfall: native queries (`createNativeQuery`) ignore `@Filter` — add
`WHERE tenant_id = :t` manually there, and audit report/export SQL.

## CurrentTenantIdentifierResolver + schema routing (silo)

```java
@Bean
CurrentTenantIdentifierResolver<String> tenantResolver() {
    return () -> TenantContext.get() == null ? "public" : TenantContext.get();
}

@Bean
MultiTenantConnectionProvider<String> multiTenantProvider(DataSource ds) {
    return new AbstractMultiTenantConnectionProvider() {
        protected DataSource selectDataSource(String tenant) { return ds; } // 1 DB, schemas per tenant
    };
}
```

Pitfall: returning a tenant-specific schema but caching prepared statements
globally — statement metadata is per-schema; disable statement caching or key
it by tenant.

## AbstractRoutingDataSource (per-tenant DBs)

```java
public class TenantRoutingDataSource extends AbstractRoutingDataSource {
    @Override protected Object determineCurrentLookupKey() {
        return TenantContext.get();
    }
}

@Bean
Map<Object, Object> targets(Map<String, DataSource> tenants) { return Map.copyOf(tenants); }
```

Pitfall: routing key must be set *before* the first connection checkout of the
request; lazy DataSource wiring (lookup against a service registry) must be
thread-safe.

## Async context propagation

```java
@Bean
Executor tenantAwareExecutor() {
    ThreadPoolTaskExecutor ex = new ThreadPoolTaskExecutor();
    ex.setTaskDecorator(r -> {
        String tenant = TenantContext.get();
        return () -> { try { TenantContext.set(tenant); r.run(); } finally { TenantContext.clear(); } };
    });
    ex.initialize();
    return ex;
}
```

Pitfall: `@Async` methods without the task decorator inherit a random
treadmill of previous tenant ids from the pool — intermittent cross-tenant
writes that pass tests and fail audits.

## Cache keys and RLS

```java
@Cacheable(value = "documents", key = "#root.target.tenantId() + ':' + #id")
public Document find(Long id) { ... }
```

Plus in Postgres: `ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_iso ON documents USING (tenant_id = current_setting('app.tenant'));`
Set `app.tenant` per connection checkout — belt and suspenders with the
Hibernate filter.
