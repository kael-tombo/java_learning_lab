# 09 — Administration (Workspaces, Security Posture, Monitoring, Lifecycle)

## Overview

Run APEX as a platform, not just build in it: provision workspaces and
schemas, enforce instance security posture (password policy, session
timeout, HTTPS, outbound allow-listing), monitor with the activity log,
back up via declarative exports + database backup, and patch/upgrade with
a tested fallback.

## Learning Objectives

- [ ] Provision workspaces/schemas/developers with least-privilege roles
- [ ] Harden the instance (password policy, session timeout, HTTPS, REST outbound allow-list, service size limits)
- [ ] Monitor via `apex_workspace_activity_log` (top pages, slow queries, error spikes) + instance dashboard
- [ ] Back up (app export + workspace export + DB backup) and restore in order; patch with fallback

## Topics Covered

### 1. Provisioning (workspace → schema → developers)
Internal workspace; `APEX_INSTANCE_ADMIN.ADD_WORKSPACE`; parsing-schema
assignment; workspace-admin vs developer vs end-user roles; schema quota.
`WORKED_SQL_EXAMPLE.sql` §1.

### 2. Security posture (instance settings)
Password policy (`STRONG_PASSWORD_*`); session timeout (ties to lab
03-security's 15-minute rule); require HTTPS; outbound network allow-list
(`APEX_INSTANCE_ADMIN` + ACLs); max workarea/file sizes. §2.

### 3. Monitoring (activity log + debug)
`apex_workspace_activity_log` top-pages/slow-runs/errors queries;
`APEX_DEBUG` session tracing; ORDS pool pressure signs. §3.

### 4. Backup/restore + patching (exports, order, fallback)
App export (`APEXExport`/`apex_export`), workspace export, DB backup;
restore order (workspace → schema objects → app → ORDS config); patch flow
(backup → stage → test → prod + flashback/RMAN fallback). §4.

## Prerequisites

- APEX internal workspace access; SQL (+DBA views); ORDS basics (lab 05)

## Further Reading

- APEX Administration Guide (instance settings, workspaces, packaging)
- `../03-security/` (app-level auth the instance posture protects)
- `../05-restful-services/` (ORDS surface the allow-list constrains)
