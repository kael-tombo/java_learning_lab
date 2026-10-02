-- WORKED_SQL_EXAMPLE — Supply Chain (Min-Max & ROP)
-- Companion to PROBLEM_WALKTHROUGH.md Steps 1–6. Sandbox only.

---------------------------------------------------------------
-- §1. Classification spot-checks (Step 1)
---------------------------------------------------------------

-- 1a. Top-10 SKUs by usage value (the ABC head)
SELECT msib.segment1 AS item, msib.description,
       SUM(NVL(mtln.transaction_quantity,0) * NVL(mtln.transaction_cost,0)) AS usage_value
FROM   mtl_system_items_b msib
LEFT JOIN mtl_transaction_lt_account mtln
  ON   msib.inventory_item_id = mtln.inventory_item_id
  AND  msib.organization_id = mtln.organization_id
  AND  mtln.transaction_date > SYSDATE - 365
WHERE  msib.organization_id = :org_id
AND    msib.inventory_item_flag = 'Y'
GROUP  BY msib.segment1, msib.description
ORDER  BY usage_value DESC
FETCH  FIRST 10 ROWS ONLY;

-- 1b. Current class distribution (after classify_all_items)
SELECT attribute1 AS abc, attribute2 AS fsn, COUNT(*) AS skus
FROM   mtl_system_items_b
WHERE  organization_id = :org_id AND attribute_category = 'INV_CLASSIFICATION'
GROUP  BY attribute1, attribute2
ORDER  BY 1, 2;

---------------------------------------------------------------
-- §2. Parameters for one SKU (Steps 2–4)
---------------------------------------------------------------

-- 2a. Demand params + lead-time params + computed SS/ROP (bind :item, :org)
SELECT dp.avg_monthly_demand, dp.demand_std_dev, dp.demand_cv,
       lp.avg_leadtime_days, lp.leadtime_std_dev,
       xx_reorder_calc_pkg.calculate_safety_stock(:item, :org, 0.95) AS ss_95,
       xx_reorder_calc_pkg.calculate_reorder_point(:item, :org, 0.95) AS rop_95
FROM   xx_inv_demand_params dp
LEFT JOIN xx_inv_leadtime_params lp
  ON   dp.inventory_item_id = lp.inventory_item_id
  AND  dp.organization_id = lp.organization_id
WHERE  dp.inventory_item_id = :item AND dp.organization_id = :org;

-- 2b. z-factor ladder (sanity: 98/95/90 → 2.05/1.64/1.28)
SELECT xx_reorder_calc_pkg.get_z_factor(0.98) AS z98,
       xx_reorder_calc_pkg.get_z_factor(0.95) AS z95,
       xx_reorder_calc_pkg.get_z_factor(0.90) AS z90
FROM DUAL;

---------------------------------------------------------------
-- §3. Recommendations + health (Steps 5–6)
---------------------------------------------------------------

-- 3a. Regenerate and read top priorities for an org
BEGIN xx_generate_replenishment(:org_id); END;
/

SELECT item_code, current_onhand, min_quantity, max_quantity,
       recommended_order_qty, priority
FROM   xx_replenishment_recommendations
WHERE  organization_id = :org_id
ORDER  BY CASE priority WHEN 'CRITICAL' THEN 0 WHEN 'HIGH' THEN 1
                        WHEN 'MEDIUM' THEN 2 ELSE 3 END,
           recommended_order_qty DESC
FETCH  FIRST 20 ROWS ONLY;

-- 3b. Health triage (rank 0 first)
SELECT item_code, current_onhand, reorder_point, safety_stock,
       inventory_health_status, health_priority
FROM   xx_inventory_health_dashboard
WHERE  organization_id = :org_id AND health_priority <= 1
ORDER  BY health_priority, current_onhand;
