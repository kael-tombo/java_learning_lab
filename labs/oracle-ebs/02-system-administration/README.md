# 02 — System Administration

## Overview

EBS administration through three production scenarios: bulk user
provisioning with `FND_USER_PKG` (500 warehouse users, 2-week deadline),
nightly `GL_POST` failing on `ORA-00001` duplicate journal lines, and a
PwC audit finding SOD violations plus `FND_HIDE_DB_PASSWORD=N` leaking
credentials into logs.

## Learning Objectives

- [ ] Bulk-provision users with `FND_USER_PKG.createuser` + responsibility assignment, per-row error isolation
- [ ] Diagnose `ORA-00001` on `GL_JE_LINES_U1` with duplicate-line queries and `ROW_NUMBER()` re-sequencing
- [ ] Audit profile options via `FND_PROFILE_OPTION_VALUES_HISTORY`; enforce SOD with `FND_USER_RESP_GROUPS` queries

## Topics Covered

### 1. Bulk user provisioning (`FND_USER_PKG`, responsibilities, data groups)
Role-based responsibility sets per job function; country-level data/security
groups; single concurrent program with error logging; savepoint rollback;
SOD rules per role. Implementation: `PROBLEM_WALKTHROUGH.md` Problem 1,
`WORKED_SQL_EXAMPLE.sql` §1.

### 2. Concurrent program triage (`GL_POST`, unique-constraint failure)
Log-file diagnosis → duplicate detection (`GROUP BY … HAVING COUNT(*)>1`)
→ `ROW_NUMBER() PARTITION BY je_header_id` re-sequencing → feeder fix
(`GL_JOURNAL_LINES_S.NEXTVAL`) → submission validation → monitoring.
Implementation: `PROBLEM_WALKTHROUGH.md` Problem 2, `WORKED_SQL_EXAMPLE.sql` §2.

### 3. Profile options & SOD (`FND_PROFILE`, `FND_HIDE_DB_PASSWORD`)
Site/application/responsibility/user inheritance; `LISTAGG` SOD-conflict
query; `fnd_profile.save('FND_HIDE_DB_PASSWORD','Y','SITE')`; drift-report
program. Implementation: `PROBLEM_WALKTHROUGH.md` Problem 3.

## Prerequisites

- Oracle EBS R12.2 apps schema access (APPS + custom XX schema)
- PL/SQL (cursors, bulk patterns, exception handling)
- Concurrent manager basics (request submission, log files)

## Further Reading

- Oracle EBS System Administrator's Guide (FND_USER_PKG, profile options)
- `../01-architecture/` for the apps-tier / concurrent-manager model
