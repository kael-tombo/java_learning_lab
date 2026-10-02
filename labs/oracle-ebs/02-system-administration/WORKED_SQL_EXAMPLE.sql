-- WORKED_SQL_EXAMPLE — System Administration
-- Companion to PROBLEM_WALKTHROUGH.md (Problems 1–3). Run in a sandbox.
-- Conventions: XX% = custom schema; never run destructive fixes in PROD
-- without a backup + change ticket.

---------------------------------------------------------------
-- §1. Bulk provisioning helpers
---------------------------------------------------------------

-- 1a. Staging + error tables (create once)
CREATE TABLE xx_client_import_users (
  employee_number   VARCHAR2(30),
  user_name         VARCHAR2(100),
  description       VARCHAR2(250),
  email_address     VARCHAR2(250),
  responsibility_key VARCHAR2(100),
  data_group        VARCHAR2(100),
  processed_flag    VARCHAR2(1) DEFAULT 'N',
  user_id           NUMBER
);

CREATE TABLE xx_client_import_errors (
  request_id      NUMBER,
  employee_number VARCHAR2(30),
  error_msg       VARCHAR2(2000),
  created_date    DATE DEFAULT SYSDATE
);

-- 1b. Responsibility lookup used by the loader
-- Returns the responsibility_id for a job-function key.
CREATE OR REPLACE FUNCTION get_resp_id(p_key VARCHAR2) RETURN NUMBER IS
  l_id NUMBER;
BEGIN
  SELECT responsibility_id INTO l_id
  FROM   fnd_responsibility
  WHERE  responsibility_key = p_key
  AND    SYSDATE BETWEEN NVL(start_date, SYSDATE - 1)
                 AND NVL(end_date, SYSDATE + 1);
  RETURN l_id;
EXCEPTION WHEN NO_DATA_FOUND THEN RETURN NULL;
END;
/

-- 1c. Post-load verification: unprocessed + error summary
SELECT processed_flag, COUNT(*) AS cnt
FROM   xx_client_import_users
GROUP  BY processed_flag;

SELECT employee_number, SUBSTR(error_msg, 1, 120) AS err
FROM   xx_client_import_errors
ORDER  BY created_date DESC
FETCH  FIRST 20 ROWS ONLY;

---------------------------------------------------------------
-- §2. GL_POST ORA-00001 triage kit
---------------------------------------------------------------

-- 2a. Duplicate (header, line) pairs in the failing period
SELECT je_header_id, je_line_num, COUNT(*) AS dupes
FROM   gl_je_lines
WHERE  je_header_id IN (
  SELECT je_header_id FROM gl_je_headers
  WHERE  period_name = 'DEC-24' AND status = 'U'
)
GROUP  BY je_header_id, je_line_num
HAVING COUNT(*) > 1;

-- 2b. Re-sequence duplicates (test in sandbox first!)
-- Uses ROW_NUMBER partitioned per header; ROWID addressing.
DECLARE
  CURSOR fix_cur IS
    SELECT rowid AS rid, je_header_id, je_line_num,
           ROW_NUMBER() OVER (
             PARTITION BY je_header_id
             ORDER BY je_line_num, last_update_date
           ) AS new_line_num
    FROM   gl_je_lines
    WHERE  je_header_id IN (
      SELECT je_header_id FROM gl_je_headers
      WHERE  period_name = 'DEC-24'
    );
BEGIN
  FOR rec IN fix_cur LOOP
    UPDATE gl_je_lines
    SET    je_line_num = rec.new_line_num
    WHERE  rowid = rec.rid;
  END LOOP;
  COMMIT;
END;
/

-- 2c. Prove the fix + prove re-runnability (expect 0, twice)
-- (Re-run query 2a here; second fix run must change 0 rows.)

---------------------------------------------------------------
-- §3. Profile-option & SOD audit kit
---------------------------------------------------------------

-- 3a. Who changed security profiles in the last 90 days?
SELECT profile_option_name, user_name, old_value, new_value, change_date
FROM   fnd_profile_option_values_history
WHERE  change_date > SYSDATE - 90
ORDER  BY change_date DESC;

-- 3b. SOD violators (one row per user with the conflicting set)
SELECT user_name,
       LISTAGG(responsibility_name, ', ')
         WITHIN GROUP (ORDER BY responsibility_name) AS conflicting_resps
FROM   fnd_user_resp_groups
WHERE  responsibility_name IN ('AP_INVOICE_VALIDATION', 'AP_PAYMENT_APPROVAL')
GROUP  BY user_name
HAVING COUNT(DISTINCT responsibility_name) > 1;

-- 3c. Remediate the credential leak (sandbox first, then PROD w/ ticket)
BEGIN
  fnd_profile.save('FND_HIDE_DB_PASSWORD', 'Y', 'SITE');
  COMMIT;  -- without this, the fix evaporates
END;
/
