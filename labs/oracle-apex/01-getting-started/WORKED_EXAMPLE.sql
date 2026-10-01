-- WORKED EXAMPLE: Expense Tracker core queries (labs/oracle-apex/01-getting-started)
-- Run in SQL Workshop / SQL*Plus as workspace schema.

-- 1) Department monthly totals (dashboard bar-chart source)
SELECT TO_CHAR(e.expense_date, 'YYYY-MM') AS label,
       SUM(e.amount) AS value
FROM expenses e
WHERE e.department_id = NVL(:G_DEPT_ID, e.department_id)
GROUP BY TO_CHAR(e.expense_date, 'YYYY-MM')
ORDER BY label;

-- 2) Duplicate-check validation (Form > Validations > PL/SQL Function Returning Boolean)
DECLARE
    l_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO l_count
    FROM expenses
    WHERE category    = :P2_CATEGORY
      AND amount      = :P2_AMOUNT
      AND expense_date = :P2_EXPENSE_DATE
      AND NVL(description,'~') = NVL(:P2_DESCRIPTION,'~')
      AND (:P2_EXPENSE_ID IS NULL OR expense_id != :P2_EXPENSE_ID);
    RETURN l_count = 0;  -- TRUE = valid, FALSE = reject with error message
END;
/
-- 3) Row-level-security smoke test: totals per department
SELECT d.department_name, COUNT(*) AS n, ROUND(SUM(e.amount),2) AS total
FROM expenses e JOIN departments d ON d.department_id = e.department_id
GROUP BY d.department_name
ORDER BY total DESC;
