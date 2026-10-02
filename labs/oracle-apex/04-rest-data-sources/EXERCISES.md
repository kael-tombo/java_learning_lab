# Exercises: REST Data Sources

## Exercise 1: Web Credentials & Basic API Call (Guided)
**Time**: 20 minutes  
**Difficulty**: Beginner

### Objective
Store an API key securely and make a GET request to a mock shipment tracking API.

### Steps
1. **Create Web Credential**:
   - Shared Components → Web Credentials → Create
   - Name: `MOCK_SHIPMENT_API`
   - Type: API Key
   - API Key: `tk_test_12345` (mock key)
   - Click Create

2. **Test Credential** (SQL Workshop):
   ```sql
   SELECT APEX_WEB_SERVICE.MAKE_REST_REQUEST(
       p_url => 'https://httpbin.org/get',
       p_http_method => 'GET',
       p_credential_static_id => 'MOCK_SHIPMENT_API'
   ) FROM DUAL;
   ```

3. **Create Page with API Call**:
   - Page Item: `P1_TRACKING` (Text, default: `1Z999AA10123456784`)
   - Button: "Track"
   - Dynamic Action: Click → Execute PL/SQL
   ```sql
   DECLARE
       l_resp CLOB;
   BEGIN
       l_resp := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
           p_url => 'https://httpbin.org/get?tracking=' || APEX_UTIL.URL_ENCODE(:P1_TRACKING),
           p_http_method => 'GET',
           p_credential_static_id => 'MOCK_SHIPMENT_API',
           p_timeout => 10
       );
       :P1_RAW_RESPONSE := l_resp;
   END;
   ```
   - True Action 2: Set Value on `P1_STATUS` from JSON
     ```sql
     -- In same DA, add PL/SQL:
     APEX_JSON.PARSE(:P1_RAW_RESPONSE);
     :P1_STATUS := APEX_JSON.GET_VARCHAR2('args.tracking');
     ```

### Verification
- [ ] Web Credential created
- [ ] Button click returns JSON in `P1_RAW_RESPONSE`
- [ ] `P1_STATUS` shows tracking number

---

## Exercise 2: Web Source Module for Shipment Tracking
**Time**: 25 minutes  
**Difficulty**: Beginner-Intermediate

### Objective
Create a declarative Web Source Module and use it in a region.

### Steps
1. **Create Web Source Module**:
   - Shared Components → Web Sources → Create
   - Name: `Shipment Tracking`
   - Base URL: `https://httpbin.org/`
   - Authentication: None (httpbin doesn't need auth)

2. **Define Operation**:
   - Name: `Track Shipment`
   - URL Pattern: `get`
   - Method: GET
   - Parameters:
     - `tracking` (Query, String, Required)
   - Response Profile: JSON

3. **Create Web Source Region**:
   - Page Region → Type: Web Source
   - Web Source: `Shipment Tracking`
   - Operation: `Track Shipment`
   - Parameter: `tracking` → Page Item `P1_TRACKING`
   - Columns to Display: `args.tracking`, `headers.User-Agent`, `origin`

4. **Test**: Enter tracking number → region shows parsed response

### Verification
- [ ] Web Source Module created with operation
- [ ] Region displays parsed JSON fields
- [ ] Changing `P1_TRACKING` and refreshing updates region

---

## Exercise 3: File Upload with Validation
**Time**: 25 minutes  
**Difficulty**: Intermediate

### Objective
Upload PDF/image files with MIME type and size validation.

### Steps
1. **Create Table**:
   ```sql
   CREATE TABLE uploaded_docs (
       doc_id       NUMBER PRIMARY KEY,
       filename     VARCHAR2(500),
       mime_type    VARCHAR2(100),
       file_size    NUMBER,
       file_content BLOB,
       uploaded_by  VARCHAR2(100),
       uploaded_at  DATE DEFAULT SYSDATE
   );
   CREATE SEQUENCE doc_seq START WITH 1;
   ```

2. **Page Items**:
   - `P1_FILE` (File Browse): Storage=APEX Workspace Files, Max Size=10485760, Types=pdf,png,jpg,jpeg
   - `P1_CATEGORY` (Select List): INVOICE, LABEL, PROOF, OTHER

3. **Validation (Before Submit)**:
   ```sql
   DECLARE
       l_mime VARCHAR2(100);
       l_size NUMBER;
   BEGIN
       l_mime := APEX_FILE_MANAGER.GET_FILE_MIME_TYPE(:P1_FILE);
       l_size := APEX_FILE_MANAGER.GET_FILE_SIZE(:P1_FILE);
       
       IF l_size > 5242880 THEN  -- 5MB
           RAISE_APPLICATION_ERROR(-20001, 'File exceeds 5 MB limit');
       END IF;
       
       IF l_mime NOT IN ('application/pdf','image/png','image/jpeg') THEN
           RAISE_APPLICATION_ERROR(-20002, 'Only PDF, PNG, JPEG allowed. Got: ' || l_mime);
       END IF;
   END;
   ```

4. **Process (After Submit)**:
   ```sql
   INSERT INTO uploaded_docs (doc_id, filename, mime_type, file_size, file_content, uploaded_by)
   VALUES (
       doc_seq.NEXTVAL,
       :P1_FILE,
       APEX_FILE_MANAGER.GET_FILE_MIME_TYPE(:P1_FILE),
       APEX_FILE_MANAGER.GET_FILE_SIZE(:P1_FILE),
       APEX_FILE_MANAGER.GET_FILE_CONTENT(:P1_FILE),
       :APP_USER
   );
   ```

5. **Display Region** (Classic Report):
   ```sql
   SELECT doc_id, filename, mime_type, file_size, uploaded_at,
          APEX_PAGE.GET_URL(p_page => :APP_PAGE_ID, p_items => 'P1_DL_ID', p_values => doc_id) AS download_link
   FROM uploaded_docs
   ORDER BY uploaded_at DESC;
   ```

### Verification
- [ ] Valid PDF/PNG/JPG uploads succeed
- [ ] >5MB file shows validation error
- [ ] .txt/.exe files rejected
- [ ] Report shows uploaded files with download links

---

## Exercise 4: File Download with Inline Preview
**Time**: 20 minutes  
**Difficulty**: Intermediate

### Objective
Download files and preview PDF/images inline.

### Steps
1. **Page Item**: `P1_DL_ID` (Hidden)

2. **On-Demand Process** (AJAX Callback): `GET_DOCUMENT`
   ```sql
   DECLARE
       l_doc uploaded_docs%ROWTYPE;
   BEGIN
       SELECT * INTO l_doc FROM uploaded_docs WHERE doc_id = :P1_DL_ID;
       
       OWA_UTIL.MIME_HEADER(l_doc.mime_type, FALSE);
       HTP.P('Content-Disposition: inline; filename="' || l_doc.filename || '"');
       HTP.P('Content-Length: ' || l_doc.file_size);
       OWA_UTIL.HTTP_HEADER_CLOSE;
       WPG_DOCLOAD.DOWNLOAD_FILE(l_doc.file_content);
   EXCEPTION
       WHEN NO_DATA_FOUND THEN
           HTP.P('File not found');
   END;
   ```

3. **Dynamic Action** on Download Link Click:
   - Selection Type: jQuery Selector → `.download-link`
   - Event: Click
   - True Action: Execute JavaScript
   ```javascript
   var docId = $(this.triggeringElement).data('doc-id');
   apex.server.process('GET_DOCUMENT', { x01: docId }, {
       dataType: 'binary',  // Not needed for iframe approach
       success: function() {
           // Alternative: use iframe for preview
           var url = apex.util.apexAjaxUrl('GET_DOCUMENT', { x01: docId });
           $('#preview-modal .modal-body').html(
               '<iframe src="' + url + '" style="width:100%;height:500px;border:none;"></iframe>'
           );
           $('#preview-modal').modal('show');
       }
   });
   ```

4. **Add Preview Modal** to Page (Static HTML region):
   ```html
   <div id="preview-modal" class="modal fade" tabindex="-1">
       <div class="modal-dialog modal-lg">
           <div class="modal-content">
               <div class="modal-header">
                   <h5 class="modal-title">Document Preview</h5>
                   <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
               </div>
               <div class="modal-body"></div>
           </div>
       </div>
   </div>
   ```

### Verification
- [ ] Click download link → file downloads
- [ ] Click preview button → modal shows PDF/image inline
- [ ] Large files stream correctly

---

## Exercise 5: ORDS REST Service for Shipments
**Time**: 30 minutes  
**Difficulty**: Advanced

### Objective
Expose shipments data via ORDS REST API with pagination and nested documents.

### Prerequisites
- ORDS enabled on schema
- `shipments` and `shipment_documents` tables from walkthrough

### Steps
1. **Create Module & Template**:
   ```sql
   BEGIN
       ORDS.DEFINE_MODULE(
           p_module_name    => 'shipments.v1',
           p_base_path      => '/shipments/v1/',
           p_items_per_page => 25
       );
       
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
   ```

2. **Single Shipment with Documents**:
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
                        s.created_date
           ]'
       );
       COMMIT;
   END;
   /
   ```

3. **Enable Schema & Test**:
   ```sql
   BEGIN
       ORDS.ENABLE_SCHEMA(p_enabled => TRUE);
       COMMIT;
   END;
   /
   -- Test in browser:
   -- https://your-server/ords/your-schema/shipments/v1/shipments/
   -- https://your-server/ords/your-schema/shipments/v1/shipments/10000
   ```

4. **Add POST Handler** (Update Status):
   ```sql
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
                       :response_body := '{"error":"Not found"}';
                   ELSE
                       :status_code := 200;
                       :response_body := '{"message":"Updated"}';
                   END IF;
               END;
           ]'
       );
       COMMIT;
   END;
   /
   ```

### Verification
- [ ] GET /shipments returns paginated array
- [ ] GET /shipments/:id includes nested documents array
- [ ] POST /shipments/:id with JSON `{"status":"DELIVERED"}` updates record
- [ ] Response codes correct (200, 404)

---

## Exercise 6: Bulk CSV Import with Batched API Calls
**Time**: 30 minutes  
**Difficulty**: Advanced

### Objective
Upload CSV of tracking numbers, call batch API, upsert results.

### Steps
1. **Create Page**: `P2_CSV_FILE` (File Browse, Type: CSV)

2. **Process** (After Submit):
   ```sql
   DECLARE
       l_data       APEX_DATA_PARSER.T_TABLE;
       l_track_nums APEX_T_VARCHAR2;
       l_response   CLOB;
       l_batch      CLOB;
       l_count      NUMBER := 0;
   BEGIN
       -- Parse CSV
       l_data := APEX_DATA_PARSER.PARSE(
           p_content   => APEX_FILE_MANAGER.GET_FILE_CONTENT(:P2_CSV_FILE),
           p_file_name => :P2_CSV_FILE,
           p_format    => 'CSV'
       );
       
       -- Collect tracking numbers (assume first column)
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
           
           -- Mock API call (replace with real)
           l_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
               p_url        => 'https://httpbin.org/post',
               p_http_method => 'POST',
               p_body       => l_batch,
               p_timeout    => 30
           );
           
           -- Parse and upsert (mock response parsing)
           APEX_JSON.PARSE(l_response);
           -- In real scenario: parse actual API response
           
           l_count := l_count + LEAST(50, l_track_nums.COUNT - batch_start + 1);
       END LOOP;
       
       :P2_RESULT := l_count || ' tracking numbers processed in batches of 50.';
   END;
   ```

3. **Display Result**: Page item `P2_RESULT` (Display Only)

### Verification
- [ ] CSV with 200 tracking numbers processes in 4 batches
- [ ] Each batch shows in debug log
- [ ] Result message shows correct count

---

## Exercise 7: Retry Logic Wrapper
**Time**: 20 minutes  
**Difficulty**: Advanced

### Objective
Create reusable procedure for resilient API calls.

### Steps
1. **Create Procedure**:
   ```sql
   CREATE OR REPLACE PROCEDURE resilient_api_call(
       p_url       IN VARCHAR2,
       p_method    IN VARCHAR2 DEFAULT 'GET',
       p_body      IN CLOB DEFAULT NULL,
       p_cred      IN VARCHAR2,
       p_response  OUT CLOB,
       p_max_retry IN NUMBER DEFAULT 3
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
                   IF l_attempt >= p_max_retry THEN
                       RAISE_APPLICATION_ERROR(-20001, 
                           'API failed after ' || p_max_retry || ' attempts: ' || l_last_err);
                   END IF;
                   DBMS_LOCK.SLEEP(l_attempt * 2);  -- 2s, 4s, 6s...
           END;
       END LOOP;
   END;
   /
   ```

2. **Test Page**:
   - Button: "Test Retry"
   - DA: Execute PL/SQL
   ```sql
   DECLARE
       l_resp CLOB;
   BEGIN
       resilient_api_call(
           p_url      => 'https://httpbin.org/status/500',  -- Returns 500
           p_cred     => 'MOCK_SHIPMENT_API',
           p_response => l_resp
       );
   EXCEPTION
       WHEN OTHERS THEN
           :P1_ERROR := 'Expected error: ' || SQLERRM;
   END;
   ```
   - Try with `https://httpbin.org/status/200` for success case

### Verification
- [ ] 500 endpoint triggers 3 retries with increasing delays
- [ ] 200 endpoint succeeds on first try
- [ ] Error message shows attempt count

---

## Exercise 8: API Call Audit Logging
**Time**: 15 minutes  
**Difficulty**: Intermediate

### Objective
Log all API calls with request/response for debugging.

### Steps
1. **Create Log Table**:
   ```sql
   CREATE TABLE api_audit_log (
       log_id        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
       endpoint      VARCHAR2(500),
       http_method   VARCHAR2(10),
       request_body  CLOB,
       response_body CLOB,
       http_status   NUMBER,
       duration_ms   NUMBER,
       error_msg     VARCHAR2(4000),
       called_by     VARCHAR2(100),
       created_at    DATE DEFAULT SYSDATE
   );
   ```

2. **Wrapper Procedure**:
   ```sql
   CREATE OR REPLACE PROCEDURE logged_api_call(
       p_url      IN VARCHAR2,
       p_method   IN VARCHAR2,
       p_body     IN CLOB,
       p_cred     IN VARCHAR2,
       p_response OUT CLOB
   ) IS
       l_start    NUMBER := DBMS_UTILITY.GET_TIME;
       l_status   NUMBER;
       l_err      VARCHAR2(4000);
   BEGIN
       BEGIN
           p_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
               p_url => p_url, p_http_method => p_method,
               p_body => p_body, p_credential_static_id => p_cred
           );
           l_status := 200;
       EXCEPTION
           WHEN OTHERS THEN
               l_status := 500;
               l_err := SQLERRM;
               RAISE;
       END;
   EXCEPTION
       WHEN OTHERS THEN
           INSERT INTO api_audit_log (
               endpoint, http_method, request_body, response_body,
               http_status, duration_ms, error_msg, called_by
           ) VALUES (
               p_url, p_method, p_body, p_response,
               l_status, (DBMS_UTILITY.GET_TIME - l_start) * 10,
               l_err, :APP_USER
           );
           RAISE;
   END;
   ```

3. **Test**: Call wrapper → check `api_audit_log`

### Verification
- [ ] Successful calls logged with status 200
- [ ] Failed calls logged with status 500 and error message
- [ ] Duration captured in milliseconds

---

## Solutions Reference
- `WORKED_EXAMPLE.sql` — Complete SQL for all exercises
- `MINI_PROJECT/` — Weather dashboard with 3 APIs
- `REAL_WORLD_PROJECT/` — Logistics portal with full document lifecycle