-- =====================================================================
-- WORKED EXAMPLE: REST Data Sources - Complete SQL/PLSQL
-- Lab 04: REST Data Sources
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. DATABASE SCHEMA
-- ---------------------------------------------------------------------

-- Shipments table
CREATE TABLE shipments (
    shipment_id        NUMBER PRIMARY KEY,
    tracking_number    VARCHAR2(100) UNIQUE NOT NULL,
    carrier            VARCHAR2(50),
    origin             VARCHAR2(200),
    destination        VARCHAR2(200),
    status             VARCHAR2(50),
    estimated_delivery DATE,
    actual_delivery    DATE,
    last_api_sync      DATE,
    last_api_response  CLOB,
    created_by         VARCHAR2(100),
    created_date       DATE DEFAULT SYSDATE,
    updated_date       DATE
);

-- Shipment documents
CREATE TABLE shipment_documents (
    doc_id          NUMBER PRIMARY KEY,
    shipment_id     NUMBER NOT NULL REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    filename        VARCHAR2(500) NOT NULL,
    mime_type       VARCHAR2(100),
    file_size       NUMBER,
    file_content    BLOB,
    file_charset    VARCHAR2(50),
    doc_category    VARCHAR2(50) CHECK (doc_category IN ('PROOF_OF_DELIVERY','INVOICE','LABEL','OTHER')),
    uploaded_by     VARCHAR2(100),
    uploaded_date   DATE DEFAULT SYSDATE
);

-- API call audit log
CREATE TABLE api_call_log (
    call_id         NUMBER PRIMARY KEY,
    endpoint        VARCHAR2(500),
    request_body    CLOB,
    response_body   CLOB,
    http_status     NUMBER,
    duration_ms     NUMBER,
    error_msg       VARCHAR2(4000),
    created_by      VARCHAR2(100),
    created_date    DATE DEFAULT SYSDATE
);

-- Sequences
CREATE SEQUENCE shipment_seq START WITH 10000;
CREATE SEQUENCE doc_seq START WITH 1000;
CREATE SEQUENCE api_log_seq START WITH 1;

-- Indexes
CREATE INDEX idx_shipments_tracking ON shipments(tracking_number);
CREATE INDEX idx_shipments_status ON shipments(status);
CREATE INDEX idx_docs_shipment ON shipment_documents(shipment_id);
CREATE INDEX idx_api_log_date ON api_call_log(created_date);

-- Sample data
INSERT INTO shipments VALUES (shipment_seq.NEXTVAL, '1Z999AA10123456784', 'UPS', 'New York, NY', 'Los Angeles, CA', 'IN_TRANSIT', SYSDATE + 3, NULL, NULL, NULL, 'APP', SYSDATE, NULL);
INSERT INTO shipments VALUES (shipment_seq.NEXTVAL, '9400111899223456789012', 'USPS', 'Chicago, IL', 'Miami, FL', 'DELIVERED', SYSDATE - 1, SYSDATE - 1, NULL, NULL, 'APP', SYSDATE, NULL);
INSERT INTO shipments VALUES (shipment_seq.NEXTVAL, '789012345678', 'FedEx', 'Seattle, WA', 'Austin, TX', 'PENDING', SYSDATE + 5, NULL, NULL, NULL, 'APP', SYSDATE, NULL);
COMMIT;

-- ---------------------------------------------------------------------
-- 2. WEB CREDENTIAL (Run in Shared Components UI, not SQL)
-- ---------------------------------------------------------------------
/*
Shared Components → Web Credentials → Create
  Name: SHIPMENT_API_KEY
  Type: API Key
  API Key: tk_test_mock_key_12345
  (For demo, using httpbin.org which doesn't require auth)
*/

-- ---------------------------------------------------------------------
-- 3. BASIC API CALL WITH APEX_WEB_SERVICE
-- ---------------------------------------------------------------------

-- Test call to httpbin.org (echoes request)
DECLARE
    l_response CLOB;
BEGIN
    l_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
        p_url => 'https://httpbin.org/get?tracking=1Z999AA10123456784',
        p_http_method => 'GET',
        -- p_credential_static_id => 'SHIPMENT_API_KEY',
        p_timeout => 10
    );
    DBMS_OUTPUT.PUT_LINE('Response: ' || SUBSTR(l_response, 1, 200));
END;
/

-- Parse JSON response
DECLARE
    l_response CLOB;
    l_tracking VARCHAR2(100);
BEGIN
    l_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
        p_url => 'https://httpbin.org/get?tracking=1Z999AA10123456784',
        p_http_method => 'GET',
        p_timeout => 10
    );
    
    APEX_JSON.PARSE(l_response);
    l_tracking := APEX_JSON.GET_VARCHAR2('args.tracking');
    DBMS_OUTPUT.PUT_LINE('Tracking: ' || l_tracking);
END;
/

-- ---------------------------------------------------------------------
-- 4. RESILIENT API CALL WITH RETRY LOGIC
-- ---------------------------------------------------------------------

CREATE OR REPLACE PROCEDURE call_api_with_retry(
    p_url       IN VARCHAR2,
    p_method    IN VARCHAR2 DEFAULT 'GET',
    p_body      IN CLOB DEFAULT NULL,
    p_cred      IN VARCHAR2 DEFAULT NULL,
    p_response  OUT CLOB,
    p_retries   IN NUMBER DEFAULT 3
) IS
    l_attempt   NUMBER := 0;
    l_last_err  VARCHAR2(4000);
BEGIN
    LOOP
        l_attempt := l_attempt + 1;
        BEGIN
            p_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
                p_url             => p_url,
                p_http_method     => p_method,
                p_body            => p_body,
                p_credential_static_id => p_cred,
                p_timeout         => 10
            );
            RETURN;  -- Success
        EXCEPTION
            WHEN OTHERS THEN
                l_last_err := SQLERRM;
                IF l_attempt >= p_retries THEN
                    RAISE_APPLICATION_ERROR(-20001, 
                        'API failed after ' || p_retries || ' attempts: ' || l_last_err);
                END IF;
                DBMS_LOCK.SLEEP(l_attempt * 2);  -- 2s, 4s, 6s...
        END;
    END LOOP;
END call_api_with_retry;
/

-- Test retry (httpbin.org/status/500 returns 500)
DECLARE
    l_resp CLOB;
BEGIN
    call_api_with_retry(
        p_url => 'https://httpbin.org/status/500',
        p_cred => NULL,
        p_response => l_resp,
        p_retries => 2
    );
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Expected error: ' || SQLERRM);
END;
/

-- ---------------------------------------------------------------------
-- 5. LOGGED API CALL WITH AUDIT
-- ---------------------------------------------------------------------

CREATE OR REPLACE PROCEDURE logged_api_call(
    p_url      IN VARCHAR2,
    p_method   IN VARCHAR2 DEFAULT 'GET',
    p_body     IN CLOB DEFAULT NULL,
    p_cred     IN VARCHAR2 DEFAULT NULL,
    p_response OUT CLOB
) IS
    l_start    NUMBER := DBMS_UTILITY.GET_TIME;
    l_status   NUMBER := 200;
    l_err      VARCHAR2(4000);
BEGIN
    BEGIN
        p_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
            p_url => p_url, p_http_method => p_method,
            p_body => p_body, p_credential_static_id => p_cred,
            p_timeout => 10
        );
    EXCEPTION
        WHEN OTHERS THEN
            l_status := 500;
            l_err := SQLERRM;
            RAISE;
    END;
EXCEPTION
    WHEN OTHERS THEN
        INSERT INTO api_call_log (
            endpoint, http_method, request_body, response_body,
            http_status, duration_ms, error_msg, created_by
        ) VALUES (
            p_url, p_method, p_body, p_response,
            l_status, (DBMS_UTILITY.GET_TIME - l_start) * 10,
            l_err, :APP_USER
        );
        RAISE;
END logged_api_call;
/

-- Test logged call
DECLARE
    l_resp CLOB;
BEGIN
    logged_api_call(
        p_url => 'https://httpbin.org/get?test=audit',
        p_response => l_resp
    );
    DBMS_OUTPUT.PUT_LINE('Logged call succeeded');
END;
/

SELECT * FROM api_call_log ORDER BY created_date DESC;

-- ---------------------------------------------------------------------
-- 6. SHIPMENT TRACKING API INTEGRATION (Mock)
-- ---------------------------------------------------------------------

-- Simulated tracking API response structure:
/*
{
  "tracking_number": "1Z999AA10123456784",
  "status": "in_transit",
  "location": "Memphis, TN",
  "estimated_delivery": "2026-01-20",
  "events": [
    {"date": "2026-01-15T10:00:00Z", "location": "New York, NY", "description": "Picked up"},
    {"date": "2026-01-16T08:30:00Z", "location": "Memphis, TN", "description": "In transit"}
  ]
}
*/

-- Page Process: Sync Tracking Status (Dynamic Action PL/SQL)
DECLARE
    l_response CLOB;
    l_status   VARCHAR2(50);
    l_location VARCHAR2(200);
    l_est_del  VARCHAR2(20);
BEGIN
    -- Call mock API (using httpbin to simulate)
    l_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
        p_url => 'https://httpbin.org/get?tracking=' || APEX_UTIL.URL_ENCODE(:P2_TRACKING_NUMBER),
        p_http_method => 'GET',
        p_timeout => 10
    );

    -- Log API call
    INSERT INTO api_call_log VALUES (
        api_log_seq.NEXTVAL,
        '/mock/track/' || :P2_TRACKING_NUMBER,
        NULL,
        l_response,
        200,
        NULL,
        NULL,
        :APP_USER,
        SYSDATE
    );

    -- Parse response (mock parsing - real API would have different structure)
    APEX_JSON.PARSE(l_response);
    -- Simulate extracting status from mock response
    l_status := 'IN_TRANSIT';
    l_location := 'Memphis, TN';
    l_est_del := TO_CHAR(SYSDATE + 3, 'YYYY-MM-DD');

    -- Update shipment record
    UPDATE shipments SET
        status = l_status,
        last_api_sync = SYSDATE,
        last_api_response = l_response,
        updated_date = SYSDATE
    WHERE tracking_number = :P2_TRACKING_NUMBER;

    -- Set page items for display
    :P2_TRACKING_STATUS := l_status;
    :P2_CURRENT_LOCATION := l_location;
    :P2_ESTIMATED_DELIVERY := l_est_del;

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        INSERT INTO api_call_log VALUES (
            api_log_seq.NEXTVAL,
            '/mock/track/' || :P2_TRACKING_NUMBER,
            NULL,
            SQLERRM,
            500,
            NULL,
            SQLERRM,
            :APP_USER,
            SYSDATE
        );
        :P2_TRACKING_STATUS := 'API Error - using cached data';
        :P2_CURRENT_LOCATION := 'Unavailable';
        COMMIT;
END;
/

-- Tracking Timeline Query (Classic Report Region)
SELECT
    event_date,
    location,
    description
FROM JSON_TABLE(
    (SELECT last_api_response FROM shipments WHERE tracking_number = :P2_TRACKING_NUMBER),
    '$.events[*]' COLUMNS (
        event_date  VARCHAR2(30) PATH '$.date',
        location    VARCHAR2(200) PATH '$.location',
        description VARCHAR2(500) PATH '$.description'
    )
)
ORDER BY event_date DESC;

-- ---------------------------------------------------------------------
-- 7. FILE UPLOAD PROCESSING (APEX 23.2+)
-- ---------------------------------------------------------------------

-- Page Validation (Before Submit): File Validation
DECLARE
    l_mime VARCHAR2(100);
    l_size NUMBER;
BEGIN
    l_mime := APEX_FILE_MANAGER.GET_FILE_MIME_TYPE(:P2_FILE);
    l_size := APEX_FILE_MANAGER.GET_FILE_SIZE(:P2_FILE);

    IF l_size > 10485760 THEN  -- 10 MB
        RAISE_APPLICATION_ERROR(-20001, 'File exceeds 10 MB limit');
    END IF;

    IF l_mime NOT IN ('application/pdf','image/png','image/jpeg','image/gif') THEN
        RAISE_APPLICATION_ERROR(-20002, 'Unsupported file type: ' || l_mime);
    END IF;
END;

-- Page Process (After Submit): Insert Document
DECLARE
    l_doc_id NUMBER;
BEGIN
    l_doc_id := doc_seq.NEXTVAL;

    INSERT INTO shipment_documents (
        doc_id, shipment_id, filename, mime_type,
        file_size, file_content, doc_category,
        uploaded_by, uploaded_date
    ) VALUES (
        l_doc_id,
        :P2_SHIPMENT_ID,
        :P2_FILE,
        APEX_FILE_MANAGER.GET_FILE_MIME_TYPE(:P2_FILE),
        APEX_FILE_MANAGER.GET_FILE_SIZE(:P2_FILE),
        APEX_FILE_MANAGER.GET_FILE_CONTENT(:P2_FILE),
        :P2_DOC_CATEGORY,
        :APP_USER,
        SYSDATE
    );

    :P2_UPLOAD_MSG := 'Document uploaded successfully (ID: ' || l_doc_id || ')';
END;

-- ---------------------------------------------------------------------
-- 8. FILE DOWNLOAD (On-Demand AJAX Callback)
-- ---------------------------------------------------------------------

-- Process Name: GET_DOCUMENT
-- Type: On-Demand (AJAX Callback)
DECLARE
    l_doc shipment_documents%ROWTYPE;
BEGIN
    SELECT * INTO l_doc
    FROM shipment_documents
    WHERE doc_id = :P2_DOWNLOAD_ID;

    OWA_UTIL.MIME_HEADER(l_doc.mime_type, FALSE);
    HTP.P('Content-Disposition: inline; filename="' || l_doc.filename || '"');
    HTP.P('Content-Length: ' || l_doc.file_size);
    OWA_UTIL.HTTP_HEADER_CLOSE;
    WPG_DOCLOAD.DOWNLOAD_FILE(l_doc.file_content);
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        HTP.P('Document not found');
END;

-- ---------------------------------------------------------------------
-- 9. DOCUMENT LIST QUERY (Classic Report)
-- ---------------------------------------------------------------------

SELECT
    d.doc_id,
    d.filename,
    d.mime_type,
    d.file_size,
    d.doc_category,
    d.uploaded_by,
    d.uploaded_date,
    APEX_PAGE.GET_URL(
        p_page => :APP_PAGE_ID,
        p_items => 'P2_DOWNLOAD_ID',
        p_values => d.doc_id
    ) AS download_link
FROM shipment_documents d
WHERE d.shipment_id = :P2_SHIPMENT_ID
ORDER BY d.uploaded_date DESC;

-- ---------------------------------------------------------------------
-- 10. ORDS REST SERVICE DEFINITIONS
-- ---------------------------------------------------------------------

-- Enable ORDS for schema
BEGIN
    ORDS.ENABLE_SCHEMA(p_enabled => TRUE);
    COMMIT;
END;
/

-- Module: shipments.v1
BEGIN
    ORDS.DEFINE_MODULE(
        p_module_name    => 'shipments.v1',
        p_base_path      => '/shipments/v1/',
        p_items_per_page => 25
    );
    COMMIT;
END;
/

-- Template: shipments (collection)
BEGIN
    ORDS.DEFINE_TEMPLATE(
        p_module_name => 'shipments.v1',
        p_pattern     => 'shipments'
    );

    ORDS.DEFINE_HANDLER(
        p_module_name => 'shipments.v1',
        p_pattern     => 'shipments',
        p_method      => 'GET',
        p_source_type => 'json/collection',
        p_source      => q'[
            SELECT shipment_id, tracking_number, carrier,
                   origin, destination, status,
                   estimated_delivery, actual_delivery,
                   created_date
            FROM shipments
            ORDER BY created_date DESC
        ]'
    );
    COMMIT;
END;
/

-- Template: shipments/:id (single with documents)
BEGIN
    ORDS.DEFINE_TEMPLATE(
        p_module_name => 'shipments.v1',
        p_pattern     => 'shipments/:id'
    );

    ORDS.DEFINE_HANDLER(
        p_module_name => 'shipments.v1',
        p_pattern     => 'shipments/:id',
        p_method      => 'GET',
        p_source_type => 'json/collection',
        p_source      => q'[
            SELECT s.*,
                   JSON_ARRAYAGG(
                       JSON_OBJECT(
                           'doc_id' KEY d.doc_id,
                           'filename' KEY d.filename,
                           'mime_type' KEY d.mime_type,
                           'category' KEY d.doc_category
                       ) FORMAT JSON
                   ) AS documents
            FROM shipments s
            LEFT JOIN shipment_documents d ON d.shipment_id = s.shipment_id
            WHERE s.shipment_id = :id
            GROUP BY s.shipment_id, s.tracking_number, s.carrier,
                     s.origin, s.destination, s.status,
                     s.estimated_delivery, s.actual_delivery,
                     s.last_api_sync, s.created_date
        ]'
    );
    COMMIT;
END;
/

-- POST Handler: Update Status
BEGIN
    ORDS.DEFINE_HANDLER(
        p_module_name => 'shipments.v1',
        p_pattern     => 'shipments/:id',
        p_method      => 'POST',
        p_source_type => 'plsql/block',
        p_source      => q'[
            BEGIN
                UPDATE shipments
                SET status = :status,
                    updated_date = SYSDATE
                WHERE shipment_id = :id;

                IF SQL%ROWCOUNT = 0 THEN
                    :status_code := 404;
                    :response_body := '{"error":"Shipment not found"}';
                ELSE
                    :status_code := 200;
                    :response_body := '{"message":"Status updated","shipment_id":' || :id || '}';
                END IF;
            END;
        ]'
    );
    COMMIT;
END;
/

-- Test endpoints:
-- GET https://server/ords/schema/shipments/v1/shipments/
-- GET https://server/ords/schema/shipments/v1/shipments/10000
-- POST https://server/ords/schema/shipments/v1/shipments/10000
--   Body: {"status": "DELIVERED"}

-- ---------------------------------------------------------------------
-- 11. BULK CSV IMPORT WITH BATCHED API
-- ---------------------------------------------------------------------

-- Page Process (After Submit): Bulk Import
DECLARE
    l_data       APEX_DATA_PARSER.T_TABLE;
    l_track_nums APEX_T_VARCHAR2;
    l_response   CLOB;
    l_batch      CLOB;
    l_count      NUMBER := 0;
BEGIN
    -- Parse CSV
    l_data := APEX_DATA_PARSER.PARSE(
        p_content   => APEX_FILE_MANAGER.GET_FILE_CONTENT(:P3_CSV_FILE),
        p_file_name => :P3_CSV_FILE,
        p_format    => 'CSV'
    );

    -- Collect tracking numbers (assume first column, skip header if present)
    FOR i IN 1..l_data.COUNT LOOP
        l_track_nums.EXTEND;
        l_track_nums(l_track_nums.LAST) := l_data(i).COLUMN_01;
    END LOOP;

    -- Batch API calls (50 per batch)
    FOR batch_start IN 1..l_track_nums.COUNT BY 50 LOOP
        l_batch := '{"tracking_numbers": [';
        FOR j IN batch_start..LEAST(batch_start + 49, l_track_nums.COUNT) LOOP
            IF j > batch_start THEN l_batch := l_batch || ','; END IF;
            l_batch := l_batch || '"' || APEX_JSON.ESCAPE(l_track_nums(j)) || '"';
        END LOOP;
        l_batch := l_batch || ']}';

        -- Mock batch API call
        l_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
            p_url        => 'https://httpbin.org/post',
            p_http_method => 'POST',
            p_body       => l_batch,
            p_timeout    => 30
        );

        -- Parse and upsert (in real scenario, parse actual API response)
        APEX_JSON.PARSE(l_response);
        
        -- Simulate processing each tracking number
        FOR k IN 1..APEX_JSON.GET_COUNT('json.tracking_numbers') LOOP
            DECLARE
                l_tn VARCHAR2(100) := APEX_JSON.GET_VARCHAR2('json.tracking_numbers[%d]', k);
            BEGIN
                MERGE INTO shipments s
                USING (SELECT l_tn AS tn FROM DUAL) src
                ON (s.tracking_number = src.tn)
                WHEN MATCHED THEN UPDATE SET
                    s.last_api_sync = SYSDATE,
                    s.updated_date = SYSDATE
                WHEN NOT MATCHED THEN INSERT (
                    shipment_id, tracking_number, carrier, status, created_by, created_date
                ) VALUES (
                    shipment_seq.NEXTVAL, src.tn, 'UNKNOWN', 'PENDING', :APP_USER, SYSDATE
                );
                l_count := l_count + 1;
            END;
        END LOOP;
    END LOOP;

    :P3_IMPORT_RESULT := l_count || ' shipments imported/updated in batches of 50.';
    COMMIT;
END;
/

-- ---------------------------------------------------------------------
-- 12. CIRCUIT BREAKER PACKAGE
-- ---------------------------------------------------------------------

CREATE OR REPLACE PACKAGE circuit_breaker AS
    PROCEDURE record_success(p_endpoint VARCHAR2);
    PROCEDURE record_failure(p_endpoint VARCHAR2);
    FUNCTION is_open(p_endpoint VARCHAR2) RETURN BOOLEAN;
    PROCEDURE reset(p_endpoint VARCHAR2);
END circuit_breaker;
/

CREATE OR REPLACE PACKAGE BODY circuit_breaker AS
    g_failures       PLS_INTEGER := 0;
    g_last_failure   DATE;
    g_threshold      CONSTANT PLS_INTEGER := 5;
    g_timeout_min    CONSTANT NUMBER := 1;  -- minutes

    PROCEDURE record_success(p_endpoint VARCHAR2) IS
    BEGIN
        g_failures := 0;
        g_last_failure := NULL;
    END;

    PROCEDURE record_failure(p_endpoint VARCHAR2) IS
    BEGIN
        g_failures := g_failures + 1;
        g_last_failure := SYSDATE;
        IF g_failures >= g_threshold THEN
            INSERT INTO circuit_breaker_log (endpoint, opened_at, state)
            VALUES (p_endpoint, SYSDATE, 'OPEN');
        END IF;
    END;

    FUNCTION is_open(p_endpoint VARCHAR2) RETURN BOOLEAN IS
    BEGIN
        RETURN g_failures >= g_threshold
           AND g_last_failure IS NOT NULL
           AND g_last_failure + (g_timeout_min / 1440) > SYSDATE;
    END;

    PROCEDURE reset(p_endpoint VARCHAR2) IS
    BEGIN
        g_failures := 0;
        g_last_failure := NULL;
        INSERT INTO circuit_breaker_log (endpoint, opened_at, state)
        VALUES (p_endpoint, SYSDATE, 'RESET');
    END;
END circuit_breaker;
/

-- Circuit breaker log table
CREATE TABLE circuit_breaker_log (
    log_id     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    endpoint   VARCHAR2(500),
    opened_at  DATE,
    state      VARCHAR2(20)
);

-- Usage in API wrapper:
/*
IF circuit_breaker.is_open('shipment_tracking_api') THEN
    RAISE_APPLICATION_ERROR(-20001, 'Circuit breaker open for shipment API');
END IF;

BEGIN
    call_api_with_retry(...);
    circuit_breaker.record_success('shipment_tracking_api');
EXCEPTION
    WHEN OTHERS THEN
        circuit_breaker.record_failure('shipment_tracking_api');
        RAISE;
END;
*/

-- ---------------------------------------------------------------------
-- 13. VERIFICATION QUERIES
-- ---------------------------------------------------------------------

-- Check shipments
SELECT shipment_id, tracking_number, carrier, status, last_api_sync
FROM shipments
ORDER BY created_date DESC;

-- Check documents
SELECT doc_id, shipment_id, filename, mime_type, file_size, doc_category
FROM shipment_documents
ORDER BY uploaded_date DESC;

-- Check API audit log
SELECT call_id, endpoint, http_status, duration_ms, error_msg, created_date
FROM api_call_log
ORDER BY created_date DESC;

-- Check ORDS endpoints (run in browser or curl)
-- GET /ords/schema/shipments/v1/shipments/
-- GET /ords/schema/shipments/v1/shipments/10000

-- Cleanup (if needed)
/*
DROP TABLE circuit_breaker_log;
DROP PACKAGE circuit_breaker;
DROP PROCEDURE logged_api_call;
DROP PROCEDURE call_api_with_retry;
DROP TABLE api_call_log;
DROP TABLE shipment_documents;
DROP TABLE shipments;
*/

-- =====================================================================
-- END OF WORKED EXAMPLE
-- =====================================================================