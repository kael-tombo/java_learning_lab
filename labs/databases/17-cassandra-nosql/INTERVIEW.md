# Interview Questions: Cassandra (Oracle Comparison)

## Oracle-Specific Questions
- Compare Cassandra's partition key model with Oracle Sharding for distributed data distribution.
- How does Cassandra's eventual consistency compare to Oracle's ACID consistency model?
- Compare Cassandra's CQL with Oracle SQL — what are the limitations of CQL?
- How does Cassandra's `ALLOW FILTERING` compare to Oracle full table scans?
- Compare Cassandra's lightweight transactions (LWT) with Oracle transactions.
- How does Cassandra's compaction strategy compare to Oracle's segment management?
- Compare Cassandra's hinted handoff with Oracle Data Guard gap resolution.
- When would you choose Cassandra over Oracle for time-series or IoT workloads?

## Google Cloud / Technical
- Cloud Bigtable vs Cassandra for wide-column workloads
- Cloud Spanner vs Cassandra for strong consistency + scale
- BigQuery vs Cassandra for analytics on time-series data

## Microsoft / Azure
- Azure Cosmos DB Cassandra API vs native Cassandra
- Azure Managed Instance for Apache Cassandra
- Cosmos DB consistency levels vs Cassandra tunable consistency

## Amazon / AWS
- Amazon Keyspaces (managed Cassandra) vs self-managed Cassandra
- DynamoDB vs Cassandra for key-value workloads
- AWS DMS for Oracle to Cassandra migration

## Apple
- Apple's use of Cassandra for iMessage and other services
- Data privacy in eventually consistent systems

## LeetCode-Style Problems
| Problem | Topic | Difficulty | Pattern |
|---------|-------|-----------|---------|
| Time Series | IoT Sensor Data | Medium | Wide Row Design |
| Hotspot | Celebrity Key | Hard | Partition Key |
| Counters | Like Counter | Medium | Distributed Counter |
| Timeline | User Feed | Hard | Time UUID Ordering |

## Production Scenarios
- Scenario 1: "Cassandra read repair causing high CPU during peak traffic"
- Scenario 2: "Hinted handoff queue growing — node down for extended period"
- Scenario 3: "Compaction strategy causing disk space exhaustion"
- Scenario 4: "Cassandra tombstone overload — query timeouts"

## Interview Patterns & Tips
- Oracle interviews ask Cassandra to evaluate NoSQL expertise
- Expect comparison questions: Oracle vs Cassandra for specific use cases
- Cassandra knowledge is valuable for IoT and time-series projects with Oracle
- Multi-database architects: $130K-$200K
- Cassandra + Oracle skills are rare and highly valued
