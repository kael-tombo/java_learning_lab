# Azure Fundamentals - Real World Project

## Project: Landing a New Service on Azure with Production Defaults

### Objective
Take a new service from empty subscription to production: resource group hierarchy, network
isolation, managed identities end to end, RBAC, IaC, and a landing-zone structure it can live
in without special pleading.

### Why This Matters
The first service in a new cloud environment sets the pattern. If it needs a special
exception for networking or permissions, every subsequent service asks for the same exception.

### Architecture Overview
```
  Subscription (prod)
   └── Resource group: rg-orders-prod-westeurope
        ├── Virtual network + subnets (app / integration / private endpoints)
        │     └── private endpoint → storage, key vault, sql
        ├── Azure SQL Database (+ private endpoint)
        ├── Storage account (private endpoint, no public access)
        ├── Key Vault (private endpoint, RBAC not access policies)
        ├── App Service / AKS with managed identity
        └── Application Insights + Log Analytics
   Tag policy applied at subscription: env, service, owner, costCentre
```

### Phase 1: Establish the Structure (Week 1)
1. Resource group naming: `rg-{service}-{env}-{region}`; document the standard
2. Subscription-level tag policy so untagged resources are rejected at deployment
3. Decide the sharing model: shared virtual network with per-service subnets, or per-service
   VNet. Write down the trade-off; the shared model is cheaper and simpler, the per-service
   model isolates blast radius
4. Identify the private endpoints required — services that must not have public access

### Phase 2: Network Isolation (Week 2)
1. Subnets sized for the workload with address headroom documented for the next two services
2. Private endpoints for SQL, Storage, and Key Vault; public network access disabled on all
   three
3. Service endpoints or private link for the remaining dependencies
4. NSGs as default-deny with explicit rules derived from a flow table — the same discipline as
   lab 05
5. Test the boundary: from outside, the data tier is unreachable; from the app subnet, it is

### Phase 3: Identity End to End (Week 3)
1. System-assigned or user-assigned managed identity for the compute; prefer user-assigned so
   the identity outlives a resource recreation
2. Role assignments scoped to the specific database, container, and vault
3. Key Vault with RBAC authorization (not the legacy access-policy model)
4. **No secrets in application configuration** — verified by a CI scan
5. Break-glass: a separate, time-limited, monitored path to elevated access

### Phase 4: Observability and Operations (Week 4)
1. Application Insights with request, dependency, and exception telemetry from day one — the
   cost of backfilling traces is much higher than the cost of turning it on
2. Structured logging with trace correlation via the SDK's automatic context
3. Dashboards: RED per service plus the dependency view; alert on the SLI, not the cause
4. Cost allocation: the costCentre tag flows to the billing report; verify it appears

### Phase 5: Operate and Reuse (Week 5+)
1. CI/CD pipeline with plan review, tag validation, and the secret scan
2. Blue/green or canary deployment with automated rollback on SLI breach
3. Disaster recovery documented: what is replicated, what is not, and the actual RTO
4. **Extract the reusable parts into a service template** so the next service is a parameter
   change rather than a rebuild — that is the real measure of success for this project

### Deliverables
1. Resource group hierarchy, naming standard, and subscription tag policy
2. Networked deployment with private endpoints and default-deny NSGs
3. Managed identity and scoped RBAC with no secrets, verified by CI
4. Observability wired in, plus the service template for reuse

### Success Criteria
- No resource exists without the required tags, enforced at deployment
- Data tier unreachable from the internet, verified by test
- Zero secrets in source or configuration, enforced by CI on every commit
- A second team deploys a new service from the template without platform help

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Microsoft Learn, Azure RBAC overview —
  https://learn.microsoft.com/en-us/azure/role-based-access-control/overview
  Use for: role definition versus assignment, scope inheritance, and the guidance on choosing
  the narrowest scope. Verify current built-in role names before using them in IaC.
- Microsoft Learn, managed identities —
  https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview
  Use for: system- versus user-assigned identity behaviour and the token acquisition flow the
  Java SDK uses. Verify current SDK package names against this page.

### Estimated Time
7-8 weeks part-time