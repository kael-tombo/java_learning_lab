# References: Database Security

## Academic Papers

### Foundational Papers
1. **Dynamo: Amazon's Highly Available Key-value Store** (2007)
   - Giuseppe DeCandia et al.
   - Introduced consistent hashing for production use

2. **Bigtable: A Distributed Storage System for Structured Data** (2006)
   - Fay Chang et al.
   - Described range-based partitioning at Google scale

3. **Spanner: Google's Globally-Distributed Database** (2012)
   - James C. Corbett et al.
   - Global-scale distribution with TrueTime

4. **Cassandra: A Decentralized Structured Storage System** (2009)
   - Avinash Lakshman, Prashant Malik
   - Consistent hashing with virtual nodes

### Advanced Topics
5. **Calvin: Fast Distributed Transactions for Partitioned Database Systems** (2012)
   - Alexander Thomson et al.

6. **SAGAS** (1987)
   - Hector Garcia-Molina, Kenneth Salem
   - Original Saga pattern paper

## Books
1. **Designing Data-Intensive Applications** — Martin Kleppmann
   - Chapters 5 (Replication) and 6 (Partitioning)

2. **Database Internals** — Alex Petrov
   - Part II: Distributed Systems

3. **Distributed Systems** — Maarten van Steen, Andrew S. Tanenbaum
   - Chapters on naming, consistency, replication

4. **High Performance MySQL, 4th Edition** — Silvia Botros, Jeremy Tinley
   - Chapter 11: Scaling MySQL

5. **Cassandra: The Definitive Guide, 3rd Edition** — Jeff Carpenter, Eben Hewitt
   - Chapters on replication strategies, schema design

## Online Resources

### Documentation
- Consistent Hashing: Tom White's Blog
- Vitess Documentation: vitess.io
- CockroachDB Architecture: cockroachlabs.com
- Citus Documentation: docs.citusdata.com
- MongoDB Sharding: mongodb.com/docs/manual/sharding

### Articles
- \"Sharding & IDs at Instagram\" — Instagram Engineering
- \"How Discord Scaled to 5M Users\" — Discord Engineering
- \"Uber's Scalability Best Practices\" — Uber Engineering

## Tools and Libraries

### Java Libraries
- **Guava Hashing**: com.google.common.hash.Hashing.consistentHash()
- **Apache Shardingsphere**: JDBC driver for sharding
- **Jedis**: Redis client with shard support
- **MongoDB Java Driver**: Native sharding support

### Infrastructure
- **Vitess**: MySQL-compatible sharding proxy
- **Citus**: PostgreSQL sharding extension
- **ProxySQL**: MySQL connection pool and routing
- **Kubernetes StatefulSets**: Orchestration

### Testing Tools
- **Testcontainers**: Integration testing with database containers
- **JMH**: Java Microbenchmark Harness
- **Chaos Mesh**: Chaos engineering for Kubernetes
- **Gatling**: Load testing

## Standards
- CAP Theorem: Eric Brewer (2000), proved by Gilbert and Lynch (2002)
- PACELC: Extension by Daniel J. Abadi (2012)
