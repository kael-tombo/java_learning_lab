-- WORKED_SQL_EXAMPLE — Upgrade & Migration
-- Companion to PROBLEM_WALKTHROUGH.md Problems 1–3. Sandbox only.

---------------------------------------------------------------
-- §1. ADOP readiness + editioning (Problem 1)
---------------------------------------------------------------

-- 1a. Readiness gate: expect ZERO rows before prod
SELECT object_name, object_type, owner, status
FROM   dba_objects
WHERE  owner LIKE 'XX%'
AND    edition_name IS NULL
AND    object_type IN ('TABLE','VIEW','PACKAGE','PROCEDURE','FUNCTION','INDEX')
AND    status = 'VALID'
ORDER  BY object_type, object_name;

-- 1b. Edition a table (fill PK predicates per table!)
-- ALTER TABLE xx_custom_invoice_data RENAME TO xx_custom_invoice_data_tb;
-- CREATE OR REPLACE EDITIONING VIEW xx_custom_invoice_data AS
--   SELECT * FROM xx_custom_invoice_data_tb;
-- Trigger replays DML; scope UPDATE/DELETE by primary key.
-- (Full template in walkthrough lines 37–56.)

-- 1c. Deprecated-API sweep hits
SELECT name, type, line, UPPER(text) AS snippet
FROM   user_source
WHERE  UPPER(text) LIKE '%FND_FILE%'
OR     UPPER(text) LIKE '%APPS_INIT%'
OR     UPPER(text) LIKE '% LONG %'
ORDER  BY name, line;

---------------------------------------------------------------
-- §2. Cloud endpoint verification (Problem 2)
---------------------------------------------------------------

-- 2a. Current agent hosts (before flip)
SELECT fpo.profile_option_name, fpov.profile_option_value AS value
FROM   fnd_profile_option_values fpov,
       fnd_profile_options fpo
WHERE  fpov.profile_option_id = fpo.profile_option_id
AND    fpo.profile_option_name IN (
  'APPS_JAVA_AGENT_HOST','APPS_WEB_AGENT_HOST',
  'APPS_FRAMES_AGENT_HOST','ICX_FORMS_LAUNCHER');

-- 2b. Flip to ELB (ticket + maintenance window; COMMIT required)
-- BEGIN
--   fnd_profile.save('APPS_WEB_AGENT_HOST',   'ebs-elb-123.us-east-1.elb.amazonaws.com', 'SITE');
--   fnd_profile.save('APPS_FRAMES_AGENT_HOST','ebs-elb-123.us-east-1.elb.amazonaws.com', 'SITE');
--   COMMIT;
-- END;
-- /

---------------------------------------------------------------
-- §3. 11g → 19c pre/post checks (Problem 3)
---------------------------------------------------------------

-- 3a. Deprecated features in use (must all be remediated)
SELECT name, version, detected_usages, currently_used
FROM   dba_feature_usage_statistics
WHERE  name IN ('Advanced Replication','Materialized View Rewrite',
                'Oracle Text','DBMS_STREAMS','Transportable Tablespaces')
AND    currently_used = 'TRUE';

-- 3b. LONG declarations in custom PL/SQL (all must become CLOB)
SELECT name, type, line
FROM   user_source
WHERE  owner LIKE 'XX%'
AND    UPPER(text) LIKE '% LONG%'
ORDER  BY name, line;

-- 3c. Post-upgrade stats (run as SYSDBA after cutover)
-- EXEC DBMS_STATS.GATHER_FIXED_OBJECTS_STATS;
-- EXEC DBMS_STATS.GATHER_DATABASE_STATS(gather_sys => TRUE, options => 'GATHER STALE');
