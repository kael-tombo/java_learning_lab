# Exercises: SQL Joins (Lab 02)

**Prerequisites:** Read `PROBLEM_WALKTHROUGH.md`  
**Difficulty:** Progressive (Easy → Medium → Hard)

---

## Exercise 1: JOIN Type Practice (Easy)

### Task
Write queries using different JOIN types on the sample schema.

### Schema
```sql
-- Employee: id, name, salary, departmentId
-- Department: id, name
-- Orders: id, customerId
-- Customers: id, name
```

### Requirements
```sql
-- 1a. INNER JOIN: Employees with their department names
-- 1b. LEFT JOIN: All employees, department name if exists
-- 1c. RIGHT JOIN: All departments, employee names if any
-- 1d. FULL OUTER JOIN: All employees and all departments
-- 1e. CROSS JOIN: All employee-department combinations (Cartesian)
```

---

## Exercise 2: Anti-Join Patterns (Easy)

### Task
Find customers who never ordered using 3 different approaches.

### Requirements
```sql
-- 2a. LEFT JOIN / IS NULL
-- 2b. NOT EXISTS
-- 2c. NOT IN (with NULL-safe subquery)
-- 2d. Explain which is preferred and why
```

---

## Exercise 3: Self-Join Variations (Easy)

### Task
Practice self-joins on Employee table.

### Requirements
```sql
-- 3a. Employees earning more than their manager (from walkthrough)
-- 3b. Employees with same manager (list pairs: employee1, employee2, manager_name)
-- 3c. Manager and their direct reports count
-- 3d. Employees who are also managers (have at least one report)
-- 3e. Multi-level: Employee → Manager → Director (2-level self-join)
```

---

## Exercise 4: Top N Per Group (Medium)

### Task
Variations on "Department Top 3 Salaries".

### Requirements
```sql
-- 4a. Top 2 salaries per department (DENSE_RANK)
-- 4b. Top 3 salaries per department using LATERAL (12c+)
-- 4c. Top 3 salaries per department using correlated subquery (pre-12c)
-- 4d. Bottom 3 salaries per department
-- 4e. Top 3 salaries per department, but only for departments with > 5 employees
-- 4f. Top 3 *distinct* salaries per department (already handled by DENSE_RANK)
```

---

## Exercise 5: Complex Multi-Table Joins (Medium)

### Task
Join 3+ tables with filtering.

### Requirements
```sql
-- Schema additions:
-- OrderItems: orderId, productId, quantity, unitPrice
-- Products: id, name, categoryId
-- Categories: id, name

-- 5a. Customer name, order date, product name, quantity, total (quantity * unitPrice)
-- 5b. Total revenue per customer
-- 5c. Top 5 customers by revenue
-- 5d. Products never ordered (anti-join)
-- 5e. Categories with no products
-- 5f. Customers who ordered from all categories (relational division)
```

---

## Exercise 6: LATERAL Join Practice (Medium)

### Task
Use CROSS JOIN LATERAL for correlated subqueries.

### Requirements
```sql
-- 6a. For each department, get top 2 highest-paid employees (LATERAL)
-- 6b. For each customer, get their most recent order (LATERAL)
-- 6c. For each product, get total quantity sold (LATERAL with aggregate)
-- 6d. Compare LATERAL vs correlated subquery performance
```

---

## Exercise 7: Execution Plan Analysis (Medium)

### Task
Analyze and optimize join queries.

### Requirements
```sql
-- 7a. EXPLAIN PLAN for Exercise 5a query
-- 7b. Identify: HASH JOIN vs NESTED LOOPS vs MERGE JOIN
-- 7c. Create indexes to change join method
-- 7d. Use /*+ LEADING(...) */ hint to control join order
-- 7e. Use /*+ USE_HASH(...) */ or /*+ USE_NL(...) */ hints
```

---

## Exercise 8: Advanced Scenarios (Hard)

### Task
Real-world join challenges.

### Requirements
```sql
-- 8a. Find employees who have the same salary as someone in a different department
-- 8b. Find "manager chains" - employee, their manager, their manager's manager (recursive)
-- 8c. Customer lifetime value: sum of all orders, with customer details
-- 8d. Market basket analysis: products frequently bought together (self-join on OrderItems)
-- 8e. Find gaps: dates with no orders (generate series + left join)
```

---

## Exercise 9: Partition-Wise Joins (Hard)

### Task
Design partitioning for join performance.

### Requirements
```sql
-- 9a. Partition Orders by order_date (range)
-- 9b. Partition OrderItems by orderId (reference partitioning)
-- 9c. Show how partition-wise join works for "orders in 2023 with items"
-- 9d. Create local indexes on partitioned tables
-- 9e. Compare query plan with/without partition-wise join
```

---

## Exercise 10: Cross-Dialect JOINs (Hard)

### Task
Translate join patterns to other SQL dialects.

### Requirements
```sql
-- 10a. Oracle LATERAL → PostgreSQL LATERAL / MySQL LATERAL (8.0+) / SQL Server CROSS APPLY
-- 10b. Oracle FETCH FIRST WITH TIES → PostgreSQL FETCH FIRST WITH TIES / SQL Server TOP 3 WITH TIES
-- 10c. Oracle DENSE_RANK → All dialects (standard)
-- 10d. Oracle (+) outer join syntax → ANSI JOIN syntax
-- 10e. Oracle star transformation hint → PostgreSQL enable_partitionwise_join
```

---

## Solutions

### Exercise 1
```sql
-- 1a: SELECT e.name, d.name FROM employee e JOIN department d ON e.departmentId = d.id;
-- 1b: SELECT e.name, d.name FROM employee e LEFT JOIN department d ON e.departmentId = d.id;
-- 1c: SELECT e.name, d.name FROM employee e RIGHT JOIN department d ON e.departmentId = d.id;
-- 1d: SELECT e.name, d.name FROM employee e FULL OUTER JOIN department d ON e.departmentId = d.id;
-- 1e: SELECT e.name, d.name FROM employee e CROSS JOIN department d;
```

### Exercise 2
```sql
-- 2a: SELECT c.name FROM customers c LEFT JOIN orders o ON c.id = o.customerId WHERE o.id IS NULL;
-- 2b: SELECT c.name FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customerId = c.id);
-- 2c: SELECT c.name FROM customers c WHERE c.id NOT IN (SELECT customerId FROM orders WHERE customerId IS NOT NULL);
-- 2d: NOT EXISTS preferred — handles NULLs correctly, often same plan as LEFT JOIN/IS NULL, more readable.
```

### Exercise 3
```sql
-- 3a: SELECT e1.name FROM employee e1 JOIN employee e2 ON e1.managerId = e2.id WHERE e1.salary > e2.salary;
-- 3b: SELECT e1.name emp1, e2.name emp2, m.name mgr FROM employee e1 JOIN employee e2 ON e1.managerId = e2.managerId AND e1.id < e2.id JOIN employee m ON e1.managerId = m.id;
-- 3c: SELECT m.name, COUNT(e.id) reports FROM employee m LEFT JOIN employee e ON m.id = e.managerId GROUP BY m.id, m.name;
-- 3d: SELECT DISTINCT m.name FROM employee m JOIN employee e ON m.id = e.managerId;
-- 3e: SELECT e.name emp, m.name mgr, d.name dir FROM employee e JOIN employee m ON e.managerId = m.id JOIN employee d ON m.managerId = d.id;
```

### Exercise 4
```sql
-- 4a: Change rank filter to <= 2
-- 4b: CROSS JOIN LATERAL (SELECT name, salary FROM employee WHERE departmentId = d.id ORDER BY salary DESC FETCH FIRST 3 ROWS WITH TIES)
-- 4c: SELECT * FROM employee e WHERE (SELECT COUNT(DISTINCT salary) FROM employee WHERE departmentId = e.departmentId AND salary > e.salary) < 3;
-- 4d: DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary ASC)
-- 4e: Add HAVING COUNT(*) > 5 in department inline view
-- 4f: DENSE_RANK already handles distinct salaries
```

### Exercise 5
```sql
-- 5a: SELECT c.name, o.order_date, p.name, oi.quantity, oi.quantity * oi.unitPrice total
--     FROM customers c JOIN orders o ON c.id = o.customerId
--     JOIN orderitems oi ON o.id = oi.orderId
--     JOIN products p ON oi.productId = p.id;
-- 5b: SELECT c.name, SUM(oi.quantity * oi.unitPrice) revenue FROM ... GROUP BY c.name;
-- 5c: Add ORDER BY revenue DESC FETCH FIRST 5 ROWS ONLY;
-- 5d: SELECT p.name FROM products p LEFT JOIN orderitems oi ON p.id = oi.productId WHERE oi.orderId IS NULL;
-- 5e: SELECT cat.name FROM categories cat LEFT JOIN products p ON cat.id = p.categoryId WHERE p.id IS NULL;
-- 5f: SELECT c.name FROM customers c WHERE NOT EXISTS (
--       SELECT cat.id FROM categories cat
--       WHERE NOT EXISTS (
--         SELECT 1 FROM orders o JOIN orderitems oi ON o.id = oi.orderId JOIN products p ON oi.productId = p.id
--         WHERE o.customerId = c.id AND p.categoryId = cat.id
--       )
--     );
```

### Exercise 6
```sql
-- 6a: SELECT d.name, e.name, e.salary FROM department d
--     CROSS JOIN LATERAL (SELECT name, salary FROM employee WHERE departmentId = d.id ORDER BY salary DESC FETCH FIRST 2 ROWS ONLY) e;
-- 6b: SELECT c.name, o.order_date, o.total FROM customers c
--     CROSS JOIN LATERAL (SELECT order_date, total FROM orders WHERE customerId = c.id ORDER BY order_date DESC FETCH FIRST 1 ROW ONLY) o;
-- 6c: SELECT p.name, COALESCE(oi.total_qty, 0) FROM products p
--     CROSS JOIN LATERAL (SELECT SUM(quantity) total_qty FROM orderitems WHERE productId = p.id) oi;
```

### Exercise 7
```sql
-- 7a: EXPLAIN PLAN FOR [5a query]; SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
-- 7b: Look for HASH JOIN (large tables), NESTED LOOPS (small driving table + index), MERGE JOIN (sorted inputs)
-- 7c: Index on join columns: orders(customerId), orderitems(orderId), orderitems(productId), products(categoryId)
-- 7d: /*+ LEADING(c o oi p) */ — drives from customers
-- 7e: /*+ USE_HASH(o oi) USE_NL(p) */
```

### Exercise 8
```sql
-- 8a: SELECT e1.name, e2.name, e1.salary FROM employee e1 JOIN employee e2 ON e1.salary = e2.salary AND e1.departmentId != e2.departmentId;
-- 8b: WITH RECURSIVE chain AS (
--       SELECT id, name, managerId, 1 lvl, CAST(name AS VARCHAR2(4000)) path FROM employee WHERE managerId IS NULL
--       UNION ALL
--       SELECT e.id, e.name, e.managerId, c.lvl+1, c.path || ' -> ' || e.name
--       FROM employee e JOIN chain c ON e.managerId = c.id
--     ) SELECT * FROM chain;
-- 8c: SELECT c.id, c.name, COALESCE(SUM(oi.quantity * oi.unitPrice), 0) ltv
--     FROM customers c LEFT JOIN orders o ON c.id = o.customerId
--     LEFT JOIN orderitems oi ON o.id = oi.orderId
--     GROUP BY c.id, c.name;
-- 8d: SELECT oi1.productId p1, oi2.productId p2, COUNT(DISTINCT oi1.orderId) freq
--     FROM orderitems oi1 JOIN orderitems oi2 ON oi1.orderId = oi2.orderId AND oi1.productId < oi2.productId
--     GROUP BY oi1.productId, oi2.productId ORDER BY freq DESC;
-- 8e: WITH dates AS (SELECT TRUNC(SYSDATE)-level+1 dt FROM dual CONNECT BY level <= 365)
--     SELECT d.dt FROM dates d LEFT JOIN orders o ON TRUNC(o.order_date) = d.dt WHERE o.id IS NULL;
```

### Exercise 9
```sql
-- 9a: CREATE TABLE orders (...) PARTITION BY RANGE (order_date) (...);
-- 9b: CREATE TABLE orderitems (...) PARTITION BY REFERENCE (order_fk);
-- 9c: Query with order_date filter → partition pruning on orders → partition-wise join to orderitems
-- 9d: CREATE INDEX orders_cust_idx ON orders(customerId) LOCAL;
-- 9e: Plan shows PARTITION RANGE ITERATOR + PARTITION-WISE JOIN
```

### Exercise 10
```sql
-- 10a: PostgreSQL: CROSS JOIN LATERAL; MySQL 8.0+: CROSS JOIN LATERAL; SQL Server: CROSS APPLY
-- 10b: PostgreSQL: FETCH FIRST 3 ROWS WITH TIES; SQL Server: SELECT TOP 3 WITH TIES
-- 10c: Standard SQL — same syntax
-- 10d: Oracle: WHERE a.id = b.id(+) → ANSI: FROM a LEFT JOIN b ON a.id = b.id
-- 10e: PostgreSQL: SET enable_partitionwise_join = on; (or partition tables similarly)
```

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1 | 10 | All JOIN types correct |
| 2 | 15 | Three anti-join patterns, explanation |
| 3 | 20 | Self-join variations correct |
| 4 | 25 | Top N per group with multiple methods |
| 5 | 25 | Multi-table joins with correct grain |
| 6 | 20 | LATERAL usage correct |
| 7 | 20 | Plan analysis, hints |
| 8 | 30 | Advanced scenarios solved |
| 9 | 20 | Partitioning design correct |
| 10 | 15 | Dialect translations accurate |

**Total: 200 points**

---

## Next Steps

1. Run against Oracle HR schema or equivalent
2. Practice: LeetCode SQL Medium problems
3. Study: Execution plan operations in depth
4. Read: Oracle SQL Tuning Guide — JOIN methods