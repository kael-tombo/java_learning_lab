# Interview Questions: Database Replication (Oracle Focus)

## Oracle-Specific Questions
- Explain Oracle Data Guard architecture: physical standby vs logical standby vs snapshot standby.
- How does Oracle Active Data Guard differ from regular Data Guard? What features require Active Data Guard license?
- Explain Oracle GoldenGate architecture: Extract, Pump, Replicat, and trail files.
- How does Oracle RAC with Data Guard provide high availability and disaster recovery?
- What is Oracle Far Sync for zero data loss in Data Guard?
- Explain Oracle's Maximum Protection, Maximum Availability, and Maximum Performance protection modes.
- How do you monitor Data Guard lag and resolve log transport gaps?
- Compare Oracle GoldenGate bidirectional replication with Data Guard for active-active scenarios.

## Google Cloud / Technical
- Cloud SQL read replicas vs Oracle Data Guard
- Cloud Spanner replication vs Oracle GoldenGate
- BigQuery CDC with Oracle GoldenGate

## Microsoft / Azure
- Azure SQL Active Geo-Replication vs Oracle Data Guard
- SQL Server Always On vs Oracle RAC + Data Guard
- Azure Database Migration Service for Oracle CDC

## Amazon / AWS
- Amazon RDS Multi-AZ vs Oracle Data Guard
- AWS DMS CDC from Oracle to target databases
- Aurora Global Database vs Oracle GoldenGate

## Apple
- Cross-region data replication for Apple services
- Data sovereignty compliance in replication

## LeetCode-Style Problems
| Problem | Topic | Difficulty | Pattern |
|---------|-------|-----------|---------|
| CAP Theorem | Consistency vs Availability | Medium | Distributed Systems |
| Replication Lag | Eventual Consistency | Medium | Timing Analysis |
| Conflict Resolution | Last Writer Wins | Hard | CRDT |
| Log Shipping | WAL-based Replication | Medium | Log Sequence Numbers |

## Production Scenarios
- Scenario 1: "Data Guard gap not resolving — archive log deletion before shipping"
- Scenario 2: "GoldenGate replication lag causing stale data on target"
- Scenario 3: "RAC node failure — Data Guard failover initiated incorrectly"
- Scenario 4: "Bidirectional GoldenGate conflict — same row updated on both sides"

## Interview Patterns & Tips
- Oracle interviews deeply test Data Guard and GoldenGate knowledge
- Expect architecture design questions for HA/DR using Oracle replication
- OCP covers: Data Guard Administration, Oracle Backup and Recovery
- OCM requires advanced Data Guard and RAC troubleshooting
- HA/DR architects: $140K-$210K; GoldenGate specialists: $130K-$190K
