-- WORKED_SQL_EXAMPLE — RESTful Services
-- Companion to PROBLEM_WALKTHROUGH.md Problems 1–4. Sandbox ORDS schema.

---------------------------------------------------------------
-- §1. Paginated catalog handler + count (Problem 1)
---------------------------------------------------------------

-- 1a. Collection-or-item handler (binds :id, :offset, :limit)
SELECT JSON_OBJECT(
         'product_id' KEY p.product_id,
         'name'       KEY p.product_name,
         'price'      KEY p.price,
         'category'   KEY c.category_name
       )
FROM   products p
JOIN   categories c ON c.category_id = p.category_id
WHERE  (:id IS NULL OR p.product_id = :id)
ORDER  BY p.product_name
OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;

-- 1b. Matching total (same predicate — totals must agree)
SELECT COUNT(*) AS total FROM products
WHERE  (:id IS NULL OR product_id = :id);

---------------------------------------------------------------
-- §2. Privilege + audit (Problem 2)
---------------------------------------------------------------

-- 2a. Scope the privilege to exactly the catalog templates
BEGIN
  ORDS.DEFINE_PRIVILEGE(
    p_privilege_name => 'catalog_api',
    p_roles          => 'catalog_api_role',
    p_patterns       => '/catalog/v1/products/*',
    p_module_id      => 100
  );
  COMMIT;  -- persists the definition
END;
/

-- 2b. Who called what (audit trail per client)
SELECT client_id, url, method, status_code, created_on
FROM   ords_audit_log
ORDER  BY created_on DESC
FETCH  FIRST 20 ROWS ONLY;

---------------------------------------------------------------
-- §3. 500 triage kit (Problem 4)
---------------------------------------------------------------

-- 3a. Newest 500s first
SELECT url, method, status_code, error_message, created_on
FROM   ords_log
WHERE  created_on > SYSDATE - 1
AND    status_code = 500
ORDER  BY created_on DESC;

-- 3b. Session debug for the reproduce pass
BEGIN
  APEX_DEBUG.ENABLE(p_level => APEX_DEBUG.C_LOG_ALL);
END;
/
