# Lab 07: Reporting (BI Publisher) — Code Deep Dive

## 1. Aging Calculation — Due Date Basis, Mutually Exclusive Buckets

```sql
-- Level 1: Summary by supplier category
SELECT NVL(sc.category_name, 'UNMAPPED')        AS category,
       ROUND(SUM(CASE WHEN :p_as_of_date - ps.due_date <= 0
                      THEN ps.amount_base_usd END), 2) AS current_amt,
       ROUND(SUM(CASE WHEN :p_as_of_date - ps.due_date BETWEEN  1 AND 30
                      THEN ps.amount_base_usd END), 2) AS bucket_0_30,
       ROUND(SUM(CASE WHEN :p_as_of_date - ps.due_date BETWEEN 31 AND 60
                      THEN ps.amount_base_usd END), 2) AS bucket_31_60,
       ROUND(SUM(CASE WHEN :p_as_of_date - ps.due_date BETWEEN 61 AND 90
                      THEN ps.amount_base_usd END), 2) AS bucket_61_90,
       ROUND(SUM(CASE WHEN :p_as_of_date - ps.due_date >  90
                      THEN ps.amount_base_usd END), 2) AS bucket_90_plus,
       ROUND(SUM(ps.amount_base_usd), 2)             AS total_amt,
       COUNT(DISTINCT ps.vendor_id)                  AS supplier_count
  FROM xx_ap_aging_base ps
  LEFT JOIN xx_supplier_category sc ON sc.vendor_id = ps.vendor_id
 WHERE (:p_category IS NULL OR ps.category = :p_category)
 GROUP BY NVL(sc.category_name, 'UNMAPPED')
 ORDER BY total_amt DESC;
```

## 2. The Aging Base View — Currency Conversion With Visible Missing Rates

```sql
CREATE OR REPLACE VIEW xx_ap_aging_base AS
SELECT i.invoice_id,
       i.invoice_number,
       i.invoice_date,
       ps.due_date,
       v.vendor_id,
       pv.segment1                                        AS supplier_number,
       pv.vendor_name,
       i.invoice_currency_code,
       ps.amount,
       -- Spot rate AS AT the aging date, closing rate only
       r.conversion_rate,
       CASE
         WHEN i.invoice_currency_code = 'USD' THEN ps.amount
         WHEN r.conversion_rate IS NULL      THEN NULL   -- NEVER default to 1.0
         ELSE ps.amount * r.conversion_rate
       END                                                AS amount_base_usd,
       r.rate_date                                         AS rate_used,
       sc.category_name,
       (i.invoice_currency_code <> 'USD'
        AND r.conversion_rate IS NULL)                     AS missing_rate_flag
  FROM ap_payment_schedules ps
  JOIN ap_invoices_all i   ON i.invoice_id = ps.invoice_id
  JOIN ap_vendor_sites_all v ON v.vendor_site_id = ps.vendor_site_id
  JOIN po_vendors_all pv   ON pv.vendor_id = v.vendor_id
  LEFT JOIN xx_supplier_category sc ON sc.vendor_id = v.vendor_id
  LEFT JOIN gl_daily_rates r
         ON r.set_of_books_id = i.set_of_books_id
        AND r.currency_code   = i.invoice_currency_code
        AND r.rate_type       = 'C'
        AND r.rate_date       = (SELECT MAX(r2.rate_date)
                                   FROM gl_daily_rates r2
                                  WHERE r2.set_of_books_id = r.set_of_books_id
                                    AND r2.currency_code   = r.currency_code
                                    AND r2.rate_type       = 'C'
                                    AND r2.rate_date <= :p_as_of_date);
```

**Three correctness properties**:

1. `due_date` from `ap_payment_schedules` — the aging basis, not invoice date.
2. Rate as at `:p_as_of_date`, `rate_type = 'C'` only.
3. **Missing rate yields NULL, not 1.0.** A silent 1.0 conversion misstates
   liability invisibly.

## 3. Partition Test — The Check That Guarantees Reconciliation

```sql
-- Bucket sums MUST equal the unclassified total. Zero difference required.
SELECT SUM(current_amt) + SUM(bucket_0_30) + SUM(bucket_31_60)
     + SUM(bucket_61_90) + SUM(bucket_90_plus)      AS bucket_sum,
       SUM(total_amt)                                 AS overall_total,
       SUM(bucket_sum) - SUM(overall_total)           AS difference,
       CASE WHEN SUM(bucket_sum) - SUM(overall_total) = 0
            THEN 'RECONCILES' ELSE 'BOUNDARY DEFECT' END AS status
  FROM (
    SELECT SUM(CASE WHEN :p_as_of_date - due_date <= 0
                    THEN amount_base_usd ELSE 0 END) current_amt,
           SUM(CASE WHEN :p_as_of_date - due_date BETWEEN  1 AND 30
                    THEN amount_base_usd ELSE 0 END) bucket_0_30,
           SUM(CASE WHEN :p_as_of_date - due_date BETWEEN 31 AND 60
                    THEN amount_base_usd ELSE 0 END) bucket_31_60,
           SUM(CASE WHEN :p_as_of_date - due_date BETWEEN 61 AND 90
                    THEN amount_base_usd ELSE 0 END) bucket_61_90,
           SUM(CASE WHEN :p_as_of_date - due_date >  90
                    THEN amount_base_usd ELSE 0 END) bucket_90_plus,
           SUM(amount_base_usd)                       total_amt
      FROM xx_ap_aging_base
     WHERE :p_as_of_date >= due_date          -- only what is due
  );
```

**This query belongs in an automated test**, not a review checklist. An
overlapping boundary shows up here as a non-zero difference.

## 4. Missing Rate Exception Report

```sql
SELECT vendor_name, invoice_number, invoice_currency_code, amount, due_date
  FROM xx_ap_aging_base
 WHERE missing_rate_flag = 'Y'
 ORDER BY amount DESC;
```

**Any row here is a report defect**, not a data nuisance. Route it to the
treasury owner who maintains `GL_DAILY_RATES`.

## 5. Drill-Down Level 2 — Suppliers Within a Category

```sql
SELECT ps.vendor_id,                                     -- KEY passed to level 3
       ps.supplier_number,
       ps.vendor_name,
       ps.category,
       ROUND(SUM(CASE WHEN :p_as_of_date - ps.due_date <= 0
                      THEN ps.amount_base_usd END), 2) current_amt,
       ROUND(SUM(CASE WHEN :p_as_of_date - ps.due_date BETWEEN  1 AND 30
                      THEN ps.amount_base_usd END), 2) bucket_0_30,
       ROUND(SUM(CASE WHEN :p_as_of_date - ps.due_date BETWEEN 31 AND 60
                      THEN ps.amount_base_usd END), 2) bucket_31_60,
       ROUND(SUM(CASE WHEN :p_as_of_date - ps.due_date BETWEEN 61 AND 90
                      THEN ps.amount_base_usd END), 2) bucket_61_90,
       ROUND(SUM(CASE WHEN :p_as_of_date - ps.due_date >  90
                      THEN ps.amount_base_usd END), 2) bucket_90_plus,
       ROUND(SUM(ps.amount_base_usd), 2) total_amt,
       ROUND(MAX(:p_as_of_date - ps.due_date))          AS max_days_overdue
  FROM xx_ap_aging_base ps
 WHERE ps.category = :p_category            -- from level 1
   AND (:p_supplier_id IS NULL OR ps.vendor_id = :p_supplier_id)
 GROUP BY ps.vendor_id, ps.supplier_number, ps.vendor_name, ps.category
 ORDER BY total_amt DESC;
```

## 6. Drill-Down Level 3 — Invoice Detail

```sql
SELECT ps.invoice_id,
       ps.invoice_number,
       ps.invoice_date,
       ps.due_date,
       ps.supplier_number,
       ps.vendor_name,
       ps.invoice_currency_code,
       ps.rate_used,
       ROUND(ps.amount, 2)                    AS amount_orig,
       ROUND(ps.amount_base_usd, 2)           AS amount_usd,
       :p_as_of_date - ps.due_date            AS days_overdue,
       CASE WHEN :p_as_of_date - ps.due_date <= 0 THEN 'CURRENT'
            WHEN :p_as_of_date - ps.due_date BETWEEN  1 AND 30 THEN '0-30'
            WHEN :p_as_of_date - ps.due_date BETWEEN 31 AND 60 THEN '31-60'
            WHEN :p_as_of_date - ps.due_date BETWEEN 61 AND 90 THEN '61-90'
            ELSE '90+' END                    AS aging_bucket
  FROM xx_ap_aging_base ps
 WHERE ps.vendor_id = :p_supplier_id          -- ID, not name
   AND ps.due_date <= :p_as_of_date
 ORDER BY ps.due_date;
```

## 7. BI Publisher Hyperlink — Passing Keys Not Names

```
<!-- RTF: Level 1 category cell links to Level 2 -->
{ hyperlink(url:'{concat(
    "{_reqld}",
    "&pAsOfDate={_asOfDate}",
    "&pCategory=", [category], "}'")" }
```
```
<!-- RTF: Level 2 supplier cell links to Level 3, passing the ID -->
{ hyperlink(url:'{concat(
    "{_reqld}",
    "&pAsOfDate={_asOfDate}",
    "&pCategory={category}",
    "&pSupplierId=", [vendor_id], "}'")" }
```

**`[vendor_id]`, never `[vendor_name]`.** Names are not unique; renaming breaks
every saved link.

## 8. Conditional Formatting — A Severity Scale

```
<!-- RTF conditional formatting -->
{ IF "{current_amt}" = "0" "{ IF "{bucket_0_30}" > "0" "[Orange]" ... }" }
```

| Bucket | Colour | Meaning encoded |
|--------|--------|-----------------|
| Current | Green | No action |
| 0-30 | Yellow | Monitor |
| 31-60 | Orange | Escalate |
| 61-90 | Red | Intervene |
| 90+ | Bold red | Executive escalation |

Design as a **severity ramp**, not a category list — the reader should see the
conclusion without interpreting the number.

## 9. Report Header — State the Basis

```
AP AGING REPORT
As at Date:  {[_asOfDate]}          Aging basis: Payment Due Date
Currency:    USD                   Rate basis:  GL_DAILY_RATES spot, type C
Generated:   {SYSDATE}             Generated by: {_username}

Rows with missing conversion rates are excluded from totals — see Exception Report.
```

**State the basis in the output.** A reader who cannot tell whether aging is on
invoice date or due date cannot rely on the number.

## 10. Indexes to Support the Query

```sql
-- Aging filters on due_date with a range predicate
CREATE INDEX ix_aps_due ON ap_payment_schedules (due_date, vendor_site_id);

-- Supplier category lookup
CREATE INDEX ix_xsc_vendor ON xx_supplier_category (vendor_id);

-- Rate lookup: currency + date, closing type only
CREATE INDEX ix_gdr_lookup
  ON gl_daily_rates (set_of_books_id, currency_code, rate_type, rate_date);
```

**Never filter with `TRUNC(due_date) <= :d`** — that disables the index. Use
`due_date < :p_as_of_date + 1`.

## 11. Performance Test Before Deployment

```sql
-- Production-volume test
SELECT /*+ PARALLEL(8) */ COUNT(*)
  FROM xx_ap_aging_base
 WHERE due_date < DATE '2026-02-01';

-- EXPLAIN PLAN must show index range scan, not full scan
EXPLAIN PLAN FOR
SELECT vendor_id, SUM(amount_base_usd)
  FROM xx_ap_aging_base
 WHERE due_date < DATE '2026-02-01'
 GROUP BY vendor_id;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

A report that runs in 2 seconds on test data and 4 minutes in production is
not finished. Test with production cardinality.

## 12. Bursting Definition — Query-Driven Recipients

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xapi:requestset xmlns:xapi="http://xmlns.oracle.com/oxp/xapi">
  <xapi:request select="SELECT 'TOTAL' section_key, 'CFO' recipient_role
                               FROM dual
                        UNION ALL
                        SELECT category, manager_role
                          FROM xx_category_manager
                         WHERE active_flag = 'Y'"/>
  <xapi:delivery>
    <xapi:email server="smtp.company.com" port="25" from="ap-report@company.com">
      <xapi:message id="msg1" to="xapirecipient">
        Subject: AP Aging - {section_key} - {period}
      </xapi:message>
      <xapi:attachment>report.pdf</xapi:attachment>
    </xapi:email>
  </xapi:delivery>
</xapi:requestset>
```

```sql
CREATE TABLE xx_category_manager (
  category    VARCHAR2(30) PRIMARY KEY,
  manager_name VARCHAR2(100) NOT NULL,
  manager_email VARCHAR2(120) NOT NULL,   -- recipients from CONFIG, not hardcoded
  active_flag CHAR(1) DEFAULT 'Y' NOT NULL
);
```

## 13. Guard Against Bursting Everything

```sql
-- Validate parameters before bursting
SELECT CASE
         WHEN :p_category IS NULL AND :p_burst = 'Y'
         THEN 'REFUSE: bursting all categories emails the full population'
         ELSE 'OK' END AS burst_guard;
```

**A report that emails 4,000 rows to 200 managers because a filter defaulted to
"All" is worse than no report at all.**

## 14. Concurrent Program Registration

```sql
-- Executable
INSERT INTO fnd_executables
  (execution_file_name, executable_type, description)
VALUES ('XX_AP_AGING_RPT', 'BIPUBLISHER', 'AP Aging by Supplier Category');

-- Program with parameters
DECLARE
  l_prog_id NUMBER;
BEGIN
  l_prog_id := fnd_concurrent_program_pvt.create_program(
    'XXAPAGING', 'AP Aging by Supplier Category', 'AP', NULL, 'BIPUBLISHER',
    'AP Aging Report', l_exec_id, NULL, 'ACTIVE', NULL);

  fnd_concurrent_program_pvt.add_parameter(
    l_prog_id, 'pAsOfDate', 'As At Date (YYYY-MM-DD)',
    'VARCHAR2', TO_CHAR(SYSDATE,'YYYY-MM-DD'), 'Y', NULL);

  fnd_concurrent_program_pvt.add_parameter(
    l_prog_id, 'pCategory', 'Supplier Category (blank = all)',
    'VARCHAR2', NULL, 'N', NULL);

  fnd_concurrent_program_pvt.add_parameter(
    l_prog_id, 'pBurst', 'Burst to Managers? (Y/N)',
    'VARCHAR2', 'N', 'N', NULL);
END;
/
```

## 15. Report Health Monitoring

```sql
SELECT r.request_id, r.phase_code, r.actual_total_time,
       a.executable_name, s.value AS as_of_date
  FROM fnd_concurrent_requests r
  JOIN fnd_concurrent_programs p ON p.concurrent_program_id = r.concurrent_program_id
  JOIN fnd_concurrent_executables a ON a.executable_id = p.executable_id
  CROSS APPLY (SELECT SUBSTR(arg_value,1,10) value FROM fnd_concurrent_request_args
                WHERE request_id = r.request_id
                  AND argument_name = 'pAsOfDate') s
 WHERE a.executable_name = 'XX_AP_AGING_RPT'
   AND r.requested_start_date > SYSDATE - 30
 ORDER BY r.requested_start_date DESC;
```

**If the report's runtime starts trending upward, the base view needs a
materialised or incremental refresh.** Reports on large tables eventually need
it; better to plan for that than to discover it.