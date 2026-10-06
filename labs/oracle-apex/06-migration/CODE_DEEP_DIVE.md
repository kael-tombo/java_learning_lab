# Lab 06: APEX Migration — Code Deep Dive

## 1. Forms Inventory Query

Extract the inventory from the Forms source rather than by interview.

```sql
-- Object-level inventory from the Forms source repository
-- (USER_SOURCE / ALL_SOURCE of the compiled Forms PL/SQL)
SELECT name                                   object_name,
       type                                   object_type,
       COUNT(*)                               line_count,
       CASE WHEN REGEXP_LIKE(text, '^\s*--\s*#\s*', 'i')
            THEN 'ANNOTATION' END            annotation_kind,
       MAX(CASE WHEN REGEXP_LIKE(text, 'POST-QUERY', 'i')  THEN 1 ELSE 0 END) post_query,
       MAX(CASE WHEN REGEXP_LIKE(text, 'KEY-QUERY', 'i')   THEN 1 ELSE 0 END) key_query,
       MAX(CASE WHEN REGEXP_LIKE(text, 'WHEN-NEW-(RECORD|ITEM)', 'i')
                THEN 1 ELSE 0 END)            when_new,
       MAX(CASE WHEN REGEXP_LIKE(text, 'PRE-(INSERT|UPDATE|DELETE)', 'i')
                THEN 1 ELSE 0 END)            pre_dml,
       MAX(CASE WHEN REGEXP_LIKE(text, 'WHEN-BUTTON-PRESSED', 'i')
                THEN 1 ELSE 0 END)            when_button,
       MAX(CASE WHEN REGEXP_LIKE(text, 'LOV', 'i') THEN 1 ELSE 0 END) lov_ref,
       MAX(CASE WHEN REGEXP_LIKE(text, 'SAVEPOINT|COMMIT|ROLLBACK', 'i')
                THEN 1 ELSE 0 END)            savepoint
  FROM all_source
 WHERE owner = 'FORMS_APP'
 GROUP BY name, type
 ORDER BY post_query DESC, key_query DESC, line_count DESC;
```

### Summary of the inventory

```sql
SELECT COUNT(*) trigger_objects,
       SUM(CASE WHEN post_query = 1   THEN 1 ELSE 0 END) post_query,
       SUM(CASE WHEN key_query = 1    THEN 1 ELSE 0 END) key_query,
       SUM(CASE WHEN when_new = 1     THEN 1 ELSE 0 END) when_new,
       SUM(CASE WHEN pre_dml = 1      THEN 1 ELSE 0 END) pre_dml,
       SUM(CASE WHEN when_button = 1  THEN 1 ELSE 0 END) when_button
  FROM forms_inventory_view;
```

```
trigger objects: 340
post_query:       118   ← deletion candidates, not conversions
key_query:         47   ← deletion candidates
when_new:          71   ← Dynamic Actions / processes
pre_dml:           38   ← validations + constraints
when_button:       66   ← process conditions
```

## 2. Forms-to-APEX Mapping Table

```sql
CREATE TABLE forms_apex_map (
  forms_object      VARCHAR2(100) NOT NULL,
  forms_type        VARCHAR2(40)  NOT NULL,  -- CANVAS/BLOCK/TRIGGER/LOV/ALERT/MENU
  forms_detail      VARCHAR2(200),
  migration_class   VARCHAR2(15)  NOT NULL,  -- 1TO1/SIMPLIFIED/REDUNDANT/NEW
  apex_page_id      NUMBER,
  apex_region       VARCHAR2(60),
  apex_mechanism    VARCHAR2(40),             -- PROCESS/DYNAMIC_ACTION/VALIDATION/
                                              -- REGION_SQL/DELETED/NA
  apex_component    VARCHAR2(200),
  est_hours         NUMBER,
  dependency_notes  VARCHAR2(400),
  CONSTRAINT forms_map_cls_ck CHECK (migration_class IN
    ('1TO1','SIMPLIFIED','REDUNDANT','NEW')),
  CONSTRAINT forms_map_pk PRIMARY KEY (forms_object, forms_type)
);
```

## 3. POST-QUERY Deletion — The Region SQL Does the Work

### Forms version

```sql
-- ONTBL.POST-QUERY
SELECT i.description INTO :ontbl.item_description
  FROM items i WHERE i.item_id = :ontbl.item_id;
-- Runs ONCE PER RECORD as the user navigates the block
```

### APEX version — delete the trigger, absorb into the region SQL

```sql
-- Interactive Report source. The join replaces 1 query per record
-- with 1 query for the entire result set.
SELECT o.stock_id,
       o.item_id,
       i.description  AS item_description,   -- was a POST-QUERY trigger
       i.uom,
       o.quantity_on_hand,
       o.location_id,
       l.location_name                        -- was another POST-QUERY
  FROM ontbl o
  JOIN items    i ON i.item_id    = o.item_id
  JOIN locations l ON l.location_id = o.location_id
 WHERE (:P1_ITEM_ID IS NULL OR o.item_id = :P1_ITEM_ID)
 ORDER BY o.stock_id;
```

```
Forms: 50 records × 1 query each = 50 queries in the client session
APEX:  1 query with 2 joins       = 1 query
```

## 4. WHEN-NEW-ITEM-INSTANT → Dynamic Action

### Forms version

```sql
-- ONNEW.ITEMWHEN
IF :ontbl.item_id IS NOT NULL THEN
  SELECT price INTO :ontbl.unit_price FROM items WHERE item_id = :ontbl.item_id;
END IF;
```

### APEX version — Dynamic Action

```
Dynamic Action: "Default unit price from item"
  Event:   Item (ITEM_ID) — Condition: "is not null", Event: "Value Changed"
  True Action: Set Value on UNIT_PRICE
              Source Type:  SQL Statement
              SQL:         SELECT unit_price FROM items WHERE item_id = :P2_ITEM_ID
              Condition:   is not null    ← do not clear a manually entered price
              When:        After Refresh
```

## 5. WHEN-NEW-RECORD-INSTANCE → Page Process or Dynamic Action

### Forms version

```sql
-- ONTBL.WHEN-NEW-RECORD-INSTANCE
IF INSERTING THEN
  :ontbl.stock_id     := seq.nextval;
  :ontbl.status       := 'OPEN';
  :ontbl.created_date := SYSDATE;
END IF;
```

### APEX version — two parts

```
Part 1 — default values for a new record
  Computation: "Default new stock record"
    Point: Before Header
    Type:   PL/SQL Function Expression returning a JSON value
    Source:
      BEGIN
        RETURN JSON_OBJECT(
          'STOCK_ID'     VALUE seq_stock.NEXTVAL,
          'STATUS'       VALUE 'OPEN',
          'CREATED_DATE' VALUE TO_CHAR(SYSDATE,'YYYY-MM-DD'));
      END;

Part 2 — apply only when creating
  Processes: the process condition is "is not null" on P1_STOCK_ID
            → runs on insert only, never on update
```

**The insert/update distinction matters.** In Forms, `INSERTING` made this easy.
In APEX, the equivalent is the presence or absence of a primary key item.

```sql
-- Process condition
:P1_STOCK_ID IS NULL      -- creating
:P1_STOCK_ID IS NOT NULL  -- updating
```

## 6. PRE-INSERT / PRE-UPDATE → Validation Plus Constraint

### Forms version (level 2)

```sql
-- ONTBL.PRE-INSERT
IF :ontbl.quantity_on_hand < 0 THEN
  RAISE_APPLICATION_ERROR(-20010, 'Quantity cannot be negative');
END IF;
```

### APEX version — three layers

```plsql
-- Layer 1: database constraint (the enforcement that cannot be bypassed)
ALTER TABLE ontbl ADD CONSTRAINT ck_qty_nonneg
  CHECK (quantity_on_hand >= 0);

-- Layer 2: APEX page validation (the good message)
-- Page Validation: "Quantity cannot be negative"
--   Condition: WHEN LENGTH(:P2_QUANTITY) > 0
--              AND TO_NUMBER(:P2_QUANTITY) < 0
--   Message:   'Quantity cannot be negative. You entered: ' || :P2_QUANTITY

-- Layer 3: item LOV / default (usability)
--   QUANTITY: no LOV, but a page item default of 0 on new records
```

```
Layer 1 guarantees. Layer 2 explains. Layer 3 prevents.
All three, not one.
```

### Trigger with a business rule spanning rows

```sql
-- Forms ONTBL.PRE-UPDATE: "no backorders above the credit limit"
-- This cannot be a single-item APEX validation — it needs server-side logic

-- APEX: Page Process on Update, before the DML process
--   Server-side condition: :P1_STOCK_ID IS NOT NULL
--   Source:
DECLARE
  l_credit NUMBER;
  l_backorder NUMBER;
BEGIN
  SELECT NVL(SUM(quantity_backordered), 0) INTO l_backorder
    FROM ontbl WHERE customer_id = :P2_CUSTOMER_ID
                  AND (:P1_STOCK_ID IS NULL OR stock_id <> :P1_STOCK_ID);

  SELECT credit_limit INTO l_credit FROM customers
   WHERE customer_id = :P2_CUSTOMER_ID;

  IF l_backorder > l_credit THEN
    RAISE_APPLICATION_ERROR(-20110,
      'Backorders (' || l_backorder || ') exceed credit limit (' || l_credit || ')');
  END IF;
END;
/
```

## 7. KEY-QUERY Deletion

### Forms version

```sql
-- ONTBL.KEY-QUERY
SELECT * INTO :ontbl.stock_id, :ontbl.quantity_on_hand
  FROM ontbl
 WHERE item_id = :v_item_id
   AND location_id = :v_location_id;
```

### APEX — delete entirely

```sql
-- No KEY-QUERY equivalent. The region query IS the query.
-- If the query needs parameters, they come from page items.
SELECT stock_id, item_id, location_id, quantity_on_hand, status
  FROM ontbl
 WHERE (:P1_ITEM_ID    IS NULL OR item_id    = :P1_ITEM_ID)
   AND (:P1_LOCATION_ID IS NULL OR location_id = :P1_LOCATION_ID);
```

**Converting KEY-QUERY into a process would run the query twice** — once as the
region source and once in the process.

## 8. Forms LOV → APEX Popup LOV

### Forms version

```sql
-- LOVL_ITEM
SELECT item_id, item_code || ' - ' || description
  FROM items WHERE active_flag = 'Y';
```

### APEX — shared component

```
Shared Components → Lists of Values → LOV_ITEM
  Source: SELECT item_id, item_code, description
            FROM items WHERE active_flag = 'Y'
  Display: return = item_description
           ▾ = item_code || ' - ' || description
  Depends on: P1_CATEGORY_ID   ← filtering that Forms LOVs did natively
  Filter:     512 character limit — the "contains" search users expect
```

### LOV return values → dependent items

```
Forms: LOV return values assigned automatically to other block items

APEX:  Dynamic Action
         Event: "Selection" on the ITEM_LOV page item
         True Action: Set Value on DESCRIPTION
                      Source: JavaScript expression returning the selection value
```

```javascript
// Dynamic Action JavaScript: "Set dependent item from LOV"
var v = $v(this.triggeringElement.value);      // the LOV return value
apex.item('P2_DESCRIPTION').setValue(v);
```

## 9. Forms Alert → APEX

```sql
-- Forms: ALERT_NOCONFIRM
-- 'No stock for this item. Continue?'

-- APEX version A: blocking alert
APEX_APPLICATION.ALERT(
  p_message    => 'No stock for this item. Do you want to continue?',
  p_button     => 1);      -- 1 = OK/Cancel

-- APEX version B: inline validation instead (usually better)
--   Page Validation with a clear message, no dialog to dismiss
```

**Prefer the validation.** A modal alert interrupts the user to say something a
form field could say inline.

## 10. Forms WHEN-BUTTON-PRESSED → Process Conditions

| Forms button | APEX button | Process condition |
|--------------|--------------|-------------------|
| COMMIT | Save | — (page process) |
| CANCEL | Cancel | Branch on page transition |
| POST | Post Transfer | `:REQUEST = 'POST_TRANSFER'` |
| DELETE_ROW | Delete | `:REQUEST = 'DELETE'` |

```sql
-- Process "Post transfer"
--   Condition: :REQUEST = 'POST_TRANSFER'
--   Server-side: the posting logic, server-side, transactionally
BEGIN
  UPDATE ontbl SET status = 'POSTED' WHERE stock_id = :P1_STOCK_ID;
  UPDATE inv_txn SET posted_flag = 'Y'
   WHERE stock_id = :P1_STOCK_ID AND posted_flag = 'N';
END;
/
```

## 11. Forms Menu Stack → APEX Navigation

```
Forms menu stack:
  Inventory ▸ Transactions ▸ Stock Transfer ▸ New

APEX:
  Breadcrumbs:   Home › Stock Transfer › New
  Navigation:    Inventory › Transactions › Stock Transfer
  Page action:   Cancel (returns to the list)
  Tab:           optional, for frequently used pages only
```

**Redesign from the work, not the tree.** Users do not think in the Forms menu
hierarchy once it is gone.

## 12. Forms Savepoint → APEX Transaction Semantics

```sql
-- Forms: explicit SAVEPOINT, user controls transaction boundaries
-- APEX:   no equivalent. A page process commits at request end.
```

```sql
-- Forms "Save and Close"
-- APEX: a process that saves, then a branch to the list page
-- Forms "Cancel" (discard changes)
-- APEX: branch away without a save process — changes were never submitted
```

**Do not attempt to replicate savepoint semantics.** It is not possible in a
stateless request model, and attempts produce a worse design.

## 13. Migration Coverage Tracking

```sql
CREATE OR REPLACE VIEW migration_progress AS
SELECT migration_class,
       COUNT(*) objects,
       SUM(CASE WHEN apex_component IS NOT NULL THEN 1 ELSE 0 END) migrated,
       ROUND(100 * SUM(CASE WHEN apex_component IS NOT NULL THEN 1 ELSE 0 END)
             / COUNT(*), 1) pct_complete,
       SUM(NVL(est_hours,0)) est_hours_total
  FROM forms_apex_map
 GROUP BY migration_class
 ORDER BY migration_class;

-- Objects blocked on a dependency
SELECT forms_object, dependency_notes
  FROM forms_apex_map
 WHERE apex_component IS NULL
   AND dependency_notes IS NOT NULL
 ORDER BY forms_object;
```

## 14. Parallel-Run Comparison

```sql
CREATE TABLE parallel_run_result (
  run_date       DATE,
  screen         VARCHAR2(100),
  forms_value    VARCHAR2(400),
  apex_value     VARCHAR2(400),
  match_flag     CHAR(1),
  discrepancy    VARCHAR2(400)
);

-- Discrepancies are the cutover gate
SELECT COUNT(*) total,
       SUM(CASE WHEN match_flag='Y' THEN 1 ELSE 0 END) matched,
       SUM(CASE WHEN match_flag='N' THEN 1 ELSE 0 END) mismatched
  FROM parallel_run_result
 WHERE run_date > SYSDATE - 14;
```

```sql
-- Mismatches that survived the parallel run window
SELECT screen, COUNT(*) occurrences, MAX(discrepancy) example
  FROM parallel_run_result
 WHERE match_flag = 'N'
 GROUP BY screen
 ORDER BY occurrences DESC;
```

**The parallel run is the cutover gate, not a formality.** Mismatches that
persist across two weeks are logic differences, not timing.