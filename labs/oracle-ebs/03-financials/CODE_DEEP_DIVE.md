# Lab 03: Financials — Code Deep Dive

## 1. Hold Taxonomy — Measure Before Changing Anything

```sql
SELECT h.hold_type,
       hr.hold_reason,
       COUNT(DISTINCT h.invoice_id)                AS invoice_count,
       ROUND(SUM(i.invoice_amount), 2)             AS held_value,
       ROUND(AVG(SYSDATE - i.invoice_date), 1)     AS avg_days_held
  FROM ap_holds_all h
  JOIN ap_hold_codes hr
    ON hr.hold_type = h.hold_type
   AND hr.hold_code = h.hold_code
  JOIN ap_invoices_all i
    ON i.invoice_id = h.invoice_id
 WHERE h.release_flag = 'N'          -- still held
   AND i.org_id = 101
 GROUP BY h.hold_type, hr.hold_reason
 ORDER BY held_value DESC;
```

### Hold rate baseline (record this BEFORE any change)
```sql
SELECT ROUND(100 * COUNT(DISTINCT CASE WHEN h.invoice_id IS NOT NULL
                                       THEN i.invoice_id END)
             / COUNT(DISTINCT i.invoice_id), 2) AS hold_rate_pct,
       COUNT(DISTINCT i.invoice_id)             AS total_invoices
  FROM ap_invoices_all i
  LEFT JOIN ap_holds_all h ON h.invoice_id = i.invoice_id
                           AND h.release_flag = 'N'
 WHERE i.invoice_date >= ADD_MONTHS(TRUNC(SYSDATE), -3);
```

## 2. Ordered vs Received — Proving the Root Cause

```sql
-- Invoiced quantity vs ORDERED vs RECEIVED on held invoices
SELECT i.invoice_number,
       SUM(id.quantity_invoiced)                          AS invoiced_qty,
       (SELECT SUM(quantity) FROM po_lines_all pl
         WHERE pl.po_line_id = id.po_line_id)             AS ordered_qty,
       (SELECT SUM(r.quantity_received) FROM ap_receipt_lines_all r
         WHERE r.po_line_id = id.po_line_id)              AS received_qty
  FROM ap_invoices_all i
  JOIN ap_invoice_distributions_all id ON id.invoice_id = i.invoice_id
 WHERE i.invoice_id IN (SELECT invoice_id FROM ap_holds_all WHERE release_flag='N')
 GROUP BY i.invoice_number
HAVING SUM(id.quantity_invoiced) <>
       (SELECT SUM(quantity) FROM po_lines_all pl WHERE pl.po_line_id = id.po_line_id)
 LIMIT 20;
```

**Interpretation**: invoiced equals *received* but differs from *ordered*.
The rule is comparing the wrong pair.

## 3. Variance Distribution — Deriving Tolerances From Data

```sql
-- Price variance distribution on held invoices
SELECT ROUND(ABS(((id.quantity_invoiced * id.unit_price) - r.unit_price)
                 / NULLIF(r.unit_price, 0)) * 100, 2) AS abs_price_var_pct,
       COUNT(*) AS invoice_count,
       SUM(CASE WHEN ABS(((id.quantity_invoiced * id.unit_price) - r.unit_price)
                        / NULLIF(r.unit_price,0)) <= 0.05
                THEN 1 ELSE 0 END) AS within_5pct
  FROM ap_invoice_distributions_all id
  JOIN ap_receipt_lines_all r ON r.receipt_line_id = id.receipt_line_id
 GROUP BY ROUND(ABS(((id.quantity_invoiced * id.unit_price) - r.unit_price)
                    / NULLIF(r.unit_price,0)) * 100, 2)
 ORDER BY abs_price_var_pct;
```

### Cumulative view — where does the noise end?
```sql
SELECT variance_bucket, invoice_count,
       ROUND(100 * SUM(invoice_count) OVER (ORDER BY variance_bucket)
             / SUM(invoice_count) OVER (), 2) AS cumulative_pct
  FROM (
    SELECT FLOOR(ABS(((id.quantity_invoiced * id.unit_price) - r.unit_price)
                     / NULLIF(r.unit_price,0)) * 100) AS variance_bucket,
           COUNT(*) AS invoice_count
      FROM ap_invoice_distributions_all id
      JOIN ap_receipt_lines_all r ON r.receipt_line_id = id.receipt_line_id
     GROUP BY FLOOR(ABS(((id.quantity_invoiced * id.unit_price) - r.unit_price)
                        / NULLIF(r.unit_price,0)) * 100)
  ) ORDER BY variance_bucket;
```

**Read the cumulative column**: where it crosses ~95–98%, that is where noise
ends. Set the tolerance just above it.

## 4. Quantity Variance Tolerance Check
```sql
SELECT FLOOR(ABS(SUM(id.quantity_invoiced)
                 - (SELECT SUM(r.quantity_received)
                      FROM ap_receipt_lines_all r
                     WHERE r.po_line_id = id.po_line_id))
               / NULLIF(SUM(id.quantity_invoiced),0) * 100) AS qty_var_pct,
       COUNT(*) AS line_count
  FROM ap_invoice_distributions_all id
 GROUP BY id.po_line_id
HAVING SUM(id.quantity_invoiced) <>
       (SELECT SUM(r.quantity_received) FROM ap_receipt_lines_all r
         WHERE r.po_line_id = id.po_line_id)
 ORDER BY qty_var_pct;
```

## 5. Escape Rate — The Control-Strength Metric

```sql
-- Real discrepancies that PASSED validation (should stay near zero)
SELECT COUNT(*) AS escaped_discrepancies,
       ROUND(SUM(i.invoice_amount), 2) AS escaped_value
  FROM ap_invoices_all i
  JOIN ap_invoice_distributions_all id ON id.invoice_id = i.invoice_id
  JOIN ap_receipt_lines_all r ON r.receipt_line_id = id.receipt_line_id
 WHERE i.validation_status = 'V'                    -- passed
   AND id.quantity_invoiced > r.quantity_received    -- over-invoiced
   AND r.po_line_id IS NOT NULL;
```

Run this **before and after**. If escape rate rises while hold rate falls, the
control has weakened.

## 6. Batch Hold Release with Reason Codes

```sql
CREATE OR REPLACE PACKAGE xx_ap_hold_release_pkg AS
  PROCEDURE release_candidates(
    p_tolerance_pct IN NUMBER DEFAULT 5,
    p_release_date  IN DATE   DEFAULT SYSDATE
  );
END xx_ap_hold_release_pkg;
/

CREATE OR REPLACE PACKAGE BODY xx_ap_hold_release_pkg AS

  PROCEDURE release_candidates(
    p_tolerance_pct IN NUMBER DEFAULT 5,
    p_release_date  IN DATE   DEFAULT SYSDATE
  ) IS
    CURSOR c_candidates IS
      SELECT DISTINCT h.invoice_id, h.hold_type, h.hold_code, i.invoice_amount
        FROM ap_holds_all h
        JOIN ap_invoices_all i ON i.invoice_id = h.invoice_id
        JOIN ap_invoice_distributions_all id ON id.invoice_id = i.invoice_id
        JOIN ap_receipt_lines_all r ON r.receipt_line_id = id.receipt_line_id
       WHERE h.release_flag = 'N'
         AND h.hold_type IN ('PRICE', 'QTY')
         AND ABS(((id.quantity_invoiced * id.unit_price) - r.unit_price)
                 / NULLIF(r.unit_price, 0)) * 100 <= p_tolerance_pct
         AND id.quantity_invoiced <= r.quantity_received;
    l_count PLS_INTEGER := 0;
  BEGIN
    FOR r_rec IN c_candidates LOOP
      BEGIN
        ap_holds_pkg.release_hold(
          hold_type        => r_rec.hold_type,
          hold_code        => r_rec.hold_code,
          hold_id          => NULL,
          invoice_id       => r_rec.invoice_id,
          release_on_hold  => 'Y',
          release_reason   => 'AUTO_TOLERANCE_' || TO_CHAR(p_tolerance_pct),
          hold_release_date=> p_release_date,
          released_by      => -1,           -- SYSTEM
          release_comment  => 'Auto-released: within derived tolerance'
        );
        l_count := l_count + 1;
      EXCEPTION WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('FAILED invoice ' || r_rec.invoice_id || ': ' || SQLERRM);
      END;
    END LOOP;
    DBMS_OUTPUT.PUT_LINE('Released ' || l_count || ' holds');
  END release_candidates;

END xx_ap_hold_release_pkg;
/
```

**Key point**: `release_reason` is mandatory and descriptive. There is no path
through this package that releases without a reason.

## 7. Audit Trail for Releases

```sql
CREATE TABLE xx_ap_hold_release_audit (
  audit_id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  invoice_id    NUMBER NOT NULL,
  hold_type     VARCHAR2(25),
  hold_code     VARCHAR2(25),
  release_reason VARCHAR2(100) NOT NULL,   -- NOT NULL: enforced
  released_by   NUMBER NOT NULL,
  release_date  DATE NOT NULL,
  tolerance_applied NUMBER(5,2)
);
```

### Enforce the reason code at the database level
```sql
-- Attempt to release without a reason must fail
INSERT INTO xx_ap_hold_release_audit
  (invoice_id, hold_type, hold_code, release_reason, released_by, release_date)
VALUES (999, 'PRICE', 'PRICE_VAR', NULL, -1, SYSDATE);
-- ORA-01400: cannot insert NULL into "RELEASE_REASON"
```

## 8. Hold Aging Report for Suppliers

```sql
SELECT r.vendor_name,
       i.invoice_number,
       i.invoice_date,
       hr.hold_reason,
       ROUND(SYSDATE - i.invoice_date) AS days_held,
       i.invoice_amount
  FROM ap_holds_all h
  JOIN ap_hold_codes hr ON hr.hold_type = h.hold_type AND hr.hold_code = h.hold_code
  JOIN ap_invoices_all i ON i.invoice_id = h.invoice_id
  JOIN ap_suppliers_all r ON r.vendor_id = i.vendor_id
 WHERE h.release_flag = 'N'
 ORDER BY days_held DESC;
```

## 9. Diagnosis Summary Query

```sql
SELECT
  (SELECT ROUND(100 * COUNT(DISTINCT h.invoice_id)
                / NULLIF(COUNT(DISTINCT i.invoice_id), 0), 2)
     FROM ap_invoices_all i
     LEFT JOIN ap_holds_all h ON h.invoice_id = i.invoice_id AND h.release_flag='N'
    WHERE i.invoice_date >= ADD_MONTHS(TRUNC(SYSDATE), -3))          AS hold_rate_pct,
  (SELECT COUNT(*) FROM ap_holds_all WHERE release_flag='N')          AS open_holds,
  (SELECT COUNT(*) FROM ap_invoices_all
    WHERE validation_status='V' AND invoice_date >= ADD_MONTHS(TRUNC(SYSDATE),-3)) AS validated,
  CASE WHEN (SELECT COUNT(*) FROM ap_holds_all
              WHERE release_flag='N' AND hold_type='PRICE') >
            (SELECT COUNT(*) FROM ap_holds_all
              WHERE release_flag='N' AND hold_type='QTY')
       THEN 'Price tolerance issue' ELSE 'Quantity matching issue' END AS primary_cause
FROM dual;
```