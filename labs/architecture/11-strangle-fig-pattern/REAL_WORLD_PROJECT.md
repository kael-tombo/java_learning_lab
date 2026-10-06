# Real-World Project — Strangler Fig Pattern

## Scenario

A large e-commerce company runs a 15-year-old monolithic application
that handles product catalog, inventory, orders, and customer management.
The monolith has become a bottleneck: deployments take hours, scaling
is expensive, and new features take months to ship. The company wants
to migrate to a microservices architecture without disrupting the
business or risking a big-bang rewrite.

## System Overview

The migration follows the Strangler Fig Pattern with a routing layer
gradually shifting traffic:

| Phase | Service | Duration | Traffic Split |
|-------|---------|----------|---------------|
| 1 | Product Catalog | 3 months | 10% → 100% |
| 2 | Inventory | 4 months | 10% → 100% |
| 3 | Orders | 6 months | 10% → 100% |
| 4 | Customer | 3 months | 10% → 100% |
| 5 | Decommission | 2 months | Legacy retired |

## Architecture Decisions

### Routing Layer
- **API Gateway** (Kong/AWS API Gateway) as the strangler facade
- **Configuration-driven routing** with percentage-based traffic splitting
- **Feature flags** for gradual rollout and instant rollback
- **Fallback to legacy** on new service failure (circuit breaker)

### Data Synchronization
- **Change Data Capture (CDC)** from legacy database to new services
- **Event-driven sync** using Kafka for real-time data propagation
- **Anti-corruption layer** to translate between legacy and new data models
- **Dual-write prevention** through careful routing and sync ordering

### Migration Strategy
- **Extract most independent services first** (Product Catalog)
- **Leave most coupled services for last** (Orders)
- **Maintain legacy system** until all services migrated
- **Decommission legacy** only after full migration and validation

### Risk Mitigation
- **Instant rollback** via routing configuration changes
- **Shadow testing** — route read traffic to both systems, compare results
- **Gradual traffic shifting** — 1% → 5% → 10% → 50% → 100%
- **Monitoring and alerting** on both old and new systems

## Implementation Phases

### Phase 1: Foundation
1. Set up API Gateway as routing layer
2. Implement routing configuration and feature flags
3. Set up CDC from legacy database
4. Build monitoring and alerting

### Phase 2: Product Catalog
5. Extract Product Catalog service
6. Implement data sync from legacy
7. Route product reads to new service (gradually)
8. Route product writes to new service
9. Validate data consistency

### Phase 3: Inventory
10. Extract Inventory service
11. Implement inventory data sync
12. Route inventory operations to new service
13. Validate inventory accuracy

### Phase 4: Orders
14. Extract Order service
15. Implement order data sync
16. Route order operations to new service
17. Validate order processing

### Phase 5: Decommission
18. Extract Customer service
19. Migrate remaining legacy functionality
20. Decommission legacy monolith
21. Remove routing layer
22. Optimize new architecture

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Martin Fowler — Strangler Fig Pattern**: https://martinfowler.com/bliki/StranglerFigApplication.html
  Martin Fowler's original article on the Strangler Fig Pattern,
  explaining the approach, benefits, and implementation strategies.

- **AWS — Strangler Fig Pattern**: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html
  AWS blog post on using the Strangler Fig Pattern for legacy migration,
  including practical implementation guidance and lessons learned.

## Success Metrics

- Zero downtime during migration
- Deployment frequency: from monthly to daily
- New feature delivery time: from months to weeks
- System scalability: independent scaling per service
- Legacy system decommissioned within 18 months

## Lessons from Production

1. **Start with the most independent service** — it reduces risk and
   builds confidence in the migration approach.

2. **Invest in the routing layer** — it's the backbone of the migration;
   make it robust, configurable, and observable.

3. **Data synchronization is the hardest part** — plan for it early,
   monitor it constantly, and have rollback strategies.

4. **Don't rush decommissioning** — keep the legacy system running until
   you're confident the new system is stable and complete.
