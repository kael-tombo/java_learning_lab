# Architecture: Multi-Tenancy

`
Request â”€â”€â–¶ [Tenant Filter] â”€â”€â–¶ [TenantContext.setTenantId()]
              â”‚
              â–¼
        [Controller/Service]
              â”‚
              â–¼
        [Hibernate]
              â”‚
              â–¼
    [CurrentTenantIdentifierResolver]
              â”‚
              â–¼
    [ConnectionProvider.getDataSource(tenantId)]
              â”‚
         â”Œâ”€â”€â”€â”€â”´â”€â”€â”€â”€â”
         â–¼         â–¼
    [Tenant1 DB] [Tenant2 DB]
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\21-multi-tenancy "SECURITY.md") @"
# Security: Multi-Tenancy

Critical: Never allow cross-tenant data access. Validate tenant ID matches authenticated user's tenant. Use database-level isolation (separate schemas/DBs) for sensitive data. Test tenant isolation thoroughly. Log tenant accesses for audit. Use stored procedures with tenant context for defense in depth.
