# Lab 05: Technical Foundations — Code Deep Dive

## 1. Staging and Run Control Tables

```sql
-- EDI staging
CREATE TABLE xx_price_list_stage (
  stage_id        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  file_name       VARCHAR2(200),
  line_no         NUMBER NOT NULL,
  supplier_code   VARCHAR2(30),
  item_code       VARCHAR2(30),
  unit_price      NUMBER(14,4),
  effective_date  DATE,
  currency        VARCHAR2(3),
  -- processing state
  status          VARCHAR2(12) DEFAULT 'PENDING' NOT NULL, -- PENDING/VALID/ERROR/PROCESSED
  run_id          NUMBER,
  vendor_id       NUMBER,
  error_count     NUMBER DEFAULT 0
);

-- Run header
CREATE TABLE xx_run_header (
  run_id        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  program_name  VARCHAR2(64) NOT NULL,
  mode          VARCHAR2(20)  NOT NULL,   -- VALIDATE_ONLY / PROCESS / ROLLBACK
  p_supplier_from VARCHAR2(30),
  p_supplier_to   VARCHAR2(30),
  p_category      VARCHAR2(30),
  p_effective_date DATE,
  requested_by   VARCHAR2(64) NOT NULL,
  started_at     TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  completed_at   TIMESTAMP,
  status         VARCHAR2(15) DEFAULT 'RUNNING' NOT NULL, -- RUNNING/SUCCESS/ERROR
  lines_total    NUMBER DEFAULT 0,
  lines_valid    NUMBER DEFAULT 0,
  lines_error    NUMBER DEFAULT 0,
  lines_processed NUMBER DEFAULT 0
);

-- Error log: survives failure via autonomous transaction
CREATE TABLE xx_run_error (
  error_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  run_id      NUMBER NOT NULL,
  line_no     NUMBER,
  error_code  VARCHAR2(30) NOT NULL,
  error_msg   VARCHAR2(1000) NOT NULL,
  created_at  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

-- Audit: append-only, keyed by run_id so ROLLBACK can find what to reverse
CREATE TABLE xx_run_audit (
  audit_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  run_id      NUMBER NOT NULL,
  object_type VARCHAR2(30) NOT NULL,  -- VENDOR/SITE/CONTACT/ITEM_PRICE
  object_id   VARCHAR2(30) NOT NULL,
  operation   VARCHAR2(10) NOT NULL,  -- INSERT/UPDATE
  field_name  VARCHAR2(40),
  old_value   VARCHAR2(200),
  new_value   VARCHAR2(200),
  actor       VARCHAR2(64) NOT NULL,
  created_at  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);
CREATE INDEX xx_ra_idx ON xx_run_audit (run_id, object_type);
```

## 2. Package Specification

```sql
CREATE OR REPLACE PACKAGE xx_price_list_pkg AS
  g_batch_size CONSTANT PLS_INTEGER := 500;

  -- Pure validation: no DML against EBS business data
  PROCEDURE validate(p_run_id IN NUMBER, p_commit_every IN PLS_INTEGER DEFAULT 500);

  -- Apply changes through standard APIs
  PROCEDURE process(p_run_id IN NUMBER, p_commit_every IN PLS_INTEGER DEFAULT 500);

  -- Reverse a specific prior run using the audit trail
  PROCEDURE rollback_run(p_run_id IN NUMBER);

  -- Autonomous error log: commits independently so it survives a failed txn
  PROCEDURE log_error(p_run_id IN NUMBER, p_line_no IN NUMBER,
                      p_code IN VARCHAR2, p_msg IN VARCHAR2);

  -- XML detail report
  FUNCTION build_xml_report(p_run_id IN NUMBER) RETURN CLOB;
END xx_price_list_pkg;
```

## 3. MOAC Context Handling

```sql
CREATE OR REPLACE PACKAGE BODY xx_price_list_pkg AS

  g_org_id NUMBER;

  PROCEDURE set_moac_context(p_org_id IN NUMBER) IS
    l_org_id NUMBER;
  BEGIN
    l_org_id := fnd_global_apps_pr.get_org_id(p_org_id);
    IF l_org_id = -1 THEN
      -- FAIL LOUDLY. Silent cross-org processing is an audit finding.
      RAISE_APPLICATION_ERROR(-20020,
        'No MOAC access to operating unit ' || p_org_id);
    END IF;
    mo_global_ogles.set_org_context(p_org_id, l_org_id);
    g_org_id := l_org_id;
  END set_moac_context;
```

## 4. Validation — Single Callable Unit

```sql
  PROCEDURE validate(p_run_id IN NUMBER, p_commit_every IN PLS_INTEGER DEFAULT 500) IS
    l_counter   PLS_INTEGER := 0;
    l_valid     PLS_INTEGER := 0;
    l_err       PLS_INTEGER := 0;
    l_vendor_id NUMBER;
    l_item_id   NUMBER;
    CURSOR c_rows IS
      SELECT stage_id, line_no, supplier_code, item_code,
             unit_price, effective_date, currency
        FROM xx_price_list_stage
       WHERE status = 'PENDING'
         AND supplier_code BETWEEN
             (SELECT p_supplier_from FROM xx_run_header WHERE run_id = p_run_id)
             AND (SELECT p_supplier_to   FROM xx_run_header WHERE run_id = p_run_id)
       ORDER BY line_no;
  BEGIN
    FOR r IN c_rows LOOP
      BEGIN
        -- Rule 1: supplier must exist in EBS master
        BEGIN
          SELECT vendor_id INTO l_vendor_id
            FROM po_vendors
           WHERE segment1 = r.supplier_code AND org_id = g_org_id;
        EXCEPTION WHEN NO_DATA_FOUND THEN
          log_error(p_run_id, r.line_no, 'SUPPLIER_NOT_FOUND',
                    'Supplier ' || r.supplier_code || ' not in PO_VENDORS');
          RAISE_APPLICATION_ERROR(-20001, 'supplier');
        END;

        -- Rule 2: item must exist and be active
        BEGIN
          SELECT inventory_item_id INTO l_item_id
            FROM mtl_system_items
           WHERE segment1 = r.item_code
             AND organization_id = g_org_id
             AND enabled_flag = 'Y';
        EXCEPTION WHEN NO_DATA_FOUND THEN
          log_error(p_run_id, r.line_no, 'ITEM_NOT_FOUND',
                    'Item ' || r.item_code || ' not found or disabled');
          RAISE_APPLICATION_ERROR(-20002, 'item');
        END;

        -- Rule 3: price must be positive
        IF r.unit_price IS NULL OR r.unit_price <= 0 THEN
          log_error(p_run_id, r.line_no, 'INVALID_PRICE',
                    'Unit price ' || NVL(TO_CHAR(r.unit_price),'NULL') || ' must be > 0');
          RAISE_APPLICATION_ERROR(-20003, 'price');
        END;

        -- Rule 4: effective date must be in the future or today
        IF r.effective_date < TRUNC(SYSDATE) THEN
          log_error(p_run_id, r.line_no, 'PAST_EFFECTIVE_DATE',
                    'Effective date ' || r.effective_date || ' is in the past');
          RAISE_APPLICATION_ERROR(-20004, 'date');
        END;

        UPDATE xx_price_list_stage
           SET status = 'VALID', vendor_id = l_vendor_id, error_count = 0
         WHERE stage_id = r.stage_id;
        l_valid := l_valid + 1;

      EXCEPTION WHEN OTHERS THEN
        l_err := l_err + 1;
        -- Mark the line ERROR without affecting the outer loop
        BEGIN
          UPDATE xx_price_list_stage
             SET status = 'ERROR', error_count = error_count + 1
           WHERE stage_id = r.stage_id;
        EXCEPTION WHEN OTHERS THEN NULL;  -- keep going
        END;
      END;

      l_counter := l_counter + 1;
      IF MOD(l_counter, p_commit_every) = 0 THEN
        COMMIT;
      END IF;
    END LOOP;

    COMMIT;
    UPDATE xx_run_header
       SET lines_total = l_valid + l_err, lines_valid = l_valid, lines_error = l_err
     WHERE run_id = p_run_id;
    COMMIT;
  END validate;
```

## 5. Error Logging with Autonomous Transaction

```sql
  PROCEDURE log_error(p_run_id IN NUMBER, p_line_no IN NUMBER,
                      p_code IN VARCHAR2, p_msg IN VARCHAR2) IS
    PRAGMA AUTONOMOUS_TRANSACTION;
  BEGIN
    INSERT INTO xx_run_error (run_id, line_no, error_code, error_msg)
    VALUES (p_run_id, p_line_no, SUBSTR(p_code, 1, 30), SUBSTR(p_msg, 1, 1000));
    COMMIT;   -- independent of the outer transaction, survives its rollback
  EXCEPTION WHEN OTHERS THEN
    ROLLBACK;  -- never let logging break the caller
  END log_error;
```

**This is the critical detail.** Without `PRAGMA AUTONOMOUS_TRANSACTION`, the
error row is part of the transaction that is about to roll back — and the log is
empty exactly when you need it.

## 6. Processing Through Standard APIs

```sql
  PROCEDURE process(p_run_id IN NUMBER, p_commit_every IN PLS_INTEGER DEFAULT 500) IS
    l_counter      PLS_INTEGER := 0;
    l_processed    PLS_INTEGER := 0;
    l_retval       VARCHAR2(2);
    l_errbuf       VARCHAR2(2000);
    l_vendor_site_id NUMBER;
    CURSOR c_valid IS
      SELECT s.stage_id, s.line_no, s.vendor_id, s.item_code,
             s.unit_price, s.effective_date, s.currency
        FROM xx_price_list_stage s
       WHERE s.status = 'VALID'
         AND (s.run_id IS NULL OR s.run_id <> p_run_id)   -- RESUMABLE
       ORDER BY s.line_no;
  BEGIN
    FOR r IN c_valid LOOP
      BEGIN
        -- Update purchasing item price via the standard API
        l_retval := po_requisition_import_savepoint_apis.create_po_from_req(
          NULL, NULL, NULL);

        -- The realistic price update path:
        UPDATE po_lines_all
           SET unit_price = r.unit_price
         WHERE line_id = xx_price_map(p_run_id, r.stage_id);
        -- ^ in production this is create/update through
        --   PO_REQ_CREATE_PUB / PO_CHANGE_ORDER_PUB, never direct DML.
        --   Shown here to make the audit pattern explicit.

        -- Audit: what changed, by whom, for rollback
        INSERT INTO xx_run_audit
          (run_id, object_type, object_id, operation, field_name,
           old_value, new_value, actor)
        VALUES (p_run_id, 'ITEM_PRICE', r.stage_id, 'UPDATE', 'UNIT_PRICE',
                NULL, TO_CHAR(r.unit_price), USER);

        UPDATE xx_price_list_stage
           SET status = 'PROCESSED', run_id = p_run_id
         WHERE stage_id = r.stage_id;

        l_processed := l_processed + 1;

      EXCEPTION WHEN OTHERS THEN
        log_error(p_run_id, r.line_no, 'PROCESS_FAILED', SQLERRM);
        UPDATE xx_price_list_stage SET status = 'ERROR' WHERE stage_id = r.stage_id;
      END;

      l_counter := l_counter + 1;
      IF MOD(l_counter, p_commit_every) = 0 THEN
        UPDATE xx_run_header SET lines_processed = l_processed WHERE run_id = p_run_id;
        COMMIT;   -- bounded undo, resumable
      END IF;
    END LOOP;

    COMMIT;
    UPDATE xx_run_header
       SET lines_processed = l_processed, completed_at = SYSTIMESTAMP,
           status = 'SUCCESS'
     WHERE run_id = p_run_id;
    COMMIT;
  END process;
```

## 7. ROLLBACK as a Parameter Mode

```sql
  PROCEDURE rollback_run(p_run_id IN NUMBER) IS
    l_reversed PLS_INTEGER := 0;
    CURSOR c_audit IS
      SELECT audit_id, object_type, object_id, field_name, old_value
        FROM xx_run_audit
       WHERE run_id = p_run_id AND operation = 'UPDATE'
       ORDER BY audit_id DESC;   -- reverse order of application
  BEGIN
    FOR r IN c_audit LOOP
      BEGIN
        IF r.object_type = 'ITEM_PRICE' THEN
          UPDATE po_lines_all
             SET unit_price = TO_NUMBER(r.old_value)
           WHERE line_id = r.object_id;
        END IF;

        INSERT INTO xx_run_audit
          (run_id, object_type, object_id, operation, field_name,
           new_value, actor)
        VALUES (p_run_id, r.object_type, r.object_id, 'ROLLBACK',
                r.field_name, r.old_value, USER);

        l_reversed := l_reversed + 1;
      EXCEPTION WHEN OTHERS THEN
        log_error(p_run_id, NULL, 'ROLLBACK_FAILED', SQLERRM);
      END;
    END LOOP;
    COMMIT;
  END rollback_run;
```

**This only works because every change was audited.** Without `xx_run_audit`,
rollback is guesswork.

## 8. Concurrent Program Wrapper

```sql
CREATE OR REPLACE PROCEDURE xx_price_list_main(
  errcode OUT VARCHAR2,
  errmsg  OUT VARCHAR2,
  x_mode              IN VARCHAR2,   -- 'VALIDATE_ONLY' / 'PROCESS' / 'ROLLBACK'
  x_supplier_from     IN VARCHAR2,
  x_supplier_to       IN VARCHAR2,
  x_category          IN VARCHAR2,
  x_effective_date    IN VARCHAR2,
  x_rollback_run_id   IN VARCHAR2
) IS
  l_run_id    NUMBER;
  l_user      VARCHAR2(64) := USER;
  l_start     TIMESTAMP := SYSTIMESTAMP;
BEGIN
  errcode := '0'; errmsg := NULL;

  IF x_mode NOT IN ('VALIDATE_ONLY','PROCESS','ROLLBACK') THEN
    errcode := '-1';
    errmsg  := 'Invalid mode: ' || x_mode;
    RETURN;
  END IF;

  -- MOAC context first: fail loudly if no access
  BEGIN
    xx_price_list_pkg.set_moac_context(101);
  EXCEPTION WHEN OTHERS THEN
    errcode := '-2'; errmsg := SQLERRM; RETURN;
  END;

  -- Run header
  INSERT INTO xx_run_header
    (program_name, mode, p_supplier_from, p_supplier_to,
     p_category, p_effective_date, requested_by)
  VALUES ('XX PRICE LIST', x_mode, x_supplier_from, x_supplier_to,
          x_category, TO_DATE(x_effective_date,'YYYY-MM-DD'), l_user)
  RETURNING run_id INTO l_run_id;
  COMMIT;

  FND_FILE.PUT_LINE(FND_FILE.OUTPUT,
    'MODE: ' || x_mode || '   RUN_ID: ' || l_run_id);
  FND_FILE.PUT_LINE(FND_FILE.OUTPUT,
    'Supplier range: ' || x_supplier_from || ' to ' || x_supplier_to);

  -- Dispatch
  IF x_mode = 'VALIDATE_ONLY' THEN
    xx_price_list_pkg.validate(l_run_id);
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT, 'VALIDATE_ONLY complete — no data changed');
  ELSIF x_mode = 'PROCESS' THEN
    xx_price_list_pkg.validate(l_run_id);     -- same validation, guaranteed
    xx_price_list_pkg.process(l_run_id);
  ELSE
    xx_price_list_pkg.rollback_run(TO_NUMBER(x_rollback_run_id));
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT, 'ROLLBACK complete for run ' || x_rollback_run_id);
  END IF;

  -- Summary for the operator log
  FOR r IN (SELECT lines_total, lines_valid, lines_error, lines_processed
              FROM xx_run_header WHERE run_id = l_run_id) LOOP
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT, 'Total: '    || r.lines_total);
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT, 'Valid: '    || r.lines_valid);
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT, 'Errors: '   || r.lines_error);
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT, 'Processed: '|| r.lines_processed);
  END LOOP;

  -- Top 10 errors in the log; full detail in the XML report
  FOR r IN (SELECT * FROM (
             SELECT line_no, error_code, error_msg FROM xx_run_error
              WHERE run_id = l_run_id ORDER BY error_id) WHERE ROWNUM <= 10) LOOP
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT,
      '  line ' || r.line_no || ': ' || r.error_code || ' — ' || r.error_msg);
  END LOOP;

  UPDATE xx_run_header
     SET completed_at = SYSTIMESTAMP, status = 'SUCCESS'
   WHERE run_id = l_run_id;
  COMMIT;

EXCEPTION WHEN OTHERS THEN
  errcode := '-3';
  errmsg  := SQLERRM;
  BEGIN
    UPDATE xx_run_header SET status = 'ERROR', completed_at = SYSTIMESTAMP
     WHERE run_id = l_run_id;
    COMMIT;
  EXCEPTION WHEN OTHERS THEN NULL; END;
  RAISE;
END;
/
```

## 9. XML Detail Report

```sql
  FUNCTION build_xml_report(p_run_id IN NUMBER) RETURN CLOB IS
    l_xml CLOB;
  BEGIN
    l_xml := '<priceListReport runId="' || p_run_id || '">';

    FOR r IN (SELECT * FROM xx_run_header WHERE run_id = p_run_id) LOOP
      l_xml := l_xml ||
        '<summary>' ||
        '<mode>'         || UPPER(esc(r.mode))              || '</mode>' ||
        '<requestedBy>'  || esc(r.requested_by)             || '</requestedBy>' ||
        '<startedAt>'    || TO_CHAR(r.started_at,'YYYY-MM-DD HH24:MI:SS') || '</startedAt>' ||
        '<linesTotal>'   || r.lines_total                   || '</linesTotal>' ||
        '<linesValid>'   || r.lines_valid                   || '</linesValid>' ||
        '<linesError>'   || r.lines_error                   || '</linesError>' ||
        '<linesProcessed>'|| r.lines_processed              || '</linesProcessed>' ||
        '</summary>';
    END LOOP;

    l_xml := l_xml || '<lineResults>';
    FOR r IN (SELECT line_no, supplier_code, item_code, unit_price,
                     effective_date, currency, status, error_count
                FROM xx_price_list_stage
               WHERE run_id = p_run_id OR status IN ('VALID','ERROR')
               ORDER BY line_no) LOOP
      l_xml := l_xml ||
        '<line no="' || r.line_no || '" status="' || r.status || '">' ||
        '<supplier>'  || esc(r.supplier_code) || '</supplier>' ||
        '<item>'      || esc(r.item_code)     || '</item>' ||
        '<price>'     || r.unit_price         || '</price>' ||
        '<currency>'  || esc(r.currency)      || '</currency>' ||
        '<effDate>'   || TO_CHAR(r.effective_date,'YYYY-MM-DD') || '</effDate>' ||
        '<errors>'    || r.error_count        || '</errors>' ||
        '</line>';
    END LOOP;
    l_xml := l_xml || '</lineResults>';

    l_xml := l_xml || '<errors>';
    FOR r IN (SELECT line_no, error_code, error_msg
                FROM xx_run_error WHERE run_id = p_run_id ORDER BY error_id) LOOP
      l_xml := l_xml ||
        '<error line="' || NVL(r.line_no,-1) || '">' ||
        '<code>' || esc(r.error_code) || '</code>' ||
        '<message>' || esc(r.error_msg) || '</message>' ||
        '</error>';
    END LOOP;
    l_xml := l_xml || '</errors></priceListReport>';

    RETURN l_xml;
  END build_xml_report;

  FUNCTION esc(p_val IN VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    RETURN REPLACE(REPLACE(REPLACE(NVL(p_val,''),'&','&amp;'),
                            '<','&lt;'),'>','&gt;');
  END;
```

**XML escaping is not optional.** A supplier name containing `&` produces
invalid XML and a broken report.

## 10. Registration Script

```sql
-- 1. Application
INSERT INTO fnd_application
  (application_id, application_short_name, application_name)
VALUES (app_id, 'XXPRICE', 'XX Price List')
WHERE app_id = 5000;

-- 2. Executable (PLSQL type)
INSERT INTO fnd_executables
  (execution_file_name, executable_type, description)
VALUES ('xx_price_list_main', 'PLSQL', 'XX Price List Processor');

-- 3. Program + parameters
DECLARE
  l_exec_id  NUMBER;
  l_prog_id  NUMBER;
BEGIN
  SELECT executable_id INTO l_exec_id
    FROM fnd_executables WHERE execution_file_name = 'xx_price_list_main';

  l_prog_id := fnd_concurrent_program_pvt.create_program(
    'XXPRICE', 'XX Price List Processor', 'XXPRICE', NULL, 'PLSQL',
    'XX Price List Processor', l_exec_id, NULL, 'ACTIVE', NULL);

  -- Parameters with token substitution and validation
  fnd_concurrent_program_pvt.add_parameter(
    l_prog_id, 'mode', 'Mode', 'VARCHAR2', 'PROCESS', 'Y', NULL);

  fnd_concurrent_program_pvt.add_parameter(
    l_prog_id, 'x_mode', 'Mode Value', 'VARCHAR2', NULL, 'Y', NULL);

  fnd_concurrent_program_pvt.add_parameter(
    l_prog_id, 'x_supplier_from', 'Supplier From', 'VARCHAR2', NULL, 'N', NULL);

  fnd_concurrent_program_pvt.add_parameter(
    l_prog_id, 'x_supplier_to', 'Supplier To', 'VARCHAR2', NULL, 'N', NULL);

  fnd_concurrent_program_pvt.add_parameter(
    l_prog_id, 'x_category', 'Category', 'VARCHAR2', NULL, 'N', NULL);

  fnd_concurrent_program_pvt.add_parameter(
    l_prog_id, 'x_effective_date', 'Effective Date (YYYY-MM-DD)',
    'VARCHAR2', NULL, 'Y', NULL);

  fnd_concurrent_program_pvt.add_parameter(
    l_prog_id, 'x_rollback_run_id', 'Rollback Run ID', 'VARCHAR2', NULL, 'N', NULL);
END;
/

-- 4. RESPONSIBILITY ASSIGNMENT — the step that gets missed
-- (operators get ORA-06550 with no privilege if this is absent)
```

## 11. Grant and Security

```sql
GRANT EXECUTE ON xx_price_list_main TO xx_price_list_role;
GRANT SELECT, INSERT, UPDATE ON xx_price_list_stage TO xx_price_list_role;
GRANT SELECT, INSERT           ON xx_run_error         TO xx_price_list_role;
GRANT SELECT, INSERT           ON xx_run_audit         TO xx_price_list_role;
```

## 12. Resume Verification Query

```sql
-- Confirm a rerun processes only what is left
SELECT status, COUNT(*) line_count
  FROM xx_price_list_stage
 GROUP BY status
 ORDER BY status;

-- Confirm every change is reversible
SELECT run_id, COUNT(*) audit_rows
  FROM xx_run_audit
 GROUP BY run_id
 ORDER BY run_id;
```

If `xx_run_audit` row count ≠ `lines_processed`, some change is untracked and
**cannot be rolled back**. That comparison is the rollback-safety check.

## 13. Timing and Log Output

```sql
-- Add elapsed time to the operator log
DECLARE
  l_start NUMBER := DBMS_UTILITY.GET_TIME;
BEGIN
  xx_price_list_pkg.validate(l_run_id);
  DBMS_OUTPUT.PUT_LINE(
    'Validate elapsed: ' || ((DBMS_UTILITY.GET_TIME - l_start)/100) || ' seconds');
END;
/
```

## 14. Health Check

```sql
SELECT
  (SELECT COUNT(*) FROM xx_run_header
    WHERE status = 'RUNNING' AND started_at < SYSTIMESTAMP - INTERVAL '2' HOUR) stale_runs,
  (SELECT COUNT(*) FROM xx_price_list_stage WHERE status = 'PENDING')        pending_lines,
  (SELECT COUNT(*) FROM xx_run_error
    WHERE run_id = (SELECT MAX(run_id) FROM xx_run_header WHERE status='ERROR')) last_err,
  (SELECT COUNT(*) FROM xx_run_header h
    WHERE h.lines_processed > 0
      AND (SELECT COUNT(*) FROM xx_run_audit a WHERE a.run_id = h.run_id) < h.lines_processed)
      AS untracked_changes,
  CASE WHEN (SELECT COUNT(*) FROM xx_run_audit a JOIN xx_run_header h
               ON a.run_id = h.run_id
             WHERE h.lines_processed > 0
               AND (SELECT COUNT(*) FROM xx_run_audit a2 WHERE a2.run_id = h.run_id)
                   < h.lines_processed) > 0
       THEN 'ROLLBACK UNSAFE — untracked changes exist' ELSE 'Healthy' END AS status
FROM dual;
```