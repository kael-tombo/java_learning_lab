# Exercises: Master-Detail Pages with Dynamic Actions

## Exercise 1: Build the Basic Master-Detail (Guided)
**Time**: 30 minutes  
**Difficulty**: Beginner

### Objective
Recreate the Order Management master-detail page from the walkthrough.

### Steps
1. **Create Tables** — Run the DDL from `PROBLEM_WALKTHROUGH.md` Step 1
2. **Create Application** — "Order Manager", Page 1 "Order Management"
3. **Master Region** — Interactive Report on `orders` with link column
4. **Page Item** — `P1_SELECTED_ORDER` (Hidden, Value Protected)
5. **Detail Region** — Interactive Grid on `order_items` with `WHERE order_id = :P1_SELECTED_ORDER`
6. **Dynamic Action** — Click on IR link → Set Value → Refresh Detail → Refresh Summary
6. **Test** — Click orders, verify detail updates instantly

### Verification
- [ ] Clicking Order #1001 shows 3 line items
- [ ] Clicking Order #1002 shows 2 line items
- [ ] No full page reload occurs (check browser Network tab)
- [ ] URL updates to include `P1_SELECTED_ORDER:1001`

---

## Exercise 2: Enable Inline Editing in Detail Grid
**Time**: 20 minutes  
**Difficulty**: Beginner-Intermediate

### Objective
Allow users to edit line item quantities and prices directly in the grid.

### Steps
1. **IG Attributes** — Edit: Enabled, Toolbar: Show (Add Row, Save)
2. **Column Attributes**:
   - `PRODUCT_NAME`: Text Field, Required
   - `QUANTITY`: Number Field, Required, Min=1
   - `UNIT_PRICE`: Number Field, Format: 999G999G990D00
   - `LINE_TOTAL`: Display Only (virtual column)
3. **IG Save Process** — Type: Interactive Grid - Save Data, Primary Key: `ITEM_ID`
4. **Recalc Process** — PL/SQL After IG Save:
   ```sql
   UPDATE orders o
   SET total_amount = (SELECT NVL(SUM(line_total),0) FROM order_items WHERE order_id = o.order_id)
   WHERE order_id = :P1_SELECTED_ORDER;
   ```
5. **DA: After Refresh on IG** → Refresh "Order Summary" region

### Verification
- [ ] Can edit quantity, price inline
- [ ] Clicking Save persists changes
- [ ] Order total updates automatically
- [ ] Adding new row works (ORDER_ID defaults to P1_SELECTED_ORDER)

---

## Exercise 3: Add Client-Side Line Total Calculation
**Time**: 15 minutes  
**Difficulty**: Intermediate

### Objective
Show line total instantly as user types (before Save).

### Steps
1. **Create Dynamic Action**:
   - Event: `Change`
   - Selection Type: Column(s) in Interactive Grid
   - Region: Order Items
   - Columns: `QUANTITY`, `UNIT_PRICE`
2. **True Action**: Execute JavaScript
   ```javascript
   var model = this.model;
   var record = this.record;
   var qty = parseFloat(model.getValue(record, 'QUANTITY')) || 0;
   var price = parseFloat(model.getValue(record, 'UNIT_PRICE')) || 0;
   model.setValue(record, 'LINE_TOTAL', qty * price);
   ```

### Verification
- [ ] Changing quantity instantly updates line total
- [ ] Changing price instantly updates line total
- [ ] Virtual column in DB matches on save

---

## Exercise 4: Add Order Status Transition Control
**Time**: 20 minutes  
**Difficulty**: Intermediate

### Objective
Add a status dropdown and button to update order status with validation.

### Steps
1. **Page Items**:
   - `P1_NEW_STATUS` (Select List): PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
   - Condition: `P1_SELECTED_ORDER IS NOT NULL`
2. **Button**: "Update Status" (next to select list)
3. **Dynamic Action**: Click "Update Status"
   - True Action 1: Execute PL/SQL
     ```sql
     DECLARE
         l_old_status VARCHAR2(20);
     BEGIN
         SELECT status INTO l_old_status FROM orders WHERE order_id = :P1_SELECTED_ORDER;
         CASE
             WHEN l_old_status = 'SHIPPED' AND :P1_NEW_STATUS = 'PENDING' THEN
                 RAISE_APPLICATION_ERROR(-20001, 'Cannot revert from SHIPPED to PENDING');
             WHEN l_old_status = 'DELIVERED' AND :P1_NEW_STATUS != 'CANCELLED' THEN
                 RAISE_APPLICATION_ERROR(-20002, 'Only cancellation allowed after delivery');
             ELSE
                 UPDATE orders SET status = :P1_NEW_STATUS, updated_date = SYSDATE
                 WHERE order_id = :P1_SELECTED_ORDER;
         END CASE;
     END;
     ```
   - True Action 2: Refresh "Orders" IR, "Order Items" IG, "Order Summary"

### Verification
- [ ] Valid transitions work (PENDING → CONFIRMED → SHIPPED → DELIVERED)
- [ ] Invalid transitions show error (SHIPPED → PENDING)
- [ ] Regions refresh to show new status

---

## Exercise 5: Persist Selection Across Browser Refresh
**Time**: 15 minutes  
**Difficulty**: Intermediate

### Objective
Selected order remains highlighted after F5 refresh.

### Steps
1. **Master IR Link Column Target**: 
   ```
   f?p=&APP_ID.:1:&SESSION.:::P1_SELECTED_ORDER:#ORDER_ID#
   ```
2. **Page Item `P1_SELECTED_ORDER`**: Source Type = URL, Source = `P1_SELECTED_ORDER`
3. **Dynamic Action**: Page Load
   - Condition: `P1_SELECTED_ORDER IS NOT NULL`
   - True Action 1: Refresh "Order Items" region
   - True Action 2: Refresh "Order Summary" region
   - True Action 3: Execute JavaScript (highlight row)
     ```javascript
     // Highlight the row matching P1_SELECTED_ORDER
     var orderId = apex.item('P1_SELECTED_ORDER').getValue();
     $('a.select-order-link').each(function() {
         if ($(this).text() == orderId) {
             $(this).closest('tr').addClass('highlight-row');
         }
     });
     ```

### Verification
- [ ] Select Order #1001
- [ ] Press F5 (browser refresh)
- [ ] Order #1001 still highlighted, detail shows correct items

---

## Exercise 6: Add Validation for Negative Inventory
**Time**: 15 minutes  
**Difficulty**: Intermediate

### Objective
Prevent saving line items that exceed available inventory.

### Steps
1. **Create Inventory Table**:
   ```sql
   CREATE TABLE inventory (
       product_name VARCHAR2(200) PRIMARY KEY,
       stock_quantity NUMBER DEFAULT 0
   );
   INSERT INTO inventory VALUES ('Wireless Mouse', 50);
   INSERT INTO inventory VALUES ('USB-C Hub', 30);
   INSERT INTO inventory VALUES ('Laptop Sleeve', 25);
   INSERT INTO inventory VALUES ('Monitor 27"', 10);
   INSERT INTO inventory VALUES ('Keyboard', 20);
   INSERT INTO inventory VALUES ('Webcam HD', 15);
   ```
2. **Validation on Page** (Processing → Validations → Create):
   - Type: PL/SQL Function Body (Returning Error Message)
   - Code:
     ```sql
     DECLARE
         l_shortage VARCHAR2(4000);
     BEGIN
         FOR item IN (
             SELECT oi.product_name, oi.quantity,
                    NVL(i.stock_quantity, 0) AS stock
             FROM order_items oi
             LEFT JOIN inventory i ON i.product_name = oi.product_name
             WHERE oi.order_id = :P1_SELECTED_ORDER
         ) LOOP
             IF item.stock < item.quantity THEN
                 l_shortage := l_shortage || ', ' || item.product_name
                     || ' (ordered: ' || item.quantity || ', available: ' || item.stock || ')';
             END IF;
         END LOOP;
         IF l_shortage IS NOT NULL THEN
             RETURN 'Insufficient inventory for: ' || LTRIM(l_shortage, ', ');
         END IF;
         RETURN NULL;
     END;
     ```
   - When: After IG Save Process

### Verification
- [ ] Try to order 100 "Wireless Mouse" (stock: 50)
- [ ] Save shows validation error
- [ ] Valid quantities save successfully

---

## Exercise 7: Add Keyboard Navigation (Accessibility)
**Time**: 15 minutes  
**Difficulty**: Advanced

### Objective
Allow keyboard users to navigate master rows and trigger detail refresh.

### Steps
1. **Modify Master IR**: Add `tabindex="0"` to link column
2. **Dynamic Action**: Event `Key Down` on `.select-order-link`
   - Condition: `event.key === 'Enter' || event.key === ' '`
   - True Action: Click (trigger the click DA)
3. **Dynamic Action**: Event `Focus` on `.select-order-link`
   - True Action: Execute JavaScript (visual focus indicator)
     ```javascript
     $(this.triggeringElement).closest('tr').addClass('focus-ring');
     ```
4. **Dynamic Action**: Event `Blur` on `.select-order-link`
   - True Action: Execute JavaScript
     ```javascript
     $(this.triggeringElement).closest('tr').removeClass('focus-ring');
     ```

### Verification
- [ ] Tab to navigate between order rows
- [ ] Enter/Space selects row, updates detail
- [ ] Visual focus indicator visible

---

## Exercise 8: Multi-Level Master-Detail (Challenge)
**Time**: 45 minutes  
**Difficulty**: Advanced

### Objective
Add a third level: Order Item → Serial Numbers

### Schema Extension
```sql
CREATE TABLE item_serials (
    serial_id     NUMBER PRIMARY KEY,
    item_id       NUMBER REFERENCES order_items(item_id) ON DELETE CASCADE,
    serial_number VARCHAR2(100) UNIQUE NOT NULL,
    status        VARCHAR2(20) DEFAULT 'AVAILABLE'
);
CREATE SEQUENCE serial_seq START WITH 100000;
```

### Requirements
1. Add `P1_SELECTED_ITEM` page item
2. Add third region "Serial Numbers" (IG on `item_serials WHERE item_id = :P1_SELECTED_ITEM`)
3. Dynamic Action: Click on Order Items IG row → Set `P1_SELECTED_ITEM` → Refresh Serials
4. Enable inline editing of serial numbers

### Verification
- [ ] Click Order → Shows Items
- [ ] Click Item → Shows Serials
- [ ] All three levels editable
- [ ] Cascade delete works (delete order → items → serials gone)

---

## Exercise 9: Performance Test with Large Dataset
**Time**: 20 minutes  
**Difficulty**: Advanced

### Objective
Verify master-detail performs with 100K+ orders.

### Steps
1. **Generate Test Data**:
   ```sql
   BEGIN
       FOR i IN 1..10000 LOOP
           INSERT INTO customers VALUES (100+i, 'Cust'||i, 'Test', 'cust'||i||'@test.com', '555-0000', SYSDATE);
       END LOOP;
       
       FOR i IN 1..50000 LOOP
           INSERT INTO orders VALUES (10000+i, MOD(i,10000)+101, SYSDATE-DBMS_RANDOM.VALUE(0,365),
               DECODE(MOD(i,5),0,'PENDING',1,'CONFIRMED',2,'SHIPPED',3,'DELIVERED','CANCELLED'),
               DBMS_RANDOM.VALUE(10,5000), NULL, 'TEST', SYSDATE);
       END LOOP;
       
       FOR i IN 1..200000 LOOP
           INSERT INTO order_items VALUES (100000+i, 10000+MOD(i,50000)+1, 
               'Product '||MOD(i,1000), DBMS_RANDOM.VALUE(1,10), DBMS_RANDOM.VALUE(10,500));
       END LOOP;
       COMMIT;
   END;
   /
   ```
2. **Test**:
   - Load Page 1
   - Scroll through orders (pagination)
   - Click various orders
   - Measure detail refresh time (Network tab)

### Verification
- [ ] Master IR loads in < 2 seconds
- [ ] Detail IG refreshes in < 500ms
- [ ] No "APEX session expired" errors

---

## Exercise 10: Package as Reusable Component
**Time**: 30 minutes  
**Difficulty**: Advanced

### Objective
Create a plug-in or blueprint for master-detail pattern.

### Steps
1. **Create Page Template** with two-region layout
2. **Define Substitution Strings**:
   - `#MASTER_QUERY#`
   - `#DETAIL_QUERY#`
   - `#MASTER_PK#`
   - `#DETAIL_FK#`
3. **Document Setup Instructions** in a README
4. **Test** by building a new master-detail (e.g., Customer → Contacts) in 10 minutes

### Deliverable
A reusable pattern documented in `MINI_PROJECT/master_detail_pattern.md`

---

## Solutions Reference
All exercises have working solutions in:
- `MINI_PROJECT/` — Extended solutions
- `REAL_WORLD_PROJECT/` — Production-ready implementation
- `WORKED_EXAMPLE.sql` — Complete SQL/PLSQL reference