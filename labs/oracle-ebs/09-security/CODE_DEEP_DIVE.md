# Lab 09: Security — Code Deep Dive

## 1. SOD Risk Matrix

```sql
CREATE TABLE xx_sod_duty (
  duty_code     VARCHAR2(10) PRIMARY KEY,
  duty_name     VARCHAR2(100) NOT NULL,
  function_name VARCHAR2(100),            -- EBS function where applicable
  risk_category VARCHAR2(50) NOT NULL,
  description   VARCHAR2(400)
);

CREATE TABLE xx_sod_conflict (
  conflict_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  duty_a        VARCHAR2(10) NOT NULL,
  duty_b        VARCHAR2(10) NOT NULL,
  conflict_type VARCHAR2(30) NOT NULL,   -- MUTUALLY_EXCLUSIVE / SEQUENCING
  severity      VARCHAR2(10) NOT NULL,   -- HIGH/MEDIUM/LOW
  rationale     VARCHAR2(400) NOT NULL,
  CONSTRAINT xx_sod_c_ck CHECK (severity IN ('HIGH','MEDIUM','LOW')),
  CONSTRAINT xx_sod_c_uq UNIQUE (duty_a, duty_b)
);

INSERT INTO xx_sod_duty VALUES
  ('D1', 'Create Supplier',      'PO_VENDOR',        'Vendor Master',
   'Create and maintain supplier master records'),
  ('D2', 'Approve Invoice',      'AP_INV_APPROVE',   'Invoice Approval',
   'Approve payables invoices'),
  ('D3', 'Process Payment',      'AP_PAY_PROCESS',   'Cash Disbursement',
   'Execute and release payments'),
  ('D4', 'Maintain GL',          'GL_JOURNAL',       'General Ledger',
   'Post and adjust journal entries'),
  ('D5', 'Execute Reports',      'PAYMENT_REPORT',   'Reporting',
   'Execute payment and register reports');

INSERT INTO xx_sod_conflict (duty_a, duty_b, conflict_type, severity, rationale) VALUES
  ('D2','D3','MUTUALLY_EXCLUSIVE','HIGH',
   'Classic AP fraud: approve an invoice then pay it'),
  ('D1','D3','MUTUALLY_EXCLUSIVE','HIGH',
   'Create the supplier then pay that supplier'),
  ('D1','D2','MUTUALLY_EXCLUSIVE','MEDIUM',
   'Supplier creation bias in invoice approval'),
  ('D2','D4','MUTUALLY_EXCLUSIVE','HIGH',
   'Approve an invoice and post the GL entry for it'),
  ('D3','D5','MUTUALLY_EXCLUSIVE','HIGH',
   'Execute payments and conceal them in the register report'),
  ('D4','D5','MUTUALLY_EXCLUSIVE','MEDIUM',
   'Post GL entries and hide them from reporting');
```

## 2. SOD Violation Detection — User Assignment Level

```sql
-- The violation is a property of a user's assignment SET, not of one responsibility
WITH user_duties AS (
  SELECT DISTINCT fu.user_id, fu.user_name,
                  t.duty_code, t.duty_name, t.risk_category
    FROM fnd_users fu
    JOIN fnd_user_responsibilities ur ON ur.user_id = fu.user_id
    JOIN fnd_responsibilities r       ON r.responsibility_id = ur.responsibility_id
    JOIN xx_sod_duty t                ON t.function_name = r.responsibility_name
   WHERE fu.active = 'Y'
)
SELECT ud_a.user_id,
       ud_a.user_name,
       ud_a.duty_code || '/' || ud_a.duty_name  AS duty_a,
       ud_b.duty_code || '/' || ud_b.duty_name  AS duty_b,
       c.severity,
       c.rationale
  FROM user_duties ud_a
  JOIN user_duties ud_b
    ON ud_a.user_id = ud_b.user_id
   AND ud_a.duty_code < ud_b.duty_code        -- avoid double counting
  JOIN xx_sod_conflict c
    ON (c.duty_a = ud_a.duty_code AND c.duty_b = ud_b.duty_code)
    OR (c.duty_a = ud_b.duty_code AND c.duty_b = ud_a.duty_code)
 ORDER BY c.severity DESC, ud_a.user_name;
```

**The `ud_a.duty_code < ud_b.duty_code` predicate is essential** — without it
every conflict is reported twice (A↔B and B↔A).

## 3. Risk Ranking by Value at Risk

```sql
-- Rank by what the conflict could actually cost, not by user count
SELECT v.user_id,
       v.user_name,
       COUNT(DISTINCT v.conflict_pair)                      conflict_count,
       MAX(v.severity)                                     highest_severity,
       NVL(SUM(d.payment_annual_value), 0)                 annual_payment_value_at_risk
  FROM sod_violations v
  LEFT JOIN xx_user_duty_value d ON d.user_id = v.user_id
 GROUP BY v.user_id, v.user_name
 ORDER BY annual_payment_value_at_risk DESC NULLS LAST;
```

## 4. Remediation — Revoke Only the Conflicting Responsibility

```sql
CREATE OR REPLACE PROCEDURE xx_sod_remediate(
  p_user_id             IN NUMBER,
  p_conflict_id         IN NUMBER,
  p_remove_duty         IN VARCHAR2,
  p_alternate_user      IN VARCHAR2,
  p_approved_by         IN VARCHAR2,
  p_approval_ref        IN VARCHAR2,
  p_effective_date      IN DATE
) IS
  l_resp_id NUMBER;
BEGIN
  IF p_approved_by IS NULL OR p_approval_ref IS NULL THEN
    RAISE_APPLICATION_ERROR(-20030,
      'SOD remediation requires an approver and an approval reference.');
  END IF;

  -- Resolve the responsibility holding the conflicting duty
  SELECT ur.responsibility_id INTO l_resp_id
    FROM fnd_user_responsibilities ur
    JOIN fnd_responsibilities r ON r.responsibility_id = ur.responsibility_id
    JOIN xx_sod_duty t ON t.function_name = r.responsibility_name
   WHERE ur.user_id = p_user_id AND t.duty_code = p_remove_duty
     AND ROWNUM = 1;

  IF l_resp_id IS NULL THEN
    RAISE_APPLICATION_ERROR(-20031, 'User does not hold duty ' || p_remove_duty);
  END IF;

  -- Log BEFORE revoking: this is the audit evidence
  INSERT INTO xx_sod_remediation_log
    (user_id, conflict_id, removed_duty, removed_responsibility_id,
     alternate_user, approved_by, approval_ref, effective_date, action)
  VALUES (p_user_id, p_conflict_id, p_remove_duty, l_resp_id,
          p_alternate_user, p_approved_by, p_approval_ref,
          p_effective_date, 'REVOKED');
  COMMIT;

  -- Remove ONLY the conflicting responsibility
  DELETE FROM fnd_user_responsibilities
   WHERE user_id = p_user_id AND responsibility_id = l_resp_id;

  COMMIT;
END;
/
```

**Revoking the whole role would break the business and drive users to shared
logins — a worse control than the violation.** Remove the one duty.

## 5. Exception Management — Time-Bound and Owned

```sql
CREATE TABLE xx_sod_exception (
  exception_id     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id          NUMBER NOT NULL,
  conflict_id      NUMBER NOT NULL,
  business_reason  VARCHAR2(400) NOT NULL,
  compensating_control VARCHAR2(400) NOT NULL,
  approved_by      VARCHAR2(64) NOT NULL,
  approval_ref     VARCHAR2(64) NOT NULL,
  expires_on       DATE NOT NULL,               -- NOT NULL: no indefinite
  status           VARCHAR2(15) DEFAULT 'ACTIVE' NOT NULL,
  CONSTRAINT xx_sod_e_st_ck CHECK (status IN ('ACTIVE','EXPIRED','CLOSED'))
);

-- Overdue exceptions: the report that prevents "indefinite" becoming default
SELECT e.exception_id, fu.user_name, e.business_reason,
       e.approved_by, e.expires_on,
       ROUND(SYSDATE - e.expires_on) days_overdue
  FROM xx_sod_exception e
  JOIN fnd_users fu ON fu.user_id = e.user_id
 WHERE e.status = 'ACTIVE' AND e.expires_on < TRUNC(SYSDATE)
 ORDER BY e.expires_on;
```

## 6. Preventive Control — Block Conflicting Assignments

```sql
CREATE OR REPLACE TRIGGER xx_sod_preventive
BEFORE INSERT OR UPDATE ON fnd_user_responsibilities
FOR EACH ROW
DECLARE
  l_conflict_duty VARCHAR2(10);
  l_severity      VARCHAR2(10);
  l_new_duty      VARCHAR2(10);
BEGIN
  -- Which duty does the incoming responsibility carry?
  SELECT t.duty_code INTO l_new_duty
    FROM fnd_responsibilities r
    JOIN xx_sod_duty t ON t.function_name = r.responsibility_name
   WHERE r.responsibility_id = :NEW.responsibility_id;

  -- What duties does this user already hold?
  BEGIN
    SELECT MIN(t.duty_code), MAX(c.severity)
      INTO l_conflict_duty, l_severity
      FROM fnd_user_responsibilities ur
      JOIN fnd_responsibilities r ON r.responsibility_id = ur.responsibility_id
      JOIN xx_sod_duty t ON t.function_name = r.responsibility_name
      JOIN xx_sod_conflict c
        ON (c.duty_a = t.duty_code AND c.duty_b = l_new_duty)
        OR (c.duty_a = l_new_duty AND c.duty_b = t.duty_code)
     WHERE ur.user_id = :NEW.user_id
       AND ur.responsibility_id <> :NEW.responsibility_id;

    IF l_conflict_duty IS NOT NULL THEN
      -- High severity: block outright. Medium: require approval.
      IF l_severity = 'HIGH' THEN
        RAISE_APPLICATION_ERROR(-20032,
          'SOD CONFLICT (severity ' || l_severity || '): duty ' || l_conflict_duty ||
          ' conflicts with ' || l_new_duty || '. Assign a separate user or ' ||
          'submit an approved exception.');
      END IF;
    END IF;
  EXCEPTION WHEN NO_DATA_FOUND THEN
    NULL;   -- no existing duties: no conflict
  END;
END;
/
```

**This converts "we will catch this" into "this cannot happen."** A trigger is
not the ideal mechanism for a production EBS upgrade (see below), but it
demonstrates that prevention is possible.

## 7. Preventive Control — Report Mode (Upgrade-Safe)

```sql
-- Safer for a live instance: alert rather than block
CREATE OR REPLACE TRIGGER xx_sod_preventive_alert
AFTER INSERT OR UPDATE ON fnd_user_responsibilities
FOR EACH ROW
DECLARE
  l_conflicts NUMBER;
BEGIN
  SELECT COUNT(*) INTO l_conflicts
    FROM fnd_user_responsibilities ur
    JOIN fnd_responsibilities r ON r.responsibility_id = ur.responsibility_id
    JOIN xx_sod_duty t ON t.function_name = r.responsibility_name
    JOIN xx_sod_conflict c
      ON (c.duty_a = t.duty_code AND c.duty_b = :NEW.responsibility_id)
      OR (c.duty_a = :NEW.responsibility_id AND c.duty_b = t.duty_code)
   WHERE ur.user_id = :NEW.user_id;

  IF l_conflicts > 0 THEN
    xx_sod_alert_pkg.notify_sod_violation(:NEW.user_id, l_conflicts);
  END IF;
END;
/
```

**Never modify standard EBS tables with a trigger.** `FND_USER_RESPONSIBILITIES`
is a standard table; a trigger on it creates upgrade risk. In production,
implement the preventive control as an approval workflow or a scheduled
validation report, and treat the trigger as a demonstration.

## 8. Dormant Account Detection

```sql
SELECT fu.user_id, fu.user_name, fu.description,
       TO_CHAR(fu.last_signin_date,'YYYY-MM-DD') last_signin,
       ROUND(SYSDATE - NVL(fu.last_signin_date, fu.start_date)) days_since_login,
       -- elevated access check
       (SELECT COUNT(*) FROM fnd_user_responsibilities ur
         JOIN fnd_responsibilities r ON r.responsibility_id = ur.responsibility_id
        WHERE ur.user_id = fu.user_id
          AND r.responsibility_name IN
              ('AP Manager','GL Manager','System Administrator')) elevated_roles
  FROM fnd_users fu
 WHERE fu.active = 'Y'
   AND NVL(fu.last_signin_date, fu.start_date) < TRUNC(SYSDATE) - 90
 ORDER BY days_since_login DESC;
```

```sql
-- Auto-deactivation concurrent program (after a 30-day warning period)
UPDATE fnd_users
   SET active = 'N'
 WHERE active = 'Y'
   AND NVL(last_signin_date, start_date) < TRUNC(SYSDATE) - 120;
```

## 9. Password Visibility Hardening

```sql
-- The exposed setting
SELECT profile_option_name, profile_option_value, application_id
  FROM fnd_profile_options
 WHERE profile_option_name = 'FND_HIDE_DB_PASSWORD';
-- Value 'N' = credentials visible in diagnostics and logs

-- Set to Y (application-level where it is applicable)
UPDATE fnd_profile_options
   SET profile_option_value = 'Y'
 WHERE profile_option_name = 'FND_HIDE_DB_PASSWORD'
   AND application_id = 0;

-- Scan ALL profiles: a system-level 'N' overrides a safe application-level 'Y'
SELECT o.profile_option_name, v.level, v.profile_option_value
  FROM fnd_profile_options o
  JOIN fnd_profile_values v ON v.profile_option_id = o.profile_option_id
 WHERE o.profile_option_name = 'FND_HIDE_DB_PASSWORD'
   AND v.profile_option_value = 'N';
```

**Scanning every level is essential.** A safe `Y` at application level is
overridden by a `N` at system level — and the more permissive value wins.

## 10. Least Privilege / Stale Privilege Detection

```sql
-- Users holding more AP duties than their job requires
SELECT fu.user_name,
       COUNT(DISTINCT t.duty_code) duties_held,
       MAX(r.responsibility_name) highest_risk_role
  FROM fnd_users fu
  JOIN fnd_user_responsibilities ur ON ur.user_id = fu.user_id
  JOIN fnd_responsibilities r ON r.responsibility_id = ur.responsibility_id
  JOIN xx_sod_duty t ON t.function_name = r.responsibility_name
 WHERE fu.active = 'Y'
 GROUP BY fu.user_name
HAVING COUNT(DISTINCT t.duty_code) >= 3
 ORDER BY duties_held DESC;
```

## 11. Monthly Certification Workflow

```sql
CREATE TABLE xx_sod_certification (
  cert_id       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  period        VARCHAR2(7) NOT NULL,        -- '2026-02'
  manager_id    NUMBER NOT NULL,
  user_id       NUMBER NOT NULL,
  certification VARCHAR2(20) NOT NULL,        -- CORRECT/INCORRECT/ACCEPTED_RISK
  comment       VARCHAR2(400),
  certified_at  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  CONSTRAINT xx_cert_c_ck CHECK (certification IN
    ('CORRECT','INCORRECT','ACCEPTED_RISK'))
);

-- Certification status: what has NOT been certified
SELECT p.period, p.manager_name,
       COUNT(c.cert_id) certified,
       COUNT(*) - COUNT(c.cert_id) outstanding
  FROM xx_sod_certification_scope p
  LEFT JOIN xx_sod_certification c
    ON c.user_id = p.user_id AND c.period = p.period
 GROUP BY p.period, p.manager_name
HAVING COUNT(*) - COUNT(c.cert_id) > 0
 ORDER BY outstanding DESC;
```

**The value is the attestation, not the report.** A report nobody signs proves
nothing.

## 12. Programme Health Check

```sql
SELECT
  (SELECT COUNT(*) FROM sod_violations)                        open_violations,
  (SELECT COUNT(*) FROM sod_violations WHERE severity='HIGH')  high_severity,
  (SELECT COUNT(*) FROM xx_sod_exception WHERE expires_on < TRUNC(SYSDATE)
     AND status='ACTIVE')                                       overdue_exceptions,
  (SELECT COUNT(*) FROM fnd_profile_options o
     JOIN fnd_profile_values v ON v.profile_option_id=o.profile_option_id
    WHERE o.profile_option_name='FND_HIDE_DB_PASSWORD'
      AND v.profile_option_value='N')                          password_exposed,
  (SELECT COUNT(*) FROM fnd_users WHERE active='Y'
     AND NVL(last_signin_date,start_date) < TRUNC(SYSDATE)-120) dormant_elevated,
  CASE WHEN (SELECT COUNT(*) FROM sod_violations) > 0
        THEN 'OPEN FINDINGS'
        ELSE 'CLEAN' END                                        status
FROM dual;
```

## 13. Evidence Pack for the Audit Committee

```sql
-- Every artifact the auditor should be able to produce on request
SELECT 'Risk matrix'        artifact, COUNT(*) records FROM xx_sod_conflict
UNION ALL SELECT 'Detection query output', COUNT(*) FROM sod_violations
UNION ALL SELECT 'Remediation actions',     COUNT(*) FROM xx_sod_remediation_log
UNION ALL SELECT 'Approved exceptions',      COUNT(*) FROM xx_sod_exception
UNION ALL SELECT 'Certification records',   COUNT(*) FROM xx_sod_certification
UNION ALL SELECT 'Preventive control events',COUNT(*) FROM xx_sod_block_events
UNION ALL SELECT 'Verification (post-fix)',  COUNT(*) FROM sod_violations
 WHERE remediated_on IS NOT NULL;
```

**An auditor should never need to ask for a second query.** Every number in the
evidence pack should already exist in a table.