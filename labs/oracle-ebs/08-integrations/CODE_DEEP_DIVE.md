# Lab 08: Integrations — Code Deep Dive

## 1. Core Tables

```sql
-- Idempotency claim: PK is the lock
CREATE TABLE xx_int_idempotency (
  source_system VARCHAR2(20)  NOT NULL,
  external_id   VARCHAR2(100) NOT NULL,
  payload_hash  VARCHAR2(64),
  status        VARCHAR2(15)  NOT NULL, -- IN_PROGRESS/SUCCESS/FAILED
  ebs_object_id VARCHAR2(40),
  error_message VARCHAR2(2000),
  created_at    TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  completed_at  TIMESTAMP,
  CONSTRAINT xx_idem_pk PRIMARY KEY (source_system, external_id)
);

-- Dead letter queue with the FULL payload, replayable
CREATE TABLE xx_integration_dlq (
  message_id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  source_system   VARCHAR2(20)  NOT NULL,
  message_type    VARCHAR2(30)  NOT NULL, -- OPPORTUNITY/QUOTE/ORDER_STATUS
  external_id     VARCHAR2(100) NOT NULL,
  payload         CLOB NOT NULL,            -- full message, not a summary
  error_class     VARCHAR2(20)  NOT NULL,   -- RETRYABLE/TERMINAL
  error_code      VARCHAR2(30),
  error_message   VARCHAR2(2000) NOT NULL,
  attempt_count   NUMBER DEFAULT 0 NOT NULL,
  first_failed_at TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  last_failed_at  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  status          VARCHAR2(15) DEFAULT 'OPEN' NOT NULL, -- OPEN/REPLAYED/DISCARDED
  resolved_by     VARCHAR2(64),
  resolved_at     TIMESTAMP,
  CONSTRAINT xx_dlq_st_ck CHECK (status IN ('OPEN','REPLAYED','DISCARDED')),
  CONSTRAINT xx_dlq_cl_ck CHECK (error_class IN ('RETRYABLE','TERMINAL'))
);
CREATE INDEX xx_dlq_open_idx ON xx_integration_dlq (status, first_failed_at);

-- Integration audit
CREATE TABLE xx_int_audit (
  audit_id     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  message_type VARCHAR2(30) NOT NULL,
  external_id  VARCHAR2(100),
  ebs_object_id VARCHAR2(40),
  direction    VARCHAR2(10) NOT NULL, -- INBOUND/OUTBOUND
  operation    VARCHAR2(30) NOT NULL,
  status       VARCHAR2(15) NOT NULL,
  actor        VARCHAR2(64) NOT NULL,
  elapsed_ms   NUMBER,
  created_at   TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

-- Externalised field mapping
CREATE TABLE xx_field_mapping (
  source_system  VARCHAR2(20) NOT NULL,
  entity_name    VARCHAR2(50) NOT NULL,  -- ACCOUNT/CONTACT/OPPORTUNITY
  source_field   VARCHAR2(60) NOT NULL,
  target_table   VARCHAR2(30),
  target_column  VARCHAR2(30),
  transform_rule VARCHAR2(50) DEFAULT 'DIRECT', -- DIRECT/UPPER/DEFAULT/DATE_FMT
  mandatory_flag CHAR(1) DEFAULT 'N',
  active_flag    CHAR(1) DEFAULT 'Y',
  CONSTRAINT xx_fm_pk PRIMARY KEY (source_system, entity_name, source_field)
);
```

## 2. Payload Hash for Changed-Payload Detection

```sql
CREATE OR REPLACE FUNCTION xx_int_hash(p_xml IN CLOB) RETURN VARCHAR2 IS
  l_hash RAW;
BEGIN
  -- Standard hash over the normalised payload
  l_hash := STANDARD_HASH(p_xml, 'SHA256');
  RETURN LOWER(RAWTOHEX(TO_RAW(SUBSTR(l_hash, 1, 16))));
EXCEPTION WHEN OTHERS THEN RETURN NULL;
END;
/
```

## 3. Inbound Salesforce REST Call (OAuth2 Client Credentials)

```sql
CREATE OR REPLACE PACKAGE xx_sf_auth_pkg AS
  FUNCTION get_access_token RETURN VARCHAR2;
END;
/

CREATE OR REPLACE PACKAGE BODY xx_sf_auth_pkg AS

  g_token VARCHAR2(4000);
  g_expiry TIMESTAMP;

  FUNCTION get_access_token RETURN VARCHAR2 IS
    l_req   UTL_HTTP.req;
    l_res   UTL_HTTP.resp;
    l_body  VARCHAR2(4000);
    l_json  JSON_OBJECT_T;
  BEGIN
    -- Reuse the token until shortly before expiry
    IF g_token IS NOT NULL AND g_expiry > SYSTIMESTAMP + INTERVAL '5' MINUTE' THEN
      RETURN g_token;
    END IF;

    l_req := UTL_HTTP.begin_request(
      'https://login.salesforce.com/services/oauth2/token', 'POST');
    UTL_HTTP.set_header(l_req, 'Content-Type', 'application/x-www-form-urlencoded');

    -- Secret from the CREDENTIAL STORE, never plaintext in APPL_TOP
    UTL_HTTP.set_form_data(l_req,
      'grant_type',    'client_credentials',
      'client_id',     xx_sec_pvt.get('SF_CLIENT_ID'),
      'client_secret', xx_sec_pvt.get('SF_CLIENT_SECRET'));

    l_res := UTL_HTTP.get_response(l_req);
    l_body := UTL_HTTP.get_body(l_res);
    UTL_HTTP.end_response(l_res);

    IF l_res.status_code NOT IN (200, 201) THEN
      RAISE_APPLICATION_ERROR(-20060,
        'Salesforce auth failed (' || l_res.status_code || ')');
    END IF;

    l_json := TREAT(l_body AS JSON_OBJECT_T);
    g_token  := TREAT(l_json.get('access_token') AS JSON_STRING_T).to_string;
    g_expiry := SYSTIMESTAMP
              + NUMTODSINTERVAL(
                  TREAT(l_json.get('expires_in') AS JSON_NUMBER_T).get_number
                  / 60, 'MINUTE');

    RETURN g_token;
  END get_access_token;

END;
/
```

## 4. Fetch Opportunity from Salesforce REST

```sql
CREATE OR REPLACE FUNCTION xx_sf_get_opportunity(p_sf_id IN VARCHAR2)
  RETURN CLOB IS
  l_req  UTL_HTTP.req;
  l_res  UTL_HTTP.resp;
  l_body CLOB;
  l_url  VARCHAR2(500) :=
    'https://api.salesforce.com/services/data/v59.0/sobjects/Opportunity/'
    || p_sf_id || '?expand=opportunityLineItems,Account,Contact';
BEGIN
  l_req := UTL_HTTP.begin_request(l_url, 'GET', 'HTTP/1.1');
  UTL_HTTP.set_header(l_req, 'Authorization',
                      'Bearer ' || xx_sf_auth_pkg.get_access_token);
  UTL_HTTP.set_header(l_req, 'Accept', 'application/json');

  l_res := UTL_HTTP.get_response(l_req);
  l_body := UTL_HTTP.get_body_as_clob(l_res);
  UTL_HTTP.end_response(l_res);

  IF l_res.status_code = 401 THEN
    RAISE_APPLICATION_ERROR(-20061, 'AUTH: token rejected (terminal)');
  ELSIF l_res.status_code = 503 THEN
    RAISE_APPLICATION_ERROR(-20062, 'RETRYABLE: Salesforce overloaded');
  ELSIF l_res.status_code <> 200 THEN
    RAISE_APPLICATION_ERROR(-20063,
      'Salesforce returned ' || l_res.status_code);
  END IF;

  RETURN l_body;
END;
```

## 5. Idempotency Wrapper — The Core Pattern

```sql
CREATE OR REPLACE PACKAGE xx_int_process_pkg AS
  PROCEDURE process_opportunity(
    p_sf_opportunity_id IN VARCHAR2,
    p_payload           IN CLOB,
    p_x_return_status   OUT VARCHAR2,
    p_x_return_msg      OUT VARCHAR2,
    p_x_quote_id        OUT NUMBER
  );
END;
/

CREATE OR REPLACE PACKAGE BODY xx_int_process_pkg AS

  PROCEDURE process_opportunity(
    p_sf_opportunity_id IN VARCHAR2,
    p_payload           IN CLOB,
    p_x_return_status   OUT VARCHAR2,
    p_x_return_msg      OUT VARCHAR2,
    p_x_quote_id        OUT NUMBER
  ) IS
    l_status VARCHAR2(15);
    l_obj    VARCHAR2(40);
    l_err    VARCHAR2(2000);
    l_hash   VARCHAR2(64) := xx_int_hash(p_payload);
    l_start  NUMBER := DBMS_UTILITY.GET_TIME;
  BEGIN
    p_x_return_status := 'S';

    -- STEP 1: claim the idempotency key. The PK insert IS the lock.
    BEGIN
      INSERT INTO xx_int_idempotency
        (source_system, external_id, payload_hash, status)
      VALUES ('SALESFORCE', p_sf_opportunity_id, l_hash, 'IN_PROGRESS');
      COMMIT;
    EXCEPTION WHEN DUP_VAL_ON_INDEX THEN
      SELECT status, ebs_object_id, error_message
        INTO l_status, l_obj, l_err
        FROM xx_int_idempotency
       WHERE source_system = 'SALESFORCE'
         AND external_id   = p_sf_opportunity_id;

      IF l_status = 'SUCCESS' THEN
        -- REPLAY the answer rather than duplicating the work
        p_x_quote_id := TO_NUMBER(l_obj);
        p_x_return_msg := 'Already processed; returning existing quote ' || l_obj;
        RETURN;
      ELSIF l_status = 'IN_PROGRESS' THEN
        RAISE_APPLICATION_ERROR(-20090,
          'Message ' || p_sf_opportunity_id || ' is already in progress');
      ELSE
        -- previously FAILED: allow a retry by resetting to IN_PROGRESS
        UPDATE xx_int_idempotency
           SET status = 'IN_PROGRESS', attempts = attempts + 1
         WHERE source_system='SALESFORCE' AND external_id = p_sf_opportunity_id;
        COMMIT;
      END IF;
    END;

    BEGIN
      -- STEP 2: transform Salesforce → EBS
      xx_sf_transform_pkg.opportunity_to_order(
        p_payload, l_ord_hdr_rec, l_ord_tbl_rec);

      -- STEP 3: validate BEFORE calling the API
      xx_validate_pkg.validate_order(l_ord_hdr_rec, l_ord_tbl_rec);

      -- STEP 4: standard EBS API
      p_x_quote_id := oe_order_api_pub.create_order(
        p_order_header_rec => l_ord_hdr_rec,
        p_order_tbl_rec    => l_ord_tbl_rec,
        x_return_status    => p_x_return_status,
        x_return_message   => p_x_return_msg);

      IF p_x_return_status <> 'S' THEN
        RAISE_APPLICATION_ERROR(-20070, 'ORDER_API: ' || p_x_return_msg);
      END IF;

      -- STEP 5: record success
      UPDATE xx_int_idempotency
         SET status='SUCCESS', ebs_object_id = TO_CHAR(p_x_quote_id),
             completed_at = SYSTIMESTAMP
       WHERE source_system='SALESFORCE' AND external_id = p_sf_opportunity_id;
      COMMIT;

      INSERT INTO xx_int_audit
        (message_type, external_id, ebs_object_id, direction, operation,
         status, actor, elapsed_ms)
      VALUES ('OPPORTUNITY', p_sf_opportunity_id, TO_CHAR(p_x_quote_id),
              'INBOUND', 'CREATE_ORDER', 'SUCCESS', USER,
              (DBMS_UTILITY.GET_TIME - l_start));
      COMMIT;

    EXCEPTION WHEN OTHERS THEN
      l_err := SQLERRM;
      UPDATE xx_int_idempotency
         SET status='FAILED', error_message = SUBSTR(l_err,1,2000),
             completed_at = SYSTIMESTAMP
       WHERE source_system='SALESFORCE' AND external_id = p_sf_opportunity_id;
      COMMIT;

      p_x_return_status := 'E';
      p_x_return_msg    := SUBSTR(l_err, 1, 2000);
      RAISE;
    END;
  END process_opportunity;

END;
/
```

## 6. Transformation — Salesforce JSON to EBS Records

```sql
CREATE OR REPLACE PACKAGE BODY xx_sf_transform_pkg AS

  PROCEDURE opportunity_to_order(
    p_payload IN CLOB,
    o_hdr     OUT oe_order_pub.order_rec_type,
    o_tbl     OUT oe_order_pub.order_tbl_type
  ) IS
    l_json   JSON_OBJECT_T := TREAT(p_payload AS JSON_OBJECT_T);
    l_lines  JSON_ARRAY_T;
    l_acct   JSON_OBJECT_T;
    l_ship_to VARCHAR2(100);
  BEGIN
    -- Opportunity → header
    o_hdr := oe_order_pub.missing_order_rec;
    o_hdr.order_source_code    := 'SF';
    o_hdr.ordered_date         := TRUNC(SYSDATE);
    o_hdr.sold_to_org_id       := 101;
    o_hdr.requested_ship_date  := TRUNC(SYSDATE) + 14;
    o_hdr.shipping_method_code := 'BEST';
    o_hdr.order_source_ref_num := TREAT(l_json.get('Id')
                              AS JSON_STRING_T).to_string;  -- traceable

    -- Resolve customer via the Salesforce Account Id
    l_acct := TREAT(l_json.get('Account') AS JSON_OBJECT_T);
    xx_cust_resolve_pkg.resolve_ship_to(
      TREAT(l_acct.get('Id') AS JSON_STRING_T).to_string, l_ship_to);
    o_hdr.ship_to_site_id := l_ship_to;

    -- OpportunityLineItems → order lines
    l_lines := TREAT(l_json.get('opportunityLineItems') AS JSON_ARRAY_T);
    FOR i IN 1 .. l_lines.get_Num RETURN LOOP
      l_acct := TREAT(l_lines.get(i) AS JSON_OBJECT_T);
      o_tbl(i) := oe_order_pub.missing_order_tbl_rec;
      o_tbl(i).line_type_code       := 'FULL';
      o_tbl(i).ordered_quantity     := TREAT(l_acct.get('Quantity')
                                   AS JSON_NUMBER_T).get_number;
      o_tbl(i).line_value           := TREAT(l_acct.get('TotalPrice')
                                   AS JSON_NUMBER_T).get_number;
      o_tbl(i).opportunity_line_id  := TREAT(l_acct.get('Id')
                                   AS JSON_STRING_T).to_string;
      -- Negotiated price from SF; catalogue price resolved in EBS
      o_tbl(i).unit_selling_price   := TREAT(l_acct.get('UnitPrice')
                                   AS JSON_NUMBER_T).get_number;
      o_tbl(i).inventory_item_id    :=
        xx_item_resolve_pkg.resolve_sku(
          TREAT(l_acct.get('Product2Id') AS JSON_STRING_T).to_string);
    END LOOP;

  END opportunity_to_order;

END;
/
```

## 7. Business Events — Publishing EBS State Changes

```sql
-- Business event definition (Workflow Business Event System)
-- Registered in Workflow Builder: "Order Booked"

-- Subscription: outbound message to Salesforce on ORDER_BOOKED
BEGIN
  wf_event_api_pvt.subscribe_event(
    p_event_key      => 'oracle.apps.om.order.booked',
    p_owner          => 'XX_INT',
    p_subscription   => 'SF_ORDER_STATUS_PUSH'
  );
END;
/
```

### Oracle Workflow Outbound Message to Salesforce
```sql
CREATE OR REPLACE PROCEDURE xx_push_order_status(
  p_order_number IN VARCHAR2,
  p_status       IN VARCHAR2
) IS
  l_payload JSON_OBJECT_T := JSON_OBJECT_T();
  l_req     UTL_HTTP.req;
  l_res     UTL_HTTP.resp;
BEGIN
  l_payload.put('orderNumber', p_order_number);
  l_payload.put('status',       p_status);
  l_payload.put('eventTime',    TO_CHAR(SYSTIMESTAMP,'YYYY-MM-DD"T"HH24:MI:SS'));

  l_req := UTL_HTTP.begin_request(
    'https://api.salesforce.com/services/apexrest/ebs/order/status',
    'POST', 'HTTP/1.1');
  UTL_HTTP.set_header(l_req, 'Authorization',
    'Bearer ' || xx_sf_auth_pkg.get_access_token);
  UTL_HTTP.set_header(l_req, 'Content-Type', 'application/json');
  UTL_HTTP.set_body(l_req, l_payload.to_string);

  l_res := UTL_HTTP.get_response(l_req);
  UTL_HTTP.end_response(l_res);

  IF l_res.status_code NOT IN (200,201,204) THEN
    RAISE_APPLICATION_ERROR(-20080,
      'Order status push failed: ' || l_res.status_code);  -- DLQ will capture
  END IF;
END;
/
```

## 8. Retry with Bounded Exponential Backoff

```sql
CREATE OR REPLACE PACKAGE xx_retry_pkg AS
  PROCEDURE execute(
    p_source_system IN VARCHAR2,
    p_message_type  IN VARCHAR2,
    p_external_id   IN VARCHAR2,
    p_payload       IN CLOB,
    p_max_attempts  IN PLS_INTEGER DEFAULT 5,
    p_base_delay    IN PLS_INTEGER DEFAULT 2   -- seconds
  );
END;
/

CREATE OR REPLACE PACKAGE BODY xx_retry_pkg AS

  PROCEDURE execute(
    p_source_system IN VARCHAR2, p_message_type IN VARCHAR2,
    p_external_id IN VARCHAR2,   p_payload IN CLOB,
    p_max_attempts IN PLS_INTEGER DEFAULT 5,
    p_base_delay   IN PLS_INTEGER DEFAULT 2
  ) IS
    l_attempt   PLS_INTEGER := 0;
    l_status    VARCHAR2(2);
    l_msg       VARCHAR2(2000);
    l_err       VARCHAR2(2000);
    l_terminal  BOOLEAN;
  BEGIN
    WHILE l_attempt < p_max_attempts LOOP
      l_attempt := l_attempt + 1;
      BEGIN
        xx_int_process_pkg.process_opportunity(
          p_sf_opportunity_id => p_external_id,
          p_payload           => p_payload,
          p_x_return_status   => l_status,
          p_x_return_msg      => l_msg,
          p_x_quote_id        => NULL);

        IF l_status = 'S' THEN
          RETURN;   -- success
        END IF;
        l_err := l_msg;
      EXCEPTION WHEN OTHERS THEN
        l_err := SQLERRM;
      END;

      -- CLASSIFY: only retry what a retry could fix
      l_terminal := (l_err LIKE 'VALID%' OR l_err LIKE 'API_REJECT%')
                 OR (l_err LIKE 'AUTH%');

      IF l_terminal THEN
        INSERT INTO xx_integration_dlq
          (source_system, message_type, external_id, payload,
           error_class, error_message, attempt_count, status)
        VALUES (p_source_system, p_message_type, p_external_id, p_payload,
                'TERMINAL', SUBSTR(l_err,1,2000), l_attempt, 'OPEN');
        COMMIT;
        RETURN;   -- do not retry; the data or the credential is wrong
      END IF;

      IF l_attempt < p_max_attempts THEN
        -- BOUNDED backoff: 2, 4, 8, 16, then give up
        DBMS_LOCK.SLEEP(p_base_delay * POWER(2, l_attempt - 1));
      END IF;
    END LOOP;

    -- Attempts exhausted → DLQ with the FULL payload for replay
    INSERT INTO xx_integration_dlq
      (source_system, message_type, external_id, payload,
       error_class, error_message, attempt_count, status)
    VALUES (p_source_system, p_message_type, p_external_id, p_payload,
            'RETRYABLE', SUBSTR(l_err,1,2000), l_attempt, 'OPEN');
    COMMIT;
  END execute;

END;
/
```

## 9. Scheduled DLQ Processor

```sql
CREATE OR REPLACE PROCEDURE xx_dlq_process(
  p_max_age_hours IN NUMBER DEFAULT 1
) IS
  CURSOR c IS
    SELECT message_id, source_system, message_type, external_id,
           payload, attempt_count
      FROM xx_integration_dlq
     WHERE status = 'OPEN'
       AND last_failed_at < SYSTIMESTAMP - (p_max_age_hours/24)
     ORDER BY first_failed_at;
BEGIN
  FOR r IN c LOOP
    xx_retry_pkg.execute(
      p_source_system => r.source_system,
      p_message_type  => r.message_type,
      p_external_id   => r.external_id,
      p_payload       => r.payload,
      p_max_attempts  => 3);

    UPDATE xx_integration_dlq
       SET status = CASE WHEN status = 'OPEN' THEN 'OPEN' ELSE status END,
           attempt_count = attempt_count + 1,
           last_failed_at = SYSTIMESTAMP
     WHERE message_id = r.message_id;
    COMMIT;
  END LOOP;
END;
```

## 10. Replay from the DLQ

```sql
CREATE OR REPLACE PROCEDURE xx_dlq_replay(
  p_message_id IN NUMBER,
  p_user       IN VARCHAR2
) IS
  r xx_integration_dlq%ROWTYPE;
  l_status VARCHAR2(2);
  l_msg    VARCHAR2(2000);
BEGIN
  SELECT * INTO r FROM xx_integration_dlq WHERE message_id = p_message_id;
  IF r.status <> 'OPEN' THEN
    RAISE_APPLICATION_ERROR(-20091, 'Message is not OPEN');
  END IF;

  -- Idempotency protects the replay from duplicating a completed message
  xx_int_process_pkg.process_opportunity(
    p_sf_opportunity_id => r.external_id,
    p_payload           => r.payload,
    p_x_return_status   => l_status,
    p_x_return_msg      => l_msg,
    p_x_quote_id        => NULL);

  IF l_status = 'S' THEN
    UPDATE xx_integration_dlq
       SET status='REPLAYED', resolved_by=p_user, resolved_at=SYSTIMESTAMP
     WHERE message_id = p_message_id;
  END IF;
  COMMIT;
END;
```

## 11. Monitoring — Throughput, Latency, Errors

```sql
-- Throughput and latency by message type
SELECT message_type, operation,
       COUNT(*)                    msg_count,
       ROUND(AVG(elapsed_ms), 1)   avg_ms,
       MAX(elapsed_ms)             max_ms,
       SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END) ok_count,
       SUM(CASE WHEN status<>'SUCCESS' THEN 1 ELSE 0 END) err_count,
       ROUND(100 * SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END)
             / COUNT(*), 2)       success_pct
  FROM xx_int_audit
 WHERE created_at >= TRUNC(SYSDATE) - 1
 GROUP BY message_type, operation
 ORDER BY msg_count DESC;
```

```sql
-- DLQ triage: aggregate by error class to find the dominant fix
SELECT error_class, SUBSTR(error_message, 1, 80) error_prefix,
       COUNT(*) occurrences,
       MIN(first_failed_at) oldest,
       MAX(last_failed_at)  newest
  FROM xx_integration_dlq
 WHERE status = 'OPEN'
 GROUP BY error_class, SUBSTR(error_message, 1, 80)
 ORDER BY occurrences DESC;
```

```sql
-- BUSINESS AGREEMENT: catches silent drops that error rates miss
SELECT TO_CHAR(TRUNC(s.created_at),'YYYY-MM-DD') day,
       (SELECT COUNT(*) FROM sf_opportunity_log
         WHERE created_at BETWEEN TRUNC(s.created_at) AND TRUNC(s.created_at)+1) sf_opportunities,
       COUNT(a.audit_id) ebs_orders_created,
       COUNT(a.audit_id) - (SELECT COUNT(*) FROM sf_opportunity_log
         WHERE created_at BETWEEN TRUNC(s.created_at) AND TRUNC(s.created_at)+1) AS unexplained_gap
  FROM xx_int_audit a
  LEFT JOIN sf_opportunity_log s ON s.sf_id = a.external_id
 WHERE a.message_type = 'OPPORTUNITY' AND a.operation = 'CREATE_ORDER'
 GROUP BY TO_CHAR(TRUNC(a.created_at),'YYYY-MM-DD'), TRUNC(s.created_at)
 ORDER BY day DESC;
```

## 12. Error Classification Reference

```sql
CREATE OR REPLACE FUNCTION xx_classify_error(p_err IN VARCHAR2)
  RETURN VARCHAR2 IS
BEGIN
  IF p_err LIKE 'AUTH%'            THEN RETURN 'TERMINAL';  -- credential
  IF p_err LIKE 'VALID%'           THEN RETURN 'TERMINAL';  -- bad data
  IF p_err LIKE 'API_REJECT%'      THEN RETURN 'TERMINAL';  -- EBS rejected
  IF p_err LIKE '%ORA-%'           THEN RETURN 'RETRYABLE'; -- transient DB
  IF p_err LIKE 'RETRYABLE%'       THEN RETURN 'RETRYABLE';
  IF p_err LIKE '%timeout%'        THEN RETURN 'RETRYABLE';
  IF p_err LIKE '%503%'            THEN RETURN 'RETRYABLE';
  RETURN 'TERMINAL';   -- unknown → do not retry; inspect
END;
```