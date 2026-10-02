# CODE_DEEP_DIVE — Administration scripts

All references are to `WORKED_SQL_EXAMPLE.sql` in this lab.

## 1. Provisioning (§1)

- `APEX_INSTANCE_ADMIN.ADD_WORKSPACE(p_workspace, p_primary_schema,
  p_additional_schemas)`: creates the tenant and binds schemas in one
  call — additional schemas cover parsing-schema-plus-data separation.
- Workspace-user grants are role assignments, not DB grants: the account
  gets *workspace* rights (admin/developer/end-user), while actual table
  access flows through the parsing schema. Never grant DBA/schema-owner
  to a developer account.
- Quota check queries `dba_ts_quotas` per workspace schema — run before
  every bulk-load exercise in this academy; loaders fail at quota, not at
  APEX.

## 2. Posture parameters (§2)

- Password policy reads/writes go through `APEX_INSTANCE_ADMIN`
  (`STRONG_PASSWORD_*`, lockout thresholds) — instance-wide, effective for
  internal + local accounts (LDAP/SAML auth from lab 03 still governs the
  external path).
- Session timeout + HTTPS + resource caps are the same three knobs as lab
  03's app-level settings, raised one tier: instance values are the floor
  no workspace can go below.
- Outbound allow-listing has two layers: ORDS-level host rules *and* DB
  `DBMS_NETWORK_ACL_ADMIN` ACLs — the app from lab 05's payment-gateway
  call works only if *both* permit the host. Debugging "gateway unreachable
  from APEX but curl works" starts here.

## 3. Monitoring queries (§3)

- Top-pages by views + median elapsed: `GROUP BY application_id, page_id`
  over the activity log with a 7-day window — the weekly review in one
  screen.
- Slow-run ranking (`ORDER BY elapsed_time DESC … FETCH FIRST 20`) finds
  the exact page/process to `APEX_DEBUG`-trace; error-spike grouping
  (`WHERE error_message IS NOT NULL`) finds the incident before users
  file it.
- ORDS pressure is inferred, not queried: queue growth + latency rise at
  flat DB load = pool exhaustion, not a database problem.

## 4. Backup/restore + patch (§4)

- Export order on backup, reverse on restore: app exports
  (`APEXExport`/SQLcl `apex export`) are metadata-only — without the DB
  backup (RMAN/data pump) underneath, there is nothing to import *into*.
- Pre/post-patch snapshots of `apex_applications` + instance parameters
  turn "did the patch change behavior" from opinion into diff.
- Fallback is armed *before* change: flashback window sized to the
  maintenance window, RMAN piece verified restorable — same discipline
  as the EBS `10-upgrade-migration` rehearsal rule.
