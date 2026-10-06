# Lab 04: Supply Chain (Cycle Counting) — Code Deep Dive

## 1. ABC Classification by Annual Dollar Usage

```sql
-- Metric must be annual dollar USAGE, not item value or unit count
WITH usage AS (
  SELECT msi.segment1                                   AS item,
         SUM(mt.primary_quantity * mta.actual_cost_per_unit) AS annual_usage
    FROM mtl_system_items msi
    JOIN mtl_transaction_history mt
      ON mt.inventory_item_id = msi.inventory_item_id
     AND mt.transaction_type_id IN (1,2,3,5,6)   -- issues/receipts in-house
    JOIN mtl_transaction_account mtta
      ON mtta.transaction_id = mt.transaction_id
     AND mtta.accounting_segment_id NOT IN (101,102)
    WHERE mt.transaction_date >= ADD_MONTHS(TRUNC(SYSDATE), -12)
      AND msi.organization_id = 101
    GROUP BY msi.segment1
),
ranked AS (
  SELECT item, annual_usage,
         SUM(annual_usage) OVER (ORDER BY annual_usage DESC) AS cum_usage,
         SUM(annual_usage) OVER ()                        AS total_usage,
         ROW_NUMBER() OVER (ORDER BY annual_usage DESC)   AS rn
    FROM usage
)
SELECT item,
       ROUND(annual_usage, 2)                              AS annual_dollar_usage,
       ROUND(100 * cum_usage / total_usage, 2)             AS cum_pct,
       CASE WHEN cum_usage / total_usage <= 0.80 THEN 'A'
            WHEN cum_usage / total_usage <= 0.95 THEN 'B'
            ELSE 'C' END                                   AS abc_class
  FROM ranked
 ORDER BY annual_usage DESC;
```

## 2. Movement as a Second Dimension

```sql
-- Pure ABC misses the real risk: value x movement
WITH movement AS (
  SELECT msi.segment1 item,
         COUNT(*) txn_count
    FROM mtl_system_items msi
    JOIN mtl_transaction_history mt ON mt.inventory_item_id = msi.inventory_item_id
   WHERE mt.transaction_date >= ADD_MONTHS(TRUNC(SYSDATE), -3)
     AND msi.organization_id = 101
   GROUP BY msi.segment1
)
SELECT a.item, a.abc_class, m.txn_count,
       CASE WHEN m.txn_count > 100 THEN 'HIGH_MOVEMENT'
            WHEN m.txn_count > 20  THEN 'MEDIUM'
            ELSE 'LOW' END movement_class,
       -- Risk ranking: high value AND high movement is the top risk
       CASE WHEN a.abc_class = 'A' AND m.txn_count > 100 THEN 'CRITICAL'
            WHEN a.abc_class = 'A' THEN 'HIGH'
            WHEN m.txn_count > 100 THEN 'ELEVATED'
            ELSE 'STANDARD' END risk_rank
  FROM abc_classification a
  JOIN movement m ON m.item = a.item
 ORDER BY risk_rank, m.txn_count DESC;
```

## 3. Count Frequency from Materiality (Derivation, Not Default)

```sql
-- Solve for the max count interval that keeps expected loss under materiality
WITH params AS (
  SELECT 50000 materiality_threshold,      -- $50K acceptable unreconciled loss
         0.02  discrepancy_rate,            -- 2% of item value
         416666 monthly_usage              -- $500K/month for an A item
  FROM dual
)
SELECT p.item,
       p.monthly_usage,
       p.monthly_usage * p.discrepancy_rate AS expected_monthly_loss,
       CASE WHEN p.monthly_usage * p.discrepancy_rate > p.materiality_threshold
            THEN 'DAILY COUNTING REQUIRED — single-item review'
            ELSE ROUND(p.materiality_threshold
                     / (p.discrepancy_rate * p.monthly_usage), 1) || ' months max interval'
       END AS max_count_interval
  FROM high_value_items p, params;
```

## 4. Store ABC Classification in EBS

```sql
-- ABC attributes in the item master
UPDATE mtl_system_items_b
   SET segment1_abc = 'A'          -- or use a flexfield segment
 WHERE segment1 IN (SELECT item FROM abc_ranked WHERE class = 'A');

-- Or a custom segment on the item flexfield for clean reporting
```

## 5. Cycle Count Schedule by Subinventory

```sql
CREATE TABLE xx_cycle_count_schedule (
  schedule_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  subinv_name   VARCHAR2(30) NOT NULL,
  abc_class     VARCHAR2(1)  NOT NULL,
  frequency     VARCHAR2(15) NOT NULL,  -- WEEKLY / MONTHLY / QUARTERLY / ANNUAL
  assigned_to  VARCHAR2(64) NOT NULL,  -- rotating counter
  day_of_month  NUMBER,                 -- rotation anchor
  active_flag   CHAR(1) DEFAULT 'Y' NOT NULL,
  CONSTRAINT xx_ccs_freq_ck CHECK (frequency IN
    ('WEEKLY','MONTHLY','QUARTERLY','ANNUAL'))
);

INSERT INTO xx_cycle_count_schedule
  (subinv_name, abc_class, frequency, assigned_to, day_of_month) VALUES
  ('RAW_MATERIALS',   'A', 'MONTHLY',   'counter_a', 5),
  ('WIP',             'A', 'MONTHLY',   'counter_b', 12),
  ('FINISHED_GOODS',  'B', 'QUARTERLY', 'counter_c', 20),
  ('RETURNABLE',      'C', 'ANNUAL',    'counter_a', 28);
```

### Rotation view — who counts what, this week
```sql
SELECT sc.subinv_name, sc.abc_class, sc.frequency, sc.assigned_to
  FROM xx_cycle_count_schedule sc
 WHERE sc.active_flag = 'Y'
   AND MOD(TRUNC(SYSDATE,'MM') + sc.day_of_month - 1,
           CASE sc.frequency
             WHEN 'WEEKLY'    THEN 7
             WHEN 'MONTHLY'   THEN 30
             WHEN 'QUARTERLY' THEN 91
             ELSE 365 END) < 1
 ORDER BY sc.abc_class, sc.subinv_name;
```

## 6. Tolerance Limits by ABC Class

```sql
CREATE TABLE xx_count_tolerance (
  abc_class      VARCHAR2(1) PRIMARY KEY,
  variance_pct   NUMBER(5,2) NOT NULL,
  max_adj_value  NUMBER(14,2),           -- absolute cap regardless of %
  approver_role  VARCHAR2(64) NOT NULL,
  CONSTRAINT xx_ct_pct_ck CHECK (variance_pct BETWEEN 0 AND 100)
);

INSERT INTO xx_count_tolerance VALUES
  ('A', 0.5,  5000,  'Inventory Manager'),
  ('B', 2.0, 2000,  'Warehouse Supervisor'),
  ('C', 5.0,  500,  'Count Team Lead');
```

## 7. Cycle Count Request via EBS API

```sql
-- Trigger cycle count requests for a subinventory/ABC class
BEGIN
  FOR r IN (SELECT msi.inventory_item_id, msi.segment1
              FROM mtl_system_items msi
             WHERE msi.segment1_abc = 'A'
               AND msi.organization_id = 101) LOOP

    inv_cycle_count_api.create_cycle_count_request(
      p_api_version       => 1.0,
      p_init_msg_list     => x_msg_list,
      p_return_status     => x_status,
      p_count_quantity_source => inv_cycle_count_api.g_primary_uom_qty_src,  -- PRIMARY
      p_org_id            => 101,
      p_subinventory_code => 'RAW_MATERIALS',
      p_inventory_item_id => r.inventory_item_id,
      p_count_date        => TRUNC(SYSDATE),
      p_cycle_count_id    => x_cycle_count_id,
      p_error_number      => x_err_num,
      p_error_code        => x_err_code,
      p_error_messages    => x_err_msg);

    IF x_status = 'S' THEN
      DBMS_OUTPUT.PUT_LINE('Count req created: ' || r.segment1);
    END IF;
  END LOOP;
END;
/
```

## 8. Handheld Scanner Integration

```sql
-- Barcode scan posts count quantity via material status API
CREATE OR REPLACE PACKAGE xx_scan_capture_pkg AS
  PROCEDURE record_scan(
    p_barcode     IN VARCHAR2,
    p_subinv      IN VARCHAR2,
    p_locator     IN VARCHAR2,
    p_count_qty   IN NUMBER,
    p_counter     IN VARCHAR2
  );
END;
/

CREATE OR REPLACE PACKAGE BODY xx_scan_capture_pkg AS
  PROCEDURE record_scan(
    p_barcode   IN VARCHAR2, p_subinv IN VARCHAR2,
    p_locator   IN VARCHAR2, p_count_qty IN NUMBER, p_counter IN VARCHAR2
  ) IS
    l_item_id NUMBER;
    l_cycle_count_id NUMBER;
  BEGIN
    -- Resolve barcode to item (warehouse label format)
    SELECT inventory_item_id INTO l_item_id
      FROM mtl_secondary_labels sl, mtl_system_items msi
     WHERE sl.item_number = msi.segment1
       AND sl.label_value = p_barcode
       AND ROWNUM = 1;

    IF l_item_id IS NULL THEN
      RAISE_APPLICATION_ERROR(-20020, 'Unknown barcode: ' || p_barcode);
    END IF;

    -- Find the open count for this item
    SELECT cycle_count_id INTO l_cycle_count_id
      FROM mtl_cycle_count_supplies
     WHERE inventory_item_id = l_item_id
       AND subinventory_code = p_subinv
       AND status = 'OPEN'
       AND ROWNUM = 1;

    -- Record the scan
    UPDATE mtl_cycle_count_supplies
       set quantity   = p_count_qty,
           last_updated_by = p_counter,
           last_update_date = SYSDATE
     WHERE cycle_count_id = l_cycle_count_id;

    -- Audit
    INSERT INTO xx_scan_audit
      (barcode, item_id, subinv, locator, count_qty, counter, scanned_at)
    VALUES (p_barcode, l_item_id, p_subinv, p_locator, p_count_qty,
            p_counter, SYSTIMESTAMP);
  END record_scan;
END;
/
```

## 9. Variance Calculation and Tolerance Check

```sql
CREATE OR REPLACE VIEW xx_count_variance AS
SELECT ccs.cycle_count_id,
       ccs.inventory_item_id,
       msi.segment1                AS item,
       ccs.subinventory_code,
       ccs.quantity                AS counted_qty,
       onh.on_hand_qty             AS system_qty,
       ccs.quantity - onh.on_hand_qty AS variance_qty,
       ROUND(ABS(ccs.quantity - onh.on_hand_qty)
             / NULLIF(onh.on_hand_qty, 0) * 100, 2) AS variance_pct,
       msi.segment1_abc            AS abc_class,
       tol.variance_pct            AS tolerance_pct,
       ABS(ccs.quantity - onh.on_hand_qty) * mta.actual_cost_per_unit AS variance_value,
       CASE WHEN ABS(ccs.quantity - onh.on_hand_qty)
                 / NULLIF(onh.on_hand_qty,0) * 100 <= tol.variance_pct
            THEN 'AUTO_APPROVE' ELSE 'ESCALATE' END AS approval_path
  FROM mtl_cycle_count_supplies ccs
  JOIN mtl_system_items msi ON msi.inventory_item_id = ccs.inventory_item_id
  LEFT JOIN (SELECT inventory_item_id, subinventory_code,
                    SUM(transaction_quantity) on_hand_qty
               FROM mtl_on_hand_txn_qty
              GROUP BY inventory_item_id, subinventory_code) onh
    ON onh.inventory_item_id = ccs.inventory_item_id
   AND onh.subinventory_code = ccs.subinventory_code
  LEFT JOIN (SELECT inventory_item_id, subinventory_code,
                    MAX(actual_cost_per_unit) actual_cost_per_unit
               FROM mtl_transaction_account
              GROUP BY inventory_item_id, subinventory_code) mta
    ON mta.inventory_item_id = ccs.inventory_item_id
   AND mta.subinventory_code = ccs.subinventory_code
  LEFT JOIN xx_count_tolerance tol ON tol.abc_class = msi.segment1_abc
 WHERE ccs.status = 'CLOSED';
```

## 10. Root Cause Coding (The Step That Prevents Recurrence)

```sql
CREATE TABLE xx_count_discrepancy (
  discrepancy_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  cycle_count_id NUMBER NOT NULL,
  inventory_item_id NUMBER NOT NULL,
  subinventory     VARCHAR2(30) NOT NULL,
  variance_qty    NUMBER NOT NULL,
  variance_value  NUMBER(14,2) NOT NULL,
  root_cause_code VARCHAR2(3) NOT NULL,   -- MANDATORY
  cause_notes     VARCHAR2(400),
  action_taken    VARCHAR2(400),
  coded_by        VARCHAR2(64) NOT NULL,
  coded_at        TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  CONSTRAINT xx_cd_cause_ck CHECK (root_cause_code IN (
    'TRANS_ERR','UNREC_SHIP','DAMAGE','CYCLE_SHRINK','MISCNT','LOC_ERR','OTHER'))
);

-- Enforce: a discrepancy cannot be closed without a cause code
ALTER TABLE xx_count_discrepancy
  MODIFY (root_cause_code CONSTRAINT xx_cd_cause_nn NOT NULL);
```

### Cause Pareto — where the loss actually is
```sql
SELECT root_cause_code,
       COUNT(*)                AS discrepancies,
       SUM(variance_value)     AS total_value,
       ROUND(100 * SUM(variance_value)
             / SUM(SUM(variance_value)) OVER (), 1) AS cum_pct_value
  FROM xx_count_discrepancy
 WHERE coded_at >= ADD_MONTHS(TRUNC(SYSDATE), -3)
 GROUP BY root_cause_code
 ORDER BY total_value DESC;
```

**If the top code is `CYCLE_SHRINK` at 50%+, you have a security problem, not a
counting problem.** More counting will not fix it.

## 11. Accuracy Dashboard

```sql
-- Accuracy by ABC class, trended monthly
SELECT TO_CHAR(TRUNC(ccs.last_update_date,'MM'),'YYYY-MM') AS month,
       ccs.abc_class,
       COUNT(*) total_counted,
       SUM(CASE WHEN v.variance_pct = 0 THEN 1 ELSE 0 END) accurate_count,
       ROUND(100 * SUM(CASE WHEN v.variance_pct = 0 THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS accuracy_pct,
       ROUND(AVG(v.variance_pct), 3) AS avg_variance_pct
  FROM xx_count_variance v
  JOIN mtl_cycle_count_supplies ccs ON ccs.cycle_count_id = v.cycle_count_id
 GROUP BY TO_CHAR(TRUNC(ccs.last_update_date,'MM'),'YYYY-MM'), ccs.abc_class
 ORDER BY month DESC, ccs.abc_class;
```

## 12. Value at Risk Without Cycle Counting

```sql
-- Expected annual loss if counting frequency is unchanged
WITH item_stats AS (
  SELECT msi.segment1_abc abc_class,
         SUM(mt.primary_quantity * mt.primary_uom_code) dummy,
         COUNT(DISTINCT mt.inventory_item_id) item_count
    FROM mtl_transaction_history mt
    JOIN mtl_system_items msi ON msi.inventory_item_id = mt.inventory_item_id
   WHERE mt.transaction_date >= ADD_MONTHS(TRUNC(SYSDATE), -12)
   GROUP BY msi.segment1_abc
)
SELECT abc_class, item_count,
       CASE abc_class WHEN 'A' THEN 12 WHEN 'B' THEN 4 ELSE 1 END AS counts_per_year,
       CASE abc_class WHEN 'A' THEN 12 WHEN 'B' THEN 4 ELSE 1 END AS max_months_uncounted
  FROM item_stats;
```

## 13. The One-Query Programme Health Check

```sql
SELECT
  (SELECT COUNT(*) FROM xx_count_variance
    WHERE approval_path = 'ESCALATE' AND ROWNUM = 1)              AS has_open_escalations,
  (SELECT COUNT(*) FROM xx_count_variance
    WHERE approval_path = 'AUTO_APPROVE' AND ROWNUM = 1)           AS has_autos,
  (SELECT COUNT(*) FROM mtl_cycle_count_supplies
    WHERE status = 'OPEN' AND creation_date < TRUNC(SYSDATE) - 7)  AS stale_open_counts,
  (SELECT COUNT(*) FROM xx_count_variance
    WHERE variance_pct > 0 AND cycle_count_id NOT IN
          (SELECT cycle_count_id FROM xx_count_discrepancy))       AS uncoded_discrepancies,
  CASE WHEN (SELECT COUNT(*) FROM xx_count_variance
             WHERE variance_pct > 0 AND cycle_count_id NOT IN
                   (SELECT cycle_count_id FROM xx_count_discrepancy)) > 0
       THEN 'CAUSE CODING INCOMPLETE — programme not preventing'
       ELSE 'Healthy' END AS programme_status
FROM dual;
```