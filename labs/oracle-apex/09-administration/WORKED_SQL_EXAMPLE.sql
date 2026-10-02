-- WORKED_SQL_EXAMPLE — APEX Administration
-- Companion to this lab's THEORY/EXERCISES. Internal workspace / DBA as marked.

---------------------------------------------------------------
-- §1. Provisioning
---------------------------------------------------------------

-- 1a. Create workspace + bind schemas (APEX_INSTANCE_ADMIN, as INTERNAL admin)
-- BEGIN
--   APEX_INSTANCE_ADMIN.ADD_WORKSPACE(
--     p_workspace          => 'ACME_DEV',
--     p_primary_schema     => 'ACME_APP',
--     p_additional_schemas => 'ACME_DATA');
-- END;
-- /

-- 1b. Quota reality check per workspace schema
SELECT tablespace_name, username AS schema_name,
       max_bytes / 1024 / 1024 AS quota_mb,
       bytes / 1024 / 1024 AS used_mb
FROM   dba_ts_quotas
WHERE  username IN ('ACME_APP', 'ACME_DATA');

---------------------------------------------------------------
-- §2. Posture audit (instance level)
---------------------------------------------------------------

-- 2a. Password + session posture snapshot
SELECT name, value
FROM   apex_instance_parameters
WHERE  name IN ('STRONG_PASSWORD_MIN_LENGTH', 'STRONG_PASSWORD_UPPER',
                'STRONG_PASSWORD_LOWER', 'STRONG_PASSWORD_DIGITS',
                'STRONG_PASSWORD_SPECIAL', 'MAX_SESSION_IDLE_SEC',
                'REQUIRE_HTTPS')
ORDER  BY name;

-- 2b. Workspaces over 80% of quota (blast-radius watch)
SELECT username, tablespace_name,
       ROUND(bytes / NULLIF(max_bytes, 0) * 100, 1) AS pct_used
FROM   dba_ts_quotas
WHERE  max_bytes > 0
AND    bytes / max_bytes > 0.8;

---------------------------------------------------------------
-- §3. Monitoring (activity log triage)
---------------------------------------------------------------

-- 3a. Hottest pages, last 7 days
SELECT application_id, page_id, COUNT(*) AS views,
       ROUND(AVG(elapsed_time), 3) AS avg_elapsed_s
FROM   apex_workspace_activity_log
WHERE  view_date > SYSDATE - 7
GROUP  BY application_id, page_id
ORDER  BY views DESC
FETCH  FIRST 20 ROWS ONLY;

-- 3b. Slowest runs (trace candidates)
SELECT application_id, page_id, apex_user, elapsed_time, error_message,
       view_date
FROM   apex_workspace_activity_log
WHERE  view_date > SYSDATE - 7
ORDER  BY elapsed_time DESC
FETCH  FIRST 20 ROWS ONLY;

-- 3c. Error spikes by page (incident detector)
SELECT application_id, page_id, COUNT(*) AS errors,
       MIN(view_date) AS first_seen, MAX(view_date) AS last_seen
FROM   apex_workspace_activity_log
WHERE  view_date > SYSDATE - 1
AND    error_message IS NOT NULL
GROUP  BY application_id, page_id
ORDER  BY errors DESC;

---------------------------------------------------------------
-- §4. Patch snapshot (before/after diff)
---------------------------------------------------------------

-- 4a. Application versions present
SELECT application_id, application_name, version, owner
FROM   apex_applications
ORDER  BY application_id;

-- 4b. Capture instance parameters pre-change (spool to file, diff post)
SELECT name, value
FROM   apex_instance_parameters
ORDER  BY name;
