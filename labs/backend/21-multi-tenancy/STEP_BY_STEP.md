# Step by Step: Multi-Tenancy

## Step 1: Tenant Context
`java
public class TenantContext {
    private static final ThreadLocal<String> CURRENT_TENANT = new ThreadLocal<>();
    public static void setTenantId(String tenantId) { CURRENT_TENANT.set(tenantId); }
    public static String getTenantId() { return CURRENT_TENANT.get(); }
    public static void clear() { CURRENT_TENANT.remove(); }
}
`

## Step 2: Tenant Filter
`java
@Component
public class TenantFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) {
        String tenantId = ((HttpServletRequest) req).getHeader("X-Tenant-ID");
        TenantContext.setTenantId(tenantId);
        chain.doFilter(req, res);
        TenantContext.clear();
    }
}
`

## Step 3: Hibernate Multi-Tenancy
`java
@Bean
public HibernatePropertiesCustomizer tenantCustomizer() {
    return props -> {
        props.put(AvailableSettings.MULTI_TENANT, MultiTenancyStrategy.SCHEMA);
        props.put(AvailableSettings.MULTI_TENANT_IDENTIFIER_RESOLVER, tenantResolver());
        props.put(AvailableSettings.MULTI_TENANT_CONNECTION_PROVIDER, connectionProvider());
    };
}
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\21-multi-tenancy "CODE_DEEP_DIVE.md") @"
# Code Deep Dive: Multi-Tenancy

## AbstractDataSourceBasedMultiTenantConnectionProviderImpl
This abstract class provides DataSource per tenant. The method selectDataSource() is called for each database operation. It maps tenant ID to a DataSource, allowing dynamic tenant isolation.

## CurrentTenantIdentifierResolverImpl
Hibernate calls resolveCurrentTenantIdentifier() for every JDBC connection. The implementation reads from TenantContext ThreadLocal. For schema-per-tenant, it returns the schema name.
