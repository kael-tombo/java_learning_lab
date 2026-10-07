# Google Interview Guide — Oracle EBS Academy

## Interview Process for EBS Roles

### Rounds
- **Round 1 – Phone Screen (45 min)**: Data structures and algorithms in PL/SQL or Java context. Expect to write a query that solves a non-trivial data problem. "Write a query to find the top 10 suppliers by invoice volume with rolling variance."
- **Round 2 – Technical Coding (1 hr)**: Google-style coding round but with EBS schema. Write an algorithm to allocate inventory optimally, reconcile batches, or detect financial anomalies. Must handle edge cases, write test assertions, and discuss complexity.
- **Round 3 – Systems Design (1 hr)**: Design a large-scale EBS integration or platform. Google cares about distributed systems thinking — how would you decouple EBS using event-driven architecture? Design for high availability, consistency, and partition tolerance.
- **Round 4 – Googleyness / Leadership (45 min)**: Ambiguity, collaboration, navigating tough trade-offs, and cognitive ability questions. "Tell me about a time you had to make a decision with incomplete information."
- **Timeline**: 4–6 weeks. Google is methodical.

### EBS-Specific Expectations
- Google does NOT run EBS as their ERP. They use custom-built systems. EBS roles at Google are typically for Google Cloud (supporting customers migrating EBS to GCP) or for acquired companies.
- Google values engineering excellence — clean code, thorough testing, documentation, automated deployments.
- Experience with GCP (BigQuery, Pub/Sub, Cloud SQL, Dataflow) is a strong plus.
- You'll be expected to write scalable, maintainable PL/SQL and Java. "Don't Repeat Yourself" (DRY), SOLID principles.
- Google asks "distilled" questions — they strip away irrelevant complexity and test core problem-solving.

## Top Technical Problems by Lab

### Lab 01: EBS Architecture and Fundamentals

#### Problem: EBS Audit Trail — Identity and Access Review
- **Difficulty/Frequency**: High / Very Frequent
- **Problem statement**: Write a PL/SQL procedure that generates an audit trail report showing all changes made to the responsibility and user assignments in the last 30 days. Show who changed what, when, the old value, and the new value. Google needs this for SOX compliance reporting.
- **Interview walkthrough**: EBS has audit columns on `FND_USER`, `FND_RESPONSIBILITY`, and `FND_USER_RESP_GROUPS_DIRECT`. Use `WHO` columns (`created_by`, `creation_date`, `last_updated_by`, `last_update_date`, `last_update_login`). For detailed audit, use `FND_AUDIT_TABLES` or `FND_LOGIN_RESP_FORMS` for login history. For responsibility changes, use `FND_USER_RESP_GROUPS_DIRECT` with WHO columns.
- **SQL/PLSQL/Java solution**:
```sql
CREATE OR REPLACE PROCEDURE audit_user_resp_changes (
  p_days_back  IN NUMBER DEFAULT 30
) AS
  CURSOR c_audit IS
    WITH user_changes AS (
      SELECT 'USER_CREATE' action_type,
             user_id entity_id,
             user_name entity_value,
             created_by changed_by,
             creation_date change_date,
             NULL old_value,
             user_name new_value,
             creation_date effective_start,
             NULL effective_end
        FROM fnd_user
       WHERE creation_date >= SYSDATE - p_days_back
      UNION ALL
      SELECT 'USER_UPDATE',
             user_id, user_name,
             last_updated_by,
             last_update_date,
             NULL, NULL,  -- Would join FND_AUDIT for details
             last_update_date, NULL
        FROM fnd_user
       WHERE last_update_date >= SYSDATE - p_days_back
         AND last_update_date <> creation_date
      UNION ALL
      SELECT 'RESP_ASSIGN',
             fur.user_id,
             fu.user_name || ' -> ' || frt.responsibility_name,
             fur.created_by,
             fur.creation_date,
             DECODE(fur.start_date, fur.start_date, NULL),
             fur.responsibility_id,
             fur.start_date, fur.end_date
        FROM fnd_user_resp_groups_direct fur,
             fnd_user fu,
             fnd_responsibility_tl frt
       WHERE fur.user_id = fu.user_id
         AND fur.responsibility_id = frt.responsibility_id
         AND fur.creation_date >= SYSDATE - p_days_back
    )
    SELECT * FROM user_changes
    ORDER BY change_date DESC;

  l_rec_count NUMBER := 0;
BEGIN
  fnd_file.put_line(fnd_file.output,
    'Action,Entity,ChangedBy,ChangeDate,OldValue,NewValue');
  FOR rec IN c_audit LOOP
    fnd_file.put_line(fnd_file.output,
      rec.action_type || ',' ||
      rec.entity_value || ',' ||
      rec.changed_by || ',' ||
      TO_CHAR(rec.change_date, 'YYYY-MM-DD HH24:MI:SS') || ',' ||
      NVL(rec.old_value, 'N/A') || ',' ||
      NVL(rec.new_value, 'N/A'));
    l_rec_count := l_rec_count + 1;
  END LOOP;
  fnd_file.put_line(fnd_file.output, 'Total changes: ' || l_rec_count);
END audit_user_resp_changes;
/
```
- **EBS-specific context**: `FND_USER`, `FND_USER_RESP_GROUPS_DIRECT`, `FND_RESPONSIBILITY_TL`, `FND_LOGIN_RESP_FORMS`, WHO columns, `FND_AUDIT_TABLES`.
- **What Google evaluates**: Audit coverage, clean SQL (CTEs, UNION ALL), data lineage thinking, SOX compliance knowledge.
- **Follow-ups**: How does EBS WHO auditing work? Explain `FND_AUDIT_TABLES` setup. How do you handle GDPR data deletion requests in EBS?

#### Problem: Data Migration — BigQuery from EBS
- **Difficulty/Frequency**: High / Frequent
- **Problem statement**: You need to migrate 5 years of PO and AP data from EBS to Google BigQuery for analytics. Design the extraction transformation pipeline. Write the PL/SQL to export data in a format suitable for BigQuery ingestion (partitioned by date, columnar-friendly).
- **Interview walkthrough**: Use `UTL_FILE` to write GZipped CSV files partitioned by month. Use external table stage on GCS (Google Cloud Storage). Transform EBS dates to TIMESTAMP format. Flatten PO distributions into denormalized rows. Use Google Dataflow or BigQuery Transfer Service for scheduled loading.
- **SQL/PLSQL/Java solution**:
```sql
CREATE OR REPLACE PROCEDURE export_po_bigquery (
  p_start_date  DATE,
  p_end_date    DATE
) AS
  l_output  UTL_FILE.FILE_TYPE;
  l_batch   NUMBER := 0;
  CURSOR c_po_data IS
    WITH po_flat AS (
      SELECT pha.segment1 po_number,
             pha.po_header_id,
             pha.creation_date,
             pha.po_release_num,
             pha.authorization_status,
             pha.org_id,
             pll.line_num,
             pll.item_description,
             pll.quantity,
             pll.unit_price,
             pll.quantity * pll.unit_price line_amount,
             pd.distribution_num,
             pd.deliver_to_location_id,
             pd.amount_ytd,
             pd.gl_encumbered_date,
             pd.destination_type_code
        FROM po_headers_all pha,
             po_lines_all pll,
             po_distributions_all pd
       WHERE pha.po_header_id = pll.po_header_id
         AND pll.line_id = pd.line_id
         AND pha.creation_date BETWEEN p_start_date AND p_end_date
    )
    SELECT * FROM po_flat;
BEGIN
  l_output := UTL_FILE.FOPEN('EXPORT_DIR',
    'po_export_' || TO_CHAR(p_start_date, 'YYYYMM') || '.csv',
    'W', 32767);

  -- Header with BigQuery-compatible column names
  UTL_FILE.PUT_LINE(l_output,
    'po_number,po_header_id,creation_date,po_release_num,' ||
    'authorization_status,org_id,line_num,item_description,' ||
    'quantity,unit_price,line_amount,distribution_num,' ||
    'deliver_to_location_id,amount_ytd,encumbered_date,' ||
    'destination_type_code');

  FOR rec IN c_po_data LOOP
    UTL_FILE.PUT_LINE(l_output,
      rec.po_number || ',' ||
      rec.po_header_id || ',' ||
      TO_CHAR(rec.creation_date, 'YYYY-MM-DD HH24:MI:SS') || ',' ||
      NVL(rec.po_release_num, 0) || ',' ||
      rec.authorization_status || ',' ||
      rec.org_id || ',' ||
      rec.line_num || ',' ||
      '"' || REPLACE(NVL(rec.item_description, ''), '"', '""') || '"' || ',' ||
      TO_CHAR(rec.quantity) || ',' ||
      TO_CHAR(rec.unit_price) || ',' ||
      TO_CHAR(rec.line_amount) || ',' ||
      rec.distribution_num || ',' ||
      NVL(rec.deliver_to_location_id, 0) || ',' ||
      TO_CHAR(NVL(rec.amount_ytd, 0)) || ',' ||
      NVL(TO_CHAR(rec.gl_encumbered_date, 'YYYY-MM-DD'), '') || ',' ||
      rec.destination_type_code);
  END LOOP;

  UTL_FILE.FCLOSE(l_output);
  COMMIT;
END export_po_bigquery;
/
```
- **EBS-specific context**: `PO_HEADERS_ALL`, `PO_LINES_ALL`, `PO_DISTRIBUTIONS_ALL`, `UTL_FILE`, GCS external tables, BigQuery schema design.
- **What Google evaluates**: Big data pipeline thinking, data quality (quoting/escaping in CSV), partitioning strategy, GCP awareness.
- **Follow-ups**: How do you handle incremental loads vs full refresh in BigQuery? Explain BigQuery clustering and partitioning on date columns. How does GCS transfer work for large datasets?

### Lab 06: Customization / OAF

#### Problem: OAF Page as REST API — Order Status Lookup
- **Difficulty/Frequency**: High / Frequent
- **Problem statement**: Google Cloud needs to expose an EBS order status lookup as a REST API. Design the approach and write the Java code for the OAF page (or custom servlet) that accepts an HTTP GET request with order number and returns JSON with order status, line items, and shipment details.
- **Interview walkthrough**: OAF can serve as a REST endpoint via `OAControllerImpl` or custom servlet registered in OHS. Better approach: Use Oracle's `OA_TAG` for page-based rendering or write a Java servlet that uses BC4J AM (Application Module) to query `OE_ORDER_LINES_ALL`. Return JSON using `OAViewObject` and serialization via `Gson/Jackson`. For authentication, use EBS session ID or API key.
- **SQL/PLSQL/Java solution**:
```java
// Java — OAF REST Controller for Order Lookup
/*
import oracle.apps.fnd.framework.OAApplicationModule;
import oracle.apps.fnd.framework.server.OAApplicationModuleImpl;
import oracle.jbo.domain.Number;
import oracle.jbo.server.ViewObjectImpl;
import org.json.JSONObject;
import org.json.JSONArray;

public class OrderRESTController {
  public String getOrder(String orderNumber) {
    JSONObject response = new JSONObject();
    OAApplicationModule am =
      OAApplicationModuleImpl.create("oracle.apps.oe.rest.OrderAM");

    try {
      ViewObjectImpl vo =
        (ViewObjectImpl) am.findViewObject("OrderLinesVO");
      vo.setWhereClause("ORDER_NUMBER = :1");
      vo.setWhereClauseParam(0, orderNumber);
      vo.executeQuery();

      JSONArray lines = new JSONArray();
      while (vo.hasNext()) {
        Object[] row = vo.next();
        JSONObject line = new JSONObject();
        line.put("lineId", ((Number) row[0]).longValue());
        line.put("item", (String) row[1]);
        line.put("quantity", ((Number) row[2]).doubleValue());
        line.put("status", (String) row[3]);
        line.put("shipmentStatus", (String) row[4]);
        lines.put(line);
      }

      response.put("orderNumber", orderNumber);
      response.put("lines", lines);
      response.put("status", "success");
    } catch (Exception e) {
      response.put("status", "error");
      response.put("message", e.getMessage());
    } finally {
      am.remove();
    }
    return response.toString();
  }
}
*/
```
- **EBS-specific context**: `OAApplicationModule`, `OAViewObject`, `OAControllerImpl`, `OE_ORDER_LINES_ALL`, `WSH_DELIVERY_DETAILS`, BC4J, Struts, servlets in OHS.
- **What Google evaluates**: Clean API design, JSON serialization, BC4J framework usage, error handling, authentication awareness.
- **Follow-ups**: How does EBS authenticate external API calls? Explain `ICX_SESSIONS` token validation. How would you rate-limit this API for Google-scale traffic? How do you cache order lookups?

### Lab 08: Integrations

#### Problem: Event-Driven Integration with Google Pub/Sub
- **Difficulty/Frequency**: High / Frequent
- **Problem statement**: Design an event-driven integration where every time an invoice is created in EBS, a notification is published to Google Pub/Sub. Write the PL/SQL for the EBS side and describe the GCP subscriber architecture.
- **Interview walkthrough**: Use Oracle Advanced Queuing (AQ) or Business Event System (BES) to capture invoice creation. Create a PL/SQL procedure that enqueues a JSON payload to an AQ queue. Use Oracle Gateway or a custom Java program (running on the app tier) that dequeues and publishes to Pub/Sub via the Google Cloud Java Client. Alternatively, use `UTL_HTTP` to call Pub/Sub REST API directly.
- **SQL/PLSQL/Java solution**:
```sql
CREATE OR REPLACE PACKAGE invoice_pubsub AS
  PROCEDURE publish_invoice_event (
    p_invoice_id     IN NUMBER,
    p_invoice_num    IN VARCHAR2,
    p_invoice_amount IN NUMBER,
    p_vendor_id      IN NUMBER,
    p_invoice_date   IN DATE,
    p_org_id         IN NUMBER
  );
END invoice_pubsub;
/

CREATE OR REPLACE PACKAGE BODY invoice_pubsub AS
  PROCEDURE publish_invoice_event (
    p_invoice_id     IN NUMBER,
    p_invoice_num    IN VARCHAR2,
    p_invoice_amount IN NUMBER,
    p_vendor_id      IN NUMBER,
    p_invoice_date   IN DATE,
    p_org_id         IN NUMBER
  ) AS
    l_req    UTL_HTTP.REQ;
    l_resp   UTL_HTTP.RESP;
    l_url    VARCHAR2(500) := '(link removed)' ||
                              'projects/my-project/topics/invoice-events:publish';
    l_token  VARCHAR2(500) := 'Bearer <access-token>';  -- via OAuth2
    l_body   CLOB;
  BEGIN
    -- Build JSON message
    l_body := '{
      "messages": [{
        "data": "' ||
          UTL_ENCODE.BASE64_ENCODE(
            UTL_RAW.CAST_TO_RAW(
              '{"invoice_id":' || p_invoice_id ||
              ',"invoice_num":"' || p_invoice_num ||
              '","amount":' || p_invoice_amount ||
              ',"vendor_id":' || p_vendor_id ||
              ',"invoice_date":"' ||
              TO_CHAR(p_invoice_date, 'YYYY-MM-DD') ||
              '","org_id":' || p_org_id || '}'
            )
          ) || '"
      }]
    }';

    l_req := UTL_HTTP.BEGIN_REQUEST(l_url, 'POST', 'HTTP/1.1');
    UTL_HTTP.SET_HEADER(l_req, 'Content-Type', 'application/json');
    UTL_HTTP.SET_HEADER(l_req, 'Authorization', l_token);
    UTL_HTTP.SET_HEADER(l_req, 'Content-Length', LENGTH(l_body));
    UTL_HTTP.WRITE_TEXT(l_req, l_body);
    l_resp := UTL_HTTP.GET_RESPONSE(l_req);
    UTL_HTTP.END_RESPONSE(l_resp);

  EXCEPTION
    WHEN OTHERS THEN
      -- Log failure and retry via concurrent program
      INSERT INTO pubsub_failed_events
      (event_type, event_key, payload, error_msg, retry_count)
      VALUES ('INVOICE_CREATE', TO_CHAR(p_invoice_id),
              l_body, SQLERRM, 0);
      COMMIT;
  END publish_invoice_event;
END invoice_pubsub;
/

-- Trigger the event from AP Invoice validation
CREATE OR REPLACE TRIGGER trg_ap_invoice_pubsub
  AFTER INSERT ON ap_invoices_all
  FOR EACH ROW
BEGIN
  invoice_pubsub.publish_invoice_event(
    p_invoice_id     => :NEW.invoice_id,
    p_invoice_num    => :NEW.invoice_num,
    p_invoice_amount => :NEW.invoice_amount,
    p_vendor_id      => :NEW.vendor_id,
    p_invoice_date   => :NEW.invoice_date,
    p_org_id         => :NEW.org_id
  );
END trg_ap_invoice_pubsub;
/
```
- **EBS-specific context**: `AP_INVOICES_ALL`, `UTL_HTTP`, `UTL_ENCODE`, Oracle AQ, Business Event System, `FND_EVENT_QUEUE_PKG`, `FND_EVENT_PKG`.
- **What Google evaluates**: Event-driven architecture, Google Cloud Pub/Sub knowledge, HTTP callout from PL/SQL, error handling, idempotency.
- **Follow-ups**: How do you secure the Pub/Sub endpoint? Explain OAuth2 client credentials flow for service-to-service auth. How do you handle Pub/Sub message ordering and exactly-once delivery?

## EBS-Specific Deep Dive Questions

- **EBS on Google Cloud**: How would you deploy EBS on GCP? Use Compute Engine with Solver configurations, Cloud SQL for database, Cloud Storage for concurrent manager logs. Explain network setup (VPC, Cloud VPN, Private Google Access).
- **BigQuery for EBS Analytics**: Design a BigQuery data warehouse for EBS — dimensional model for GL, AP, AR. How does BigQuery's columnar storage benefit financial data? Partitioning by ledger and month. Clustering by account.
- **Dataflow vs ETL**: When would you use Google Dataflow (Apache Beam) vs traditional ETL for EBS data extraction? Dataflow for streaming events (new invoices), traditional batch for month-end GL close.
- **Looker + EBS**: How would you build a Looker semantic model on top of EBS data in BigQuery? Explains LookML dimensions, measures, and explores for GL account analysis.
- **Scalability and Reliability**: Google expects systems that never go down. How would you make EBS highly available? Active-passive with Data Guard, load-balanced app tiers, automated failover.
- **Site Reliability Engineering (SRE)**: How do you monitor EBS health? Key metrics — concurrent manager queue depth, FND_LOGIN_RESP_FORMS active sessions, APPS database wait events. SLIs and SLOs for EBS.

## Behavioral Questions (STAR)

- **Situation**: A critical custom OAF page failed during month-end close for all users.
  - **Task**: Diagnose and fix under extreme pressure.
  - **Action**: Traced the issue to a missing `OADBTransaction` connection caused by a DB pool exhaustion. Wrote an emergency patch that switched from entity-based VO to read-only forward-only VO. Added connection pool monitoring.
  - **Result**: Site operational in 22 minutes. Root cause documented in postmortem.

- **Situation**: EBS to BigQuery pipeline was failing silently — 3 days of data lost.
  - **Task**: Recover data and make pipeline observable.
  - **Action**: Added checkpointing using `CUSTOM_EXTRACT_LOG` with watermark columns. Built Dataflow pipeline with dead-letter queue. Implemented alerting via Pub/Sub->Cloud Monitoring.
  - **Result**: Zero data loss after fix. Pipeline reliability at 99.99%.

- **Situation**: Ambiguous requirement for a complex financial report — the business couldn't define the logic.
  - **Task**: Deliver the report without a clear spec.
  - **Action**: Built a prototype in BI Publisher with parameterized drill-downs. Presented 3 iterations over 2 weeks, refining with business feedback. Used `GL_DAILY_BALANCES` for faster exploration.
  - **Result**: Report delivered on time. CFO adopted it for board reporting.

- **Situation**: Two conflicting EBS customizations were corrupting inventory data.
  - **Task**: Identify root cause and fix.
  - **Action**: Isolated the issue to a race condition between `INV_TXN_MANAGER` and a custom trigger on `MTL_ONHAND_QUANTITIES`. Removed the trigger, redesigned using `MTL_TRANSACTIONS_INTERFACE` with proper locking.
  - **Result**: Data integrity restored. Error rate dropped to zero.

- **Situation**: Team lacked automated testing for EBS customizations.
  - **Task**: Implement testing culture.
  - **Action**: Created PL/SQL unit test framework using `UTL_UTEST` pattern. Wrote test cases for all concurrent programs. Set up CI/CD using Cloud Build that runs tests on a staging EBS instance.
  - **Result**: Defect rate reduced by 70%. Release cycle shortened from 4 weeks to 1 week.

## Study Plan

| Priority | Labs |
|----------|------|
| Must | Lab 01 (Architecture), Lab 06 (OAF), Lab 08 (Integrations), Lab 09 (Security) |
| Recommended | Lab 07 (Reporting), Lab 10 (Upgrade/Migration), Lab 03 (Financials) |
| Additional | Lab 02 (System Admin), Lab 04 (Supply Chain) |
| Niche | Lab 05 (HRMS) |

### Lab 10: Upgrade / Migration

#### Problem: EBS to GCP Migration — Cutover Automation
- **Difficulty/Frequency**: High / Frequent
- **Problem statement**: A client is migrating their on-premise EBS R12.2 to Google Compute Engine. Design the migration cutover plan with zero data loss. Write the PL/SQL validation scripts that verify data consistency before and after migration, and the cutover automation logic.
- **Interview walkthrough**: Migration strategy: use Oracle Data Guard for database replication to Cloud SQL or GCE VM with Oracle DB. For application tier, snapshot the filesystem and replicate to GCE. Cutover steps: stop app tier, apply final redo, switch Data Guard, start app tier on GCE. Validation: compare counts on key tables (GL_BALANCES, AP_INVOICES_ALL, FND_USER) using checksums or DBMS_COMPARISON. Use Cloud Monitoring for cutover status dashboard.
- **SQL/PLSQL/Java solution**:
```sql
CREATE OR REPLACE PROCEDURE validate_migration_consistency (
  p_source_db_link  IN VARCHAR2,
  p_table_name      IN VARCHAR2,
  p_key_column      IN VARCHAR2,
  p_threshold_pct   IN NUMBER DEFAULT 0.01
) AS
  l_source_count NUMBER;
  l_target_count NUMBER;
  l_diff_pct     NUMBER;
BEGIN
  -- Count rows in source
  EXECUTE IMMEDIATE
    'SELECT COUNT(*) FROM ' || p_table_name || '@' || p_source_db_link
    INTO l_source_count;

  -- Count rows in target (current DB)
  EXECUTE IMMEDIATE
    'SELECT COUNT(*) FROM ' || p_table_name
    INTO l_target_count;

  -- Calculate difference percentage
  IF l_source_count = 0 AND l_target_count = 0 THEN
    l_diff_pct := 0;
  ELSIF l_source_count = 0 THEN
    l_diff_pct := 100;
  ELSE
    l_diff_pct := ABS(l_source_count - l_target_count) / l_source_count * 100;
  END IF;

  -- Log result
  INSERT INTO migration_validation_log
  (table_name, source_count, target_count, diff_pct, status, validated_date)
  VALUES (p_table_name, l_source_count, l_target_count,
          l_diff_pct,
          CASE WHEN l_diff_pct <= p_threshold_pct THEN 'PASS' ELSE 'FAIL' END,
          SYSDATE);

  IF l_diff_pct > p_threshold_pct THEN
    fnd_file.put_line(fnd_file.log,
      'FAIL: ' || p_table_name || ' source=' || l_source_count ||
      ' target=' || l_target_count || ' diff%=' || ROUND(l_diff_pct, 4));
  ELSE
    fnd_file.put_line(fnd_file.log,
      'PASS: ' || p_table_name || ' count=' || l_source_count);
  END IF;

  COMMIT;
END validate_migration_consistency;
/

-- Checksum-based validation for data integrity
CREATE OR REPLACE FUNCTION table_checksum (
  p_table_name VARCHAR2,
  p_db_link    VARCHAR2 DEFAULT NULL
) RETURN VARCHAR2 IS
  l_checksum VARCHAR2(100);
  l_from     VARCHAR2(200) := p_table_name;
BEGIN
  IF p_db_link IS NOT NULL THEN
    l_from := l_from || '@' || p_db_link;
  END IF;
  EXECUTE IMMEDIATE
    'SELECT TO_CHAR(SUM(ORA_HASH(ROWIDTOCHAR(ROWID)))) FROM ' || l_from
    INTO l_checksum;
  RETURN l_checksum;
END table_checksum;
/
```
- **EBS-specific context**: Data Guard, GCE/Cloud SQL, DBMS_COMPARISON, ORA_HASH, migration validation, cutover sequencing, FND_CONCURRENT_REQUESTS for app tier verification.
- **What Google evaluates**: Migration expertise, validation rigor (checksums, row counts), GCP awareness, zero-data-loss cutover design.
- **Follow-ups**: How do you handle EBS concurrent manager failover in the cloud? What about ADOP patching on GCE? How do you migrate EBS to Cloud SQL vs GCE with Oracle DB? Explain the GCP network architecture for EBS.

## Tips

- **Google engineering standards**: Write clean, modular PL/SQL. Use packages, avoid literals, handle exceptions properly, include pragma for autonomous transactions. Google engineers will judge code quality.
- **GCP awareness is non-negotiable**: Even for EBS roles, Google expects familiarity with GCP services — BigQuery, Pub/Sub, Dataflow, Cloud Storage, Compute Engine.
- **Design for failure**: Google SRE culture — assume everything fails. Every answer should include: "what happens when this fails?" and "how do we recover?"
- **Data-driven**: Google is obsessed with data. Show how you'd measure EBS performance, user adoption, error rates. Use of instrumented concurrent programs.
- **No politics**: "Googleyness" means being humble, collaborative, and open. Avoid bad-mouthing previous employers or colleagues.
- **Cognitive ability**: Google may ask brainteaser-type questions ("how many EBS instances run in North America?"). They test structured thinking, not the answer.
