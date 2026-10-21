# Interview Questions: Database Sharding (Oracle Focus)

## Oracle-Specific Questions
- How does Oracle Sharding (Oracle Database 12c+) compare to MongoDB sharding and Cassandra partitioning?
- Explain Oracle Sharding architecture: shard directors, shard catalogs, and shard deployment topologies.
- How does Oracle Sharding handle cross-shard queries and distributed transactions?
- Compare Oracle Sharding with Oracle RAC — when would you choose sharding vs RAC for scalability?
- How does Oracle Sharding handle schema management across shards? Explain global vs sharded tables.
- What is the Oracle SDB (Sharded Database) connection pool architecture?
- How does Oracle Sharding compare to application-level sharding patterns?
- Explain Oracle Sharding's automatic rebalancing: how does it redistribute data when adding shards?

## Google Cloud / Technical
- Cloud Spanner vs Oracle Sharding for global data distribution
- Cloud SQL read replicas vs Oracle Sharding for read scalability
- BigTable vs Oracle Sharding for wide-column workloads

## Microsoft / Azure
- Azure SQL Database elastic scale vs Oracle Sharding
- Cosmos DB partitioning vs Oracle sharding
- Azure SQL sharding library patterns

## Amazon / AWS
- Amazon Aurora global database vs Oracle Sharding
- DynamoDB partitioning vs Oracle sharding
- RDS multi-AZ vs Oracle Sharding for HA

## Apple
- Global data distribution for Apple services
- Data residency compliance with sharding

## LeetCode-Style Problems
| Problem | Topic | Difficulty | Pattern |
|---------|-------|-----------|---------|
| Consistent Hashing | Ring-based distribution | Hard | Distributed Systems |
| Shard Key Selection | Hotspot avoidance | Hard | Data Modeling |
| Cross-Shard Join | Scatter-gather | Hard | Distributed Query |
| Rebalancing | Data migration | Hard | Incremental Migration |

## Production Scenarios
- Scenario 1: "Hot shard — uneven data distribution in Oracle SDB"
- Scenario 2: "Cross-shard query performance — scatter-gather timeout"
- Scenario 3: "Shard rebalancing causing application downtime"
- Scenario 4: "Adding new shard — data redistribution takes too long"

## Interview Patterns & Tips
- Oracle Sharding is a premium topic for high-scale architecture interviews
- Know the trade-offs: RAC vs Sharding vs Partitioning vs Application-level sharding
- Oracle Sharding is newer — experience is a differentiator
- Distributed database architects: $150K-$220K
- OCP: Oracle Database 19c Sharding certification recommended
