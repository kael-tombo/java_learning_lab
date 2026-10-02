# Theory: REST Data Sources in Oracle APEX

## Why REST Integration in APEX?

Modern applications rarely operate in isolation. They consume external APIs (payment gateways, shipping carriers, CRM systems) and expose their own data via REST for mobile apps, partners, and microservices. APEX provides declarative and programmatic tools for both directions.

## Consuming External REST APIs

### 1. Web Credentials (Secure Secret Storage)

**Never hardcode API keys.** Store them in APEX Credential Vault:

```
Shared Components → Web Credentials → Create
  Name: SHIPMENT_API_KEY
  Type: API Key
  API Key: tk_live_xxxxxxxxxxxxxxxx
  Vault: APEX Credential Vault (encrypted)
```

**Usage in PL/SQL:**
```sql
APEX_WEB_SERVICE.MAKE_REST_REQUEST(
    p_url                     => 'https://api.carrier.com/v1/track/12345',
    p_http_method             => 'GET',
    p_credential_static_id    => 'SHIPMENT_API_KEY',
    p_timeout                 => 10
);
```

### 2. Web Source Modules (Declarative REST Client)

Define the API once, use everywhere:

```
Shared Components → Web Sources → Create
  Name: Shipment Tracking API
  Base URL: https://api.mock-shipping.com/v2/
  Authentication: API Key → SHIPMENT_API_KEY
```

**Operations (Endpoints):**
| Operation | Method | URL Pattern | Parameters |
|-----------|--------|-------------|------------|
| Track Shipment | GET | `track/{tracking_number}` | Path: tracking_number |
| Batch Track | POST | `track/batch` | Body: `{"tracking_numbers": [...]}` |

**Use in APEX:**
- **Web Source Region**: Auto-generates report/form from operation
- **PL/SQL**: `APEX_WEB_SOURCE.GET_DATA(p_web_source_name => 'Shipment Tracking API', ...)`

### 3. APEX_WEB_SERVICE (Programmatic Control)

Low-level PL/SQL API for complex scenarios:

```sql
DECLARE
    l_response CLOB;
BEGIN
    l_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
        p_url             => 'https://api.example.com/v1/resource',
        p_http_method     => 'POST',
        p_body            => '{"key":"value"}',
        p_credential_static_id => 'MY_CREDENTIAL',
        p_wallet_path     => NULL,  -- For HTTPS with custom certs
        p_timeout         => 30,    -- Seconds
        p_proxy_override  => 'proxy.company.com:8080'
    );
    
    -- Parse JSON response
    APEX_JSON.PARSE(l_response);
    l_status := APEX_JSON.GET_VARCHAR2('status');
END;
```

**Key Parameters:**
| Parameter | Purpose |
|-----------|---------|
| `p_timeout` | Critical! Prevents hanging pages (default: 180s, set 5-30s) |
| `p_wallet_path` | For mTLS or custom CA certificates |
| `p_proxy_override` | Corporate proxy |
| `p_transfer_timeout` | Total transfer timeout |

## JSON Parsing with APEX_JSON

```sql
DECLARE
    l_response CLOB := '{"tracking_number":"1Z999","status":"in_transit","events":[{"date":"2026-01-15","location":"Memphis, TN"}]}';
BEGIN
    APEX_JSON.PARSE(l_response);
    
    -- Scalar values
    l_tracking := APEX_JSON.GET_VARCHAR2('tracking_number');
    l_status   := APEX_JSON.GET_VARCHAR2('status');
    
    -- Array iteration
    FOR i IN 1..APEX_JSON.GET_COUNT('events') LOOP
        l_date := APEX_JSON.GET_VARCHAR2('events[%d].date', i);
        l_loc  := APEX_JSON.GET_VARCHAR2('events[%d].location', i);
    END LOOP;
    
    -- Nested objects
    APEX_JSON.PARSE(l_response, 'events[1]');  -- Parse subset
END;
```

## File Upload in APEX

### File Browse Item
```
Page Item: P1_FILE
Type: File Browse
Settings:
  - Storage Type: APEX Workspace Files (temporary) or BLOB in table
  - Allowed File Types: application/pdf,image/png,image/jpeg
  - Max File Size: 10485760 (10 MB)
  - Multiple: No
```

### Processing Upload (After Submit)

**APEX 23.2+ (Recommended):**
```sql
DECLARE
    l_doc_id NUMBER;
BEGIN
    l_doc_id := doc_seq.NEXTVAL;
    INSERT INTO documents (doc_id, filename, mime_type, file_size, file_content, ...)
    VALUES (
        l_doc_id,
        :P1_FILE,
        APEX_FILE_MANAGER.GET_FILE_MIME_TYPE(:P1_FILE),
        APEX_FILE_MANAGER.GET_FILE_SIZE(:P1_FILE),
        APEX_FILE_MANAGER.GET_FILE_CONTENT(:P1_FILE),
        ...
    );
END;
```

**Legacy (APEX_APPLICATION globals):**
```sql
-- G_X01 = file_id, G_X02 = mime_type, G_X03 = file_size, G_X04 = BLOB content
INSERT INTO documents (...) VALUES (..., APEX_APPLICATION.G_X04, ...);
```

### File Validation (Before Submit - Validation)
```sql
DECLARE
    l_mime VARCHAR2(100);
    l_size NUMBER;
BEGIN
    l_mime := APEX_FILE_MANAGER.GET_FILE_MIME_TYPE(:P1_FILE);
    l_size := APEX_FILE_MANAGER.GET_FILE_SIZE(:P1_FILE);
    
    IF l_size > 10485760 THEN
        RAISE_APPLICATION_ERROR(-20001, 'File exceeds 10 MB limit');
    END IF;
    
    IF l_mime NOT IN ('application/pdf','image/png','image/jpeg','image/gif') THEN
        RAISE_APPLICATION_ERROR(-20002, 'Unsupported file type: ' || l_mime);
    END IF;
END;
```

## File Download and Preview

### Download Process (On-Demand AJAX Callback)
```sql
DECLARE
    l_doc documents%ROWTYPE;
BEGIN
    SELECT * INTO l_doc FROM documents WHERE doc_id = :P1_DOWNLOAD_ID;
    
    OWA_UTIL.MIME_HEADER(l_doc.mime_type, FALSE);
    HTP.P('Content-Disposition: inline; filename="' || l_doc.filename || '"');
    HTP.P('Content-Length: ' || l_doc.file_size);
    OWA_UTIL.HTTP_HEADER_CLOSE;
    WPG_DOCLOAD.DOWNLOAD_FILE(l_doc.file_content);
END;
```

### Inline Preview (JavaScript)
```javascript
function previewDocument(docId) {
    apex.server.process('GET_DOCUMENT', { x01: docId }, {
        success: function(data) {
            var previewUrl = 'data:' + data.mimeType + ';base64,' + data.base64Content;
            $('#preview-container').html(
                '<iframe src="' + previewUrl + '" width="100%" height="600px"></iframe>'
            );
        }
    });
}
```

## Exposing REST Services via ORDS

### Architecture
```
External Client → ORDS (ORDS_METADATA) → Your Schema → PL/SQL / SQL
```

### Step-by-Step

**1. Define Module:**
```sql
BEGIN
    ORDS.DEFINE_MODULE(
        p_module_name    => 'shipments.v1',
        p_base_path      => '/shipments/v1/',
        p_items_per_page => 50
    );
    COMMIT;
END;
/
```

**2. Define Template (URL Pattern):**
```sql
BEGIN
    ORDS.DEFINE_TEMPLATE(
        p_module_name => 'shipments.v1',
        p_pattern     => 'shipments'
    );
    COMMIT;
END;
/
```

**3. Define Handler (GET Collection):**
```sql
BEGIN
    ORDS.DEFINE_HANDLER(
        p_module_name => 'shipments.v1',
        p_pattern     => 'shipments',
        p_method      => 'GET',
        p_source_type => 'json/collection',
        p_source      => q'[
            SELECT shipment_id, tracking_number, carrier,
                   origin, destination, status,
                   estimated_delivery, actual_delivery
            FROM shipments
            ORDER BY created_date DESC
        ]'
    );
    COMMIT;
END;
/
```

**4. Single Item Handler (with nested documents):**
```sql
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
                           'mime_type' KEY d.mime_type
                       ) FORMAT JSON
                   ) AS documents
            FROM shipments s
            LEFT JOIN shipment_documents d ON d.shipment_id = s.shipment_id
            WHERE s.shipment_id = :id
            GROUP BY s.shipment_id, s.tracking_number, ...
        ]'
    );
    COMMIT;
END;
/
```

**5. Enable Schema:**
```sql
BEGIN
    ORDS.ENABLE_SCHEMA(p_enabled => TRUE);
    COMMIT;
END;
/
```

**Test:** `https://server/ords/schema/shipments/v1/shipments/`

### Handler Source Types
| Type | Use Case |
|------|----------|
| `json/collection` | Array of objects (default pagination) |
| `json/item` | Single object |
| `plsql/block` | Custom PL/SQL with HTP output |
| `media/resource` | Binary file serving |

## Bulk CSV Processing

### APEX_DATA_PARSER (23.1+)
```sql
DECLARE
    l_data APEX_DATA_PARSER.T_TABLE;
BEGIN
    l_data := APEX_DATA_PARSER.PARSE(
        p_content   => APEX_FILE_MANAGER.GET_FILE_CONTENT(:P1_CSV_FILE),
        p_file_name => :P1_CSV_FILE,
        p_format    => 'CSV'
    );
    
    FOR i IN 1..l_data.COUNT LOOP
        -- l_data(i).COLUMN_01, COLUMN_02, etc.
        -- or l_data(i).<COLUMN_NAME> if header row
    END LOOP;
END;
```

### Batched API Calls (Resilience)
```sql
-- Process 1000 tracking numbers in batches of 100
FOR batch_start IN 1..l_track_nums.COUNT BY 100 LOOP
    l_batch := '{"tracking_numbers": [';
    FOR j IN batch_start..LEAST(batch_start+99, l_track_nums.COUNT) LOOP
        l_batch := l_batch || '"' || APEX_JSON.ESCAPE(l_track_nums(j)) || '",';
    END LOOP;
    l_batch := RTRIM(l_batch, ',') || ']}';
    
    l_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
        p_url        => 'https://api.carrier.com/v1/track/batch',
        p_http_method => 'POST',
        p_body       => l_batch,
        p_credential_static_id => 'CARRIER_API'
    );
    
    -- Parse and upsert
    APEX_JSON.PARSE(l_response);
    FOR i IN 1..APEX_JSON.GET_COUNT('results') LOOP
        MERGE INTO shipments s
        USING (SELECT ... FROM DUAL) src
        ON (s.tracking_number = src.tracking_number)
        WHEN MATCHED THEN UPDATE SET ...
        WHEN NOT MATCHED THEN INSERT ...;
    END LOOP;
END LOOP;
```

## Resilience Patterns

### Retry with Exponential Backoff
```sql
CREATE OR REPLACE PROCEDURE call_api_with_retry(
    p_url      IN VARCHAR2,
    p_response OUT CLOB,
    p_retries  IN NUMBER DEFAULT 3
) IS
    l_last_err VARCHAR2(4000);
BEGIN
    FOR attempt IN 1..p_retries LOOP
        BEGIN
            p_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
                p_url => p_url, p_http_method => 'GET',
                p_credential_static_id => 'MY_CREDS', p_timeout => 5
            );
            RETURN;
        EXCEPTION
            WHEN OTHERS THEN
                l_last_err := SQLERRM;
                IF attempt < p_retries THEN
                    DBMS_LOCK.SLEEP(attempt * 2);  -- 2s, 4s, 8s...
                END IF;
        END;
    END LOOP;
    RAISE_APPLICATION_ERROR(-20001, 'Failed after ' || p_retries || ' retries: ' || l_last_err);
END;
```

### Audit Logging
```sql
INSERT INTO api_call_log (call_id, endpoint, request_body, response_body, http_status, duration_ms, created_date)
VALUES (api_log_seq.NEXTVAL, p_url, p_request, l_response, 200, l_duration, SYSDATE);
```

### Circuit Breaker (Advanced)
```sql
-- Track failures in memory/table, stop calling if > 5 failures in 1 min
-- Use DBMS_REDACT or custom package for state
```

## Security Best Practices

1. **Never hardcode secrets** → Web Credentials
2. **Validate file uploads** → MIME type, size, virus scan
3. **Sanitize filenames** → Prevent path traversal
4. **HTTPS only** → Enforce in Web Source, ORDS
5. **Rate limiting** → ORDS: `p_items_per_page`, custom throttle
6. **CSRF on REST** → Session State Protection, custom headers
7. **CORS** → ORDS `ORDS.DEFINE_MODULE(..., p_cors_enabled => TRUE)`

## Summary: Integration Patterns

| Pattern | Tool | When |
|---------|------|------|
| Simple API call | Web Source Module | Standard CRUD on external API |
| Complex auth/flow | APEX_WEB_SERVICE | OAuth, custom headers, streaming |
| File upload | File Browse + APEX_FILE_MANAGER | User document upload |
| File download | On-Demand Process + WPG_DOCLOAD | Secure document retrieval |
| Expose data | ORDS DEFINE_MODULE/HANDLER | Mobile apps, partners, microservices |
| Bulk import | APEX_DATA_PARSER + Batched API | CSV/Excel with external enrichment |
| Resilience | Retry proc + Audit log | Production external dependencies |