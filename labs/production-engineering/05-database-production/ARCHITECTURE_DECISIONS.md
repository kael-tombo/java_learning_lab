# ARCHITECTURE DECISIONS: Database Connection & Transaction Architecture
## Lab 05 | Production Engineering Academy

---

## ADR-01: Connection Pooling & Multiplexing Strategy (PgBouncer vs In-App Sizing)

### Status: ACCEPTED

### Context
Our microservices fleet consists of 30 services deployed across 150 Kubernetes Pods, accessing a 32-core Amazon Aurora PostgreSQL cluster. At peak traffic, pod autoscaling caused connection count to surge past 2,500 connections, exceeding PostgreSQL memory limits and causing connection rejections.

### Decision
1. **Deploy Centralized Connection Poolers**:
   - Provision HA PgBouncer proxy layer (3 instances) between Kubernetes and Aurora.
   - Configure PgBouncer in **Transaction Pooling Mode**.
   - Set server connection limit to 120 total physical connections to PostgreSQL.
2. **Standardize Application HikariCP Sizing**:
   - Every Java service pod is restricted to `maximumPoolSize = 10`.
   - `minimumIdle` set equal to `maximumPoolSize` (fixed pool).
   - `connectionTimeout` set to `3000ms` (fail-fast principle).
3. **Application Guidelines for Transaction Pooling**:
   - Forbid the use of prepared statement sessions that leak across transaction boundaries without session reset.
   - Forbid `LISTEN/NOTIFY` over pooled transactional connections.

### Consequences
- Total server-side connections reduced by 94% (from 2,500 down to 120).
- PostgreSQL cache hit ratio improved from 88% to 99.4% due to freed memory buffers.
- Maximum database throughput increased by $4.2\times$.
