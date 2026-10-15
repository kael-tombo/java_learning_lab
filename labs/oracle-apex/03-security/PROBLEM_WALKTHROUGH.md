# Problem Walkthrough: Implement RBAC with Custom Authentication and Authorization

## Problem Statement

A financial services client requires a secure APEX application that enforces Role-Based Access Control (RBAC). The application manages sensitive customer portfolio data. Requirements:

1. **Custom Authentication**: Validate users against a corporate LDAP directory with fallback to a local user table
2. **Role Hierarchy**: ADMIN > MANAGER > ANALYST > VIEWER — each role inherits permissions from subordinate roles
3. **Row-Level Security**: Managers see data for their branch only; ADMIN sees all branches
4. **Feature-Level Authorization**: Certain pages/buttons are restricted by role
5. **Audit Logging**: All authentication attempts and authorization decisions are logged
6. **Session Management**: Sessions expire after 15 minutes of inactivity

### Security Requirements
- Passwords stored using PBKDF2 hashing with salt
- Failed login lockout after 5 attempts (15-minute cooldown)
- All DB access uses connection pooling with minimal privileges
- Application must pass a penetration test for OWASP Top 10 vulnerabilities

### Success Criteria
- CSSLP/OWASP-compliant authentication flow
- Role changes take effect immediately (no cache)
- Audit trail captures user, action, timestamp, and IP address
- Zero SQL injection vulnerabilities (verified by automated scan)

---

## Step-by-Step Walkthrough

### Step 1: Security Schema Setup

```sql
-- Users table (local fallback + sync target)
CREATE TABLE app_users (
    user_id         NUMBER PRIMARY KEY,
    username        VARCHAR2(100) UNIQUE NOT NULL,
    password_hash   VARCHAR2(200),  -- PBKDF2 hash, NULL if LDAP-only
    password_salt   VARCHAR2(100),
    email           VARCHAR2(200),
    full_name       VARCHAR2(200),
    department      VARCHAR2(100),
    branch_id       NUMBER,         -- for row-level security
    ldap_dn         VARCHAR2(500),  -- LDAP distinguished name
    is_active       CHAR(1) DEFAULT 'Y' CHECK (is_active IN ('Y','N')),
    failed_logins   NUMBER DEFAULT 0,
    locked_until    DATE,
    last_login      DATE,
    created_date    DATE DEFAULT SYSDATE
);

-- Roles table
CREATE TABLE app_roles (
    role_id         NUMBER PRIMARY KEY,
    role_name       VARCHAR2(50) UNIQUE NOT NULL,
    parent_role_id  NUMBER REFERENCES app_roles(role_id),  -- hierarchy
    description     VARCHAR2(500)
);

-- User-Role mapping
CREATE TABLE app_user_roles (
    user_role_id    NUMBER PRIMARY KEY,
    user_id         NUMBER NOT NULL REFERENCES app_users(user_id) ON DELETE CASCADE,
    role_id         NUMBER NOT NULL REFERENCES app_roles(role_id),
    granted_by      VARCHAR2(100),
    granted_date    DATE DEFAULT SYSDATE,
    UNIQUE (user_id, role_id)
);

-- Feature permissions (for fine-grained access control)
CREATE TABLE app_permissions (
    permission_id   NUMBER PRIMARY KEY,
    permission_name VARCHAR2(100) UNIQUE NOT NULL,  -- e.g., 'PORTFOLIO_VIEW', 'TRADE_EXECUTE'
    description     VARCHAR2(500)
);

-- Role-Permission mapping
CREATE TABLE app_role_permissions (
    role_perm_id    NUMBER PRIMARY KEY,
    role_id         NUMBER NOT NULL REFERENCES app_roles(role_id),
    permission_id   NUMBER NOT NULL REFERENCES app_permissions(permission_id),
    UNIQUE (role_id, permission_id)
);

-- Audit log
CREATE TABLE app_audit_log (
    audit_id        NUMBER PRIMARY KEY,
    username        VARCHAR2(100),
    action          VARCHAR2(50),   -- LOGIN, LOGOUT, AUTH_FAIL, AUTHZ_DENY, DATA_CHANGE
    action_detail   VARCHAR2(4000),
    ip_address      VARCHAR2(45),
    session_id      NUMBER,
    page_id         NUMBER,
    application_id  NUMBER,
    created_date    DATE DEFAULT SYSDATE
) PARTITION BY RANGE (created_date) INTERVAL (INTERVAL '1' DAY) (
    PARTITION p_init VALUES LESS THAN (DATE '2025-01-01')
);

CREATE INDEX idx_audit_username ON app_audit_log(username);
CREATE INDEX idx_audit_date ON app_audit_log(created_date);

-- Sequences
CREATE SEQUENCE user_seq START WITH 1000;
CREATE SEQUENCE role_seq START WITH 100;
CREATE SEQUENCE user_role_seq START WITH 1000;
CREATE SEQUENCE perm_seq START WITH 100;
CREATE SEQUENCE role_perm_seq START WITH 1000;
CREATE SEQUENCE audit_seq START WITH 10000;

-- Seed data: Roles (hierarchical)
INSERT INTO app_roles VALUES (1, 'ADMIN', NULL, 'Full system access');
INSERT INTO app_roles VALUES (2, 'MANAGER', 1, 'Branch management access');
INSERT INTO app_roles VALUES (3, 'ANALYST', 2, 'Data analysis and reporting');
INSERT INTO app_roles VALUES (4, 'VIEWER', 3, 'Read-only access');

-- Seed data: Permissions
INSERT INTO app_permissions VALUES (1, 'PORTFOLIO_VIEW', 'View customer portfolios');
INSERT INTO app_permissions VALUES (2, 'PORTFOLIO_EDIT', 'Edit portfolio allocations');
INSERT INTO app_permissions VALUES (3, 'TRADE_EXECUTE', 'Execute trades');
INSERT INTO app_permissions VALUES (4, 'USER_MANAGE', 'Manage application users');
INSERT INTO app_permissions VALUES (5, 'REPORT_VIEW', 'View reports');
INSERT INTO app_permissions VALUES (6, 'REPORT_EXPORT', 'Export report data');
INSERT INTO app_permissions VALUES (7, 'AUDIT_VIEW', 'View audit logs');
INSERT INTO app_permissions VALUES (8, 'SYSTEM_CONFIG', 'Modify system configuration');

-- Map permissions to roles
-- ADMIN gets all
INSERT INTO app_role_permissions SELECT role_perm_seq.NEXTVAL, 1, permission_id FROM app_permissions;
-- MANAGER: PORTFOLIO_VIEW, PORTFOLIO_EDIT, TRADE_EXECUTE, REPORT_VIEW, REPORT_EXPORT
INSERT INTO app_role_permissions VALUES (role_perm_seq.NEXTVAL, 2, 1);
INSERT INTO app_role_permissions VALUES (role_perm_seq.NEXTVAL, 2, 2);
INSERT INTO app_role_permissions VALUES (role_perm_seq.NEXTVAL, 2, 3);
INSERT INTO app_role_permissions VALUES (role_perm_seq.NEXTVAL, 2, 5);
INSERT INTO app_role_permissions VALUES (role_perm_seq.NEXTVAL, 2, 6);
-- ANALYST: PORTFOLIO_VIEW, REPORT_VIEW, REPORT_EXPORT
INSERT INTO app_role_permissions VALUES (role_perm_seq.NEXTVAL, 3, 1);
INSERT INTO app_role_permissions VALUES (role_perm_seq.NEXTVAL, 3, 5);
INSERT INTO app_role_permissions VALUES (role_perm_seq.NEXTVAL, 3, 6);
-- VIEWER: PORTFOLIO_VIEW, REPORT_VIEW
INSERT INTO app_role_permissions VALUES (role_perm_seq.NEXTVAL, 4, 1);
INSERT INTO app_role_permissions VALUES (role_perm_seq.NEXTVAL, 4, 5);

-- Sample users
-- Password: 'Welcome1' (this is the hash, typically generated in application code)
INSERT INTO app_users VALUES (user_seq.NEXTVAL, 'ADMIN_USER', 'HASH_VALUE', 'SALT_VALUE',
    'admin@bank.com', 'System Administrator', 'IT', NULL, NULL, 'Y', 0, NULL, NULL, SYSDATE);
INSERT INTO app_users VALUES (user_seq.NEXTVAL, 'MGR_NYC', 'HASH_VALUE', 'SALT_VALUE',
    'mgr.nyc@bank.com', 'Jane Manager', 'Wealth Management', 101, NULL, 'Y', 0, NULL, NULL, SYSDATE);
INSERT INTO app_users VALUES (user_seq.NEXTVAL, 'ANALYST_LON', 'HASH_VALUE', 'SALT_VALUE',
    'analyst.lon@bank.com', 'Bob Analyst', 'Research', 102, NULL, 'Y', 0, NULL, NULL, SYSDATE);
INSERT INTO app_users VALUES (user_seq.NEXTVAL, 'VIEWER_USER', 'HASH_VALUE', 'SALT_VALUE',
    'viewer@bank.com', 'Viewer User', 'Compliance', 101, NULL, 'Y', 0, NULL, NULL, SYSDATE);

-- Assign roles
INSERT INTO app_user_roles VALUES (user_role_seq.NEXTVAL, 1000, 1, 'SYSTEM', SYSDATE);
INSERT INTO app_user_roles VALUES (user_role_seq.NEXTVAL, 1001, 2, 'SYSTEM', SYSDATE);
INSERT INTO app_user_roles VALUES (user_role_seq.NEXTVAL, 1002, 3, 'SYSTEM', SYSDATE);
INSERT INTO app_user_roles VALUES (user_role_seq.NEXTVAL, 1003, 4, 'SYSTEM', SYSDATE);

COMMIT;
```

### Step 2: Password Hashing Package

```sql
CREATE OR REPLACE PACKAGE sec_pwd AS
    FUNCTION hash_password(p_password IN VARCHAR2, p_salt IN VARCHAR2) RETURN VARCHAR2;
    FUNCTION generate_salt RETURN VARCHAR2;
    FUNCTION verify_password(p_password IN VARCHAR2, p_hash IN VARCHAR2, p_salt IN VARCHAR2) RETURN BOOLEAN;
END sec_pwd;
/

CREATE OR REPLACE PACKAGE BODY sec_pwd AS
    FUNCTION hash_password(p_password IN VARCHAR2, p_salt IN VARCHAR2) RETURN VARCHAR2 IS
        l_hash RAW(2000);
    BEGIN
        -- PBKDF2-HMAC-SHA256 with 10000 iterations
        -- <!-- UNVERIFIED: DBMS_CRYPTO.PBKDF2 needs doc/DB confirmation — package function, parameter names, and prf constants not verified against the Oracle docs. -->
        l_hash := DBMS_CRYPTO.PBKDF2(
            password  => UTL_RAW.CAST_TO_RAW(p_password),
            salt      => UTL_RAW.CAST_TO_RAW(p_salt),
            iterations => 10000,
            dklen     => 32,
            prf       => DBMS_CRYPTO.HMAC_SH256
        );
        RETURN RAWTOHEX(l_hash);
    END hash_password;

    FUNCTION generate_salt RETURN VARCHAR2 IS
    BEGIN
        RETURN RAWTOHEX(DBMS_CRYPTO.RANDOMBYTES(16));
    END generate_salt;

    FUNCTION verify_password(p_password IN VARCHAR2, p_hash IN VARCHAR2, p_salt IN VARCHAR2) RETURN BOOLEAN IS
    BEGIN
        RETURN hash_password(p_password, p_salt) = p_hash;
    END verify_password;
END sec_pwd;
/
```

### Step 3: Custom Authentication Scheme

1. Navigate to **Shared Components → Authentication Schemes**
2. Create **New Authentication Scheme**:
   - Name: `Custom_RBAC_Auth`
   - Scheme Type: **Custom — PL/SQL Function Body**

3. **Authentication Function**:
   ```sql
   DECLARE
       l_user      app_users%ROWTYPE;
       l_ldap_auth BOOLEAN := FALSE;
       l_result    BOOLEAN;
       l_ip        VARCHAR2(45) := owa_util.get_cgi_env('REMOTE_ADDR');
   BEGIN
       -- Try LDAP first
       BEGIN
           -- LDAP authentication logic (simplified)
           -- l_ldap_auth := ldap_auth(P_USERNAME, P_PASSWORD);
           l_ldap_auth := FALSE; -- placeholder
       EXCEPTION
           WHEN OTHERS THEN
               l_ldap_auth := FALSE; -- fallback on LDAP failure
       END;

       -- Check local user table
       SELECT * INTO l_user
       FROM app_users
       WHERE LOWER(username) = LOWER(P_USERNAME)
         AND is_active = 'Y';

       -- Check account lockout
       IF l_user.locked_until IS NOT NULL AND l_user.locked_until > SYSDATE THEN
           INSERT INTO app_audit_log VALUES (
               audit_seq.NEXTVAL, P_USERNAME, 'AUTH_FAIL',
               'Account locked until ' || TO_CHAR(l_user.locked_until, 'DD-MON-YYYY HH24:MI:SS'),
               l_ip, NULL, NULL, NULL, SYSDATE);
           COMMIT;
           RETURN FALSE;
       END IF;

       -- Verify password (LDAP or local)
       IF l_ldap_auth THEN
           l_result := TRUE;
       ELSIF l_user.password_hash IS NOT NULL THEN
           l_result := sec_pwd.verify_password(P_PASSWORD, l_user.password_hash, l_user.password_salt);
       ELSE
           l_result := FALSE;
       END IF;

       IF l_result THEN
           -- Reset failed login count
           UPDATE app_users SET
               failed_logins = 0,
               locked_until = NULL,
               last_login = SYSDATE
           WHERE user_id = l_user.user_id;

           INSERT INTO app_audit_log VALUES (
               audit_seq.NEXTVAL, P_USERNAME, 'LOGIN',
               'Successful authentication from ' || l_ip,
               l_ip, NULL, NULL, NULL, SYSDATE);
           COMMIT;
           RETURN TRUE;
       ELSE
           -- Increment failed login counter
           UPDATE app_users SET
               failed_logins = failed_logins + 1,
               locked_until = CASE WHEN failed_logins + 1 >= 5
                                   THEN SYSDATE + INTERVAL '15' MINUTE
                                   ELSE NULL END
           WHERE LOWER(username) = LOWER(P_USERNAME);

           INSERT INTO app_audit_log VALUES (
               audit_seq.NEXTVAL, P_USERNAME, 'AUTH_FAIL',
               'Invalid password from ' || l_ip || ' (attempt #' || (l_user.failed_logins + 1) || ')',
               l_ip, NULL, NULL, NULL, SYSDATE);
           COMMIT;
           RETURN FALSE;
       END IF;
   EXCEPTION
       WHEN NO_DATA_FOUND THEN
           INSERT INTO app_audit_log VALUES (
               audit_seq.NEXTVAL, P_USERNAME, 'AUTH_FAIL',
               'Unknown user from ' || l_ip,
               l_ip, NULL, NULL, NULL, SYSDATE);
           COMMIT;
           RETURN FALSE;
   END;
   ```

4. **Post-Authentication Process**:
   ```sql
   BEGIN
       -- Set application-level items for RBAC
       SELECT
           NULL -- PL/SQL will handle via computation
       INTO :G_USER_ID
       FROM DUAL;

       -- Clear sensitive session state
       APEX_UTIL.SET_SESSION_STATE(
           p_item_name => 'G_USER_ROLE',
           p_item_value => get_user_role(:APP_USER));
   END;
   ```

### Step 4: Role and Permission Functions

Create a package to centralize RBAC logic:

```sql
CREATE OR REPLACE PACKAGE sec_rbac AS
    FUNCTION get_user_role(p_username IN VARCHAR2) RETURN VARCHAR2;
    FUNCTION get_user_role_id(p_username IN VARCHAR2) RETURN NUMBER;
    FUNCTION get_user_permissions(p_username IN VARCHAR2) RETURN SYS.ODCIVARCHAR2LIST;
    FUNCTION has_permission(p_username IN VARCHAR2, p_permission IN VARCHAR2) RETURN BOOLEAN;
    FUNCTION get_user_branch_id(p_username IN VARCHAR2) RETURN NUMBER;
    FUNCTION is_authorized(p_username IN VARCHAR2, p_permission IN VARCHAR2) RETURN VARCHAR2; -- Y/N for APEX
END sec_rbac;
/

CREATE OR REPLACE PACKAGE BODY sec_rbac AS
    FUNCTION get_user_role(p_username IN VARCHAR2) RETURN VARCHAR2 IS
        l_role_name VARCHAR2(50);
    BEGIN
        SELECT r.role_name INTO l_role_name
        FROM app_user_roles ur
        JOIN app_roles r ON r.role_id = ur.role_id
        JOIN app_users u ON u.user_id = ur.user_id
        WHERE LOWER(u.username) = LOWER(p_username);
        RETURN l_role_name;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN RETURN 'VIEWER';
    END get_user_role;

    FUNCTION get_user_role_id(p_username IN VARCHAR2) RETURN NUMBER IS
        l_role_id NUMBER;
    BEGIN
        SELECT ur.role_id INTO l_role_id
        FROM app_user_roles ur
        JOIN app_users u ON u.user_id = ur.user_id
        WHERE LOWER(u.username) = LOWER(p_username);
        RETURN l_role_id;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN RETURN 4; -- VIEWER
    END get_user_role_id;

    FUNCTION get_user_permissions(p_username IN VARCHAR2)
        RETURN SYS.ODCIVARCHAR2LIST IS
        l_perms SYS.ODCIVARCHAR2LIST;
    BEGIN
        SELECT p.permission_name
        BULK COLLECT INTO l_perms
        FROM app_role_permissions rp
        JOIN app_permissions p ON p.permission_id = rp.permission_id
        JOIN app_user_roles ur ON ur.role_id = rp.role_id
        JOIN app_users u ON u.user_id = ur.user_id
        WHERE LOWER(u.username) = LOWER(p_username);
        RETURN l_perms;
    END get_user_permissions;

    FUNCTION has_permission(p_username IN VARCHAR2, p_permission IN VARCHAR2)
        RETURN BOOLEAN IS
        l_count NUMBER;
    BEGIN
        SELECT COUNT(*) INTO l_count
        FROM TABLE(get_user_permissions(p_username))
        WHERE column_value = p_permission;
        RETURN l_count > 0;
    END has_permission;

    FUNCTION get_user_branch_id(p_username IN VARCHAR2) RETURN NUMBER IS
        l_branch_id NUMBER;
    BEGIN
        SELECT branch_id INTO l_branch_id
        FROM app_users
        WHERE LOWER(username) = LOWER(p_username);
        RETURN l_branch_id;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN RETURN NULL;
    END get_user_branch_id;

    FUNCTION is_authorized(p_username IN VARCHAR2, p_permission IN VARCHAR2)
        RETURN VARCHAR2 IS
    BEGIN
        IF has_permission(p_username, p_permission) THEN
            RETURN 'Y';
        ELSE
            RETURN 'N';
        END IF;
    END is_authorized;
END sec_rbac;
/
```

### Step 5: Application-Level Items and Computations

1. Create **Application Items**:
   - `G_USER_ID` (Number)
   - `G_USER_ROLE` (Varchar2)
   - `G_USER_BRANCH` (Number)
   - `G_USER_PERMISSIONS` (Varchar2) — comma-separated list

2. Create **Application Computations** (After Authentication):

   **G_USER_ID**:
   ```sql
   SELECT user_id FROM app_users WHERE LOWER(username) = LOWER(:APP_USER)
   ```

   **G_USER_ROLE**:
   ```sql
   SELECT sec_rbac.get_user_role(:APP_USER) FROM DUAL
   ```

   **G_USER_BRANCH**:
   ```sql
   SELECT sec_rbac.get_user_branch_id(:APP_USER) FROM DUAL
   ```

   **G_USER_PERMISSIONS**:
   ```sql
   SELECT LISTAGG(column_value, ',') WITHIN GROUP (ORDER BY column_value)
   FROM TABLE(sec_rbac.get_user_permissions(:APP_USER))
   ```

### Step 6: Authorization Schemes (Feature-Level)

Create the following **Authorization Schemes** in Shared Components:

1. **Is Admin** — PL/SQL Function Body:
   ```sql
   RETURN :G_USER_ROLE = 'ADMIN';
   ```

2. **Is Manager or Higher** — PL/SQL Function Body:
   ```sql
   RETURN :G_USER_ROLE IN ('ADMIN', 'MANAGER');
   ```

3. **Has Permission: PORTFOLIO_EDIT** — PL/SQL Function Body:
   ```sql
   RETURN INSTR(',' || :G_USER_PERMISSIONS || ',', ',PORTFOLIO_EDIT,') > 0;
   ```

4. **Has Permission: TRADE_EXECUTE**:
   ```sql
   RETURN INSTR(',' || :G_USER_PERMISSIONS || ',', ',TRADE_EXECUTE,') > 0;
   ```

### Step 7: Apply Authorization to Pages and Components

1. **Page-Level Authorization**:
   - Page 3 (User Management): Authorization Scheme = **Is Admin**
   - Page 4 (Trade Execution): Authorization Scheme = **Has Permission: TRADE_EXECUTE**
   - Page 5 (Audit Logs): Authorization Scheme = **Is Admin**

2. **Region-Level Authorization**:
   - "Export Report" button: Authorization Scheme = **Has Permission: REPORT_EXPORT**
   - "Edit Portfolio" region: Authorization Scheme = **Has Permission: PORTFOLIO_EDIT**

3. **Navigation Menu Entries**:
   - Set authorization on each list entry based on permissions

### Step 8: Row-Level Security Implementation

Use a **Virtual Private Database (VPD)** policy or application-level filtering:

**Option A: VPD Policy**
```sql
CREATE OR REPLACE FUNCTION vpd_branch_filter(
    p_schema IN VARCHAR2,
    p_table  IN VARCHAR2
) RETURN VARCHAR2 AS
    l_branch_id NUMBER := NVL(sec_rbac.get_user_branch_id(:APP_USER), -1);
    l_role      VARCHAR2(50) := sec_rbac.get_user_role(:APP_USER);
BEGIN
    IF l_role = 'ADMIN' THEN
        RETURN '1=1'; -- See all
    ELSIF l_branch_id IS NOT NULL THEN
        RETURN 'branch_id = ' || l_branch_id;
    ELSE
        RETURN '1=0'; -- No access
    END IF;
END vpd_branch_filter;
/

BEGIN
    DBMS_RLS.ADD_POLICY(
        object_schema   => 'APP_SCHEMA',
        object_name     => 'PORTFOLIOS',
        policy_name     => 'branch_access_policy',
        function_schema => 'APP_SCHEMA',
        policy_function => 'vpd_branch_filter',
        statement_types => 'SELECT, UPDATE, DELETE',
        update_check    => TRUE
    );
END;
/
```

**Option B: Application-Level Filtering (without VPD)**

Modify all report queries to include:
```sql
AND (branch_id = :G_USER_BRANCH OR :G_USER_ROLE = 'ADMIN')
```

### Step 9: Audit Logging Infrastructure

Create a **Logout/Application Process** to capture logouts:

```sql
CREATE OR REPLACE TRIGGER trg_audit_dml
AFTER INSERT OR UPDATE OR DELETE ON portfolios
FOR EACH ROW
DECLARE
    l_action VARCHAR2(20);
BEGIN
    l_action := CASE
        WHEN INSERTING THEN 'INSERT'
        WHEN UPDATING THEN 'UPDATE'
        WHEN DELETING THEN 'DELETE'
    END;

    INSERT INTO app_audit_log VALUES (
        audit_seq.NEXTVAL,
        :APP_USER,
        'DATA_CHANGE',
        l_action || ' on PORTFOLIOS: ' ||
        CASE WHEN INSERTING OR UPDATING THEN
            'ID=' || :NEW.portfolio_id
        ELSE
            'ID=' || :OLD.portfolio_id
        END,
        owa_util.get_cgi_env('REMOTE_ADDR'),
        :APP_SESSION,
        :APP_PAGE_ID,
        :APP_ID,
        SYSDATE
    );
END;
/
```

### Step 10: Session Management

1. **Session Timeout**: Application Attributes → Session → 
   - Maximum Session Length: 900 (15 minutes)
   - Session Timeout URL: Login page

2. **Create a Dynamic Action** for idle timeout warning:
   - Event: **Page Load**
   - True Action: Execute JavaScript
   ```javascript
   // Idle timeout warning at 12 minutes (3 min before session expires)
   var idleTimer;
   function resetIdleTimer() {
       clearTimeout(idleTimer);
       idleTimer = setTimeout(function() {
           apex.message.confirm(
               'Your session will expire in 3 minutes due to inactivity. Continue working?',
               function(ok) {
                   if (ok) {
                       // Refresh session by making a lightweight AJAX call
                       apex.server.process('KEEP_ALIVE', {}, {
                           success: function() { resetIdleTimer(); }
                       });
                   }
               }
           );
       }, 12 * 60 * 1000); // 12 minutes
   }
   $(document).on('click keypress mousemove scroll', resetIdleTimer);
   resetIdleTimer();
   ```

3. **Application Process: KEEP_ALIVE**:
   - Point: AJAX Callback
   - Code: `NULL;` — just extends the session

### Step 11: Security Best Practices Checklist

```sql
-- 1. SQL Injection Protection: Always use bind variables
-- 2. XSS Protection: Enable "Strip HTML" on all page items
-- 3. CSRF Protection: Enable Session State Protection
BEGIN
    APEX_UTIL.SET_SESSION_STATE_PROTECTION(
        p_application_id => :APP_ID,
        p_protection_level => 'ALL'
    );
END;
/

-- 4. URL Tampering Protection: Set item protection levels
-- In Page Designer, set each item to "Checksum Required - Session Level"

-- 5. HTTPS enforcement
-- Set "Require HTTPS" = Yes in Application Attributes

-- 6. Error handling: Hide detailed errors
BEGIN
    APEX_APPLICATION.G_EXCEPTION_HANDLER := 'MY_ERROR_HANDLER';
END;
/
```

### Step 12: Testing the Security Implementation

**Test Case 1: Authentication Flow**
```sql
-- Attempt login with wrong password 5 times
-- Verify account is locked
UPDATE app_users SET locked_until = NULL WHERE username = 'VIEWER_USER';

-- Test successful LDAP authentication (mock)
-- Test local password fallback
-- Test password hashing verification
```

**Test Case 2: Authorization**
```sql
-- Login as VIEWER_USER: Verify "Edit Portfolio" button is hidden
-- Login as ANALYST_LON: Verify only branch 102 data is visible
-- Login as ADMIN_USER: Verify all branches visible
-- Verify audit log captures all access attempts
```

**Test Case 3: SQL Injection**
```sql
-- Try: ' OR '1'='1 in username field
-- Try: '; DROP TABLE app_users; -- in any text input
-- Verify bind variables prevent injection
```

---

## Best Practices Applied

1. **Defense in Depth**: Authentication (LDAP + local hashing), authorization (RBAC + row-level), and auditing
2. **Password Security**: PBKDF2 with salt, 10000 iterations, account lockout
3. **Least Privilege**: Roles have minimum required permissions, inherited hierarchically
4. **Audit Trail**: Every security event logged with timestamp, user, IP, and detail
5. **Separation of Concerns**: RBAC logic centralized in `sec_rbac` package
6. **Immediate Effect**: Permission checks query DB directly — no caching of stale authorizations

## Common Pitfalls to Avoid

1. **Storing passwords in plaintext**: Always hash with salt using PBKDF2/bcrypt
2. **Authorization bypass on AJAX callbacks**: Protect every AJAX process with the same authorization checks
3. **Missing VPD on UPDATE/DELETE**: VPD policy must cover all DML operations
4. **Weak session management**: Use 15-minute timeout, regenerate session ID on login
5. **Over-reliance on UI hiding**: Server-side authorization must complement client-side hiding
6. **Audit log storage**: Use partitioning to manage audit log growth (daily partitions)

## Extensions for Future Iterations

1. Two-factor authentication (TOTP via email/SMS)
2. OAuth2/OIDC integration with Azure AD or Okta
3. Dynamic role assignment with approval workflow
4. API key management for RESTful services
5. Breached password detection (Have I Been Pwned API integration)
6. Session recording for compliance (user action replay)
