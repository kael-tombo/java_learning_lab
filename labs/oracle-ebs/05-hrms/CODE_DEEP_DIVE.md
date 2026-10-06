# Lab 05: HRMS Data Migration — Code Deep Dive

## 1. Staging Layer

```sql
CREATE TABLE xx_stage_people (
  src_row_id        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  src_system        VARCHAR2(20) NOT NULL,
  employee_number   VARCHAR2(30),
  national_id       VARCHAR2(50),
  first_name        VARCHAR2(100),
  last_name         VARCHAR2(100),
  birth_date_raw    VARCHAR2(30),        -- RAW: never parse in staging
  gender            VARCHAR2(2),
  nationality       VARCHAR2(3),
  hire_date_raw     VARCHAR2(30),
  legislative_code  VARCHAR2(6),
  email             VARCHAR2(120),
  -- derived / validated
  birth_date        DATE,
  hire_date         DATE,
  validation_status VARCHAR2(10) DEFAULT 'PENDING' NOT NULL, -- PENDING/VALID/ERROR
  error_count       NUMBER DEFAULT 0
);

CREATE TABLE xx_stage_assignments (
  src_row_id     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  employee_number VARCHAR2(30) NOT NULL,
  position_code   VARCHAR2(30),
  org_code        VARCHAR2(30),
  manager_empno   VARCHAR2(30),
  start_date_raw  VARCHAR2(30),
  end_date_raw    VARCHAR2(30),
  emp_status      VARCHAR2(30),
  start_date      DATE,
  end_date        DATE,
  validation_status VARCHAR2(10) DEFAULT 'PENDING' NOT NULL,
  error_count     NUMBER DEFAULT 0
);
```

**Key**: raw string columns are preserved alongside derived columns. The raw
value survives so a parser fix never requires a re-extract.

## 2. Error Report Structure

```sql
CREATE TABLE xx_mig_error (
  error_id     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  run_id       NUMBER NOT NULL,
  domain       VARCHAR2(20) NOT NULL,   -- PERSON/ASSIGNMENT/SUPERVISOR/IDENTIFIER/DATE
  entity_type  VARCHAR2(20) NOT NULL,
  src_row_id   NUMBER,
  src_system   VARCHAR2(30),
  employee_number VARCHAR2(30),
  error_code   VARCHAR2(30) NOT NULL,   -- machine-readable for grouping
  field_name   VARCHAR2(40),
  bad_value    VARCHAR2(400),           -- the offending value
  rule_text    VARCHAR2(400),           -- what was expected
  severity     VARCHAR2(10) DEFAULT 'ERROR' NOT NULL, -- ERROR/WARNING
  CONSTRAINT xx_mig_err_sev_ck CHECK (severity IN ('ERROR','WARNING'))
);

CREATE INDEX xx_mig_err_idx ON xx_mig_error (run_id, domain, error_code);
```

## 3. Date Normalisation — Detect, Don't Guess

```sql
CREATE OR REPLACE PACKAGE xx_date_norm_pkg AS
  FUNCTION parse_flexible(
    p_raw     IN VARCHAR2,
    p_row_id  IN NUMBER,
    p_country IN VARCHAR2,
    p_field   IN VARCHAR2
  ) RETURN DATE;   -- NULL signals reject
END;
/

CREATE OR REPLACE PACKAGE BODY xx_date_norm_pkg AS

  FUNCTION parse_flexible(
    p_raw IN VARCHAR2, p_row_id IN NUMBER,
    p_country IN VARCHAR2, p_field IN VARCHAR2
  ) RETURN DATE IS
    l_d1 NUMBER; l_d2 NUMBER;
  BEGIN
    IF p_raw IS NULL OR TRIM(p_raw) IS NULL THEN RETURN NULL; END IF;

    -- ISO dates need no guessing
    IF REGEXP_LIKE(p_raw, '^\d{4}-\d{2}-\d{2}$') THEN
      RETURN TO_DATE(p_raw, 'YYYY-MM-DD');
    END IF;

    -- Dotted form
    IF REGEXP_LIKE(p_raw, '^\d{1,2}\.\d{1,2}\.\d{4}$') THEN
      RETURN TO_DATE(p_raw, 'DD.MM.YYYY');
    END IF;

    -- Slash or dash form with two components
    IF REGEXP_LIKE(p_raw, '^(\d{1,2})[/|-](\d{1,2})[/|-](\d{4})$') THEN
      l_d1 := TO_NUMBER(REGEXP_SUBSTR(p_raw, '^(\d{1,2})', 1, 1, NULL, 1));
      l_d2 := TO_NUMBER(REGEXP_SUBSTR(p_raw, '^(\d{1,2})[/|-]', 1, 1, NULL, 1));

      IF l_d1 > 12 AND l_d2 <= 12 THEN
        RETURN TO_DATE(p_raw, CASE WHEN INSTR(p_raw,'/')>0 THEN 'DD/MM/YYYY' ELSE 'DD-MM-YYYY' END);
      ELSIF l_d2 > 12 AND l_d1 <= 12 THEN
        RETURN TO_DATE(p_raw, CASE WHEN INSTR(p_raw,'/')>0 THEN 'MM/DD/YYYY' ELSE 'MM-DD-YYYY' END);
      ELSE
        -- BOTH ≤ 12: genuinely ambiguous. REJECT — do not guess.
        INSERT INTO xx_mig_error
          (run_id, domain, entity_type, src_row_id, employee_number,
           error_code, field_name, bad_value, rule_text, severity)
        VALUES (p_row_id=>p_row_id, domain=>'DATE', entity_type=>'PEOPLE',
                src_row_id=>p_row_id, employee_number=>NULL,
                error_code=>'AMBIGUOUS_DATE', field_name=>p_field,
                bad_value=>p_raw,
                rule_text=>'Both components ≤ 12; country '||p_country||
                           ' convention must be supplied by source owner',
                severity=>'ERROR');
        RETURN NULL;
      END IF;
    END IF;

    INSERT INTO xx_mig_error
      (run_id, domain, entity_type, src_row_id, error_code, field_name,
       bad_value, rule_text, severity)
    VALUES (p_row_id, 'DATE', 'PEOPLE', p_row_id, 'UNPARSEABLE_DATE',
            p_field, p_raw, 'Not a recognised date format', 'ERROR');
    RETURN NULL;
  END parse_flexible;

END xx_date_norm_pkg;
/
```

**Design rule**: ambiguity produces an error, never a guess. A wrong date
discovered at payroll is far more expensive than a rejected row.

## 4. National Identifier Validation with Checksum

```sql
CREATE OR REPLACE PACKAGE xx_nid_pkg AS
  FUNCTION validate(p_nid IN VARCHAR2, p_legislation IN VARCHAR2)
    RETURN VARCHAR2;   -- NULL = valid, else error code
END;
/

CREATE OR REPLACE PACKAGE BODY xx_nid_pkg AS

  -- Singapore NRIC: letter prefix encodes weight table, letter suffix is checksum
  FUNCTION nric_checksum_valid(p_nid IN VARCHAR2) RETURN BOOLEAN IS
    TYPE wt IS TABLE OF NUMBER INDEX BY PLS_INTEGER;
    l_weights wt := (2,7,6,5,4,3,2);
    l_sum NUMBER := 0; l_digit NUMBER;
    l_table CONSTANT PLS_INTEGER :=
      CASE SUBSTR(UPPER(p_nid),1,1)
        WHEN 'S' THEN 0 WHEN 'T' THEN 1
        WHEN 'F' THEN 2 WHEN 'G' THEN 3 ELSE -1 END;
    l_alpha CONSTANT VARCHAR2(20) := 'JZIHGFEDCBA';
  BEGIN
    IF NOT REGEXP_LIKE(p_nid, '^[STFGMstfgm]\d{7}[A-Za-z]$') THEN RETURN FALSE; END IF;
    FOR i IN 1..7 LOOP
      l_digit := TO_NUMBER(SUBSTR(p_nid, i+1, 1));
      l_sum   := l_sum + l_digit * l_weights(i);
    END LOOP;
    l_sum := l_sum + l_table * 4;
    RETURN SUBSTR(l_alpha, MOD(l_sum, 11) + 1, 1)
           = UPPER(SUBSTR(p_nid, 9, 1));
  END nric_checksum_valid;

  FUNCTION validate(p_nid IN VARCHAR2, p_legislation IN VARCHAR2)
    RETURN VARCHAR2 IS
  BEGIN
    IF p_nid IS NULL THEN RETURN 'MISSING_NID'; END IF;
    CASE p_legislation
      WHEN 'US' THEN
        IF NOT REGEXP_LIKE(p_nid, '^\d{9}$') THEN RETURN 'US_NID_FORMAT'; END IF;
      WHEN 'GB' THEN
        IF NOT REGEXP_LIKE(p_nid, '^[A-Z]{2}\d{6}[A-Z]$') THEN RETURN 'GB_NID_FORMAT'; END IF;
      WHEN 'DE' THEN
        IF NOT REGEXP_LIKE(p_nid, '^\d{11}$') THEN RETURN 'DE_NID_FORMAT'; END IF;
      WHEN 'SG' THEN
        IF NOT nric_checksum_valid(p_nid) THEN RETURN 'SG_NID_CHECKSUM'; END IF;
      WHEN 'IN' THEN
        IF NOT REGEXP_LIKE(p_nid, '^\d{12}$') THEN RETURN 'IN_AADHAAR_FORMAT'; END IF;
      ELSE
        NULL;  -- no rule configured: warn, do not block
    END CASE;
    RETURN NULL;
  END validate;

END xx_nid_pkg;
/
```

## 5. Domain Validator — Person

```sql
CREATE OR REPLACE PROCEDURE xx_val_person(p_run_id IN NUMBER) IS
  l_err VARCHAR2(30);
  CURSOR c IS
    SELECT src_row_id, national_id, first_name, last_name,
           birth_date_raw, hire_date_raw, legislative_code
      FROM xx_stage_people WHERE validation_status = 'PENDING';
BEGIN
  FOR r IN c LOOP
    l_err := NULL;

    IF r.last_name IS NULL OR TRIM(r.last_name) IS NULL THEN
      INSERT INTO xx_mig_error (run_id,domain,entity_type,src_row_id,error_code,
        field_name,bad_value,rule_text)
      VALUES (p_run_id,'PERSON','PEOPLE',r.src_row_id,'MISSING_LAST_NAME',
              'last_name',r.last_name,'last_name is mandatory');
    END IF;

    IF r.first_name IS NULL THEN
      INSERT INTO xx_mig_error (run_id,domain,entity_type,src_row_id,error_code,
        field_name,rule_text)
      VALUES (p_run_id,'PERSON','PEOPLE',r.src_row_id,'MISSING_FIRST_NAME',
              'first_name','first_name is mandatory');
    END IF;

    -- Identifier: shape AND checksum
    l_err := xx_nid_pkg.validate(r.national_id, r.legislative_code);
    IF l_err IS NOT NULL THEN
      INSERT INTO xx_mig_error (run_id,domain,entity_type,src_row_id,error_code,
        field_name,bad_value,rule_text)
      VALUES (p_run_id,'IDENTIFIER','PEOPLE',r.src_row_id,l_err,
              'national_id',r.national_id,
              'Expected '||r.legislative_code||' format with valid checksum');
    END IF;

    -- Dates
    UPDATE xx_stage_people
       SET birth_date = xx_date_norm_pkg.parse_flexible(
             birth_date_raw, src_row_id, legislative_code, 'birth_date'),
           hire_date  = xx_date_norm_pkg.parse_flexible(
             hire_date_raw, src_row_id, legislative_code, 'hire_date')
     WHERE src_row_id = r.src_row_id;

    -- Plausibility: DOB must leave a plausible working age
    IF r.birth_date_raw IS NOT NULL THEN
      UPDATE xx_stage_people p
         SET validation_status = CASE
               WHEN p.birth_date IS NULL THEN 'ERROR'
               WHEN p.birth_date > SYSDATE THEN 'ERROR'
               WHEN MONTHS_BETWEEN(p.birth_date, p.hire_date) < 216 THEN 'ERROR'
               ELSE p.validation_status END,
             error_count = (SELECT COUNT(*) FROM xx_mig_error
                             WHERE src_row_id = p.src_row_id AND run_id = p_run_id)
       WHERE p.src_row_id = r.src_row_id;
    END IF;
  END LOOP;
END;
/
```

## 6. Overlap Detection (Detection Automated, Classification Routed)

```sql
-- Detect overlapping assignments — do NOT auto-fix
INSERT INTO xx_mig_error
  (run_id, domain, entity_type, src_row_id, employee_number,
   error_code, field_name, bad_value, rule_text, severity)
SELECT p_run_id, 'ASSIGNMENT', 'ASSIGNMENTS', a.src_row_id, a.employee_number,
       'OVERLAPPING_ASSIGNMENT', 'effective_dates',
       a.start_date||' to '||COALESCE(a.end_date,'OPEN')||' overlaps '||
       b.start_date||' to '||COALESCE(b.end_date,'OPEN'),
       'HR must classify: correction, transfer, or genuine dual-role',
       'ERROR'
  FROM xx_stage_assignments a
  JOIN xx_stage_assignments b
    ON a.employee_number = b.employee_number
   AND a.src_row_id < b.src_row_id
   AND a.start_date IS NOT NULL AND b.start_date IS NOT NULL
   AND a.start_date <= NVL(b.end_date, DATE '9999-12-31')
   AND b.start_date <= NVL(a.end_date, DATE '9999-12-31')
 WHERE p_run_id = p_run_id;

-- Resolution is a business decision, applied explicitly
UPDATE xx_stage_assignments
   SET end_date = (SELECT MIN(b.start_date) - 1
                     FROM xx_stage_assignments b
                    WHERE b.employee_number = xx_stage_assignments.employee_number
                      AND b.start_date > xx_stage_assignments.start_date)
 WHERE employee_number IN (SELECT employee_number FROM xx_mig_error
                            WHERE error_code = 'OVERLAPPING_ASSIGNMENT')
   AND resolution_flag = 'HR_CONFIRMED_CORRECTION';
```

## 7. Load Pass 1 — People

```sql
CREATE OR REPLACE PROCEDURE xx_load_people(p_run_id IN NUMBER) IS
  l_person_id NUMBER;
  l_err       VARCHAR2(4000);
BEGIN
  FOR r IN (SELECT s.* FROM xx_stage_people s
             WHERE s.validation_status = 'VALID') LOOP
    BEGIN
      hr_people_api.create_person(
        p_effective_start_date => r.hire_date,
        p_effective_end_date   => NULL,
        p_person => hr_people_api.g_person_id_rec(
                      person_type         => 'EMPLOYEE',
                      national_identifier => r.national_id,
                      date_of_birth       => r.birth_date,
                      sex                 => r.gender,
                      person_last_name    => r.last_name,
                      person_first_name   => r.first_name),
        p_person_id      => l_person_id,
        p_error_indicator=> 'Y',
        p_error_messages => l_err);

      IF l_err IS NOT NULL THEN
        INSERT INTO xx_mig_error (run_id,domain,entity_type,src_row_id,
          error_code,rule_text)
        VALUES (p_run_id,'LOAD','PEOPLE',r.src_row_id,'API_REJECT',l_err);
      ELSE
        UPDATE xx_stage_people SET validation_status = 'LOADED'
         WHERE src_row_id = r.src_row_id;
      END IF;
    EXCEPTION WHEN OTHERS THEN
      INSERT INTO xx_mig_error (run_id,domain,entity_type,src_row_id,
        error_code,rule_text)
      VALUES (p_run_id,'LOAD','PEOPLE',r.src_row_id,'API_EXCEPTION',SQLERRM);
    END;
  END LOOP;
END;
/
```

## 8. Load Pass 2 — Assignments (via API, effective dated)

```sql
CREATE OR REPLACE PROCEDURE xx_load_assignments(p_run_id IN NUMBER) IS
  l_err VARCHAR2(4000);
  l_position_id NUMBER; l_org_id NUMBER;
BEGIN
  FOR r IN (SELECT s.* FROM xx_stage_assignments s
             WHERE s.validation_status = 'VALID'
             ORDER BY s.employee_number, s.start_date) LOOP  -- ordered!
    BEGIN
      SELECT position_id INTO l_position_id FROM hr_all_positions_v
       WHERE position_code = r.position_code;
      SELECT organization_id INTO l_org_id FROM hr_all_organizations_v
       WHERE organization_code = r.org_code;

      hr_assignment_api.create_assignment(
        p_effective_start_date => r.start_date,
        p_effective_end_date   => r.end_date,
        p_assignment => hr_assignment_api.g_assignment_rec(
                         assignment_type => 'E',
                         primary_flag    => 'Y',
                         position_id     => l_position_id,
                         organization_id => l_org_id,
                         assignment_status => 'ACTIVE'),
        p_error_indicator => 'Y',
        p_error_messages  => l_err);

      IF l_err IS NOT NULL THEN
        INSERT INTO xx_mig_error (run_id,domain,entity_type,src_row_id,
          error_code,rule_text)
        VALUES (p_run_id,'LOAD','ASSIGNMENTS',r.src_row_id,'API_REJECT',l_err);
      ELSE
        UPDATE xx_stage_assignments SET validation_status = 'LOADED'
         WHERE src_row_id = r.src_row_id;
      END IF;
    EXCEPTION WHEN NO_DATA_FOUND THEN
      INSERT INTO xx_mig_error (run_id,domain,entity_type,src_row_id,error_code,rule_text)
      VALUES (p_run_id,'LOAD','ASSIGNMENTS',r.src_row_id,
              'POSITION_NOT_FOUND','Position '||r.position_code||' not in HRMS');
    END WHEN OTHERS THEN
      INSERT INTO xx_mig_error (run_id,domain,entity_type,src_row_id,error_code,rule_text)
      VALUES (p_run_id,'LOAD','ASSIGNMENTS',r.src_row_id,'API_EXCEPTION',SQLERRM);
    END;
  END LOOP;
END;
/
```

## 9. Load Pass 3 — Placeholders then Supervisor Links

```sql
-- 3a. Placeholder supervisors for orphans (runs BEFORE the manager update)
INSERT INTO per_all_people_f
  (person_id, effective_start_date, effective_end_date, person_type,
   person_last_name, person_first_name, national_identifier)
SELECT DISTINCT s.manager_empno,
       DATE '2000-01-01', DATE '9999-12-31', 'EMPLOYEE',
       'PLACEHOLDER', 'MGR_'||s.manager_empno, 'PLACEHOLDER-'||s.manager_empno
  FROM xx_stage_assignments s
 WHERE s.manager_empno IS NOT NULL
   AND s.validation_status = 'VALID'
   AND NOT EXISTS (SELECT 1 FROM per_all_people_f p
                    WHERE TO_CHAR(p.person_id) = s.manager_empno);

-- Mark placeholders explicitly so they are visible on the exception report
UPDATE per_all_people_b
   SET national_identifier = 'PLACEHOLDER-'||person_id
 WHERE national_identifier LIKE 'PLACEHOLDER-%';

-- 3b. Now set managers (assignments already exist)
UPDATE per_all_assignments_f a
   SET a.manager_id = (SELECT TO_NUMBER(s.manager_empno)
                         FROM xx_stage_assignments s
                        WHERE s.employee_number =
                              (SELECT employee_number FROM xx_stage_emp_map
                                WHERE person_id = a.person_id)
                          AND s.validation_status = 'VALID')
 WHERE a.assignment_type = 'E'
   AND a.primary_flag = 'Y'
   AND EXISTS (SELECT 1 FROM xx_stage_emp_map m WHERE m.person_id = a.person_id);

-- 3c. Pre-flight assertion: this MUST return 0
SELECT COUNT(*) AS unresolved_managers
  FROM per_all_assignments_f
 WHERE assignment_type = 'E' AND primary_flag = 'Y' AND manager_id IS NULL;
```

## 10. Reconciliation — Four Checks

```sql
-- Check 1: counts per domain
SELECT 'PEOPLE' domain,
       (SELECT COUNT(*) FROM xx_stage_people WHERE validation_status='LOADED') loaded,
       (SELECT COUNT(*) FROM xx_stage_people WHERE validation_status='VALID')  to_load,
       (SELECT COUNT(*) FROM xx_stage_people WHERE validation_status='ERROR')  rejected
  FROM dual
UNION ALL
SELECT 'ASSIGNMENTS',
       (SELECT COUNT(*) FROM xx_stage_assignments WHERE validation_status='LOADED'),
       (SELECT COUNT(*) FROM xx_stage_assignments WHERE validation_status='VALID'),
       (SELECT COUNT(*) FROM xx_stage_assignments WHERE validation_status='ERROR')
  FROM dual;

-- Check 2: hierarchy integrity — orphan managers
SELECT COUNT(*) orphan_managers
  FROM per_all_assignments_f a
 WHERE a.manager_id IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM per_all_people_f p WHERE p.person_id = a.manager_id);

-- Check 3: effective-date sanity — overlaps and missing end dates
SELECT COUNT(*) overlapping_assignments
  FROM per_all_assignments_f a
  JOIN per_all_assignments_f b
    ON a.person_id = b.person_id AND a.assignment_id < b.assignment_id
   AND a.effective_start_date <= NVL(b.effective_end_date, DATE '9999-12-31')
   AND b.effective_start_date <= NVL(a.effective_end_date, DATE '9999-12-31');

-- Check 4: sample spot-check against source
SELECT s.employee_number, s.last_name, p.person_last_name, p.person_first_name
  FROM xx_stage_people s
  JOIN xx_stage_emp_map m ON m.src_row_id = s.src_row_id
  JOIN per_all_people_f p ON p.person_id = m.person_id
 WHERE ROWNUM <= 20
   AND (p.person_last_name <> s.last_name OR p.person_first_name <> s.first_name);
```

## 11. Error Summary Dashboard

```sql
SELECT domain, error_code, COUNT(*) occurrences,
       MIN(bad_value) sample_value, MIN(rule_text) expected
  FROM xx_mig_error
 WHERE run_id = :run_id AND severity = 'ERROR'
 GROUP BY domain, error_code
 ORDER BY COUNT(*) DESC;
```

## 12. Cycle Detection in the Loaded Hierarchy

```sql
WITH RECURSIVE emp_path (person_id, mgr_id, path, depth) AS (
  SELECT a.person_id, a.manager_id, ', ' || a.person_id || ',', 1
    FROM per_all_assignments_f a
   WHERE a.assignment_type = 'E' AND a.primary_flag = 'Y'
  UNION ALL
  SELECT e.person_id, a.manager_id, p.path || a.manager_id || ',', p.depth + 1
    FROM emp_path p
    JOIN per_all_assignments_f a ON a.person_id = p.mgr_id
   WHERE p.depth < 25 AND INSTR(p.path, ', ' || a.manager_id || ',') = 0
)
SELECT person_id, depth, path FROM emp_path
 WHERE depth = (SELECT MAX(depth) FROM emp_path);
```

A result at depth 25 indicates a **cycle** — a migration defect that produces
an infinite org chart and breaks every hierarchy-walking report.

## 13. Performance: Bulk Load Considerations

```sql
-- Check current state before optimising
SELECT COUNT(*) total_rows,
       COUNT(DISTINCT employee_number) distinct_emps
  FROM xx_stage_assignments;

-- Batch the load; do not hold one transaction across 20,000 API calls
-- Commit every N rows so a failure resumes rather than restarts:
--   xx_load_assignments processes N=500 per commit
```

```bash
-- Direct DML is faster but UNSUPPORTED and skips validation:
#   Prohibited for PER_ALL_* tables — use hr_people_api / hr_assignment_api
#   20,000 records via API typically 2-4 hours. Plan the window accordingly.
```