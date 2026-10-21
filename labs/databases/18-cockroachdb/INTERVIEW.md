# Interview Questions: CockroachDB (Oracle Comparison)

## Oracle-Specific Questions
- Compare CockroachDB's distributed SQL architecture with Oracle RAC + Sharding.
- How does CockroachDB's serializable isolation compare to Oracle's isolation levels?
- Compare CockroachDB's range-based sharding (automatic) with Oracle Sharding (manual).
- How does CockroachDB handle distributed transactions (parallel commit) compared to Oracle?
- Compare CockroachDB's replication (RAFT consensus) with Oracle Data Guard (redo shipping).
- How does CockroachDB's geo-partitioning compare to Oracle Partitioning for data residency?
- Compare CockroachDB's SQL compatibility with Oracle SQL — what features are missing?
- When would you choose CockroachDB over Oracle for a globally distributed application?

## Google Cloud / Technical
- Cloud Spanner vs CockroachDB — both globally distributed SQL
- Cloud SQL vs CockroachDB for single-region deployments
- CockroachDB on GKE vs Google Cloud Spanner

## Microsoft / Azure
- Azure Cosmos DB Core (SQL) API vs CockroachDB
- CockroachDB on Azure AKS vs Azure SQL Hyperscale
- Azure SQL Managed Instance vs CockroachDB

## Amazon / AWS
- Amazon Aurora vs CockroachDB for multi-region SQL
- DynamoDB vs CockroachDB for key-value + transaction needs
- CockroachDB on EKS vs RDS Multi-AZ

## Apple
- Apple's use of CockroachDB for iCloud services
- Data residency requirements met by CockroachDB geo-partitioning

## LeetCode-Style Problems
| Problem | Topic | Difficulty | Pattern |
|---------|-------|-----------|---------|
| Distributed TX | 2PC vs Parallel Commit | Hard | Consensus |
| Geo-Partition | Data Residency | Medium | Locality |
| Range Splitting | Hot Range | Hard | Load-based Splitting |
| Online DDL | Schema Changes | Medium | Non-blocking |

## Production Scenarios
- Scenario 1: "Hot range causing single-node bottleneck in CockroachDB cluster"
- Scenario 2: "Distributed transaction contention — serialization failures"
- Scenario 3: "CockroachDB node decommission taking too long"
- Scenario 4: "Locality-constrained access not using optimal replica"

## Interview Patterns & Tips
- Oracle interviews ask CockroachDB to evaluate distributed SQL expertise
- Know how CockroachDB's architecture differs from Oracle's
- CockroachDB + Oracle knowledge is valued for migration and modernization projects
- Distributed SQL architects: $150K-$220K
- CockroachDB certification is a plus for cloud-native roles
