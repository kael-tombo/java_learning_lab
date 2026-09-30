# PRODUCTION SCENARIOS: Major Incident Case Studies
## Lab 14 | Production Engineering Academy

---

## Post-Mortem: The 84-Minute Payment Gateway Outage (Sev-1)

### Executive Summary
On 2026-06-14 from 13:10 UTC to 14:34 UTC (84 minutes), the global Payment Service failed to process credit card transactions, resulting in an estimated $1.4M in lost revenue and 42,000 failed checkout attempts.

### Timeline of Events (All times UTC)
- **13:10**: Payment Service latency spikes from 120ms to 8,000ms.
- **13:12 (MTTD = 2m)**: PagerDuty fires P1 alert: `PaymentService_HighErrorRate_SLO_Breach`.
- **13:15 (MTTA = 3m)**: Primary On-Call engineer acknowledges page and spins up emergency bridge.
- **13:20**: 15 engineers join the Zoom bridge simultaneously. Cross-talk ensues; 3 different people attempt manual restarts without coordinating.
- **13:28**: VP of Product joins bridge demanding immediate updates, distracting technical lead for 12 minutes.
- **13:40**: Staff Architect establishes formal Incident Command (IC) role, silences the bridge, and assigns Comms Lead to manage executives in Slack channel.
- **13:48**: Scribe logs finding from async-profiler: 98% of Tomcat threads BLOCKED on database connection pool.
- **13:55**: Database DBA discovers PostgreSQL vacuum freeze on `transaction_audit_log` table caused by a long-running uncommitted analytical query initiated by BI team.
- **14:05**: IC approves terminating the rogue query (`SELECT pg_terminate_backend(...)`).
- **14:15**: Locks clear, but connection pools remain wedged due to TCP socket deadlocks.
- **14:25**: IC orders coordinated rolling restart of Payment Service pods.
- **14:34 (MTTR = 84m)**: All health checks green, error rate returns to 0.01%. Incident closed.

### 5 Whys Root Cause Analysis
1. *Why did payments fail?* $\rightarrow$ Payment service ran out of database connections.
2. *Why did it run out of connections?* $\rightarrow$ Queries on `transaction_audit_log` stalled waiting for exclusive table locks.
3. *Why was a lock held?* $\rightarrow$ Autovacuum was blocked by an uncommitted BI query open for 14 hours.
4. *Why was a BI query running on the primary database?* $\rightarrow$ The BI reporting tool connection string pointed to primary instead of read-replica.
5. *Why did the BI user have credentials to the primary?* $\rightarrow$ Shared database user credential lacked least-privilege role segregation.

### Action Items
- [ ] Migrate BI tool credentials to read-replica with hard statement timeout of 60s (Owner: Data Platform, Jira: DATA-402).
- [ ] Implement separate Incident Commander and Comms Lead protocol for all P1/P2 bridges (Owner: SRE Lead, Jira: SRE-110).
- [ ] Set `idle_in_transaction_session_timeout = 60000` in PostgreSQL (Owner: DBA, Jira: DBA-88).
