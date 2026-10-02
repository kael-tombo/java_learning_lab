# Flashcards: REST Data Sources

## Web Credentials & Authentication

---
**Q**: Where to store API keys securely in APEX?
**A**: Shared Components → Web Credentials → APEX Credential Vault (encrypted). Reference by Static ID.

---
**Q**: How to use Web Credential in PL/SQL API call?
**A**: `APEX_WEB_SERVICE.MAKE_REST_REQUEST(p_credential_static_id => 'MY_CREDS', ...)`

---
**Q**: What authentication types does Web Credentials support?
**A**: API Key, OAuth 2.0 Client Credentials, OAuth 2.0 Authorization Code, Basic Auth, Custom.

---
**Q**: Critical parameter to prevent hanging on external API calls?
**A**: `p_timeout => 10` (seconds). Default 180s is too long for UX.

---
**Q**: How to use corporate proxy for API calls?
**A**: `p_proxy_override => 'proxy.corp.com:8080'` in MAKE_REST_REQUEST.

---

## JSON Parsing (APEX_JSON)

---
**Q**: Parse JSON CLOB into memory?
**A**: `APEX_JSON.PARSE(l_response_clob)`

---
**Q**: Get scalar value from parsed JSON?
**A**: `APEX_JSON.GET_VARCHAR2('path.to.field')` — also GET_NUMBER, GET_DATE, GET_BOOLEAN.

---
**Q**: Iterate JSON array `items`?
**A**: `FOR i IN 1..APEX_JSON.GET_COUNT('items') LOOP val := APEX_JSON.GET_VARCHAR2('items[%d].name', i); END LOOP;`

---
**Q**: Check if field exists before getting?
**A**: `IF APEX_JSON.DOES_EXIST('optional_field') THEN ... END IF;`

---
**Q**: Parse only subset of large JSON?
**A**: `APEX_JSON.PARSE(l_clob, p_path => 'results[1]')` — parses only that path.

---
**Q**: Free memory after APEX_JSON.WRITE operations?
**A**: `APEX_JSON.FREE_OUTPUT`

---

## Web Source Modules (Declarative)

---
**Q**: What is a Web Source Module?
**A**: Declarative REST client definition: base URL, auth, operations (endpoints), parameters, response profiles.

---
**Q**: How to use Web Source in a region?
**A**: Region Type = Web Source → Select Module + Operation → Map parameters to page items.

---
**Q**: Parameter binding types in Web Source?
**A**: Path (`{param}`), Query (`?param=`), Header, Body (JSON template).

---
**Q**: Call Web Source from PL/SQL?
**A**: `APEX_WEB_SOURCE.GET_DATA(p_web_source_name, p_operation_name, p_parameters, p_format, p_max_rows)`

---
**Q**: Where is Web Source metadata stored?
**A**: `APEX_APPLICATION_WEB_SOURCES`, `APEX_APPLICATION_WS_OPERATIONS`, `APEX_APPLICATION_WS_PARAMETERS`.

---

## File Upload (APEX 23.2+)

---
**Q**: File Browse item storage options?
**A**: APEX Workspace Files (temporary, auto-cleanup) or BLOB in table (permanent).

---
**Q**: Get uploaded file content (BLOB)?
**A**: `APEX_FILE_MANAGER.GET_FILE_CONTENT(:P1_FILE)`

---
**Q**: Get MIME type of uploaded file?
**A**: `APEX_FILE_MANAGER.GET_FILE_MIME_TYPE(:P1_FILE)`

---
**Q**: Get file size in bytes?
**A**: `APEX_FILE_MANAGER.GET_FILE_SIZE(:P1_FILE)`

---
**Q**: Validate file before submit?
**A**: Validation (Before Submit) → PL/SQL calling APEX_FILE_MANAGER functions → RAISE_APPLICATION_ERROR if invalid.

---
**Q**: Clean up temporary file after processing?
**A**: `APEX_FILE_MANAGER.DELETE_FILE(:P1_FILE)` or auto-cleanup on session end.

---

## File Download & Preview

---
**Q**: On-Demand process for file download?
**A**: Process Type = On-Demand (AJAX Callback) → PL/SQL with OWA_UTIL + WPG_DOCLOAD.

---
**Q**: Headers for inline preview (not download)?
**A**: `OWA_UTIL.MIME_HEADER(mime, FALSE); HTP.P('Content-Disposition: inline; filename="..."'); OWA_UTIL.HTTP_HEADER_CLOSE; WPG_DOCLOAD.DOWNLOAD_FILE(blob);`

---
**Q**: JavaScript to preview PDF/image in modal?
**A**: `apex.server.process('GET_DOC', {x01: id}, {success: f(data) { $('#preview').html('<iframe src="data:'+mime+';base64,'+data+'">') }})`

---

## ORDS REST Services

---
**Q**: Create ORDS module?
**A**: `ORDS.DEFINE_MODULE(p_module_name=>'x.v1', p_base_path=>'/x/v1/', p_items_per_page=>50)`

---
**Q**: Define template (URL pattern)?
**A**: `ORDS.DEFINE_TEMPLATE(p_module_name=>'x.v1', p_pattern=>'items')`

---
**Q**: Define GET handler returning collection?
**A**: `ORDS.DEFINE_HANDLER(p_module_name=>'x.v1', p_pattern=>'items', p_method=>'GET', p_source_type=>'json/collection', p_source=>'SELECT ...')`

---
**Q**: Path parameter binding in SQL source?
**A**: Pattern `items/:id` → SQL uses `WHERE id = :id` (bind variable)

---
**Q**: Enable schema for ORDS?
**A**: `ORDS.ENABLE_SCHEMA(p_enabled => TRUE)`

---
**Q**: Handler source types?
**A**: `json/collection` (array), `json/item` (object), `plsql/block` (HTP output), `media/resource` (binary).

---
**Q**: Test ORDS endpoint?
**A**: `https://server/ords/schema/module/v1/pattern/`

---
**Q**: POST handler for updates?
**A**: `p_method=>'POST', p_source_type=>'plsql/block', p_source=>'BEGIN UPDATE ... :status_code := 200; END;'`

---

## Bulk CSV Processing

---
**Q**: Parse CSV file in APEX 23.1+?
**A**: `APEX_DATA_PARSER.PARSE(p_content => blob, p_file_name => 'x.csv', p_format => 'CSV')`

---
**Q**: Return type of PARSE?
**A**: `APEX_DATA_PARSER.T_TABLE` — associative array of records with `COLUMN_01..COLUMN_N`.

---
**Q**: Access column by header name?
**A**: If first row is header, `l_data(i).column_name` works. Otherwise `l_data(i).COLUMN_01`.

---
**Q**: Batch API calls for large datasets?
**A**: Loop in chunks (50-200), build JSON array, POST to batch endpoint, parse response, MERGE upsert.

---
**Q**: Idempotent upsert pattern?
**A**: `MERGE INTO target USING (SELECT :id AS id, :val AS val FROM DUAL) src ON (t.id = src.id) WHEN MATCHED THEN UPDATE ... WHEN NOT MATCHED THEN INSERT ...`

---

## Resilience Patterns

---
**Q**: Retry with exponential backoff?
**A**: `FOR attempt IN 1..3 LOOP BEGIN call(); RETURN; EXCEPTION WHEN OTHERS THEN DBMS_LOCK.SLEEP(attempt * 2); END; END LOOP; RAISE;`

---
**Q**: Circuit breaker purpose?
**A**: Stop calling failing endpoint after N failures for T minutes. Prevents cascade failures.

---
**Q**: Audit log for API calls?
**A**: Table with endpoint, request, response, status, duration, error. Insert in wrapper procedure.

---
**Q**: JSON injection prevention?
**A**: Use `APEX_JSON.WRITE` / `APEX_JSON.WRITE_OBJECT` — auto-escapes. Never concatenate strings into JSON.

---

## Debugging

---
**Q**: Enable APEX debug for REST calls?
**A**: URL: `&p_debug=YES&p_debug_level=9` → Search for "APEX_WEB_SERVICE" in debug output.

---
**Q**: Log request/response for troubleshooting?
**A**: Wrapper procedure inserts to `api_audit_log` table with `DBMS_UTILITY.GET_TIME` for duration.

---
**Q**: Test ORDS handler SQL?
**A**: Run handler source query directly in SQL Workshop with bind variables.

---

## Quick Reference: PL/SQL Patterns

| Task | Code |
|------|------|
| Secure API call | `APEX_WEB_SERVICE.MAKE_REST_REQUEST(p_credential_static_id=>'CREDS', p_timeout=>10)` |
| Parse JSON | `APEX_JSON.PARSE(clob); v := APEX_JSON.GET_VARCHAR2('path[%d]', i)` |
| Web Source call | `APEX_WEB_SOURCE.GET_DATA(p_web_source_name=>'X', p_operation_name=>'Y')` |
| File upload (23.2) | `APEX_FILE_MANAGER.GET_FILE_CONTENT/BLOB/MIME/SIZE(:P1_FILE)` |
| File download | `OWA_UTIL.MIME_HEADER; HTP.P('Content-Disposition: inline...'); WPG_DOCLOAD.DOWNLOAD_FILE(blob)` |
| ORDS GET collection | `ORDS.DEFINE_HANDLER(p_source_type=>'json/collection', p_source=>'SELECT ...')` |
| CSV parse | `APEX_DATA_PARSER.PARSE(p_content=>blob, p_format=>'CSV')` |
| Retry with backoff | `FOR i IN 1..3 LOOP BEGIN ... EXCEPTION WHEN OTHERS THEN DBMS_LOCK.SLEEP(i*2); END; END LOOP;` |
| Circuit breaker | Package tracking failures + timeout |
| Audit log | `INSERT INTO api_log(endpoint, req, resp, status, duration_ms, error, user) VALUES(...)` |
| JSON safe write | `APEX_JSON.OPEN_OBJECT; APEX_JSON.WRITE('key', :val); APEX_JSON.CLOSE_OBJECT;` |

---

## Study Tips
1. **Create Web Credential first** — always, before any API code
2. **Test API in SQL Workshop** — `SELECT APEX_WEB_SERVICE.MAKE_REST_REQUEST(...) FROM DUAL`
3. **Use httpbin.org** — free test endpoints: `/get`, `/post`, `/status/200`, `/status/500`, `/delay/3`
4. **Enable ORDS early** — `ORDS.ENABLE_SCHEMA` required before testing
5. **Batch size = 50-100** — balance between round trips and payload limits
6. **Always `COMMIT` after `APEX_MAIL.SEND`** — mail queued on commit
7. **Validate files server-side** — client validation is bypassable
8. **Use `MERGE` for upserts** — safe for retries, idempotent