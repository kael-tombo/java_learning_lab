# Code Deep Dive: REST Data Sources Internals

## APEX_WEB_SERVICE Internals

### MAKE_REST_REQUEST Flow
```
PL/SQL Call
     │
     ▼
┌─────────────────────────────────────┐
│ UTL_HTTP / UTL_TCP (Internal)       │
│ 1. Resolve DNS                      │
│ 2. TCP Connect (with timeout)       │
│ 3. TLS Handshake (if HTTPS)         │
│ 4. Send HTTP Request                │
│    - Headers (Auth, Content-Type)   │
│    - Body (if POST/PUT)             │
│ 5. Read Response Headers            │
│ 6. Read Response Body (streaming)   │
│ 7. Close Connection                 │
└─────────────────────────────────────┘
     │
     ▼
Return CLOB (or BLOB for binary)
```

### Key Implementation Details

**Connection Pooling**: APEX uses `UTL_HTTP` which doesn't pool connections by default. Each call = new TCP connection.

**Wallet Handling**:
```sql
-- For custom CA or mTLS
APEX_WEB_SERVICE.MAKE_REST_REQUEST(
    p_wallet_path => 'file:/u01/wallets/my_wallet',
    p_wallet_pwd  => 'wallet_password'
);
```

**Proxy Support**:
```sql
p_proxy_override => 'proxy.corp.com:8080'
-- Bypasses database default proxy
```

### Error Handling
```sql
BEGIN
    l_resp := APEX_WEB_SERVICE.MAKE_REST_REQUEST(...);
EXCEPTION
    WHEN UTL_HTTP.END_OF_BODY THEN NULL;  -- Normal for streaming
    WHEN UTL_HTTP.REQUEST_FAILED THEN
        -- Network error, DNS, timeout
    WHEN UTL_HTTP.TOO_MANY_REQUESTS THEN
        -- 429 Rate limited
    WHEN OTHERS THEN
        -- SQLERRM contains HTTP status if available
END;
```

## APEX_JSON Internals

### Parsing Architecture
```
APEX_JSON.PARSE(p_json_clob)
     │
     ▼
┌─────────────────────────────────────┐
│ 1. Validate JSON syntax             │
│ 2. Build DOM tree in memory         │
│    (PL/SQL collections + temp LOBs) │
│ 3. Store in package state           │
│    (APEX_JSON.G_VALUES)             │
└─────────────────────────────────────┘
```

### Memory Considerations
- Large JSON (> 10MB) → PGA memory pressure
- Use `APEX_JSON.PARSE(p_json_clob, p_path => 'results[1]')` to parse subset
- Always `APEX_JSON.FREE_OUTPUT` after `APEX_JSON.WRITE` operations

### XPath-like Access
```sql
APEX_JSON.GET_VARCHAR2('orders[5].customer.name')     -- Array index + path
APEX_JSON.GET_VARCHAR2('orders[%d].customer.name', i) -- Loop variable
APEX_JSON.GET_COUNT('orders')                          -- Array length
APEX_JSON.DOES_EXIST('optional_field')                -- Null-safe check
```

## Web Source Module Internals

### Metadata Storage
```
APEX_APPLICATION_WEB_SOURCES
  - Module definition (base URL, auth)
APEX_APPLICATION_WS_OPERATIONS
  - Operations (endpoints, params, response profiles)
APEX_APPLICATION_WS_PARAMETERS
  - Parameters (path, query, header, body)
```

### Runtime Execution
```sql
-- When Web Source Region renders:
APEX_WEB_SOURCE.GET_DATA(
    p_web_source_name    => 'Shipment API',
    p_operation_name     => 'Track Shipment',
    p_parameters         => 'tracking_number=1Z999',
    p_format             => 'JSON',
    p_max_rows           => 100
);
```

**Parameter Binding**:
| Source | Syntax | Example |
|--------|--------|---------|
| Path | `{param}` | `track/{tracking_number}` |
| Query | `?param=value` | `?format=json&detail=true` |
| Header | `Header-Name: value` | `X-API-Version: 2` |
| Body | JSON template | `{"id": "{tracking_number}"}` |

## APEX_FILE_MANAGER Internals (23.2+)

### Temporary File Storage
```
User Upload → APEX Temp Table (WWV_FLOW_FILES$)
     │
     ├── GET_FILE_CONTENT → Returns BLOB
     ├── GET_FILE_MIME_TYPE → Detects from content/header
     ├── GET_FILE_SIZE → Returns bytes
     └── DELETE_FILE → Cleanup after processing
```

### Implementation
```sql
-- GET_FILE_CONTENT uses:
SELECT blob_content FROM wwv_flow_files$
WHERE name = :p_file_name AND security_group_id = :g_sgid;

-- MIME detection:
DBMS_LOB.SUBSTR(blob_content, 256, 1) → magic bytes
+ filename extension fallback
```

### Cleanup Critical
```sql
-- After processing, ALWAYS clean up:
APEX_FILE_MANAGER.DELETE_FILE(:P1_FILE);
-- Or bulk:
DELETE FROM wwv_flow_files$ WHERE name IN (SELECT ...);
```

## ORDS Handler Execution

### Request Flow
```
HTTP Request → ORDS Listener
     │
     ▼
┌─────────────────────────────────────┐
│ 1. Match Module → Template → Handler │
│ 2. Bind path params (:id)           │
│ 3. Bind query params (?q=...)       │
│ 4. Execute Source                   │
│    - SQL → Cursor → JSON            │
│    - PL/SQL → HTP output            │
│ 5. Format Response                  │
│    - json/collection → Array        │
│    - json/item → Single object      │
│    - media/resource → Binary        │
│ 6. Set Headers (Cache, CORS)        │
└─────────────────────────────────────┘
```

### JSON/Collection Source
```sql
-- Returns: {"items": [...], "hasMore": true, "limit": 50, "offset": 0, "count": 50}
-- Pagination: ?offset=50&limit=50
-- Filter: ?q={"status":"SHIPPED"} (if enabled)
```

### PL/SQL Block Handler (Full Control)
```sql
BEGIN
    ORDS.DEFINE_HANDLER(
        p_module_name => 'custom.v1',
        p_pattern     => 'export',
        p_method      => 'GET',
        p_source_type => 'plsql/block',
        p_source      => q'[
            DECLARE
                l_csv CLOB;
            BEGIN
                l_csv := generate_csv;
                OWA_UTIL.MIME_HEADER('text/csv', FALSE);
                HTP.P('Content-Disposition: attachment; filename="export.csv"');
                OWA_UTIL.HTTP_HEADER_CLOSE;
                HTP.PRN(l_csv);
            END;
        ]'
    );
END;
/
```

### Parameter Binding in Handlers
```sql
-- Path parameter :id → automatically bound
-- Query parameter ?status=X → :status
-- Header X-Custom → :x_custom (lowercase, hyphens to underscore)
-- Body JSON → :body (CLOB) or individual fields
```

## APEX_DATA_PARSER Internals

### Parse Flow
```
APEX_DATA_PARSER.PARSE(p_content, p_format)
     │
     ▼
┌─────────────────────────────────────┐
│ 1. Detect encoding (BOM, charset)   │
│ 2. Format-specific parser:          │
│    CSV: Custom state machine        │
│    XLSX: Apache POI (Java) → XML    │
│    JSON: APEX_JSON                  │
│    XML: DBMS_XMLPARSE               │
│ 3. Return T_TABLE (collection of    │
│    records with COLUMN_01..N or     │
│    named columns if header row)     │
└─────────────────────────────────────┘
```

### T_TABLE Structure
```sql
TYPE t_row IS RECORD (
    line_number   NUMBER,
    col_count     NUMBER,
    column_01     VARCHAR2(4000),
    column_02     VARCHAR2(4000),
    -- ... up to column_300
    column_300    VARCHAR2(4000)
);
TYPE t_table IS TABLE OF t_row INDEX BY PLS_INTEGER;
```

### Large File Handling
```sql
-- For files > 50MB, use streaming:
APEX_DATA_PARSER.PARSE(
    p_content   => blob_locator,  -- BLOB instead of CLOB
    p_format    => 'CSV',
    p_max_rows  => 10000          -- Limit rows
);
```

## Bulk API Processing Patterns

### Batch Size Optimization
```sql
-- Optimal batch size depends on:
-- - API rate limits (e.g., 100 req/min)
-- - Payload size (max 1-5 MB typical)
-- - Timeout (5-30s per batch)

-- Formula: batch_size = min(api_limit, payload_limit / avg_record_size)
-- Typical: 50-200 records per batch
```

### Idempotency for Retries
```sql
-- Use MERGE with unique key for safe retries
MERGE INTO shipments s
USING (SELECT :tracking AS tn, :status AS st FROM DUAL) src
ON (s.tracking_number = src.tn)
WHEN MATCHED THEN UPDATE SET
    s.status = src.st,
    s.last_sync = SYSDATE,
    s.sync_attempts = s.sync_attempts + 1
WHEN NOT MATCHED THEN INSERT (
    tracking_number, status, last_sync, sync_attempts
) VALUES (src.tn, src.st, SYSDATE, 1);
```

### Progress Tracking
```sql
-- Log table for resumable jobs
CREATE TABLE bulk_import_log (
    job_id        NUMBER,
    batch_num     NUMBER,
    status        VARCHAR2(20),  -- PENDING, PROCESSING, DONE, ERROR
    records_in    NUMBER,
    records_ok    NUMBER,
    records_err   NUMBER,
    error_msg     VARCHAR2(4000),
    started_at    DATE,
    completed_at  DATE
);
```

## Resilience Patterns Implementation

### Circuit Breaker (PL/SQL)
```sql
CREATE OR REPLACE PACKAGE circuit_breaker AS
    PROCEDURE record_success(p_endpoint VARCHAR2);
    PROCEDURE record_failure(p_endpoint VARCHAR2);
    FUNCTION is_open(p_endpoint VARCHAR2) RETURN BOOLEAN;
    PROCEDURE reset(p_endpoint VARCHAR2);
END;
/

CREATE OR REPLACE PACKAGE BODY circuit_breaker AS
    g_failures PLS_INTEGER := 0;
    g_last_failure DATE;
    g_threshold CONSTANT PLS_INTEGER := 5;
    g_timeout CONSTANT INTERVAL DAY TO SECOND := INTERVAL '1' MINUTE;
    
    PROCEDURE record_failure(p_endpoint VARCHAR2) IS
    BEGIN
        g_failures := g_failures + 1;
        g_last_failure := SYSDATE;
        IF g_failures >= g_threshold THEN
            -- Circuit open
            INSERT INTO circuit_breaker_log VALUES (p_endpoint, SYSDATE, 'OPEN');
        END IF;
    END;
    
    FUNCTION is_open(p_endpoint VARCHAR2) RETURN BOOLEAN IS
    BEGIN
        RETURN g_failures >= g_threshold 
           AND g_last_failure + g_timeout > SYSDATE;
    END;
END;
/
```

### Usage in API Call
```sql
IF circuit_breaker.is_open('shipment_api') THEN
    RAISE_APPLICATION_ERROR(-20001, 'Circuit breaker open for shipment API');
END IF;

BEGIN
    call_api_with_retry(p_url => l_url, p_response => l_resp);
    circuit_breaker.record_success('shipment_api');
EXCEPTION
    WHEN OTHERS THEN
        circuit_breaker.record_failure('shipment_api');
        RAISE;
END;
```

## Debugging REST Calls

### Enable Network Tracing
```sql
-- Database level (requires DBA)
EXEC DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
    host => 'api.example.com',
    ace  => xs$ace_type(privilege_list => xs$name_list('connect', 'resolve'))
);

-- APEX Debug
-- URL: &p_debug=YES&p_debug_level=9
-- Look for: "APEX_WEB_SERVICE: Request:", "Response status:", "Response body:"
```

### Log Request/Response
```sql
CREATE TABLE rest_debug_log (
    id          NUMBER GENERATED ALWAYS AS IDENTITY,
    endpoint    VARCHAR2(500),
    request_hdr CLOB,
    request_body CLOB,
    response_hdr CLOB,
    response_body CLOB,
    status_code NUMBER,
    duration_ms NUMBER,
    created_at  DATE DEFAULT SYSDATE
);

-- In wrapper procedure:
INSERT INTO rest_debug_log (...) VALUES (...);
```

## Performance Optimization

### Connection Reuse (Advanced)
```sql
-- Use UTL_HTTP directly for connection pooling
DECLARE
    l_req  UTL_HTTP.REQ;
    l_resp UTL_HTTP.RESP;
BEGIN
    l_req := UTL_HTTP.BEGIN_REQUEST(
        url => l_url,
        method => 'GET',
        http_version => 'HTTP/1.1'
    );
    UTL_HTTP.SET_HEADER(l_req, 'Authorization', 'Bearer ' || l_token);
    UTL_HTTP.SET_HEADER(l_req, 'Connection', 'keep-alive');
    l_resp := UTL_HTTP.GET_RESPONSE(l_req);
    -- Read body...
    UTL_HTTP.END_RESPONSE(l_resp);
END;
```

### Parallel Batch Processing
```sql
-- Use DBMS_SCHEDULER or APEX_AUTOMATION for parallel batches
-- Each batch runs in separate job
BEGIN
    FOR batch IN 1..10 LOOP
        DBMS_SCHEDULER.CREATE_JOB(
            job_name        => 'BATCH_JOB_' || batch,
            job_type        => 'PLSQL_BLOCK',
            job_action      => 'process_batch(' || batch || ');',
            enabled         => TRUE,
            auto_drop       => TRUE
        );
    END LOOP;
END;
```

## Security: Input Validation

### JSON Injection Prevention
```sql
-- NEVER concatenate into JSON
-- BAD: '{"tracking":"' || :P1_TRACK || '"}'
-- GOOD:
APEX_JSON.WRITE_OBJECT(
    p_name => 'tracking',
    p_value => :P1_TRACK  -- Auto-escaped
);
```

### File Upload Validation
```sql
-- Server-side validation (client can be bypassed)
DECLARE
    l_magic RAW(4);
BEGIN
    l_magic := DBMS_LOB.SUBSTR(:P1_FILE_BLOB, 4, 1);
    -- Check magic bytes
    IF l_magic NOT IN (HEXTORAW('25504446'),  -- PDF %PDF
                       HEXTORAW('89504E47'),  -- PNG
                       HEXTORAW('FFD8FFE0'),  -- JPEG
                       HEXTORAW('FFD8FFE1')) THEN
        RAISE_APPLICATION_ERROR(-20001, 'Invalid file format');
    END IF;
END;
```

## Summary: Key Code Patterns

| Task | Code Pattern |
|------|--------------|
| Secure API call | `APEX_WEB_SERVICE.MAKE_REST_REQUEST(p_credential_static_id=>'CREDS')` |
| Parse JSON | `APEX_JSON.PARSE(clob); val := APEX_JSON.GET_VARCHAR2('path')` |
| Web Source call | `APEX_WEB_SOURCE.GET_DATA(p_web_source_name=>'X', p_operation_name=>'Y')` |
| File upload (23.2) | `APEX_FILE_MANAGER.GET_FILE_CONTENT(:P1_FILE)` |
| File download | `OWA_UTIL.MIME_HEADER; WPG_DOCLOAD.DOWNLOAD_FILE(blob)` |
| ORDS GET collection | `ORDS.DEFINE_HANDLER(p_source_type=>'json/collection', p_source=>'SELECT...')` |
| CSV parse | `APEX_DATA_PARSER.PARSE(p_content=>blob, p_format=>'CSV')` |
| Retry with backoff | `FOR i IN 1..3 LOOP BEGIN ... EXCEPTION WHEN OTHERS THEN DBMS_LOCK.SLEEP(i*2); END; END LOOP;` |
| Circuit breaker | Package with failure count + timeout |
| Audit log | `INSERT INTO api_log(endpoint, req, resp, status, duration) VALUES(...)` |