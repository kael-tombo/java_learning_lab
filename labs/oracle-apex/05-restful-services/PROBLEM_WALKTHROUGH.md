# Problem Walkthrough: RESTful Services

## Problem 1: Creating a RESTful Service Module — Oracle
### APEX Interview Scenario
"Oracle's customer wants to expose an APEX application's product catalog as a REST API for a mobile app."

### Problem
Create a RESTful service module in APEX that returns product data in JSON format with pagination and search.

### Solution Walkthrough
1. **Open ORDS** — SQL Workshop → RESTful Services → Create Module
2. **Module Name** — `catalog/v1/`
3. **Create Template** — `products/` with URI pattern: `products/:id`
4. **Create GET Handler** — Source: SQL query
5. **Add Pagination** — Use `:offset` and `:limit` bind variables:
   ```sql
   SELECT * FROM products
   WHERE (:id IS NULL OR product_id = :id)
   ORDER BY product_name
   OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
   ```
6. **Set Response Headers** — `Content-Type: application/json`
7. **Enable Pagination Headers** — `X-Total-Count` via:
   ```sql
   SELECT COUNT(*) AS total FROM products WHERE (:id IS NULL OR product_id = :id);
   ```
8. **Test** — Use cURL or Postman to verify

### Code
```sql
-- Product list handler
SELECT JSON_OBJECT(
    'product_id' KEY p.product_id,
    'name'       KEY p.product_name,
    'price'      KEY p.price,
    'category'   KEY c.category_name
)
FROM products p
JOIN categories c ON c.category_id = p.category_id
WHERE (:id IS NULL OR p.product_id = :id)
OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;

-- Count handler
SELECT COUNT(*) FROM products
WHERE (:id IS NULL OR product_id = :id);
```

### Company Evaluation
- **Oracle**: ORDS architecture, handler types, bind variable mapping
- **Deloitte**: API documentation for mobile app developers
- **Accenture**: Versioning strategy, backward compatibility

---

## Problem 2: RESTful Service with Authentication — Deloitte
### APEX Interview Scenario
"Deloitte's client needs the REST API to be secured. Only authenticated clients with a valid API key can access it."

### Problem
Add OAuth2 client credentials authentication to an ORDS RESTful service.

### Solution Walkthrough
1. **Create OAuth2 Role** — In ORDS: `ords admin` → `add restful service privilege`
2. **Create Privilege** — Named `catalog_api`, assign to template `products/`
3. **Create OAuth Client** — Register client app with client ID and secret
4. **Configure APEX** — Set authentication scheme to "OAuth2 Client Credentials"
5. **Client Flow**:
   - Client POSTs to `/oauth/token` with grant_type=client_credentials
   - Receives `access_token`
   - Passes token in `Authorization: Bearer` header
6. **Token Validation** — ORDS validates, extracts username, checks privilege
7. **Audit** — Log API calls with client ID and timestamp

### Code
```sql
-- Register OAuth client (via SQLcl)
-- > ORDS ENABLE OAUTH;
-- > ORDS CREATE OAUTH CLIENT --name mobile_app --grant_type client_credentials

-- ORDS privilege SQL
-- <!-- UNVERIFIED: ORDS.DEFINE_PRIVILEGE signature including p_module_id => 100 needs doc/DB confirmation. -->
BEGIN
    ORDS.DEFINE_PRIVILEGE(
        p_privilege_name => 'catalog_api',
        p_roles          => 'catalog_api_role',
        p_patterns       => '/catalog/v1/products/*',
        p_module_id      => 100
    );
    COMMIT;
END;
/
```

### Company Evaluation
- **Deloitte**: API security standards, OAuth2 flows for client requirements
- **Accenture**: Token management, refresh token rotation strategies
- **Oracle**: ORDS OAuth2 internals, privilege evaluation order

---

## Problem 3: APEX Calling External REST API — Accenture
### APEX Interview Scenario
"Accenture's APEX app needs to call an external payment gateway REST API to process transactions."

### Problem
Make an outbound REST call from APEX to a third-party payment API and handle the response.

### Solution Walkthrough
1. **Create Web Credential** — Shared Components → Web Credentials → Store API key
2. **Create Web Source Module** — Shared Components → Web Sources → REST Source
3. **Configure Endpoint** — Base URL: `https://api.paymentgateway.com/v2/`
4. **Set Authentication** — OAuth2 or API Key from credential store
5. **Add Operations** — `POST /charge` with JSON body
6. **Call from APEX** — Use dynamic action (PL/SQL) or process:
   ```sql
   l_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
       p_url          => 'https://api.paymentgateway.com/v2/charge',
       p_http_method  => 'POST',
       p_body         => l_json_body,
       p_credential   => 'PAYMENT_GW'
   );
   ```
7. **Parse Response** — Use `APEX_JSON` to extract transaction ID, status
8. **Handle Errors** — Check HTTP status, retry logic for 5xx

### Code
```sql
DECLARE
    l_body    CLOB;
    l_result  CLOB;
BEGIN
    l_body := JSON_OBJECT(
        'amount'     KEY :P4_AMOUNT,
        'currency'   KEY 'USD',
        'card_token' KEY :P4_CARD_TOKEN
    );

    l_result := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
        p_url         => 'https://api.paymentgateway.com/v2/charge',
        p_http_method => 'POST',
        p_body        => l_body,
        p_credential  => 'PAYMENT_GW',
        p_wallet_path => 'file:/etc/oracle/wallet'
    );

    APEX_JSON.PARSE(l_result);
    :P4_TRANSACTION_ID := APEX_JSON.GET_VARCHAR2('transaction_id');
    :P4_STATUS := APEX_JSON.GET_VARCHAR2('status');
EXCEPTION
    WHEN OTHERS THEN
        :P4_ERROR := SQLERRM;
END;
/
```

### Company Evaluation
- **Accenture**: Integration patterns, error handling, retry strategies
- **Deloitte**: API selection criteria for client projects
- **Oracle**: APEX_WEB_SERVICE package, wallet configuration for HTTPS

---

## Problem 4: Debugging RESTful Services — Oracle
### APEX Interview Scenario
"At Oracle, a RESTful service returns 500 Internal Server Error with no details. Debug it."

### Problem
ORDS returns HTTP 500. Need to find and fix the root cause.

### Solution Walkthrough
1. **Check ORDS Logs** — Review `ords_log` table in APEX schema:
   ```sql
   -- <!-- UNVERIFIED: ords_log table and columns need doc/DB confirmation. -->
   SELECT * FROM ords_log ORDER BY created_on DESC;
   ```
2. **Enable ORDS Debugging** — Set `ords.debug=true` in `defaults.xml`
3. **Check SQL Errors** — Look for ORA- errors in log
4. **Validate JSON** — Ensure SQL output is valid JSON:
   ```sql
   SELECT JSON_OBJECT('key' KEY column) FROM bad_query; -- syntax error
   ```
5. **Test Handler SQL Directly** — Run the handler SQL in SQL Workshop with same bind variables
6. **Check Privileges** — Verify `APEX_WS_CREDENTIALS` and user permissions
7. **Common Fixes**:
   - Missing `COMMIT` in POST handler
   - Ambiguous column names in JSON output
   - Bind variable mismatch (`:id` vs `:product_id`)

### Code
```sql
-- Enable APEX debug for current session
BEGIN
    APEX_DEBUG.ENABLE(p_level => APEX_DEBUG.C_LOG_ALL);
END;
/

-- Check ORDS log
-- <!-- UNVERIFIED: ords_log table and columns need doc/DB confirmation. -->
SELECT url, method, status_code, error_message, created_on
FROM ords_log
WHERE created_on > SYSDATE - 1
  AND status_code = 500
ORDER BY created_on DESC;
```

### Company Evaluation
- **Oracle**: ORDS log analysis, debugging methodology
- **Accenture**: Structured troubleshooting playbook for support teams
- **Deloitte**: Client communication during API outages
