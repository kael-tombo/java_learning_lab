# Interview Questions: Database Testing (Oracle Focus)

## Oracle-Specific Questions
- How do you test Oracle database schema changes in CI/CD? Explain `SQLcl` and `Flyway` in testing pipeline.
- What is Oracle Real Application Testing (RAT)? Explain SQL Performance Analyzer (SPA) and Database Replay.
- How do you use Oracle's `DBMS_SQLPA` to test query performance after system changes?
- What are Oracle unit testing options for PL/SQL? Explain `UTPLSQL`, `utPLSQL` v3, and `DBMS_TUNE`.
- How do you test Oracle RAC failover scenarios? What tools do you use?
- Explain how you would load-test an Oracle database using Swingbench or HammerDB.
- How do you test Data Guard switchover/failover procedures?
- What are Oracle's testing tools for backup and recovery? Explain `RMAN` validation and `RESTORE ... VALIDATE`.

## Google Cloud / Technical
- Cloud SQL database testing vs Oracle RAT
- Load testing on Cloud SQL vs Oracle on compute
- CI/CD database testing with Cloud Build

## Microsoft / Azure
- Azure SQL database testing tools vs Oracle
- SQL Server Data Tools vs Oracle SQL Developer testing
- Azure DevOps database deployments testing

## Amazon / AWS
- RDS Oracle testing with AWS DMS replication tests
- Aurora testing toolkit vs Oracle RAT
- Database migration testing automation on AWS

## Apple
- Testing compliance with Apple's data privacy requirements
- Database testing for Apple supplier data security

## LeetCode-Style Problems
| Problem | Topic | Difficulty | Pattern |
|---------|-------|-----------|---------|
| Test Case | Migration Rollback | Medium | Integration Test |
| Test Plan | HA Failover | Hard | Chaos Engineering |
| Benchmark | TPS Measurement | Medium | Performance Test |
| Validation | Data Integrity | Medium | Reconciliation |

## Production Scenarios
- Scenario 1: "SQL Performance Analyzer finds 20% queries regressed after upgrade"
- Scenario 2: "Database Replay shows 50% throughput drop in production-like test"
- Scenario 3: "PL/SQL unit tests passing in DEV but failing in PROD due to data differences"
- Scenario 4: "Load test causes ORA-1555 — testing didn't catch undo exhaustion"

## Interview Patterns & Tips
- Oracle RAT (Real Application Testing) is a key differentiator for senior DBA roles
- Know SPA (SQL Performance Analyzer) and Database Replay features
- OCP covers backup/recovery validation and testing
- Testing automation specialists: $120K-$175K
- Chaos engineering for databases is an emerging skill
