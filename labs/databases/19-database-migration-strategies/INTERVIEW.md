# Interview Questions: Database Migration Strategies (Oracle Focus)

## Oracle-Specific Questions
- What are the key strategies for migrating Oracle databases to the cloud (OCI, AWS RDS, Azure SQL)?
- How does Oracle GoldenGate enable zero-downtime migration? Explain the trickle-feed approach.
- Compare Oracle export/import (`expdp`/`impdp`) vs RMAN for database migration.
- How do you migrate Oracle EBS to OCI? What are the certification requirements and supported configurations?
- Explain Oracle's Automatic Data Optimization (ADO) and Information Lifecycle Management (ILM) in migrations.
- How do you migrate from Oracle to PostgreSQL using ora2pg or AWS DMS?
- What are the common challenges in Oracle to cloud migrations? (licensing, character sets, timezone)
- How do you migrate Oracle PL/SQL to PostgreSQL PL/pgSQL? What are the key syntax differences?

## Google Cloud / Technical
- Database Migration Service (DMS) for Oracle to Cloud SQL PostgreSQL
- Striim and GoldenGate for Oracle to BigQuery streaming
- Cloud SQL vs Bare Metal Solution for Oracle workloads

## Microsoft / Azure
- Azure Database Migration Service for Oracle to Azure SQL
- SQL Server Migration Assistant (SSMA) for Oracle
- Azure SQL Managed Instance vs Oracle — feature comparison

## Amazon / AWS
- AWS DMS for Oracle to Aurora PostgreSQL migration
- AWS Schema Conversion Tool (SCT) for Oracle schema conversion
- RDS Oracle to Aurora Oracle — migration best practices

## Apple
- Data privacy during database migration — encryption at rest/in transit
- Compliance validation in migration procedures

## LeetCode-Style Problems
| Problem | Topic | Difficulty | Pattern |
|---------|-------|-----------|---------|
| Migration Plan | Zero-Downtime Cutover | Hard | Rollback Strategy |
| Data Validation | Record-level Reconciliation | Medium | Checksum |
| Schema Conversion | PL/SQL to PL/pgSQL | Hard | Syntax Mapping |
| Performance Baseline | Before/After Comparison | Medium | AWR vs pg_stat |

## Production Scenarios
- Scenario 1: "Oracle to PostgreSQL migration — character set conversion corrupts data"
- Scenario 2: "GoldenGate migration lag causes cutover decision difficulty"
- Scenario 3: "Schema conversion tool fails on complex PL/SQL package"
- Scenario 4: "Migration rollback needed — data written to both databases inconsistently"

## Interview Patterns & Tips
- Oracle cloud migration interviews are high-demand in the current market
- Expect to design a complete migration strategy with zero-downtime cutover
- OCP + Cloud certification is highly valued for migration roles
- Migration architects: $140K-$210K; Cloud migration leads: $160K-$240K
- Migration experience is one of the most sought-after Oracle skills
