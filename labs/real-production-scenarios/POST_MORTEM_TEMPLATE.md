# Post-Mortem Template

## Title

`[Incident ID] - [Severity] - [Brief Description] - [YYYY-MM-DD]`

## Metadata

| Field | Value |
|-------|-------|
| **Incident ID** | INC-YYYY-NNN |
| **Title** | |
| **Date** | YYYY-MM-DD |
| **Duration** | Start: [UTC] → End: [UTC] |
| **Severity** | SEV1 / SEV2 / SEV3 |
| **Services Affected** | |
| **Regions Affected** | |
| **Incident Commander** | |
| **Report Author** | |
| **Reviewers** | |

## Executive Summary

*1-2 paragraph summary suitable for executive audience. Include: what happened, impact to users/customers, how long it lasted, root cause, and key actions taken.*

## Impact

### Customer Impact

| Metric | Value |
|--------|-------|
| **User-facing downtime** | XX minutes |
| **Users affected** | XX% of total |
| **Error rate during incident** | XX% |
| **Latency P99 during incident** | XX ms (baseline: XX ms) |
| **Lost transactions** | XX (est. $XX revenue impact) |
| **Support tickets filed** | XX |

### Business and Engineering Impact

- [Number] on-call engineers paged
- [Number] engineering hours spent on investigation and resolution
- [List] dependent services affected (cascading failures)
- [Details] of any data loss / integrity issues
- [Details] of any SLA breach / regulatory implications

## Timeline

*All times in UTC. Include: detection, key decision points, mitigation, resolution.*

| Time (UTC) | Duration | Event |
|-----------|----------|-------|
| 00:00 | | Incident begins (first user-facing impact) |
| 00:00 | +0 | Monitoring alert triggered |
| 00:00 | +0 | On-call engineer acknowledges page |
| 00:00 | +0 | SEV1 declared, incident command established |
| 00:00 | +0 | Initial stakeholder notification sent |
| 00:00 | +0 | Root cause identified |
| 00:00 | +0 | Mitigation started (rollback, feature flag, etc.) |
| 00:00 | +0 | Mitigation verified (metrics returning to baseline) |
| 00:00 | +0 | Resolution confirmed (customer impact ended) |
| 00:00 | +0 | Final status update sent |
| 00:00 | +0 | Post-mortem data collection begins |

## Root Cause Analysis

### Direct Cause

*What directly caused the incident? Be specific and technical. 1-2 sentences.*

### Contributing Factors

*What conditions made the incident possible or worse?*

1. [Factor 1]
2. [Factor 2]
3. [Factor 3]

### Trigger

*What event triggered the incident? Deployment, configuration change, traffic spike, external dependency failure?*

### Detection Failures

*Why wasn't this detected earlier? Were there gaps in monitoring, alerting, or observability?*

### Prevention Failures

*Why weren't there protections against this? Missing tests, code review gaps, architectural weaknesses?*

## 5 Whys Analysis

| Why | Answer |
|-----|--------|
| **Why did the incident occur?** | [Answer] |
| **Why did that happen?** | [Answer] |
| **Why did that happen?** | [Answer] |
| **Why did that happen?** | [Answer] |
| **Why did that happen?** | [Root cause — systemic/process/culture] |

## Action Items

### Immediate (completed during incident)

| # | Action Item | Owner | Status |
|---|------------|-------|--------|
| 1 | Roll back deployment to previous version | On-call | Done |
| 2 | Restart database connection pool | On-call | Done |
| 3 | Notify affected customers via status page | Comms Lead | Done |

### Short-term (within 1 week)

| # | Action Item | Owner | Due Date | Status |
|---|------------|-------|----------|--------|
| 1 | | | | |
| 2 | | | | |

### Medium-term (within 1 month)

| # | Action Item | Owner | Due Date | Status |
|---|------------|-------|----------|--------|
| 1 | | | | |
| 2 | | | | |

### Long-term (within 3 months)

| # | Action Item | Owner | Due Date | Status |
|---|------------|-------|----------|--------|
| 1 | | | | |
| 2 | | | | |

## Lessons Learned

### What Went Well

1. **Fast detection:** Alert fired within 1 minute of error rate spike
2. **Effective rollback:** Deployment rollback completed in 3 minutes
3. **Good communication:** Status updates sent every 15 minutes
4. **No blame culture:** Team focused on fix, not fault

### What Could Be Improved

1. **Leak detection threshold was too high:** 30-minute threshold meant pool was exhausted before detection
2. **Missing test coverage:** No test for the code path that leaked connections
3. **No automated rollback:** Rollback was manual, should be automated
4. **Insufficient monitoring:** No dashboard showing connection pool utilization trend

### Surprises

- Connection pool exhausted much faster than expected (4 minutes vs. estimated 15 minutes)
- The slow query was pre-existing and unrelated to the deployment, amplifying the impact

## Blameless Culture Principles

### Why Blameless?

A blameless post-mortem creates psychological safety, which enables:
- **Honest reporting:** People share what really happened without fear
- **Systemic thinking:** Focus on how the system allowed the failure, not who made a mistake
- **Better action items:** Address root causes, not symptoms
- **Organizational learning:** Knowledge shared across teams
- **Continuous improvement:** Each incident makes the system more resilient

### How to Run a Blameless Post-Mortem

1. **Start with facts:** Objective timeline based on logs, metrics, and chat transcripts
2. **Assume good intent:** Everyone was acting on the information they had at the time
3. **Focus on systems:** Ask "how did the system allow this?" not "who did this?"
4. **No punitive language:** Replace "engineer made a mistake" with "code review missed the issue"
5. **Include everyone:** All involved participate in the review
6. **Action-oriented:** Every finding becomes a tracked, assigned, dated action item
7. **Share widely:** Post-mortem is accessible to everyone in the organization

### Language to Avoid vs. Language to Use

| Avoid | Use Instead |
|-------|-------------|
| "Engineer forgot to close the connection" | "The code path did not ensure connection closure on exception" |
| "Developer didn't test the change" | "Tests did not cover the exception handling path" |
| "Operations missed the alert" | "Alert routing did not reach the on-call engineer" |
| "Poor code quality" | "Code review did not flag the missing resource cleanup" |
| "Someone should have caught this" | "The system lacked automated checks for this pattern" |

## Example: Google SRE Post-Mortem (Adapted)

**Incident:** Compute Engine regional outage
**Severity:** P0
**Duration:** 4 hours 10 minutes
**Root Cause:** Configuration error during routine network maintenance caused cascading failures in BGP route propagation, isolating an entire region.

**Timeline Highlights:**
- 14:00 — Network maintenance begins
- 14:07 — BGP session reset causes route withdrawal
- 14:09 — Automated health checks detect 50% of instances unreachable
- 14:12 — Incident declared, teams mobilized
- 14:45 — Root cause identified: missing route filter in maintenance script
- 15:20 — Route filter applied, routes begin to propagate
- 18:10 — Full connectivity restored

**Action Items:**
1. Add pre-validation step for network maintenance scripts
2. Implement canary route changes (apply to 1% of routers first)
3. Add automated rollback for BGP configuration changes
4. Improve monitoring: add per-router BGP session health dashboard

**Lessons:**
- What went well: Incident command structure worked effectively
- What went wrong: Maintenance script bypassed peer review process
- Surprise: One region's route withdrawals cascaded to other regions

## Example: Atlassian Post-Mortem (Adapted)

**Incident:** Bitbucket service outage
**Severity:** SEV1
**Duration:** 2 hours 28 minutes
**Root Cause:** Database migration script caused extended downtime due to table locking that blocked all read/write operations.

**Timeline Highlights:**
- 06:00 UTC — Database migration begins (schema change on large table)
- 06:02 — Read/write operations begin to fail (DDL lock blocks queries)
- 06:05 — Monitoring alerts fire
- 06:08 — Incident declared
- 06:30 — Migration identified as root cause
- 06:45 — Decision: let migration complete (85% done) rather than kill it
- 07:28 — Migration completes, service recovers

**Action Items:**
1. Use online schema change tools (pt-online-schema-change, gh-ost)
2. Implement read-only mode during migrations to prevent partial failures
3. Add monitoring: alert on DDL locks lasting > 5 seconds
4. Document migration runbook with expected duration and rollback procedure

**Lessons:**
- What went well: Team avoided the temptation to kill the migration at 85%
- What went wrong: Migration was not load-tested on production-sized data
- Surprise: DDL locks on PostgreSQL 9.x blocked reads as well as writes

## Example: AWS Post-Mortem (Adapted)

**Incident:** S3 service error rate spike (US-EAST-1)
**Severity:** SEV1
**Duration:** 4 hours 38 minutes
**Root Cause:** An internal subsystem responsible for S3 metadata management was overwhelmed by a higher than normal volume of requests, causing the service to return elevated error rates for a subset of requests.

**Timeline Highlights:**
- 09:37 — Error rate begins to increase
- 09:48 — AWS Support receives first reports
- 10:10 — Team identifies the affected subsystem
- 10:30 — Mitigation begins: traffic shaping and request prioritization
- 11:15 — Error rate begins to decrease
- 14:15 — Full recovery

**Action Items:**
1. Increase capacity of the metadata management subsystem for peak load
2. Improve isolation between request types to prevent one type from affecting others
3. Enhance monitoring to detect subsystem-level saturation earlier
4. Implement faster automated mitigation for request prioritization

**Lessons:**
- What went well: Team avoided making the situation worse by acting methodically
- What went wrong: The subsystem was designed for normal load patterns, not the specific spike
- Surprise: The trigger was a routine internal operation that created a feedback loop with customer traffic

---

## References

- Google SRE Workbook — Post-Mortem Chapter: (link removed)
- Atlassian Post-Mortem Templates: https://www.atlassian.com/incident-management/postmortem
- AWS Well-Architected — Operational Excellence Pillar
- Etsy's "Blameless Post-Mortems" by John Allspaw
- "How to Run a Post-Mortem" — PagerDuty Incident Response Docs

## Post-Mortem Checklist

- [ ] Incident timeline is complete and verified (from logs, not memory)
- [ ] Root cause is identified with supporting evidence
- [ ] 5 Whys analysis is complete
- [ ] All action items have assigned owners and due dates
- [ ] Blast radius and customer impact are quantified
- [ ] Detection gaps are identified
- [ ] Prevention gaps are identified
- [ ] "What went well" section is included
- [ ] "What could be improved" section is included
- [ ] Post-mortem is shared with the affected team(s)
- [ ] Post-mortem is stored in a searchable location
- [ ] Action items are tracked in project management tool
- [ ] Post-mortem is reviewed within 72 hours of incident resolution
- [ ] Executives receive an executive summary
