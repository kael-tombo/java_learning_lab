# Lab 01: APEX Getting Started — Code Deep Dive

## 1. Schema

```sql
CREATE TABLE department (
  department_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  department_name VARCHAR2(100) NOT NULL UNIQUE
);

CREATE TABLE app_user (
  user_id       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  username      VARCHAR2(64)  NOT NULL UNIQUE,
  display_name  VARCHAR2(120) NOT NULL,
  department_id NUMBER NOT NULL REFERENCES department(department_id)
);

CREATE TABLE expense (
  expense_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  department_id NUMBER        NOT NULL REFERENCES department(department_id),
  expense_date  DATE          NOT NULL,
  category      VARCHAR2(30)  NOT NULL,
  amount        NUMBER(12,2)  NOT NULL CHECK (amount > 0),
  description   VARCHAR2(400),
  status        VARCHAR2(20)  DEFAULT 'SUBMITTED' NOT NULL,
  created_by    VARCHAR2(64),
  created_at    TIMESTAMP     DEFAULT SYSTIMESTAMP NOT NULL,
  updated_at    TIMESTAMP     DEFAULT SYSTIMESTAMP
);

CREATE INDEX ix_exp_dept_date ON expense (department_id, expense_date);
CREATE INDEX ix_exp_cat       ON expense (category);
```

**`CHECK (amount > 0)` at the database level** is the backstop. Page validation
gives a good message; the constraint guarantees the rule regardless of how the
row was written.

## 2. Session Context — Set Once at Authentication

```sql
-- On a page that runs when the user logs in (or a process on page 0)
BEGIN
  APEX_UTIL.SET_SESSION_STATE('MY_CTX_DEPARTMENT_ID', :P_DEPARTMENT_ID);
  APEX_UTIL.SET_SESSION_STATE('MY_CTX_USERNAME',    :APP_USER);
  -- Client IP for audit; behind a proxy this may be the proxy address
  APEX_UTIL.SET_SESSION_STATE('MY_CTX_CLIENT_IP',
                              OWA_SECURITY.c_get_client_ip);
END;
/
```

## 3. Fail-Closed Scoping Function

```sql
CREATE OR REPLACE FUNCTION current_department RETURN NUMBER IS
  l_dept NUMBER;
BEGIN
  l_dept := TO_NUMBER(APEX_UTIL.SESSION_STATE('MY_CTX_DEPARTMENT_ID'));
  -- NULL context means NO DATA, not ALL DATA.
  RETURN NVL(l_dept, -1);
EXCEPTION WHEN OTHERS THEN
  RETURN -1;
END;
/
```

## 4. List Page — Interactive Report Region Query

```sql
-- The scoping predicate is present from the first query.
SELECT e.expense_id,
       e.expense_date,
       e.category,
       e.amount,
       e.description,
       e.status,
       e.updated_at
  FROM expense e
 WHERE e.department_id = current_department()          -- ALWAYS
   AND (:P1_FROM_DATE IS NULL OR e.expense_date >= :P1_FROM_DATE)
   AND (:P1_TO_DATE   IS NULL OR e.expense_date <= :P1_TO_DATE)
   AND (:P1_CATEGORY  IS NULL OR e.category      = :P1_CATEGORY)
 ORDER BY e.expense_date DESC, e.expense_id DESC;
```

**Use `NVL(current_department(), -1)` if the function could ever return NULL.**
The function above already handles it.

## 5. Summary Region — Also Scoped (The Common Omission)

```sql
SELECT e.category,
       COUNT(*)          expense_count,
       ROUND(SUM(e.amount), 2) total_amount,
       ROUND(AVG(e.amount), 2) avg_amount,
       ROUND(MAX(e.amount), 2) max_amount
  FROM expense e
 WHERE e.department_id = current_department()          -- MUST be here
   AND (:P1_FROM_DATE IS NULL OR e.expense_date >= :P1_FROM_DATE)
   AND (:P1_TO_DATE   IS NULL OR e.expense_date <= :P1_TO_DATE)
 GROUP BY e.category
 ORDER BY total_amount DESC;
```

```sql
-- Month-level summary, also scoped
SELECT TO_CHAR(e.expense_date, 'YYYY-MM') month,
       COUNT(*)                expense_count,
       ROUND(SUM(e.amount), 2) total_amount
  FROM expense e
 WHERE e.department_id = current_department()
   AND e.expense_date >= ADD_MONTHS(TRUNC(SYSDATE,'MM'), -12)
 GROUP BY TO_CHAR(e.expense_date, 'YYYY-MM')
 ORDER BY month DESC;
```

## 6. Form Page — Read Query (Scoped)

```sql
-- Form page 2, when not creating
SELECT expense_id, expense_date, category, amount, description, status
  FROM expense
 WHERE expense_id = :P1_EXPENSE_ID
   AND department_id = current_department();    -- prevents editing another's row
```

**The scoping predicate on the form query is what stops IDOR.** Without it, a user
who changes `P1_EXPENSE_ID` in session state could load any expense. Session
state is not user-editable from the browser, but the query must still not depend
on that alone.

## 7. Save Process — Handles Create and Update

```sql
-- Page process: "Save Expense"
-- When:     Create or Update   (standard Form condition)
-- Server-side condition:
IF :P1_EXPENSE_ID IS NULL THEN
  INSERT INTO expense
    (department_id, expense_date, category, amount, description, status, created_by)
  VALUES
    (current_department(), TO_DATE(:P2_EXPENSE_DATE,'YYYY-MM-DD'),
     :P2_CATEGORY, TO_NUMBER(:P2_AMOUNT), :P2_DESCRIPTION,
     'SUBMITTED', APEX_UTIL.SESSION_STATE('MY_CTX_USERNAME'));
ELSE
  UPDATE expense
     SET expense_date = TO_DATE(:P2_EXPENSE_DATE,'YYYY-MM-DD'),
         category     = :P2_CATEGORY,
         amount       = TO_NUMBER(:P2_AMOUNT),
         description  = :P2_DESCRIPTION,
         updated_at   = SYSTIMESTAMP
   WHERE expense_id   = :P1_EXPENSE_ID
     AND department_id = current_department();   -- scoped UPDATE
END IF;
```

**The `department_id` predicate on the UPDATE matters.** An unscoped `UPDATE ... 
WHERE expense_id = :P1` will happily update another department's row.

## 8. Validation Rules

```sql
-- Page validation: "Amount must be positive"
-- Condition (server-side, when displayed and not null):
WHEN LENGTH(:P2_AMOUNT) > 0 AND TO_NUMBER(:P2_AMOUNT) <= 0
-- Error message:
'Amount must be greater than zero. You entered: ' || :P2_AMOUNT
```

```sql
-- "Date cannot be in the future"
WHEN :P2_EXPENSE_DATE IS NOT NULL
 AND TO_DATE(:P2_EXPENSE_DATE,'YYYY-MM-DD') > TRUNC(SYSDATE)
-- Message:
'Expense date cannot be in the future. You entered: ' || :P2_EXPENSE_DATE
```

```sql
-- "Category is required"
WHEN :P2_CATEGORY IS NULL
-- Message:
'Select a category. See the category list for the available options.'
```

| Rule | Message quality |
|------|-----------------|
| Bad: "Invalid amount" | Good: "Amount must be greater than zero. You entered: -50" |

## 9. Delete with Confirmation and Audit

```sql
CREATE TABLE expense_delete_audit (
  audit_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  expense_id  NUMBER        NOT NULL,
  department_id NUMBER      NOT NULL,
  deleted_by  VARCHAR2(64) NOT NULL,
  deleted_at  TIMESTAMP    DEFAULT SYSTIMESTAMP NOT NULL,
  expense_snapshot CLOB     NOT NULL,   -- the row as it was, for the record
  reason      VARCHAR2(400)
);
```

```sql
-- Page process: "Delete Expense"
-- Confirmation message:
'Delete this expense permanently? This cannot be undone.'

IF :P1_CONFIRM_DELETE = 'Y' THEN
  INSERT INTO expense_delete_audit
    (expense_id, department_id, deleted_by, expense_snapshot, reason)
  SELECT e.expense_id, e.department_id,
         APEX_UTIL.SESSION_STATE('MY_CTX_USERNAME'),
         TO_CLOB(TO_CHAR(e.expense_date)||'|'||e.category||'|'||e.amount
                 ||'|'||e.description||'|'||e.status),
         :P2_DELETE_REASON
    FROM expense e
   WHERE e.expense_id   = :P1_EXPENSE_ID
     AND e.department_id = current_department();

  DELETE FROM expense
   WHERE expense_id   = :P1_EXPENSE_ID
     AND department_id = current_department();

  APEX_UTIL.SET_SESSION_STATE('MY_CTX_DEPARTMENT_ID',
                              APEX_UTIL.SESSION_STATE('MY_CTX_DEPARTMENT_ID'));
END IF;
```

The snapshot column means the audit row is useful even though the source row is
gone.

## 10. Navigation — Setting Session State

```sql
-- Process on the Interactive Report: "Edit"
-- Get row values → set session state → branch
BEGIN
  APEX_UTIL.SET_SESSION_STATE('P1_EXPENSE_ID', :EXPENSE_ID);
END;
/
-- Then branch to Page 2 with "Page is: is not null on page load"
```

```sql
-- On page 2, when creating, the "New" button sets:
BEGIN
  APEX_UTIL.SET_SESSION_STATE('P1_EXPENSE_ID', NULL);  -- null ⇒ create mode
  APEX_UTIL.SET_SESSION_STATE('P1_NEW_RECORD', 'Y');
END;
/
```

## 11. Cascading Filter — Category List

```sql
-- Shared component: LOV for P1_CATEGORY
SELECT DISTINCT category FROM expense
 WHERE department_id = current_department()
 ORDER BY 1;
```

```sql
-- Populate P1_TO_DATE default to today, P1_FROM_DATE to 30 days ago
BEGIN
  :P1_TO_DATE   := TO_CHAR(TRUNC(SYSDATE), 'YYYY-MM-DD');
  :P1_FROM_DATE := TO_CHAR(TRUNC(SYSDATE) - 30, 'YYYY-MM-DD');
END;
/
```

## 12. Row Security Verification Query

```sql
-- Run this as each user; every result must be empty
SELECT 'DETAIL LEAK' finding, expense_id, department_id
  FROM expense
 WHERE expense_id = :OTHER_USERS_EXPENSE_ID
   AND department_id <> current_department();

SELECT 'SUMMARY LEAK' finding, category, SUM(amount) total
  FROM expense
 GROUP BY category
HAVING SUM(amount) <> (
        SELECT SUM(amount) FROM expense
         WHERE department_id = current_department());
```

## 13. Application Export — The Restore Path

```bash
# Export from SQL Command (or the app UI) with Export / Splitter
BEGIN APEX_APPLICATION.PAGE_EXPORT(           -- in newer APEX
  p_application_id => 100,
  p_schema         => 'MY_SCHEMA',
  p_application    => 'MY_WORKSPACE',
  p_format         => 'YAML',                  -- or 'SQL'
  p_file_name      => 'expense_app',
  p_export_package_id => NULL); END;
/
```

Keep in source control:

```
expense_app/
  ├── app.yaml              ← pages, regions, items, processes
  ├── ddl/01_schema.sql
  ├── ddl/02_indexes.sql
  ├── seed/01_test_data.sql
  └── README.md
```

## 14. Load Test Preparation

```sql
-- 50,000 rows across 12 departments for realistic list-page timing
INSERT INTO expense (department_id, expense_date, category, amount,
                     description, status, created_by)
SELECT MOD(LEVEL, 12) + 1,
       SYSDATE - MOD(LEVEL, 720),
       CASE MOD(LEVEL, 5)
         WHEN 0 THEN 'Travel'  WHEN 1 THEN 'Supplies' WHEN 2 THEN 'Software'
         WHEN 3 THEN 'Training' ELSE 'Other' END,
       ROUND(DBMS_RANDOM.VALUE(10, 5000), 2),
       'Generated expense ' || LEVEL, 'APPROVED', 'SYSTEM'
  FROM dual CONNECT BY LEVEL <= 50000;
COMMIT;
```

## 15. Component Health Check

```sql
SELECT
  (SELECT COUNT(*) FROM expense WHERE department_id IS NULL) unscoped_rows,
  (SELECT COUNT(*) FROM expense WHERE amount <= 0)             invalid_amounts,
  (SELECT COUNT(*) FROM expense_delete_audit
     WHERE deleted_at > TRUNC(SYSDATE) - 1)                   deletes_24h,
  CASE WHEN (SELECT COUNT(*) FROM expense WHERE department_id IS NULL) = 0
       THEN 'DATA OK' ELSE 'SCHEMA PROBLEM' END               data_status
FROM dual;
```

```sql
-- Confirm no region query is missing the scoping predicate.
-- Review every region source in the app export and confirm
-- current_department() appears in each one that touches expense.
```