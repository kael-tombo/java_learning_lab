# Lab 21: Multi-Tenancy

## Overview
Multi-tenancy allows a single application instance to serve multiple customers (tenants). Learn schema-per-tenant, database-per-tenant, and discriminator column approaches.

## Topics Covered
- Multi-tenant architecture patterns
- Schema-per-tenant with Hibernate
- Database-per-tenant with routing
- Tenant identification strategies (subdomain, header, JWT)
- Tenant context propagation
- Flyway/Flyway multi-tenant migrations
- SaaS application patterns

## Prerequisites
- Java 21+
- Spring Boot 3.3+
- JPA/Hibernate knowledge

## Key Dependencies
`xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\21-multi-tenancy "THEORY.md") @"
# Theory: Multi-Tenancy

## 1. Multi-Tenant Architecture Patterns

### Database-per-Tenant
Each tenant gets a separate database. Highest isolation, higher operational cost, no cross-tenant data leak.

### Schema-per-Tenant
Each tenant uses the same database but different schema. Good isolation, shared connection pool, more complex migration.

### Discriminator Column
All tenants share the same tables, with a tenant_id column. Lowest isolation, simplest, highest risk of data leak.

## 2. Comparison

| Pattern | Isolation | Cost | Complexity | Scalability |
|---------|-----------|------|------------|-------------|
| DB Per Tenant | Highest | High | High | Best |
| Schema Per Tenant | High | Medium | Medium | Good |
| Discriminator | Low | Low | Low | Limited |

## 3. Tenant Resolution

- Subdomain (tenant1.app.com)
- Header (X-Tenant-ID)
- JWT claim
- URL path (/api/v1/{tenant}/users)
- Custom DNS (each tenant has unique CNAME)

## 4. Tenant Context

ThreadLocal stores current tenant ID, propagated via:
- Filter/interceptor
- Feign/WebClient interceptors
- Hibernate CurrentTenantIdentifierResolver
- Message listener interceptors
