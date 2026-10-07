# Lab 09: Disk Space Capacity Incident — Production Disks Fill Up, Data Corruption Risk

## Situation Overview

**Severity**: SEV1 (Critical — Data Integrity Risk)  
**Classification**: P0 Incident — Imminent Data Loss  
**Duration**: 132 minutes from first alert to full resolution  
**Scope**: 8 production database servers at 100% disk capacity, 12 application servers at >95% capacity  
**Users Impacted**: ~670,000 transactions blocked, 43% API failure rate  
**Platform**: Google SRE-inspired — Linux servers, PostgreSQL database, logrotate, tmpwatch, custom monitoring

### Incident Summary

Production disks across 8 database servers and 12 application servers reached 100% capacity over a 4-hour window, causing database transaction failures, application crashes, and a significant risk of data corruption. The root cause was a combination of three failures: log rotation was configured with a maximum of 5 rotated files (insufficient for the traffic volume), temporary files were not being cleaned (tmpwatch/cron job misconfigured), and an application audit table grew unbounded (no partition management or retention policy).

The incident required emergency disk space recovery by the SRE team, including manual log purging, database table truncation, and temporary file deletion. The 132-minute recovery time exceeded the organization's RTO (Recovery Time Objective) of 60 minutes for SEV1 incidents.

This incident mirrors real-world Google SRE experiences documented in the Google SRE Book (Chapter 6: "Monitoring Distributed Systems" and Chapter 12: "Managing Disk Space"). Netflix and Atlassian have also documented similar incidents in their engineering blogs.

### Infrastructure Context

The production environment consists of:
- **Database Tier**: 8 PostgreSQL 15 servers (4 primary, 4 replica) with 500GB SSD each
- **Application Tier**: 12 Java/Spring Boot application servers with 200GB SSD each
- **Monitoring**: Prometheus + Grafana, PagerDuty alerts at 80% and 95% disk capacity
- **Log Management**: logrotate (hourly rotation), rsyslog, centralized logging to ELK
- **Temp File Management**: tmpwatch configured to clean /tmp every 6 hours

### The Three Failure Modes

1. **Log Rotation Failure**: `logrotate` was configured with `rotate 5` (keep 5 rotated logs) and `maxage 30` (delete after 30 days). Under normal traffic, applications generated 2GB of logs per day per server — 5 rotated files = ~10GB reserved, which was acceptable. However, a recent release had introduced verbose debug logging that increased log volume to 15GB per day. With `rotate 5`, each server retained 75GB of logs, consuming 37.5% of disk capacity.

2. **Temp File Leak**: The application generated temporary files during report generation (PDF exports) but had a bug where temp files were not deleted after processing. With 500 reports per hour at an average of 5MB per report, temp files accumulated at 2.5GB/hour. The tmpwatch cleanup job was configured with `/tmp` path but the application wrote to `{app-home}/temp` which was not covered.

3. **Unbounded Audit Table**: The `audit_log` table in PostgreSQL had no partition management or retention policy. The table grew by 1.2GB per day, accumulating 360GB over 10 months. The table consumed 72% of the 500GB database disk alone. When combined with the log and temp file growth, the disk reached capacity.

### Why This Lab Matters

Disk space incidents are among the most common production issues in on-premise and cloud infrastructure. Google SRE's experience shows that disk space monitoring is one of the "Four Golden Signals" (latency, traffic, errors, saturation) — and disk space is a primary saturation metric. The Google SRE Book dedicates significant content to capacity planning and disk space management.

This lab simulates a realistic disk space capacity incident. You will:
1. Analyze disk usage patterns to identify the three failure modes
2. Configure proper log rotation policies (30-day retention, compression)
3. Implement temp file cleanup (tmpwatch/cron with correct paths)
4. Implement database partition management and retention policies
5. Configure automated disk space monitoring and alerting

### Key Engineering Concepts

- **Logrotate**: Linux utility for rotating, compressing, and removing log files. Key configs: `rotate` (count to keep), `maxage` (max age in days), `compress` (gzip), `delaycompress` (delay one rotation), `postrotate` (restart service).
- **tmpwatch/tmpreaper**: Utilities for removing files not accessed in N hours. Critical for preventing temp file accumulation.
- **Database Partitioning**: Dividing large tables into smaller partitions based on a key (usually date). Enables efficient deletion of old data via partition drop.
- **Inode Exhaustion**: A condition where the filesystem runs out of inodes (file metadata structures) even though disk space is available. This can occur when millions of tiny files accumulate.
- **Capacity Planning**: The process of forecasting resource requirements and ensuring sufficient capacity before saturation occurs.

### References

- Google SRE Book — Chapter 6: "Monitoring Distributed Systems" (Four Golden Signals)
- Google SRE Book — Chapter 12: "Managing Disk Space" — (link removed)
- Netflix Tech Blog: "Linux Performance Tools" — https://netflixtechblog.com/linux-performance-tools-7c9d2e6b8f2c
- Atlassian Engineering: "How We Fixed Disk Space Issues at Scale" — (link removed)
- PostgreSQL Documentation: "Table Partitioning" — https://www.postgresql.org/docs/15/ddl-partitioning.html
- Google SRE Book — Chapter 17: "Testing for Reliability" (capacity testing)

### Severity Assessment

This incident qualified as SEV1/P0 because:
- 20 servers at or near 100% disk capacity
- Risk of data corruption from incomplete database writes
- 43% transaction failure rate
- Recovery time (132 min) exceeded RTO (60 min)
- Manual intervention required on all 20 servers
- Unbounded audit table posed data retention compliance risk

---

## Incident Timeline Summary

| Time | Event |
|------|-------|
| 06:00 | Overnight batch report generation creates 30GB of temp files (bug introduced in v3.1) |
| 08:00 | Production traffic ramp-up — verbose debug logging consuming 15GB/day |
| 10:00 | First server hits 85% disk — alert fires (not acknowledged, classified as non-urgent) |
| 11:00 | 5 servers at >90% disk — PagerDuty warning alert fires |
| 11:30 | 8 database servers at 95% — PagerDuty critical alert fires |
| 11:32 | SEV1 declared |
| 11:45 | Root cause identified: log rotation + temp files + audit table |
| 12:15 | Emergency disk recovery actions completed |
| 13:00 | All servers below 60% disk |
| 13:32 | Incident formally resolved |

### Full details in INCIDENT_REPORT.md

## Expanded Analysis: Disk Space Management at Scale

### Understanding Disk Exhaustion Patterns

Disk space exhaustion typically follows one of three patterns:

**Pattern 1: Gradual Growth (Months/Years)**
- Database tables grow slowly over time (audit logs, event data)
- Log files accumulate over months
- Symptom: disk utilization increases steadily, predictable
- Prevention: capacity planning, automated retention, partition management

**Pattern 2: Rapid Accumulation (Hours/Days)**
- Debug logging enabled in a new release (log volume increases 10x)
- Temp files not cleaned up (bug in application)
- Batch jobs generate large temporary data
- Symptom: disk utilization increases rapidly, requires immediate action
- Prevention: log volume testing, temp file cleanup, monitoring

**Pattern 3: Compound Failure (Our Incident — All Three)**
- Gradual: audit_log table grows unbounded over 10 months (340GB)
- Rapid: debug logging increases log volume 7.5x overnight
- Rapid: temp file leak accumulates 30GB over a few hours
- Result: All three fill the disk simultaneously

### Understanding Inode Exhaustion

Inode exhaustion is a related but distinct failure mode:
- **Disk space exhaustion**: No more space to write data
- **Inode exhaustion**: No more file metadata slots, even if space is available

In our incident, inode exhaustion was avoided because the log files were large (not numerous). However, the temp file leak could have caused inode exhaustion if the bug created many small temp files instead of few large ones. The emergency response plan now includes inode monitoring alongside disk space monitoring.

### Comparison with Industry Incidents

**Google SRE — Disk Space Management**:
The Google SRE Book (Chapter 12: "Managing Disk Space") describes Google's approach:
- Automated disk cleanup tools that run regularly
- Disk usage quotas per service and per team
- "Disk pressure" monitoring that alerts when a disk is projected to fill within 7 days
- Automated "disk emergency" procedures that trigger when a disk exceeds 95%
- Continuous capacity planning with trend-based forecasting

**Netflix — Linux Performance Tools**:
Netflix's engineering blog describes their approach to disk space management:
- At Netflix scale (thousands of servers), manual disk management is impossible
- Automated disk cleanup agents run on every server
- Disk space metrics are tracked centrally with trends and predictions
- Any server exceeding 80% disk generates an automatic ticket
- Servers exceeding 90% trigger automatic cleanup (or auto-scaling of storage)

**Atlassian — Disk Space at Scale**:
Atlassian documented a similar incident where JIRA's audit log grew unbounded:
- Database tables (audit_log, historical_data) grew without retention limits
- Log files consumed 60% of available disk on large instances
- Their solution: automated partition management with configurable retention
- Key lesson: "Audit log retention should not be infinite — even compliance requirements have limits"

### Expanded Technical Details

**Logrotate Mechanics**:
Logrotate works by renaming the current log file and creating a new one. The old file is compressed and retained for a configured number of rotations. Understanding logrotate behavior is critical for proper configuration:

```
Rotation cycle (daily):
Day 1: application.log [active]
Day 2: application.log [active], application.log.1 [rotated, not yet compressed]
Day 3: application.log [active], application.log.1.gz [compressed], application.log.2 [rotated]
Day 4: application.log [active], application.log.1.gz, application.log.2.gz, application.log.3
...
Day 6: application.log [active], application.log.1.gz, ... application.log.5.gz
Day 7: Oldest log (application.log.5.gz) deleted, new rotation shifts all files
```

With `rotate 5`: maximum of 5 compressed log files + 1 active log = 6 files total
With `rotate 30`: maximum of 30 compressed log files + 1 active log = 31 files total

The space savings from compression are significant:
- Uncompressed log: 500MB per file
- Compressed (gzip): 50MB per file (90% reduction)
- With `rotate 5` and compression: 5 × 50MB + 500MB = 750MB max
- With `rotate 30` and compression: 30 × 50MB + 500MB = 2GB max
- Without compression and `rotate 5`: 5 × 500MB + 500MB = 3GB per day

**Database Partitioning Mechanics**:
PostgreSQL partitioning divides a large table into smaller, manageable pieces based on a partition key (typically a date range). The key insight: dropping an entire partition is a metadata-only operation (instant) while deleting individual rows generates WAL and can be slow.

```sql
-- Dropping a partition (instant, metadata only)
DROP TABLE audit_log_2026_01;

-- Deleting from a non-partitioned table (slow, generates WAL)
DELETE FROM audit_log WHERE created_at < '2026-02-01';
```

This is why partitioning is essential for time-series data — it enables efficient retention management.

**tmpwatch Mechanics**:
tmpwatch removes files based on access time (atime) rather than modification time (mtime). This is important because:
- A file written at 10:00 but last accessed at 14:00 will be deleted at 15:00 (1 hour after last access, not last write)
- For temp files that are accessed once (download), this is correct behavior
- For files that are never accessed after creation, they will be deleted based on creation time

The `--atime` vs `--mtime` option in tmpwatch controls which timestamp is used:
- `tmpwatch --atime 1 /tmp`: delete files not accessed in 1 hour
- `tmpwatch --mtime 1 /tmp`: delete files not modified in 1 hour

### Expanded Severity Assessment

**Data Integrity Risk Analysis**:
The risk of data corruption at 100% disk is severe:
- PostgreSQL writes to WAL (Write-Ahead Log) before writing to data files
- If WAL write fails due to disk full, the database may crash
- On restart, PostgreSQL attempts to replay WAL — if the WAL file is incomplete, recovery may fail
- This can result in unrecoverable data loss
- The risk increases with duration at 100% disk

In this incident, the database was at 100% disk for approximately 12 minutes before emergency cleanup freed space. The database did not crash, but write operations were failing during this window.

**Compliance Implications**:
- **GDPR**: The audit_log table may contain personal data. If any data was lost due to corruption, it could violate data protection requirements.
- **SOX**: Financial audit trails must be retained for regulatory compliance. Losing audit data due to disk full could be a compliance violation.
- **PCI DSS**: If customer payment data was in logs or audit tables, the incident could trigger PCI reporting requirements.

**Business Impact**:
The 43% API failure rate affected:
- Customer-facing transactions: 670,000 failed
- Partner API integrations: 15 partners affected
- Internal reporting: 3 critical reports failed to generate
- Revenue impact: estimated $95,000 in lost transactions during the 132-minute incident

### Expanded Learning Resources and References

**Recommended Reading**:
- "Site Reliability Engineering" by Google — Chapter 6 (Monitoring), Chapter 12 (Managing Disk Space)
- "The Practice of System and Network Administration" by Limoncelli et al. — Disk management best practices
- "Linux System Administration" by Tom Adelstein — Disk management, logrotate, tmpwatch
- "PostgreSQL Administration Cookbook" by Simon Riggs — Partition management, maintenance

**Industry Case Studies**:
1. **Google SRE — Disk Space Incidents**: The Google SRE Book describes multiple disk space incidents where automated cleanup and capacity planning prevented SEV1 scenarios. Google's practice of "disk pressure" monitoring (projected fill time) is highlighted.

2. **Netflix — Chaos Engineering for Storage**: Netflix's Chaos Engineering practices include "Chaos Gorilla" (simulate entire availability zone failure) and storage-specific tests that validate disk cleanup procedures.

3. **Atlassian — JIRA Audit Log Incident**: Atlassian documented a similar incident where JIRA's audit_log table grew to 300GB+ due to no retention policy. Their solution was automated partition management with configurable retention periods.

4. **GitLab — Database Overflow Incident**: GitLab experienced a database overflow when a background job generated excessive log entries. They implemented partition management and real-time disk monitoring.

### Practical Exercises

**Exercise 1: Logrotate Configuration**
Design a logrotate configuration for a service that:
- Generates 10GB of logs per day
- Has 500GB of disk space
- Must retain logs for 45 days (compliance requirement)
- Should minimize disk usage through compression

**Exercise 2: Capacity Planning**
Given the following data:
- Current disk usage: 350GB out of 500GB
- Daily growth rate: 1.5GB
- Monthly audit table cleanup: 30GB (first of each month)
- Calculate: days until disk reaches 90% (450GB)
- Calculate: days until disk reaches 100% (500GB)
- Recommend: when should capacity be added?

**Exercise 3: Emergency Cleanup Script**
Write a PowerShell or Bash script that performs emergency disk cleanup:
- Check current disk utilization
- If > 90%: run cleanup actions (compress logs, clean temp files, drop old DB partitions)
- Log all actions taken
- Verify disk freed after cleanup
- Send notification with results

### Glossary

| Term | Definition |
|------|-----------|
| Logrotate | Linux utility for rotating, compressing, and deleting log files |
| tmpwatch | Utility for removing files based on access time |
| Inode | File system metadata structure (one per file) |
| Inode Exhaustion | Running out of file metadata slots (filesystem full of tiny files) |
| Partition Management | Automated creation and deletion of database partitions |
| WAL (Write-Ahead Log) | PostgreSQL transaction log for crash recovery |
| Capacity Planning | Forecasting resource requirements and ensuring sufficient capacity |
| Data Retention Policy | Rules for how long different types of data are kept |
| Shared Buffer | PostgreSQL cache for database pages in memory |
| Checkpoint | PostgreSQL operation that flushes dirty pages to disk |

### Monitoring Best Practices Expansion

**Disk Monitoring Thresholds**:
- 50%: OK — normal operation
- 70%: Caution — review growth trends
- 80%: Warning — investigate, create action plan
- 90%: Critical — immediate action required
- 95%: Emergency — page SRE team, prepare for data corruption risk
- 97%: Severe — automated emergency cleanup triggered
- 100%: Data corruption risk — manual intervention required

**Inode Monitoring Thresholds**:
- 50%: OK — normal operation
- 70%: Caution — check for small file accumulation
- 80%: Warning — investigate file count growth
- 90%: Critical — immediate cleanup required

**Capacity Planning Time Horizons**:
- Weekly: Growth rate tracking
- Monthly: Trend analysis
- Quarterly: 6-month projection
- Annually: 2-year projection (hardware refresh cycle)


### Expanded Maintenance Schedule

**Daily Tasks** (automated):
- Disk utilization check (all servers)
- Logrotate execution
- Temp file cleanup

**Weekly Tasks**:
- Review disk growth trends
- Check for tables approaching size limits
- Verify backup completion and space requirements

**Monthly Tasks**:
- Partition maintenance (drop old, create new)
- Capacity review (current usage vs forecast)
- Log retention verification
- Database maintenance (VACUUM, ANALYZE)

**Quarterly Tasks**:
- Full capacity planning review
- Review and update retention policies
- Validate backup restore procedures
- Update monitoring thresholds if needed
