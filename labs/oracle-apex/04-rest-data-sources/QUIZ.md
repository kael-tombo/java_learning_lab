# Quiz: REST Data Sources

---

## Question 1: Web Credentials Storage
**Where are API keys stored securely in APEX?**

A) In page item `P1_API_KEY` with Value Protected = Yes
B) In Application Definition → Security → API Keys
C) **Shared Components → Web Credentials → APEX Credential Vault**
D) In `apex_application.g_x01` during runtime

**Answer: C**

**Explanation**: Web Credentials store secrets encrypted in the APEX Credential Vault. They're referenced by static ID in `APEX_WEB_SERVICE` calls, never exposed in page source or session state.

---

## Question 2: APEX_WEB_SERVICE Timeout
**What is the critical parameter to prevent hanging pages when calling external APIs?**

A) `p_wallet_path`
B) `p_proxy_override`
C) **`p_timeout` (seconds)**
D) `p_transfer_timeout`

**Answer: C**

**Explanation**: `p_timeout` sets the maximum seconds to wait for a response. Default is 180s (too long for UX). Always set explicitly (5-30s). `p_transfer_timeout` is for total transfer time including download.

---

## Question 3: JSON Parsing Array Access
**How to iterate over a JSON array `events` with APEX_JSON?**

A) `FOR i IN 1..JSON_ARRAY_LENGTH('events') LOOP ... END LOOP;`
B) **`FOR i IN 1..APEX_JSON.GET_COUNT('events') LOOP val := APEX_JSON.GET_VARCHAR2('events[%d].field', i); END LOOP;`**
C) `APEX_JSON.PARSE_ARRAY('events')` then `APEX_JSON.NEXT_ELEMENT`
D) `SELECT * FROM JSON_TABLE(...)`

**Answer: B**

**Explanation**: `APEX_JSON.GET_COUNT(path)` returns array length. `GET_VARCHAR2(path, index)` uses `%d` placeholder for 1-based index. This is the standard APEX_JSON pattern.

---

## Question 4: File Upload (APEX 23.2+)
**Which package provides `GET_FILE_CONTENT`, `GET_FILE_MIME_TYPE`, `GET_FILE_SIZE` for File Browse items?**

A) `APEX_APPLICATION`
B) `WWV_FLOW_FILES`
C) **`APEX_FILE_MANAGER`**
D) `APEX_UTIL`

**Answer: C**

**Explanation**: `APEX_FILE_MANAGER` (introduced 23.2) is the modern API for accessing uploaded file metadata and content. Legacy code uses `APEX_APPLICATION.G_X01..G_X04`.

---

## Question 5: File Download Headers
**What is the correct header for inline PDF preview (not download)?**

A) `Content-Disposition: attachment; filename="doc.pdf"`
B) **`Content-Disposition: inline; filename="doc.pdf"`**
C) `Content-Type: application/force-download`
D) `Content-Transfer-Encoding: base64`

**Answer: B**

**Explanation**: `inline` tells browser to display in-tab (PDF viewer, image). `attachment` forces download dialog. Both need `Content-Type` set via `OWA_UTIL.MIME_HEADER`.

---

## Question 6: ORDS Handler Source Types
**Which `p_source_type` returns a paginated array with `items`, `hasMore`, `limit`, `offset`, `count`?**

A) `json/item`
B) **`json/collection`**
C) `plsql/block`
D) `media/resource`

**Answer: B**

**Explanation**: `json/collection` is the default for REST endpoints returning lists. Supports `?offset=50&limit=25` pagination automatically. `json/item` returns single object.

---

## Question 7: ORDS Parameter Binding
**In an ORDS handler with pattern `shipments/:id`, how is the `:id` value accessed in the SQL source?**

A) `WHERE shipment_id = '&id.'`
B) **`WHERE shipment_id = :id`**
C) `WHERE shipment_id = v('id')`
D) `WHERE shipment_id = APEX_APPLICATION.G_X01`

**Answer: B**

**Explanation**: ORDS automatically binds path parameters (`:id`) and query parameters (`?status=X` → `:status`) as bind variables in the SQL/PLSQL source. Use standard Oracle bind syntax.

---

## Question 8: APEX_DATA_PARSER CSV Output
**What does `APEX_DATA_PARSER.PARSE(p_format => 'CSV')` return?**

A) CLOB with CSV text
B) **`T_TABLE` collection of records with `COLUMN_01..COLUMN_N`**
C) `SYS_REFCURSOR`
D) `APEX_JSON` object

**Answer: B**

**Explanation**: Returns `APEX_DATA_PARSER.T_TABLE` (associative array of records). Each record has `LINE_NUMBER`, `COL_COUNT`, and `COLUMN_01` through `COLUMN_300`. If CSV has header row, first record contains headers.

---

## Question 9: Batched API Calls
**When processing 10,000 records via external API with 100-record batch limit, how many HTTP requests?**

A) 1 (send all at once)
B) **100 (10,000 / 100)**
C) 10,000 (one per record)
D) Depends on `p_items_per_page`

**Answer: B**

**Explanation**: Batch size is typically limited by API (payload size, rate limits). 10,000 records ÷ 100 per batch = 100 HTTP requests. Process in loop with `DBMS_LOCK.SLEEP` between batches for rate limiting.

---

## Question 10: Retry with Exponential Backoff
**What is the correct backoff pattern for 3 retries?**

A) Sleep 1s, 1s, 1s
B) Sleep 0s, 1s, 2s
C) **Sleep 2s, 4s, 6s (attempt × 2)**
D) Sleep 10s, 10s, 10s

**Answer: C**

**Explanation**: Exponential backoff: `attempt * base_delay`. For base=2: attempt 1→2s, 2→4s, 3→6s. This prevents thundering herd on recovering service. Jitter (random ±10%) recommended in production.

---

## Answer Key
1. C | 2. C | 3. B | 4. C | 5. B | 6. B | 7. B | 8. B | 9. B | 10. C