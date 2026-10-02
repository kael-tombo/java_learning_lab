# 10 — Upgrade & Migration (12.1→12.2, Cloud, 11g→19c)

## Overview

Three production cutovers: EBS 12.1.3→12.2.10 with ADOP editioning on a
12 TB DB (4-day window); on-prem→AWS (DMS replication, <2 h cutover,
99.95% uptime); Oracle 11.2.0.4→19c on RAC inside an 8-hour window with
application patching in the same outage.

## Learning Objectives

- [ ] Harden custom objects for ADOP (editioning views, deprecated-API replacement)
- [ ] Plan a DMS-based cloud cutover (assess → replicate → promote → ASG/ELB/CloudWatch)
- [ ] Execute an 11g→19c upgrade (preupgrd, deprecated features, AutoUpgrade, stats)

## Topics Covered

### 1. ADOP upgrade (`dba_objects` editioning audit, INSTEAD OF triggers, FND_LOG)
Readiness report; table→`_tb` + editioning view + trigger; `FND_FILE`→
`FND_LOG`; phased dev→prod, dress rehearsals ×3, flashback fallback.
Walkthrough Problem 1.

### 2. Cloud migration (DMS, RDS Custom, ASG/ELB, CloudWatch)
OATM sizing; Direct Connect; DMS ongoing replication; RDS promotion;
context-file ELB endpoints (`fnd_profile.save`); cross-Region DR.
Walkthrough Problem 2.

### 3. Database upgrade (preupgrd, AutoUpgrade, 19c deltas, stats)
Deprecated-feature audit; LONG→CLOB; standby-first cutover; fixed +
dictionary stats; plan-baseline review. Walkthrough Problem 3,
`WORKED_SQL_EXAMPLE.sql`.

## Prerequisites

- EBS apps + DBA basics (ADOP concepts, concurrent manager, FND_PROFILE)
- Oracle upgrade paths; AWS primitives (DMS, RDS, ASG, ELB, CloudWatch)

## Further Reading

- Oracle EBS Upgrade Guide 12.1→12.2 (ADOP, editioning)
- `../02-system-administration/` for request/log triage during cutover
