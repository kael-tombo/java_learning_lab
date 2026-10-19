# Mini Project: Multi-Tenancy

## The assignment

This multi-tenancy mini build produces a working fitness-studio SaaS tenants you can run locally.
Scope stays deliberately small so every multi-tenancy behavior remains observable.
Budget roughly one focused evening for the fitness-studio SaaS tenants implementation.
Success means demonstrating multi-tenancy judgment, not just compiling code.
Keep a lab journal noting each multi-tenancy surprise encountered.
Hold the line at the acceptance checks; nothing extra sneaks in beyond them.

## Parts you will wire

- Tenant-resolution strategies.
- Schema-per-tenant versus discriminator choice.
- Tenant-scoped queries.
- Onboarding and offboarding flows.
- Cross-tenant leak testing.

## Build order

1. Serve three fitness studios from one deployed service for the service.
2. Resolve tenants from request context explicitly.
3. Scope every class-booking query to its tenant.
4. Onboard a fourth studio without touching existing data.
5. Attempt cross-tenant reads and prove they fail.

## Acceptance checks

- [ ] 3 seeded studios operate with fully isolated bookings in the solution.
- [ ] Resolution strategy documented with its trade-off in the platform.
- [ ] All 40 booking queries carry tenant scope.
- [ ] Fourth studio onboarded with zero existing-data disturbance.
- [ ] 10 crafted cross-tenant reads all denied.

## Stretch

Grow the project by adding one realistic complication you select.
Write the two-paragraph retro: which multi-tenancy decision proved hardest.
Demo time: the peer sees the system with just the acceptance checks as the guide.
