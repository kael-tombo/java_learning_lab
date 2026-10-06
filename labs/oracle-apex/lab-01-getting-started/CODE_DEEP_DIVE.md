# Lab 01: APEX Getting Started — Code Deep Dive

Annotated SQL and PL/SQL for the expense application. Every block is the pattern,
not just the syntax.

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
  amount        NUMBER(12,2)  NOT NULL CHECK (amount > 0),  -- backstop
  description   VARCHAR2(400),
  status        VARCHAR2(20)  DEFAULT 'SUBMITTED' NOT NULL,
  created_by    VARCHAR2(64),
  created_at    TIMESTAMP     DEFAULT SYSTIMESTAMP NOT NULL,
  updated_at    TIMESTAMP
);
```

**Identity columns, not sequences.** `GENERATED ALWAYS AS IDENTITY` means the
database assigns the key and no code can forget to. The `CHECK (amount > 0)` is
the authoritative rule — page validation only produces a good message.

```sql
-- Composite index covering both the filter and the sort.
-- Column order matters: equality predicate first, then the sort column.
CREATE INDEX ix_exp_dept_date ON expense (department_id, expense_date);
CREATE INDEX ix_exp_cat       ON expense (category);

-- Non-sargable month predicate:
--   WHERE TO_CHAR(expense_date,'YYYY-MM') = :p_month
-- Sargable equivalent — use this:
CREATE INDEX ix_exp_date ON expense (expense_date DESC);
```

## 2. Session Context — Set Once at Authentication

```plsql
-- After-Login computation, or a process on page 0.
-- Runs once per session, not per page.
DECLARE
  l_dept NUMBER;
BEGIN
  SELECT department_id INTO l_dept
    FROM app_user WHERE username = :APP_USER;

  APEX_UTIL.SET_SESSION_STATE('MY_CTX_DEPARTMENT_ID', l_dept);
  APEX_UTIL.SET_SESSION_STATE('MY_CTX_USERNAME',    :APP_USER);
  APEX_UTIL.SET_SESSION_STATE('MY_CTX_CLIENT_IP',
                              OWA_SECURITY.c_get_client_ip);  -- proxy address, if any
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    -- Fail closed: an authenticated user with no department gets -1,
    -- which matches no rows. Never leave the context unset.
    APEX_UTIL.SET_SESSION_STATE('MY_CTX_DEPARTMENT_ID', -1);
END;
/
```

## 3. The Fail-Closed Scoping Function

```plsql
CREATE OR REPLACE FUNCTION current_department RETURN NUMBER IS
BEGIN
  RETURN NVL(TO_NUMBER(APEX_UTIL.SESSION_STATE('MY_CTX_DEPARTMENT_ID')), -1);
EXCEPTION WHEN OTHERS THEN
  -- Any failure — bad session, cleared context, conversion error —
  -- resolves to "no department", never "all departments".
  RETURN -1;
END;
/
```

**Why `-1` and not NULL.** `WHERE department_id = NULL` happens to match no rows,
which is safe by accident and unsafe by intent. `NVL(context, department_id)` with
a NULL context matches every row, which is the catastrophe. The `-1` sentinel makes
the safe behaviour explicit and survives someone later changing the query shape.

## 4. Interactive Report Source Query

```sql
SELECT e.expense_id,
       e.expense_date,
       d.department_name,
       e.category,
       e.amount,
       e.status,
       CASE e.status
         WHEN 'APPROVED' THEN 'fa-good'
         WHEN 'REJECTED' THEN 'fa-bad'
         ELSE 'fa-warning'
       END AS status_css
  FROM expense e
  JOIN department d ON d.department_id = e.department_id
 WHERE e.department_id = current_department()          -- 1. scoping, never omit
   AND e.expense_date >= NVL(:P1_DATE_FROM, DATE '1900-01-01')   -- 2. sargable
   AND e.expense_date <  NVL(:P1_DATE_TO,   DATE '2999-12-31') + 1
   AND (:P1_CATEGORY IS NULL OR e.category = :P1_CATEGORY)        -- 3. optional
 ORDER BY e.expense_date DESC, e.expense_id DESC    -- 4. deterministic, index-friendly
```

**Annotation**
1. The scoping predicate is first and unconditional. It is the predicate you must
   never forget, so it is the one that is hardest to make optional.
2. Date items use `NVL` **on the bind**. The indexed column is untouched, so the
   index still works. `NVL(e.expense_date, ...)` would destroy it.
3. An optional filter written as an `OR` on a bind is fine; the optimizer can
   still use the index for the date range, which carries the selectivity.
4. A trailing tiebreaker column makes pagination deterministic. Without it, rows
   with identical dates can appear on two pages or on neither.

## 5. Summary Regions — Scoped Identically

```sql
-- By category
SELECT e.category AS label, SUM(e.amount) AS value, COUNT(*) AS row_count
  FROM expense e
 WHERE e.department_id = current_department()
   AND e.expense_date >= NVL(:P1_DATE_FROM, DATE '1900-01-01')
 GROUP BY e.category
 ORDER BY value DESC;
```

**This is where prototypes leak.** Drop the `department_id` predicate and the
chart still renders — it renders *other departments' totals*, inferred from
duplicate labels with identical sums. The predicate is not a detail-region
concern; it is a requirement of every region that reads `expense`.

## 6. Form Page — Scoped Read Query

```sql
SELECT e.expense_id, e.department_id, e.expense_date, e.category,
       e.amount, e.description, e.status
  FROM expense e
 WHERE e.expense_id = :P2_EXPENSE_ID
   AND e.department_id = current_department();   -- 0 rows for another department
```

```sql
-- Before Process: move the session value into the page item, then clear it.
BEGIN
  IF :P2_EXPENSE_ID IS NULL THEN
    :P2_EXPENSE_ID := TO_NUMBER(APEX_UTIL.SESSION_STATE('MY_CTX_EXPENSE_ID'));
  END IF;
END;
/
```

**The scoped read query returning zero rows is the first line of defence.** The
scoped `UPDATE` below is the second — a page item populated from a zero-row query
is blank, so an attacker must forge both the item and the submission.

## 7. Save Process — One Process, Both Modes

```plsql
-- Page Process
--   Name:     Save Expense
--   Type:     PL/SQL Code
--   When:     Submit and Process
--   Language: PL/SQL
--   PL/SQL:
DECLARE
  l_dept NUMBER := current_department();
BEGIN
  IF :P2_EXPENSE_ID IS NULL THEN
    INSERT INTO expense (department_id, expense_date, category,
                         amount, description, status, created_by, created_at)
    VALUES (l_dept, :P2_EXPENSE_DATE, :P2_CATEGORY,
            :P2_AMOUNT, :P2_DESCRIPTION, 'SUBMITTED', :APP_USER, SYSTIMESTAMP)
    RETURNING expense_id INTO :P2_EXPENSE_ID;      -- so the page can re-read
  ELSE
    -- The WHERE clause carries the scoping predicate: an UPDATE against
    -- another department's row affects ZERO rows. That is the enforcement.
    UPDATE expense
       SET expense_date = :P2_EXPENSE_DATE,
           category     = :P2_CATEGORY,
           amount       = :P2_AMOUNT,
           description  = :P2_DESCRIPTION,
           updated_at   = SYSTIMESTAMP
     WHERE expense_id = :P2_EXPENSE_ID
       AND department_id = l_dept;
    IF SQL%ROWCOUNT = 0 THEN
      RAISE_APPLICATION_ERROR(-20001,
        'Expense '||:P2_EXPENSE_ID||' does not exist in your department.');
    END IF;
  END IF;
END;
/
```

**`SQL%ROWCOUNT = 0` is the authorisation check.** Without it, a cross-department
attempt reports success while silently doing nothing — a confusing failure that
users report as "the save button doesn't work".

## 8. Validations

```plsql
-- Validation 1: amount, PL/SQL Function Returning Boolean, When = Submit
--               and Process = Before Processing
DECLARE
BEGIN
  IF :P2_AMOUNT IS NULL THEN
    :P2_AMOUNT_ERROR := 'Amount is required. Entered: (blank)';
    RETURN FALSE;
  ELSIF :P2_AMOUNT <= 0 THEN
    :P2_AMOUNT_ERROR := 'Amount must be greater than 0. Entered: '||:P2_AMOUNT;
    RETURN FALSE;
  END IF;
  RETURN TRUE;
END;
```

```plsql
-- Validation 2: description required above a threshold
DECLARE
BEGIN
  IF :P2_AMOUNT > 500 AND :P2_DESCRIPTION IS NULL THEN
    :P2_DESCRIPTION_ERROR :=
      'A description is required for expenses over 500. Amount entered: '||:P2_AMOUNT;
    RETURN FALSE;
  END IF;
  RETURN TRUE;
END;
```

```plsql
-- Validation 3: category from a fixed set
DECLARE
  l_allowed VARCHAR2(30) := 'TRAVEL,SUPPLIES,SOFTWARE,TRAINING,OTHER';
BEGIN
  IF INSTR(','||l_allowed||',', ','||:P2_CATEGORY||',') = 0 THEN
    :P2_CATEGORY_ERROR :=
      'Category must be one of '||REPLACE(l_allowed,',',', ')||'. Entered: '||:P2_CATEGORY;
    RETURN FALSE;
  END IF;
  RETURN TRUE;
END;
```

Every message names the field and the value entered. The last one echoes the
allowed set so the user can fix it without guessing.

## 9. Delete with Audit Snapshot

```plsql
-- Page Process
--   Type:  Execute Code (PL/SQL)
--   When:  Submit and Process
--   Confirmation dialog: "Delete expense :P2_EXPENSE_ID? This cannot be undone."
DECLARE
  l_id NUMBER := :P2_EXPENSE_ID;
BEGIN
  -- 1. Snapshot BEFORE the delete — afterwards the row is gone.
  INSERT INTO expense_audit (expense_id, department_id, expense_date, category,
                             amount, description, status, deleted_by, deleted_at)
  SELECT expense_id, department_id, expense_date, category,
         amount, description, status, :APP_USER, SYSTIMESTAMP
    FROM expense
   WHERE expense_id = l_id
     AND department_id = current_department();

  IF SQL%ROWCOUNT = 0 THEN
    RAISE_APPLICATION_ERROR(-20002, 'Expense '||l_id||' was not deleted — not in your department.');
  END IF;

  -- 2. Delete, still scoped.
  DELETE FROM expense
   WHERE expense_id = l_id
     AND department_id = current_department();
END;
/
```

Both statements share the transaction, so either both happen or neither does. The
audit row is self-sufficient — it holds the amount, category, and description, so
reversing the action later needs no join to a table that no longer has the row.

## 10. Health Check Query — Put It in a Page

```sql
-- Page 0, administrator only. Answers "is any region leaking?"
SELECT region_name,
       CASE WHEN upper(query_text) LIKE '%CURRENT_DEPARTMENT%'
            THEN 'scoped' ELSE 'UNSCOPED — REVIEW' END AS status,
       SUBSTR(query_text, 1, 60) AS query_head
  FROM apex_application_pages p
  JOIN apex_application_page_columns c ON c.page_id = p.page_id
 WHERE p.application_id = :APP_ID
   AND lower(query_text) LIKE '%from expense%'
 ORDER BY status DESC, region_name;
```

This is the control that scales: once there are 40 regions and 200 queries, no
human reviews them all before every release. A query that searches for
`FROM expense` and does not find `current_department()` is the finding.
