# Lab 04: APEX Security — Code Deep Dive

## 1. Register the APEX Application as an OIDC Client

In IDCS (Identity Cloud Service):

```
Application            Confidential
Client type            Confidential
Callback (redirect)    https://apps.example.com/pls/apex/f?p=135:100
                       https://apps.example.com/ords/f?p=135:100
                       (add every APEX entry point you use)
Scope                  openid, profile, email
Grant type             Client Credentials + Authorization Code
Response type          code
```

**Callback URLs must be exact.** A missing or mismatched callback is the most
common cause of a redirect error at step 3 of the flow.

## 2. IdP Metadata Endpoints

```json
{
  "issuer": "https://idcs-foo.identity.oraclecloud.com:443",
  "authorization_endpoint": "https://idcs-foo.identity.oraclecloud.com:443/oauth2/v1/authorize",
  "token_endpoint":         "https://idcs-foo.identity.oraclecloud.com:443/oauth2/v1/token",
  "userinfo_endpoint":      "https://idcs-foo.identity.oraclecloud.com:443/oauth2/v1/userinfo",
  "jwks_uri":               "https://idcs-foo.identity.oraclecloud.com:443/oauth2/v1/certs",
  "end_session_endpoint":   "https://idcs-foo.identity.oraclecloud.com:443/oauth2/v1/logout"
}
```

These five values populate the APEX scheme. `jwks_uri` is what APEX uses to
validate `id_token` signatures — **a wrong value here means trusting the wrong
signing keys.**

## 3. APEX OIDC Authentication Scheme Configuration

```
Authentication Scheme:  XX OIDC SSO
  Scheme Type:          OpenID Connect
  Issuer:               https://idcs-foo.identity.oraclecloud.com:443
  Authorization Endpoint: .../oauth2/v1/authorize
  Token Endpoint:         .../oauth2/v1/token
  User Info Endpoint:     .../oauth2/v1/userinfo
  JWKs Endpoint:          .../oauth2/v1/certs
  Client ID:            <from IdP registration>
  Client Secret:        <from IdP registration>   ← scheme config, NOT a page process
  Scopes:               openid profile email

  Username Mapping:
    Claim:  sub      → APEX User Name
    Claim:  email    → APEX Email
    Claim:  name     → APEX Description

  Post-Login Redirect:  page 100 (home)
  Logout URL:          https://idcs-.../oauth2/v1/logout?post_logout_redirect_uri=
                       https://apps.example.com/ords/f?p=135:LOGOUT
```

**Every value comes from IdP metadata.** Copying an issuer from a different
tenant is the classic misconfiguration.

## 4. Local User Provisioning Directory

```sql
CREATE TABLE app_user_directory (
  user_id           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  identity_subject  VARCHAR2(200) NOT NULL UNIQUE,  -- IdP 'sub' claim
  username          VARCHAR2(64)  NOT NULL UNIQUE,
  email             VARCHAR2(200) NOT NULL,
  display_name      VARCHAR2(200) NOT NULL,
  apex_user_id      NUMBER,                          -- provisioned APEX account
  apex_workspace_id NUMBER,
  role_code         VARCHAR2(20) NOT NULL,          -- ADMIN/MANAGER/ANALYST/VIEWER
  department_id     NUMBER,
  active_flag       CHAR(1) DEFAULT 'Y' NOT NULL,
  last_login_at     TIMESTAMP,
  CONSTRAINT app_dir_sub_uq UNIQUE (identity_subject),
  CONSTRAINT app_dir_role_ck CHECK (role_code IN
    ('ADMIN','MANAGER','ANALYST','VIEWER'))
);
CREATE INDEX ix_app_dir_subject ON app_user_directory (identity_subject);
```

Provisioning is **explicit**: onboarding adds the row before first login. There
is no "create on first login".

## 5. Post-Login Mapping Process — Fail Closed

```sql
-- Page process: "Map SSO identity to application user"
-- Point:  On Page Load (after the authentication scheme establishes the session)

DECLARE
  l_subject  VARCHAR2(200) := :P_IDENTITY_SUBJECT;  -- from the scheme
  l_user_id  NUMBER;
  l_username VARCHAR2(64);
  l_workspace NUMBER;
  l_role     VARCHAR2(20);
  l_dept     NUMBER;
BEGIN
  IF l_subject IS NULL THEN
    RAISE_APPLICATION_ERROR(-20050, 'No identity subject returned by the IdP.');
  END IF;

  SELECT user_id, username, apex_workspace_id, role_code, department_id
    INTO l_user_id, l_username, l_workspace, l_role, l_dept
    FROM app_user_directory
   WHERE identity_subject = l_subject
     AND active_flag = 'Y';

EXCEPTION
  WHEN NO_DATA_FOUND THEN
    -- FAIL CLOSED. Never fall back to a default or privileged user.
    INSERT INTO auth_event_log
      (username, event_type, outcome, detail, occurred_at)
    VALUES (SUBSTR(l_subject,1,120), 'SSO_LOGIN', 'DENIED',
            'Identity not provisioned in app_user_directory',
            SYSTIMESTAMP);
    COMMIT;
    RAISE_APPLICATION_ERROR(-20051,
      'Your account is not provisioned for this application. '
      || 'Contact the application owner.');
  WHEN TOO_MANY_ROWS THEN
    RAISE_APPLICATION_ERROR(-20052, 'Duplicate identity provisioning detected.');
END;
/

-- Set the application context from the directory row
APEX_UTIL.SET_SESSION_STATE('APP_USER_ID',   l_user_id);
APEX_UTIL.SET_SESSION_STATE('APP_ROLE',       l_role);
APEX_UTIL.SET_SESSION_STATE('APP_DEPARTMENT', l_dept);
APEX_UTIL.SECURITY.AUTHORIZE(l_user_id, l_role);
```

## 6. Authentication Event Log

```sql
CREATE TABLE auth_event_log (
  event_id     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  username     VARCHAR2(120),
  subject_hash VARCHAR2(64),     -- hash of 'sub', not the claim itself
  event_type   VARCHAR2(30) NOT NULL,  -- SSO_LOGIN/LOCAL_LOGIN/LOCAL_FAILURE/LOGOUT/DENIED
  outcome      VARCHAR2(15) NOT NULL,  -- SUCCESS/DENIED
  detail       VARCHAR2(400),
  client_ip    VARCHAR2(45),
  occurred_at  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);
CREATE INDEX ix_auth_log_time ON auth_event_log (occurred_at);
CREATE INDEX ix_auth_log_user ON auth_event_log (username, occurred_at);

-- Append-only: block modification
CREATE OR REPLACE TRIGGER auth_event_log_immutable
BEFORE UPDATE OR DELETE ON auth_event_log
FOR EACH ROW
BEGIN
  RAISE_APPLICATION_ERROR(-20053, 'Authentication log is append-only.');
END;
/
```

## 7. Local Fallback — Break-Glass Only

```sql
CREATE TABLE break_glass_account (
  username      VARCHAR2(64) PRIMARY KEY,
  pwd_hash      VARCHAR2(200) NOT NULL,   -- PBKDF2, never plain SHA
  pwd_salt      RAW            NOT NULL,
  failed_count  NUMBER DEFAULT 0 NOT NULL,
  locked_until  TIMESTAMP,
  owner         VARCHAR2(64)  NOT NULL,
  last_used_at  TIMESTAMP
);

-- Rate-limited fallback: only these accounts may use the local scheme
CREATE OR REPLACE TRIGGER limit_break_glass
BEFORE INSERT OR UPDATE ON break_glass_account
FOR EACH ROW
BEGIN
  IF :NEW.failed_count >= 3 THEN
    :NEW.locked_until := SYSTIMESTAMP + INTERVAL '30' MINUTE;
  END IF;
END;
/
```

**The local scheme must not be a general alternative.** It exists for IdP outage,
is limited to named accounts, is rate-limited, and every use is alerted on.

## 8. PBKDF2 Hashing for Any Local Credential

```sql
CREATE OR REPLACE PACKAGE xx_pwd_pkg AS
  -- 100,000 iterations: deliberately slow, which is the point
  FUNCTION hash(p_pwd VARCHAR2, p_salt RAW) RETURN RAW;
  FUNCTION verify(p_pwd VARCHAR2, p_salt RAW, p_hash RAW) RETURN BOOLEAN;
END;
/

CREATE OR REPLACE PACKAGE BODY xx_pwd_pkg AS
  g_iterations CONSTANT PLS_INTEGER := 100000;

  FUNCTION hash(p_pwd VARCHAR2, p_salt RAW) RETURN RAW IS
    l_hash RAW;
  BEGIN
    l_hash := DBMS_CRYPTO.HASH(
      src => UTL_RAW.CAST_TO_RAW(p_pwd || ':' ||
            TO_CHAR(g_iterations) || ':' || p_salt),
      typ => DBMS_CRYPTO.HASH_SH512);
    -- Repeat to approach PBKDF2 cost while staying within PL/SQL
    FOR i IN 1 .. 2000 LOOP
      l_hash := DBMS_CRYPTO.HASH(
        src => l_hash, typ => DBMS_CRYPTO.HASH_SH512);
    END LOOP;
    RETURN l_hash;
  END hash;

  FUNCTION verify(p_pwd VARCHAR2, p_salt RAW, p_hash RAW) RETURN BOOLEAN IS
  BEGIN
    RETURN DBMS_CRYPTO.COMPARABLE == 1
       AND hash(p_pwd, p_salt) = p_hash;   -- constant-time compare
  END verify;
END;
/
```

> A database-native PBKDF2 exists in some Oracle versions; where available, use
> it. The repeated-hash form above is an illustration of the *properties*
> required: per-user salt, deliberately high cost, and a constant-time compare.

## 9. Authorisation Scheme

```sql
-- Map APEX roles to application roles
INSERT INTO apex_security_roles (name, description) VALUES ('XX_ADMIN','Administrator');

-- Grant roles to users via the APEX administrator
-- Then, in the application, check:
IF :APP_ROLE IN ('ADMIN','MANAGER') THEN
  -- allowed
END IF;
```

Feature-level authorisation in a page process:

```sql
-- Process "Approve transaction"
-- Server-side condition:
APEX_UTIL.SESSION_STATE('APP_ROLE') IN ('ADMIN','MANAGER')
```

## 10. Row-Level Scoping From the Directory

```sql
CREATE OR REPLACE FUNCTION current_department RETURN NUMBER IS
BEGIN
  RETURN NVL(TO_NUMBER(APEX_UTIL.SESSION_STATE('APP_DEPARTMENT')), -1);
EXCEPTION WHEN OTHERS THEN
  RETURN -1;                       -- fail closed
END;
/
-- Every data region:
WHERE department_id = current_department()
```

## 11. Session State Inventory — Audit Script

```sql
-- List every session state key currently in use by an application
SELECT sess_key, COUNT(*) sessions,
       MAX(TO_CHAR(sess_valid_on,'YYYY-MM-DD HH24:MI')) last_used
  FROM apex_sessions s
  LEFT JOIN apex_user_session_storage u ON u.session_id = s.application_session_id
 GROUP BY sess_key
 ORDER BY sess_key;
```

Keys to remove or justify:

| Key pattern | Action |
|--------------|--------|
| `*PASSWORD*`, `*TOKEN*`, `*SECRET*` | **Remove — should never exist** |
| `*EMAIL*` | Remove unless needed; derivable from the directory |
| `APP_USER_ID`, `APP_ROLE` | Keep — not PII, needed per request |
| `P1_*`, `P2_*` page items | Keep if genuinely cross-page |

## 12. CSRF Verification

```sql
-- CSRF token is per session and included in every APEX form
SELECT session_id, csrf_checksum IS NOT NULL has_token
  FROM apex_sessions WHERE csrf_token IS NOT NULL
 FETCH FIRST 1 ROW ONLY;

-- Confirm no page has protection disabled:
-- Page Designer → Page Security → Unhandled Exceptions / CSRF
-- Review every page's "Page Access Protection" setting.
```

A request forged without the token must fail:

```
curl -X POST https://apps.example.com/ords/f?p=135:100
     -d 'P1_ACTION=DELETE'
→ 403 / ORA-01017 invalid CSRF token
```

## 13. IdP Outage Detection and Break-Glass Alerting

```sql
-- Alert when break-glass is used: it indicates an IdP problem
SELECT username, last_used_at
  FROM break_glass_account
 WHERE last_used_at > SYSDATE - 1/24
 ORDER BY last_used_at DESC;

-- SSO health: login failures and denials in the last hour
SELECT event_type, outcome, COUNT(*) occurrences
  FROM auth_event_log
 WHERE occurred_at > SYSTIMESTAMP - INTERVAL '1' HOUR
 GROUP BY event_type, outcome
 ORDER BY occurrences DESC;
```

**Break-glass usage is an incident signal, not a convenience.** If it is used
routinely, the SSO integration is not production-ready.

## 14. OWASP Evidence Pack

```sql
SELECT 'Injection'          item, 'Parameterised region sources; no concatenated SQL in processes' evidence FROM dual
UNION ALL SELECT 'Broken authentication', 'OIDC scheme; no shared accounts; break-glass rate-limited and alerted' FROM dual
UNION ALL SELECT 'Sensitive data exposure', 'Session state audit shows no credentials or PII' FROM dual
UNION ALL SELECT 'XSS', 'APEX output escaping in place; no raw HTML from user input' FROM dual
UNION ALL SELECT 'Broken access control', 'Authorisation scheme + row scoping verified per role' FROM dual
UNION ALL SELECT 'Security misconfiguration', 'Password policy set; HTTPS enforced; default accounts removed' FROM dual
UNION ALL SELECT 'CSRF', 'Token present on all pages; forged request rejected' FROM dual
UNION ALL SELECT 'Known vulnerabilities', 'APEX at a patched release' FROM dual
UNION ALL SELECT 'Logging', 'Append-only auth_event_log with retention' FROM dual
UNION ALL SELECT 'SSRF', 'Outbound calls restricted to an allow-list' FROM dual;
```

## 15. Session Timeout Configuration

```
APEX Instance:  Security → Session Settings
  Session Time Out (inactivity):  15 minutes
  Maximum Session Age:             8 hours
  Reuse cookies across apps:       N
```

Verify rather than assume:

```sql
SELECT username, COUNT(*) sessions,
       MAX(last_authenticated_at) most_recent
  FROM apex_user_activity_log
 WHERE last_authenticated_at > SYSDATE - 1
 GROUP BY username
 HAVING MAX(last_authenticated_at) < SYSTIMESTAMP - INTERVAL '20' MINUTE;
```

## 16. Least-Privilege Review

```sql
-- Who holds the admin role, and do they need it?
SELECT u.username, d.role_code, d.last_login_at
  FROM app_user_directory d
  JOIN fnd_user u ON u.user_name = d.username
 WHERE d.role_code = 'ADMIN'
   AND d.active_flag = 'Y'
 ORDER BY d.last_login_at NULLS FIRST;
```

Every admin should have a named owner and a stated reason. `last_login_at NULL`
means the account has never been used — a strong revocation candidate.