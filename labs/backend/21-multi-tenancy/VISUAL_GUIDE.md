# Visual Guide: Multi-Tenancy

`
DB-per-Tenant:      Schema-per-Tenant:   Discriminator:
â”Œâ”€â”€â”€â”€â”€â”â”Œâ”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ T1  â”‚â”‚ T2  â”‚     â”‚ public.schema1   â”‚  â”‚ Table with       â”‚
â”‚ DB  â”‚â”‚ DB  â”‚     â”‚ public.schema2   â”‚  â”‚ tenant_id column â”‚
â””â”€â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\21-multi-tenancy "DEBUGGING.md") @"
# Debugging: Multi-Tenancy

1. Enable SQL logging to verify schema/DB switching
2. Check tenant ID in request context
3. Verify ThreadLocal cleanup in finally blocks
4. Test with multiple tenants simultaneously
5. Verify DataSource pool per tenant
6. Check Hibernate multi-tenancy configuration
