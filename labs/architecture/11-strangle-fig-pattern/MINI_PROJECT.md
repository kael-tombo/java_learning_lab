# Mini Project — Strangler Fig Pattern

## Goal

Migrate a legacy monolithic inventory system to a new microservices
architecture using the Strangler Fig Pattern. Build a routing layer that
gradually shifts traffic from the old system to the new one.

## Requirements

### Legacy System (Simulated)
- Monolithic inventory management
- Single database
- All functionality in one deployable unit

### New System (Microservices)
- `Product Service` — product catalog management
- `Stock Service` — stock level tracking
- `Pricing Service` — price management

### Routing Layer (Strangler)
- Intercepts all incoming requests
- Routes to legacy or new system based on migration status
- Supports gradual traffic shifting (percentage-based)
- Handles fallback to legacy on new system failure

### Migration Phases

**Phase 1: Product Catalog**
- Route product read requests to new Product Service
- Product writes still go to legacy system
- Sync product data between systems

**Phase 2: Stock Management**
- Route stock requests to new Stock Service
- Legacy system receives stock updates via events
- Gradually shift read traffic

**Phase 3: Pricing**
- Route pricing requests to new Pricing Service
- Legacy system decommissioned for pricing
- Full migration complete

## Technical Specifications

1. **Routing layer**
   - Reverse proxy or API gateway
   - Configuration-driven routing rules
   - Percentage-based traffic splitting
   - Fallback to legacy on failure

2. **Data synchronization**
   - Event-driven sync from legacy to new system
   - Anti-corruption layer for data transformation
   - Conflict resolution strategy

3. **Monitoring**
   - Track traffic split between systems
   - Monitor error rates on both paths
   - Alert on new system failures

## Steps

1. Set up legacy system (simulated monolith)
2. Build routing layer with configuration
3. Implement Product Service
4. Route product reads to new service
5. Implement data sync from legacy
6. Implement Stock Service
7. Route stock requests to new service
8. Implement Pricing Service
9. Route pricing requests to new service
10. Decommission legacy system
11. Remove routing layer
12. Write tests for routing and fallback

## Acceptance Criteria

- [ ] Routing layer correctly routes based on configuration
- [ ] Traffic can be gradually shifted (percentage-based)
- [ ] New system failures fall back to legacy
- [ ] Data is synchronized between systems
- [ ] Each phase can be rolled back independently
- [ ] Legacy system is eventually decommissioned

## Stretch Goals

- Implement feature flags for routing decisions
- Add canary deployment for new services
- Implement event sourcing for data sync
- Add monitoring dashboard for migration progress
