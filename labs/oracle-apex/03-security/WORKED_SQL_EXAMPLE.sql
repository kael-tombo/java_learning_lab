-- WORKED_SQL_EXAMPLE — APEX RBAC Security
-- Companion to PROBLEM_WALKTHROUGH.md Steps 1–12. Sandbox schema only.

---------------------------------------------------------------
-- §1. Schema + seeds (Step 1, abridged to the load-bearing parts)
---------------------------------------------------------------
-- (Full DDL in walkthrough lines 32–161; key constraints to verify:)
-- UNIQUE(user_id, role_id), UNIQUE(role_id, permission_id),
-- audit interval-partitioned daily, username/date indexes.

-- 1a. Role gradient check (expect 8/5/3/2)
SELECT r.role_name, COUNT(*) AS perms
FROM   app_role_permissions rp
JOIN   app_roles r ON r.role_id = rp.role_id
GROUP  BY r.role_name
ORDER  BY perms DESC;

---------------------------------------------------------------
-- §2. Password lifecycle (Step 2)
---------------------------------------------------------------

-- 2a. Create a salted hash for a new user
-- (Run in a block; store both outputs — never the plaintext.)
DECLARE
  l_salt VARCHAR2(100) := sec_pwd.generate_salt;
  l_hash VARCHAR2(200) := sec_pwd.hash_password('Welcome1', l_salt);
BEGIN
  DBMS_OUTPUT.PUT_LINE('SALT=' || l_salt);
  DBMS_OUTPUT.PUT_LINE('HASH=' || l_hash);
END;
/

-- 2b. Verify path (what the auth function calls)
-- SELECT CASE WHEN sec_pwd.verify_password('Welcome1', :hash, :salt)
--             THEN 'OK' ELSE 'DENIED' END FROM DUAL;

---------------------------------------------------------------
-- §3. RBAC checks (Steps 4–6)
---------------------------------------------------------------

-- 3a. Effective role + branch for a user
SELECT sec_rbac.get_user_role('ANALYST_LON') AS role,
       sec_rbac.get_user_branch_id('ANALYST_LON') AS branch
FROM DUAL;

-- 3b. Permission list (BULK COLLECT under the hood)
SELECT column_value AS permission
FROM   TABLE(sec_rbac.get_user_permissions('MGR_NYC'));

-- 3c. Y/N wrapper (what authorization schemes call)
SELECT sec_rbac.is_authorized('VIEWER_USER', 'TRADE_EXECUTE') AS verdict
FROM DUAL;  -- expect N

---------------------------------------------------------------
-- §4. Audit + lockout forensics (Steps 3, 9, 12)
---------------------------------------------------------------

-- 4a. Brute-force footprint per user (lockout at 5)
SELECT username, COUNT(*) AS fails,
       MAX(created_date) AS last_attempt
FROM   app_audit_log
WHERE  action = 'AUTH_FAIL'
AND    created_date > SYSDATE - 1
GROUP  BY username
HAVING COUNT(*) >= 5;

-- 4b. Authorization denials by page (missing-scheme detector)
SELECT page_id, COUNT(*) AS denies
FROM   app_audit_log
WHERE  action = 'AUTHZ_DENY'
GROUP  BY page_id
ORDER  BY denies DESC;
