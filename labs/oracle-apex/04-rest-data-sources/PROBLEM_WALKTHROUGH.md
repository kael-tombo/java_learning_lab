# Problem Walkthrough: Build a REST API Integration with File Upload and Download

## Problem Statement

A logistics company needs an APEX application that integrates with external REST APIs for shipment tracking and document management. The requirements are:

1. **REST API Integration**: Consume a third-party shipment tracking API to display real-time shipment status
2. **File Upload**: Attach delivery proof documents (PDF, images) to shipment records
3. **File Download**: Retrieve and display uploaded documents inline
4. **REST Service Exposure**: Expose an ORDS RESTful service for mobile apps to query shipment status
5. **Bulk Operations**: Upload CSV of tracking numbers and batch-retrieve status from the API
6. **Error Handling**: Graceful handling of API failures with retry logic and fallback display

### Technical Requirements
- APEX 23.2+
- ORDS enabled on the workspace schema
- External API: (simulated) shipment tracking endpoint
- File storage: APEX Workspace Files or Oracle Object Store
- CSV parsing via APEX_DATA_PARSER

### Success Criteria
- File uploads are virus-scanned and validated
- REST API calls complete within 5 seconds with timeout
- Files can be previewed directly in the browser
- ORDS endpoints return JSON with proper pagination headers
- Bulk CSV upload processes 1000+ records in under 30 seconds

---

## Step-by-Step Walkthrough

### Step 1: Database Schema

```sql
-- Shipments table
CREATE TABLE shipments (
    shipment_id     NUMBER PRIMARY KEY,
    tracking_number VARCHAR2(100) UNIQUE NOT NULL,
    carrier         VARCHAR2(50),
    origin          VARCHAR2(200),
    destination     VARCHAR2(200),
    status          VARCHAR2(50),
    estimated_delivery DATE,
    actual_delivery    DATE,
    last_api_sync      DATE,
    last_api_response  CLOB,
    created_by      VARCHAR2(100),
    created_date    DATE DEFAULT SYSDATE,
    updated_date    DATE
);

-- File attachments
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

-- API call log for audit
CREATE TABLE api_call_log (
    call_id         NUMBER PRIMARY KEY,
    endpoint        VARCHAR2(500),
    request_body    CLOB,
    response_body   CLOB,
    http_status     NUMBER,
    duration_ms     NUMBER,
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
INSERT INTO shipments VALUES (shipment_seq.NEXTVAL, '1Z999AA10123456784', 'UPS',
    'New York, NY', 'Los Angeles, CA', 'IN_TRANSIT',
    SYSDATE + 3, NULL, NULL, NULL, 'APP', SYSDATE, NULL);
INSERT INTO shipments VALUES (shipment_seq.NEXTVAL, '9400111899223456789012', 'USPS',
    'Chicago, IL', 'Miami, FL', 'DELIVERED',
    SYSDATE - 1, SYSDATE - 1, NULL, NULL, 'APP', SYSDATE, NULL);
INSERT INTO shipments VALUES (shipment_seq.NEXTVAL, '789012345678', 'FedEx',
    'Seattle, WA', 'Austin, TX', 'PENDING',
    SYSDATE + 5, NULL, NULL, NULL, 'APP', SYSDATE, NULL);

COMMIT;
```

### Step 2: Create Web Credential for External API

1. Navigate to **Shared Components → Web Credentials**
2. Create **New Credential**:
   - Name: `SHIPMENT_API_KEY`
   - Type: **API Key**
   - API Key: `tk_xxxxxxxxxxxxxxxxxxxx`
   - Store in: APEX credential vault

3. Test the credential:
   ```sql
   SELECT APEX_WEB_SERVICE.MAKE_REST_REQUEST(
       p_url => 'https://api.shipping-example.com/v1/status',
       p_http_method => 'GET',
       p_credential_static_id => 'SHIPMENT_API_KEY'
   ) FROM DUAL;
   ```

### Step 3: Create Web Source Module for Shipment Tracking

1. Navigate to **Shared Components → Web Sources**
2. Create **New Web Source**:
   - Name: **Shipment Tracking API**
   - Base URL: `https://api.mock-shipping.com/v2/`
   - Authentication: API Key (referencing `SHIPMENT_API_KEY`)

3. Define **Operations**:

   **GET Track Shipment**:
   - URL Pattern: `track/{tracking_number}`
   - Method: GET
   - Expected Response: JSON
   ```json
   {
       "tracking_number": "1Z999AA10123456784",
       "status": "in_transit",
       "location": "Memphis, TN",
       "estimated_delivery": "2026-08-02",
       "events": [
           {"date": "2026-07-28T10:00:00Z", "location": "New York, NY", "description": "Picked up"},
           {"date": "2026-07-29T08:30:00Z", "location": "Newark, NJ", "description": "Arrived at facility"},
           {"date": "2026-07-30T02:15:00Z", "location": "Memphis, TN", "description": "In transit"}
       ]
   }
   ```

   **POST Batch Track**:
   - URL Pattern: `track/batch`
   - Method: POST
   - Request Body: `{"tracking_numbers": ["..."]}`
   - Response: Array of tracking results

### Step 4: Create the Main Shipments Page

1. Create a new **Blank Page** named "Shipment Tracking"
2. Add an **Interactive Report** region:
   ```sql
   SELECT
       s.shipment_id,
       s.tracking_number,
       s.carrier,
       s.origin,
       s.destination,
       s.status,
       s.estimated_delivery,
       s.actual_delivery,
       s.last_api_sync,
       (SELECT COUNT(*) FROM shipment_documents d WHERE d.shipment_id = s.shipment_id) AS doc_count
   FROM shipments s
   ORDER BY s.created_date DESC
   ```

3. Link Column: Tracking Number links to Shipment Detail page

### Step 5: Shipment Detail Page with API Integration

Create a **Form Page** (Page 2) for shipment details. Add regions:

**Region 1: Shipment Information (Form)**

**Region 2: Real-Time Tracking Status (Dynamic Content)**

Create a **Dynamic Action** on page load:
- Event: **Page Load**
- Condition: `P2_TRACKING_NUMBER IS NOT NULL`

True Action: Execute PL/SQL
```sql
DECLARE
    l_response CLOB;
    l_status   VARCHAR2(50);
    l_parsed   APEX_JSON.T_VALUES;
BEGIN
    -- Call external tracking API
    l_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
        p_url             => 'https://api.mock-shipping.com/v2/track/' ||
                             APEX_UTIL.URL_ENCODE(:P2_TRACKING_NUMBER),
        p_http_method     => 'GET',
        p_credential_static_id => 'SHIPMENT_API_KEY',
        p_wallet_path     => NULL,
        p_timeout         => 10
    );

    -- Log API call
    INSERT INTO api_call_log VALUES (
        api_log_seq.NEXTVAL,
        '/v2/track/' || :P2_TRACKING_NUMBER,
        NULL,
        l_response,
        200,
        NULL,
        SYSDATE
    );

    -- Parse JSON response
    APEX_JSON.PARSE(l_response);
    l_status := APEX_JSON.GET_VARCHAR2('status');

    -- Update shipment record
    UPDATE shipments SET
        status = INITCAP(REPLACE(l_status, '_', ' ')),
        last_api_sync = SYSDATE,
        last_api_response = l_response,
        updated_date = SYSDATE
    WHERE shipment_id = :P2_SHIPMENT_ID;

    -- Set page items from response
    :P2_TRACKING_STATUS := INITCAP(REPLACE(l_status, '_', ' '));
    :P2_CURRENT_LOCATION := APEX_JSON.GET_VARCHAR2('location');
    :P2_ESTIMATED_DELIVERY := APEX_JSON.GET_VARCHAR2('estimated_delivery');

EXCEPTION
    WHEN OTHERS THEN
        -- Log error
        INSERT INTO api_call_log VALUES (
            api_log_seq.NEXTVAL,
            '/v2/track/' || :P2_TRACKING_NUMBER,
            NULL,
            SQLERRM,
            500,
            NULL,
            SYSDATE
        );
        :P2_TRACKING_STATUS := 'API Error — using cached data';
        :P2_CURRENT_LOCATION := 'Unavailable';
END;
```

**Region 3: Tracking Timeline** — Classic Report:
```sql
SELECT
    event_date,
    location,
    description
FROM JSON_TABLE(
    (SELECT last_api_response FROM shipments WHERE shipment_id = :P2_SHIPMENT_ID),
    '$.events[*]' COLUMNS (
        event_date  VARCHAR2(30) PATH '$.date',
        location    VARCHAR2(200) PATH '$.location',
        description VARCHAR2(500) PATH '$.description'
    )
)
ORDER BY event_date DESC
```

**Region 4: Sync Button** — Button that runs a dynamic action to re-fetch tracking status

### Step 6: File Upload Implementation

**Step 6.1: Create Upload Page/Region**

Add a region "Upload Document" on the detail page with:

1. **File Browse Item**: `P2_FILE` (File Browse)
   - Allowed File Types: `application/pdf,image/png,image/jpeg,image/gif`
   - Max File Size: 10485760 (10 MB)
   - Storage Type: **APEX Workspace Files** (or BLOB in table)

2. **Select List**: `P2_DOC_CATEGORY`
   - LOV: PROOF_OF_DELIVERY, INVOICE, LABEL, OTHER

3. **Button**: "Upload" — Submit page

**Step 6.2: Process Upload (After Submit)**

```sql
DECLARE
    l_doc_id NUMBER;
    l_file_id NUMBER;
BEGIN
    -- Get file from APEX temporary storage
    l_file_id := APEX_APPLICATION.G_X01;

    INSERT INTO shipment_documents (
        doc_id,
        shipment_id,
        filename,
        mime_type,
        file_size,
        file_content,
        doc_category,
        uploaded_by,
        uploaded_date
    ) VALUES (
        doc_seq.NEXTVAL,
        :P2_SHIPMENT_ID,
        :P2_FILE,  -- filename from the file item
        APEX_APPLICATION.G_X02,  -- MIME type
        APEX_APPLICATION.G_X03,  -- file size
        APEX_APPLICATION.G_X04,  -- file BLOB content
        :P2_DOC_CATEGORY,
        :APP_USER,
        SYSDATE
    );
END;
```

**Alternative: Using APEX_FILE_MANAGER** (APEX 23.2+)

```sql
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
        -- <!-- UNVERIFIED: APEX_FILE_MANAGER.* needs doc/DB confirmation — package and function signatures not verified against the APEX docs. Applies to all APEX_FILE_MANAGER calls in this file. -->
        APEX_FILE_MANAGER.GET_FILE_MIME_TYPE(:P2_FILE),
        APEX_FILE_MANAGER.GET_FILE_SIZE(:P2_FILE),
        APEX_FILE_MANAGER.GET_FILE_CONTENT(:P2_FILE),
        :P2_DOC_CATEGORY,
        :APP_USER,
        SYSDATE
    );
END;
```

**Step 6.3: File Validation (Before Submit)**

```sql
DECLARE
    l_mime VARCHAR2(100);
    l_size NUMBER;
BEGIN
    l_mime := APEX_FILE_MANAGER.GET_FILE_MIME_TYPE(:P2_FILE);
    l_size := APEX_FILE_MANAGER.GET_FILE_SIZE(:P2_FILE);

    IF l_size > 10485760 THEN
        RAISE_APPLICATION_ERROR(-20001, 'File exceeds 10 MB limit');
    END IF;

    IF l_mime NOT IN ('application/pdf','image/png','image/jpeg','image/gif') THEN
        RAISE_APPLICATION_ERROR(-20002, 'Unsupported file type: ' || l_mime);
    END IF;
END;
```

### Step 7: File Download and Preview

**Step 7.1: Document List Region**

Create a **Classic Report** showing uploaded documents:
```sql
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
        p_items => 'P2_DOWNLOAD_DOC',
        p_values => d.doc_id
    ) AS download_link
FROM shipment_documents d
WHERE d.shipment_id = :P2_SHIPMENT_ID
ORDER BY d.uploaded_date DESC
```

**Step 7.2: Download Process**

Create a **Page Process** (On Demand / AJAX Callback):

```sql
DECLARE
    l_doc shipment_documents%ROWTYPE;
BEGIN
    SELECT * INTO l_doc
    FROM shipment_documents
    WHERE doc_id = :P2_DOWNLOAD_DOC;

    -- Set response headers for download
    OWA_UTIL.MIME_HEADER(l_doc.mime_type, FALSE);
    HTP.P('Content-Disposition: inline; filename="' || l_doc.filename || '"');
    HTP.P('Content-Length: ' || l_doc.file_size);
    OWA_UTIL.HTTP_HEADER_CLOSE;
    WPG_DOCLOAD.DOWNLOAD_FILE(l_doc.file_content);
END;
```

**Step 7.3: Inline Preview via JavaScript**

For PDF and images, create a **Dynamic Action** on the download link:

```javascript
function previewDocument(docId) {
    apex.server.process('GET_DOCUMENT', {
        x01: docId
    }, {
        success: function(data) {
            // Show in modal or inline div
            var previewUrl = 'data:' + data.mimeType + ';base64,' + data.base64Content;
            $('#preview-container').html(
                '<iframe src="' + previewUrl + '" width="100%" height="600px"></iframe>'
            );
        }
    });
}
```

### Step 8: Expose ORDS RESTful Service

**Step 8.1: Create ORDS Module**

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

**Step 8.2: Create GET Handler — List Shipments**

```sql
BEGIN
    ORDS.DEFINE_TEMPLATE(
        p_module_name    => 'shipments.v1',
        p_pattern        => 'shipments'
    );

    ORDS.DEFINE_HANDLER(
        p_module_name    => 'shipments.v1',
        p_pattern        => 'shipments',
        p_method         => 'GET',
        p_source_type    => 'json/collection',
        p_source         => 'SELECT shipment_id, tracking_number, carrier,
                                    origin, destination, status,
                                    estimated_delivery, actual_delivery
                             FROM shipments
                             ORDER BY created_date DESC'
    );
    COMMIT;
END;
/
```

**Step 8.3: Create GET Handler — Single Shipment with Documents**

```sql
BEGIN
    ORDS.DEFINE_TEMPLATE(
        p_module_name    => 'shipments.v1',
        p_pattern        => 'shipments/:id'
    );

    ORDS.DEFINE_HANDLER(
        p_module_name    => 'shipments.v1',
        p_pattern        => 'shipments/:id',
        p_method         => 'GET',
        p_source_type    => 'json/collection',
        p_source         => 'SELECT s.shipment_id, s.tracking_number, s.carrier,
                                    s.origin, s.destination, s.status,
                                    s.estimated_delivery, s.actual_delivery,
                                    s.last_api_sync,
                                    -- MAX() because a CLOB cannot appear in GROUP BY (ORA-00979)
                                    MAX(s.last_api_response) AS last_api_response,
                                    s.created_by, s.created_date, s.updated_date,
                                    JSON_ARRAYAGG(
                                        JSON_OBJECT(
                                            ''doc_id'' KEY d.doc_id,
                                            ''filename'' KEY d.filename,
                                            ''mime_type'' KEY d.mime_type,
                                            ''doc_category'' KEY d.doc_category
                                        ) FORMAT JSON
                                    ) AS documents
                             FROM shipments s
                             LEFT JOIN shipment_documents d ON d.shipment_id = s.shipment_id
                             WHERE s.shipment_id = :id
                             GROUP BY s.shipment_id, s.tracking_number, s.carrier,
                                      s.origin, s.destination, s.status,
                                      s.estimated_delivery, s.actual_delivery,
                                      s.last_api_sync, s.created_by, s.created_date,
                                      s.updated_date'
    );
    COMMIT;
END;
/
```

**Step 8.4: Create POST Handler — Update Status**

```sql
BEGIN
    ORDS.DEFINE_HANDLER(
        p_module_name    => 'shipments.v1',
        p_pattern        => 'shipments/:id',
        p_method         => 'POST',
        p_source_type    => 'plsql/block',
        p_source         => 'BEGIN
                                UPDATE shipments
                                SET status = :status,
                                    updated_date = SYSDATE
                                WHERE shipment_id = :id;

                                IF SQL%ROWCOUNT = 0 THEN
                                    HTP(404, ''Shipment not found'');
                                ELSE
                                    HTP(200, ''Status updated'');
                                END IF;
                             END;'
    );
    COMMIT;
END;
/
```

**Step 8.5: Enable ORDS and Test**

```sql
-- Enable ORDS for the schema
BEGIN
    ORDS.ENABLE_SCHEMA(p_enabled => TRUE);
    COMMIT;
END;
/

-- Test: https://your-server/ords/your-schema/shipments/v1/shipments/
-- Test: https://your-server/ords/your-schema/shipments/v1/shipments/10000
```

### Step 9: Bulk CSV Upload

**Step 9.1: Create Upload Page**

1. New page: **Bulk Shipment Import**
2. **File Browse**: `P3_CSV_FILE` — accept `.csv`
3. **Button**: "Import and Track"

**Step 9.2: CSV Processing Process**

```sql
DECLARE
    l_data       APEX_DATA_PARSER.T_TABLE;
    l_track_nums APEX_T_VARCHAR2;
    l_response   CLOB;
    l_batch      CLOB;
    l_count      NUMBER := 0;
BEGIN
    -- Parse CSV file
    l_data := APEX_DATA_PARSER.PARSE(
        p_content   => APEX_FILE_MANAGER.GET_FILE_CONTENT(:P3_CSV_FILE),
        p_file_name => :P3_CSV_FILE,
        p_format    => 'CSV'
    );

    -- Collect tracking numbers
    FOR i IN 1..l_data.COUNT LOOP
        l_track_nums.EXTEND;
        l_track_nums(l_track_nums.LAST) := l_data(i).COLUMN_01;
    END LOOP;

    -- Batch call to API (max 100 per batch)
    FOR batch_start IN 1..l_track_nums.COUNT BY 100 LOOP
        -- Build JSON array for this batch
        l_batch := '{"tracking_numbers": [';
        FOR j IN batch_start..LEAST(batch_start + 99, l_track_nums.COUNT) LOOP
            IF j > batch_start THEN l_batch := l_batch || ','; END IF;
            l_batch := l_batch || '"' || APEX_JSON.ESCAPE(l_track_nums(j)) || '"';
        END LOOP;
        l_batch := l_batch || ']}';

        -- Call batch tracking API
        l_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
            p_url        => 'https://api.mock-shipping.com/v2/track/batch',
            p_http_method => 'POST',
            p_body       => l_batch,
            p_credential_static_id => 'SHIPMENT_API_KEY'
        );

        -- Parse batch response and upsert shipments
        APEX_JSON.PARSE(l_response);
        FOR i IN 1..APEX_JSON.GET_COUNT('results') LOOP
            MERGE INTO shipments s
            USING (
                SELECT
                    APEX_JSON.GET_VARCHAR2('results[' || i || '].tracking_number') AS tracking_number,
                    APEX_JSON.GET_VARCHAR2('results[' || i || '].status') AS status,
                    APEX_JSON.GET_VARCHAR2('results[' || i || '].location') AS location
                FROM DUAL
            ) src ON (s.tracking_number = src.tracking_number)
            WHEN MATCHED THEN UPDATE SET
                s.status = INITCAP(REPLACE(src.status, '_', ' ')),
                s.last_api_sync = SYSDATE,
                s.updated_date = SYSDATE
            WHEN NOT MATCHED THEN INSERT (
                shipment_id, tracking_number, status, created_by, created_date
            ) VALUES (
                shipment_seq.NEXTVAL, src.tracking_number,
                INITCAP(REPLACE(src.status, '_', ' ')),
                :APP_USER, SYSDATE
            );
            l_count := l_count + 1;
        END LOOP;
    END LOOP;

    :P3_IMPORT_RESULT := l_count || ' shipments imported/updated.';
END;
```

### Step 10: Error Handling and Resilience

**Retry Logic Wrapper**:
```sql
CREATE OR REPLACE PROCEDURE call_api_with_retry(
    p_url       IN VARCHAR2,
    p_response  OUT CLOB,
    p_retries   IN NUMBER DEFAULT 3
) IS
    l_last_error VARCHAR2(4000);
BEGIN
    FOR attempt IN 1..p_retries LOOP
        BEGIN
            p_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
                p_url => p_url,
                p_http_method => 'GET',
                p_credential_static_id => 'SHIPMENT_API_KEY',
                p_timeout => 5
            );
            RETURN;
        EXCEPTION
            WHEN OTHERS THEN
                l_last_error := SQLERRM;
                IF attempt < p_retries THEN
                    DBMS_LOCK.SLEEP(attempt * 2); -- exponential backoff
                END IF;
        END;
    END LOOP;
    RAISE_APPLICATION_ERROR(-20001, 'API call failed after ' || p_retries ||
                                     ' retries: ' || l_last_error);
END call_api_with_retry;
/
```

---

## Best Practices Applied

1. **REST API Security**: Credential stored in APEX vault, never hardcoded
2. **File Validation**: MIME type and size validation on upload
3. **Error Resilience**: Retry logic with exponential backoff for API calls
4. **Audit Trail**: API call log captures all requests, responses, and errors
5. **Batch Processing**: CSV upload with batched API calls (100 at a time)
6. **ORDS Standards**: Proper JSON collection output with pagination
7. **Resource Management**: Temporary file cleanup after processing

## Common Pitfalls to Avoid

1. **Hardcoded API keys**: Always use Web Credentials
2. **No timeout on API calls**: Set `p_timeout` to avoid hanging pages
3. **Ignoring API response errors**: Always check HTTP status codes
4. **Large file uploads without limits**: Enforce max file size
5. **XSS in file names**: Strip/escape file names before display
6. **No CSRF on REST endpoints**: Enable Session State Protection on ORDS handlers
7. **Memory issues with large BLOBs**: Use chunked streaming for large file downloads

## Extensions for Future Iterations

1. Webhook receiver endpoint for real-time tracking updates
2. PDF generation of shipping labels using APEX Office Print (AOP)
3. Image compression/resizing for uploaded photos
4. Virus scanning integration (ClamAV REST API)
5. Scheduled job for periodic API sync of active shipments
6. File versioning with document history tracking
