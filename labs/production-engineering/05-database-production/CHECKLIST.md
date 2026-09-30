# CHECKLIST: Database Performance & Connection Gates
## Lab 05 | Production Engineering Academy

---

## 1. HikariCP & DataSource Configuration
- [ ] `maximumPoolSize` properly sized using the core count formula, NOT set arbitrarily high.
- [ ] `minimumIdle` matches `maximumPoolSize` to prevent runtime thread allocation stalls.
- [ ] `connectionTimeout` set to $\le 3000\text{ms}$ (fast-fail on starvation).
- [ ] `leakDetectionThreshold` enabled (e.g. $5000\text{ms}$).
- [ ] `maxLifetime` set 2-5 minutes shorter than network infrastructure / firewall timeout.

## 2. JPA & Hibernate Hygiene
- [ ] `spring.jpa.open-in-view` set to `false`.
- [ ] Batch fetching enabled (`hibernate.default_batch_fetch_size: 50`).
- [ ] Verified that NO external network calls (REST/gRPC/Kafka send) occur inside `@Transactional`.
- [ ] All entity collections fetch type explicitly audited (`FetchType.LAZY` default).
- [ ] Missing index check performed on all foreign key columns and query `WHERE` predicates.

## 3. Operational & Observability Gates
- [ ] HikariCP metrics exposed to Prometheus (`hikaricp.connections.active`, `hikaricp.connections.pending`).
- [ ] Alerting rule configured for connection pool wait time $> 100\text{ms}$.
- [ ] Slow query log enabled on database (log queries taking $> 250\text{ms}$).
