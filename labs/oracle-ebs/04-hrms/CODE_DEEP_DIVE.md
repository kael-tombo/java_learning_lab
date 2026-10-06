# Lab 04: Employee Lifecycle Management (HRMS) — Code Deep Dive

## 1. Lifecycle Audit Trail (Append-Only)

```sql
CREATE TABLE xx_hr_lifecycle_audit (
  audit_id       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  person_id      NUMBER NOT NULL,
  event_type     VARCHAR2(30) NOT NULL,
  effective_from DATE NOT NULL,
  effective_to   DATE NOT NULL,
  actor          VARCHAR2(64) NOT NULL,
  approver       VARCHAR2(64),
  source_system  VARCHAR2(20) NOT NULL,  -- SELF_SERVICE / API / MIGRATION
  reason         VARCHAR2(400),
  created_at     TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  CONSTRAINT xx_hr_audit_ev_ck CHECK (event_type IN (
    'HIRE','CONFIRM','TRANSFER','PROMOTION','PAY_CHANGE','LEAVE',
    'SUSPEND','TERMINATE','REHIRE','ALUMNI')),
  CONSTRAINT xx_hr_audit_src_ck CHECK (source_system IN (
    'SELF_SERVICE','API','MIGRATION','BATCH'))
);

-- Append-only enforcement: block UPDATE and DELETE
CREATE OR REPLACE TRIGGER xx_hr_lifecycle_audit_no_upd
BEFORE UPDATE OR DELETE ON xx_hr_lifecycle_audit
FOR EACH ROW
BEGIN
  RAISE_APPLICATION_ERROR(-20001,
    'Lifecycle audit trail is append-only. Retention: 7 years.');
END;
/
```

## 2. Headcount As At Any Past Date (Correct `_F` Usage)

```sql
-- This is the query people get wrong. _F has MULTIPLE rows per person.
SELECT COUNT(DISTINCT person_id) AS headcount_as_at
  FROM per_all_assignments_f
 WHERE assignment_type = 'E'                      -- primary employment
   AND primary_flag    = 'Y'
   AND effective_start_date <= DATE '2026-02-01'
   AND effective_end_date   >= DATE '2026-02-01';
```

### Contrast with current state
```sql
-- Current state: use the _V view
SELECT COUNT(*) AS current_headcount
  FROM per_all_assignments_v
 WHERE assignment_type = 'E' AND primary_flag = 'Y';
```

### Reconstruct one person's history
```sql
SELECT a.effective_start_date, a.effective_end_date,
       p.position_name, o.name organization_name, m.person_id mgr_id
  FROM per_all_assignments_f a
  JOIN per_All_positions p ON p.position_id = a.position_id
  JOIN per_all_organizations o ON o.organization_id = a.organization_id
  LEFT JOIN per_all_people_f m ON m.person_id = a.manager_id
 WHERE a.person_id = 1001
 ORDER BY a.effective_start_date;
```

## 3. Create Person + Assignment via Public API

```sql
DECLARE
  l_person_id     NUMBER;
  l_assignment_id NUMBER;
  l_error         VARCHAR2(4000);
  c_person        hr_people_api.g_person_id_rec;
  c_assignment    hr_assignment_api.g_assignment_rec;
BEGIN
  c_person := hr_people_api.g_person_id_rec(
    effective_start_date => DATE '2026-03-01',
    effective_end_date   => DATE '9999-12-31',
    person_type          => 'EMPLOYEE',
    national_identifier  => 'EMP-100234',
    date_of_birth        => DATE '1990-05-14',
    sex                  => 'M',
    person_last_name     => 'GARCIA',
    person_first_name    => 'MARCO',
    nationality_code     => 'ES');

  hr_people_api.create_person(
    p_person_id    => l_person_id,
    p_person       => c_person,
    p_object_version => NULL,
    p_effective_start_date => DATE '2026-03-01',
    p_effective_end_date   => NULL,
    p_error_number => NULL,
    p_error_indicator => 'Y',
    p_error_messages => l_error);

  IF l_error IS NOT NULL THEN
    DBMS_OUTPUT.PUT_LINE('Person create failed: ' || l_error);
    RAISE_APPLICATION_ERROR(-20010, l_error);
  END IF;
  DBMS_OUTPUT.PUT_LINE('person_id = ' || l_person_id);
END;
/
```

**Note**: `p_error_indicator => 'Y'` means "return errors in the OUT parameter"
rather than raising. Always check it — an unchecked API call is an unchecked
failure.

## 4. Effective-Dated Transfer (Never UPDATE)

```sql
DECLARE
  l_assignment_id NUMBER;
  c_assignment    hr_assignment_api.g_assignment_rec;
BEGIN
  SELECT assignment_id INTO l_assignment_id
    FROM per_all_assignments_f
   WHERE person_id = 1001 AND assignment_type = 'E'
     AND effective_start_date <= TRUNC(SYSDATE)
     AND effective_end_date   >= TRUNC(SYSDATE);

  c_assignment := hr_assignment_api.g_assignment_rec(
    assignment_id        => l_assignment_id,
    effective_start_date => DATE '2026-08-01',   -- future-dated
    effective_end_date   => NULL,                -- close the current row
    position_id          => 5033,                -- new position
    organization_id      => 205,
    manager_id           => 1100,
    assignment_status    => 'ACTIVE');

  -- The API closes the old row and opens the new one automatically.
  hr_assignment_api.update_assignment(
    p_effective_start_date => DATE '2026-08-01',
    p_effective_end_date   => NULL,
    p_assignment_id        => l_assignment_id,
    p_assignment           => c_assignment,
    p_object_version       => NULL,
    p_validate_flag        => FALSE,
    p_error_number         => NULL,
    p_error_indicator      => 'Y',
    p_error_messages       => l_error);

  IF l_error IS NOT NULL THEN
    RAISE_APPLICATION_ERROR(-20011, l_error);
  END IF;
END;
/
```

## 5. Lifecycle Trigger Engine (Idempotent)

```sql
CREATE TABLE xx_hr_lifecycle_action (
  action_id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  event_id       NUMBER NOT NULL,
  person_id      NUMBER NOT NULL,
  action_type    VARCHAR2(30) NOT NULL,  -- PAYROLL_SETUP / BENEFITS / EQUIPMENT / ACCESS
  status         VARCHAR2(15) DEFAULT 'PENDING' NOT NULL, -- PENDING/DONE/FAILED
  attempts       NUMBER DEFAULT 0 NOT NULL,
  last_error     VARCHAR2(4000),
  CONSTRAINT xx_hr_act_uq UNIQUE (event_id, person_id, action_type)  -- idempotency
);
```

### Fire actions on an event — safe to run repeatedly
```sql
CREATE OR REPLACE PACKAGE xx_hr_lifecycle_pkg AS
  PROCEDURE raise_event(
    p_person_id  IN NUMBER,
    p_event_type IN VARCHAR2,
    p_eff_from   IN DATE,
    p_actor      IN VARCHAR2,
    p_approver   IN VARCHAR2 DEFAULT NULL
  );
END;
/

CREATE OR REPLACE PACKAGE BODY xx_hr_lifecycle_pkg AS

  PROCEDURE raise_event(
    p_person_id  IN NUMBER,
    p_event_type IN VARCHAR2,
    p_eff_from   IN DATE,
    p_actor      IN VARCHAR2,
    p_approver   IN VARCHAR2 DEFAULT NULL
  ) IS
    l_event_id NUMBER;
  BEGIN
    -- 1. Audit (append-only)
    INSERT INTO xx_hr_lifecycle_audit
      (person_id, event_type, effective_from, effective_to,
       actor, approver, source_system)
    VALUES (p_person_id, p_event_type, p_eff_from, DATE '9999-12-31',
            p_actor, p_approver, 'API');

    l_event_id := SYS_GUID();  -- logical event key

    -- 2. Cascade actions — MERGE makes this idempotent
    FOR r IN (
      SELECT t.action_type
        FROM TABLE(SYS.ODCIVARCHAR2LIST(
               'PAYROLL_SETUP','BENEFITS_ENROLLMENT','EQUIPMENT','SECURITY_PROFILE'
             )) t
    ) LOOP
      MERGE INTO xx_hr_lifecycle_action tgt
      USING (SELECT l_event_id eid, p_person_id pid, r.action_type atype
               FROM dual) src
         ON (tgt.event_id = src.eid
             AND tgt.person_id = src.pid
             AND tgt.action_type = src.atype)
       WHEN NOT MATCHED THEN
         INSERT (event_id, person_id, action_type, status)
         VALUES (src.eid, src.pid, src.atype, 'PENDING');
    END LOOP;
  END raise_event;

END xx_hr_lifecycle_pkg;
/
```

**Idempotency proof**: running `raise_event` twice with the same event key
inserts zero duplicate actions because of the `MERGE` + unique constraint.

## 6. Termination with Legislative Rules

```sql
CREATE OR REPLACE PROCEDURE xx_hr_terminate(
  p_person_id     IN NUMBER,
  p_termination_date IN DATE,
  p_reason        IN VARCHAR2
) IS
  l_notice_days   NUMBER;
  l_final_pay     NUMBER;
  l_leg_id        NUMBER;
BEGIN
  -- Legislative rule comes from CONFIGURATION, not hardcoded
  BEGIN
    SELECT leg.segment1 INTO l_leg_id
      FROM per_assignments_f a
      JOIN per_people_f p ON p.person_id = a.person_id
      JOIN per_com_legislations_f leg ON leg.legislation_id = p.legislation_id
     WHERE a.person_id = p_person_id
       AND a.effective_start_date <= p_termination_date
       AND a.effective_end_date   >= p_termination_date;
  EXCEPTION WHEN NO_DATA_FOUND THEN
    l_leg_id := NULL;
  END;

  -- Notice period from the legislative table
  SELECT MAX(notice_period_days) INTO l_notice_days
    FROM xx_leg_notice_rules
   WHERE legislation_id = l_leg_id;

  -- End the assignment (never delete the person)
  UPDATE per_all_assignments_f
     SET effective_end_date = p_termination_date - 1,
         assignment_status  = 'INACTIVE'
   WHERE person_id = p_person_id
     AND assignment_type = 'E'
     AND effective_start_date <= p_termination_date
     AND effective_end_date   >= p_termination_date;

  -- Person record retained; status updated
  UPDATE per_all_people_f
     SET effective_end_date = NULL
   WHERE person_id = p_person_id;

  xx_hr_lifecycle_pkg.raise_event(
    p_person_id => p_person_id,
    p_event_type => 'TERMINATE',
    p_eff_from  => p_termination_date,
    p_actor     => SYSTEM_USER,
    p_approver  => NULL);

  DBMS_OUTPUT.PUT_LINE('Terminated. Notice days per legislation: ' || l_notice_days);
END xx_hr_terminate;
```

## 7. Offboarding Checklist

```sql
CREATE TABLE xx_hr_offboarding (
  term_id       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  person_id     NUMBER NOT NULL,
  task_code     VARCHAR2(30) NOT NULL,
  owner         VARCHAR2(30) NOT NULL,   -- HR / IT / FINANCE / FACILITIES
  due_date      DATE NOT NULL,
  status        VARCHAR2(15) DEFAULT 'OPEN' NOT NULL,
  completed_at  TIMESTAMP,
  CONSTRAINT xx_hr_off_uq UNIQUE (person_id, task_code),
  CONSTRAINT xx_hr_off_st_ck CHECK (status IN ('OPEN','DONE','OVERDUE','WAIVED'))
);

-- Seed the standard checklist (offsets in days from termination)
INSERT INTO xx_hr_offboarding (person_id, task_code, owner, due_date) VALUES
  (1001, 'REVOKE_SSO',        'IT',          DATE '2026-03-01'),
  (1001, 'REVOKE_SYS_ACCESS', 'IT',          DATE '2026-03-02'),
  (1001, 'RECOVER_LAPTOP',    'IT',          DATE '2026-03-02'),
  (1001, 'RECOVER_BADGE',     'FACILITIES',  DATE '2026-03-02'),
  (1001, 'FINAL_PAYROLL',     'FINANCE',     DATE '2026-03-15'),
  (1001, 'BENEFITS_CONT',     'HR',          DATE '2026-03-15'),
  (1001, 'EXIT_INTERVIEW',    'HR',          DATE '2026-03-31');

-- Overdue detection (run as a concurrent program)
SELECT person_id, task_code, owner, due_date,
       ROUND(SYSDATE - due_date) days_overdue
  FROM xx_hr_offboarding
 WHERE status = 'OPEN' AND due_date < TRUNC(SYSDATE)
 ORDER BY days_overdue DESC;
```

## 8. ADP Payroll Integration Payload

```sql
CREATE OR REPLACE PACKAGE BODY xx_adp_out_pkg AS
  PROCEDURE build_hire_payload(p_person_id IN NUMBER) IS
    l_xml CLOB;
  BEGIN
    SELECT XMLAGG(XMLELEMENT(E, t.col || ': ' || t.val)).EXTRACTVAL
      INTO l_xml
      FROM (
        SELECT 'EMPLIDEE_ID' col, TO_CHAR(person_id) val FROM per_all_people_f
         WHERE person_id = p_person_id
        UNION ALL SELECT 'LAST_NAME', person_last_name FROM per_all_people_f
         WHERE person_id = p_person_id
        UNION ALL SELECT 'FIRST_NAME', person_first_name FROM per_all_people_f
         WHERE person_id = p_person_id
        UNION ALL SELECT 'NATIONAL_ID', national_identifier FROM per_all_people_f
         WHERE person_id = p_person_id
        UNION ALL SELECT 'LEGAL_ENTITY', SETVALUE(leg_id)
           FROM fnd_profile_values v
          WHERE v.profile_option_id = (SELECT profile_option_id
                                         FROM fnd_profile_options
                                        WHERE name = 'XX_HR_LEGAL_ENTITY')
            AND v.profile_option_id IN (SELECT profile_option_id FROM fnd_profile_options)
            AND ROWNUM = 1
      ) t;

    INSERT INTO xx_adp_outbound
      (payload, direction, status)
    VALUES (l_xml, 'OUT', 'PENDING');
  END build_hire_payload;
END;
/
```

## 9. Payroll Reconciliation (The Step Everyone Forgets)

```sql
-- Every employee sent must appear in the ADP response
SELECT s.national_identifier AS sent_emp,
       r.national_identifier AS received_emp,
       CASE WHEN r.national_identifier IS NULL THEN 'MISSING_IN_ADP'
            WHEN s.national_identifier IS NULL THEN 'UNEXPECTED_FROM_ADP'
            ELSE 'MATCHED' END AS status
  FROM xx_adp_outbound s
  LEFT JOIN xx_adp_inbound r
    ON r.national_identifier = s.national_identifier
   AND s.direction = 'OUT'
 WHERE s.direction = 'OUT'
   AND s.status = 'SENT'
   AND s.send_date >= ADD_MONTHS(TRUNC(SYSDATE), -1)
   AND (r.national_identifier IS NULL OR s.national_identifier IS NULL);
```

### Gross pay totals must reconcile
```sql
SELECT e.effective_payroll_id,
       ROUND(SUM(r.gross_pay), 2)    adp_gross,
       (SELECT ROUND(SUM(xx_earning_total), 2)
          FROM xx_payroll_calculated
         WHERE effective_payroll_id = e.effective_payroll_id) hrms_gross,
       ROUND(SUM(r.gross_pay) -
             (SELECT SUM(xx_earning_total) FROM xx_payroll_calculated
               WHERE effective_payroll_id = e.effective_payroll_id), 2) variance
  FROM xx_adp_inbound r
  JOIN per_payrolls_f e ON e.payroll_id = r.payroll_id
 WHERE r.pay_period = '2026-03'
 GROUP BY e.effective_payroll_id;
```

## 10. Migration Load Order (For Lifecycle Data)

```sql
-- 1. People
INSERT INTO per_all_people_f (person_id, national_identifier, person_type,
       person_last_name, person_first_name, effective_start_date, effective_end_date)
SELECT person_id, national_identifier, 'EMPLOYEE',
       last_name, first_name, hire_date, DATE '9999-12-31'
  FROM xx_stage_people
 WHERE validation_status = 'VALID';

-- 2. Assignments (depends on people existing)
INSERT INTO per_all_assignments_f (person_id, effective_start_date, effective_end_date,
       assignment_type, primary_flag, position_id, organization_id, manager_id, assignment_status)
SELECT person_id, start_date, COALESCE(end_date, DATE '9999-12-31'),
       'E', 'Y', position_id, org_id, manager_id, 'ACTIVE'
  FROM xx_stage_assignments
 WHERE validation_status = 'VALID';

-- 3. Managers (depends on assignments existing — do NOT load before step 2)
UPDATE per_all_assignments_f a
   SET a.manager_id = (SELECT s.manager_id FROM xx_stage_assignments s
                        WHERE s.person_id = a.person_id)
 WHERE a.person_id IN (SELECT person_id FROM xx_stage_assignments);

-- 4. Placeholder supervisors for orphaned manager references
INSERT INTO per_all_people_f (person_id, person_last_name, person_first_name,
       person_type, effective_start_date, effective_end_date)
SELECT DISTINCT s.manager_id, 'PLACEHOLDER', 'EMP' || s.manager_id,
       'EMPLOYEE', DATE '2000-01-01', DATE '9999-12-31'
  FROM xx_stage_assignments s
 WHERE s.manager_id IS NOT NULL
   AND s.manager_id NOT IN (SELECT person_id FROM per_all_people_f)
   AND ROWNUM = 1;
```

## 11. Performance Check

```sql
-- Before adding indexes to HRMS tables
SELECT /*+ FULL(a) */
       COUNT(DISTINCT a.person_id) headcount, a.assignment_status
  FROM per_all_assignments_f a
 WHERE a.assignment_type = 'E'
   AND a.effective_start_date <= DATE '2026-02-01'
   AND a.effective_end_date   >= DATE '2026-02-01'
 GROUP BY a.assignment_status;
```

Run this before and after any index change on HRMS tables. HRMS has strong
segmented-table and legacy-index characteristics — naive index creation can
**slow down** effective-dated queries significantly.