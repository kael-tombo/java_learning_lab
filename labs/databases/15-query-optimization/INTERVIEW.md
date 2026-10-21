# Interview Questions: Query Optimization II (Oracle Advanced)

## Oracle-Specific Questions
- Explain Oracle's Adaptive Query Optimization: adaptive plans, adaptive statistics, and automatic re-optimization.
- How does Oracle's SQL Plan Management (SPM) evolve plan baselines? Explain `DBMS_SPM.EVOLVE_SQL_PLAN_BASELINE`.
- What are Oracle's Query Optimizer hints? Explain `/*+ LEADING */`, `/*+ USE_HASH */`, `/*+ INDEX */`, `/*+ NO_EXPAND */`.
- How does Oracle handle SQL Tuning Advisor? Explain `DBMS_SQLTUNE` and automatic SQL tuning.
- Explain Oracle Real-Time SQL Monitoring: how does it capture execution statistics for long-running queries?
- What are Oracle SQL Profiles and SQL Patches? How are they different from SPM?
- Explain Oracle's Dynamic Statistics (`dynamic_sampling`) and when it improves query plans.
- How does Oracle's Result Cache work and when should it be used?

## Google Cloud / Technical
- AlloyDB query optimization vs Oracle's CBO
- Cloud SQL's `pg_hint_plan` vs Oracle optimizer hints
- BigQuery slot management vs Oracle parallel execution

## Microsoft / Azure
- SQL Server Query Store vs Oracle SPM
- Azure SQL automatic tuning vs Oracle SQL Tuning Advisor
- SQL Server indexed views vs Oracle materialized views

## Amazon / AWS
- Amazon RDS Oracle Performance Insights vs AWR
- Aurora PostgreSQL query plan management vs Oracle SPM
- Redshift query optimization vs Oracle adaptive plans

## Apple
- Query optimization for Apple-scale OLTP systems
- Cost optimization for cloud-based Oracle queries

## LeetCode-Style SQL Problems
| Problem | Topic | Difficulty | Pattern |
|---------|-------|-----------|---------|
| LC 569 | Median Employee Salary | Hard | PERCENTILE_CONT |
| LC 571 | Find Median Given Frequency | Hard | Window + SUM |
| LC 601 | Human Traffic of Stadium | Hard | Self JOIN |
| LC 615 | Average Salary | Hard | CASE + AVG |
| LC 618 | Students Report | Hard | PIVOT |
| LC 626 | Exchange Seats | Medium | CASE + LEAD |
| LC 1097 | Game Play Analysis V | Hard | Window + LEAD |

## Production Scenarios
- Scenario 1: "Adaptive plan changing mid-execution causing performance oscillation"
- Scenario 2: "SPM baseline not evolving — good plan not captured"
- Scenario 3: "SQL Tuning Advisor recommending wrong fix"
- Scenario 4: "Result cache poisoning with stale data"

## Interview Patterns & Tips
- Advanced query optimization is for senior DBA and performance architect roles
- Know Oracle's adaptive optimization features in detail
- OCM requires mastery of SPM, SQL Profiles, and SQL Tuning Advisor
- Performance Architects: $150K-$230K
- Real-world AWR/ASH analysis is expected at architect level
