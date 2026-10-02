-- =====================================================================
-- WORKED EXAMPLE: Master-Detail Order Management System
-- Complete SQL/PLSQL implementation for Lab 02: Workshop Builder
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. DATABASE SCHEMA (Run as schema owner)
-- ---------------------------------------------------------------------

-- Customers table
CREATE TABLE customers (
    customer_id   NUMBER PRIMARY KEY,
    first_name    VARCHAR2(50) NOT NULL,
    last_name     VARCHAR2(50) NOT NULL,
    email         VARCHAR2(100) UNIQUE NOT NULL,
    phone         VARCHAR2(20),
    created_date  DATE DEFAULT SYSDATE
);

-- Orders table (master)
CREATE TABLE orders (
    order_id      NUMBER PRIMARY KEY,
    customer_id   NUMBER NOT NULL REFERENCES customers(customer_id),
    order_date    DATE NOT NULL,
    status        VARCHAR2(20) DEFAULT 'PENDING'
        CHECK (status IN ('PENDING','CONFIRMED','SHIPPED','DELIVERED','CANCELLED')),
    total_amount  NUMBER(12,2) DEFAULT 0,
    notes         VARCHAR2(1000),
    created_by    VARCHAR2(100),
    created_date  DATE DEFAULT SYSDATE,
    updated_date  DATE
);

-- Order items table (detail) - with VIRTUAL column for line_total
CREATE TABLE order_items (
    item_id       NUMBER PRIMARY KEY,
    order_id      NUMBER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_name  VARCHAR2(200) NOT NULL,
    quantity      NUMBER NOT NULL CHECK (quantity > 0),
    unit_price    NUMBER(10,2) NOT NULL,
    line_total    NUMBER(12,2) GENERATED ALWAYS AS (quantity * unit_price) VIRTUAL
);

-- Inventory table (for validation exercise)
CREATE TABLE inventory (
    product_name     VARCHAR2(200) PRIMARY KEY,
    stock_quantity   NUMBER DEFAULT 0
);

-- API call log (for audit)
CREATE TABLE api_call_log (
    call_id         NUMBER PRIMARY KEY,
    endpoint        VARCHAR2(500),
    request_body    CLOB,
    response_body   CLOB,
    http_status     NUMBER,
    duration_ms     NUMBER,
    created_date    DATE DEFAULT SYSDATE
);

-- Sequences
CREATE SEQUENCE customer_seq START WITH 100;
CREATE SEQUENCE order_seq START WITH 1000;
CREATE SEQUENCE item_seq START WITH 10000;
CREATE SEQUENCE api_log_seq START WITH 1;

-- Indexes for performance
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_items_order ON order_items(order_id);

-- ---------------------------------------------------------------------
-- 2. SAMPLE DATA
-- ---------------------------------------------------------------------

INSERT ALL
    INTO customers VALUES (1, 'John', 'Smith', 'john.smith@email.com', '555-0101', SYSDATE)
    INTO customers VALUES (2, 'Jane', 'Doe', 'jane.doe@email.com', '555-0102', SYSDATE)
    INTO customers VALUES (3, 'Robert', 'Johnson', 'rjohnson@email.com', '555-0103', SYSDATE)
SELECT * FROM dual;

INSERT INTO orders VALUES (1001, 1, SYSDATE - 5, 'CONFIRMED', 299.99, 'Rush delivery', 'APP', SYSDATE, NULL);
INSERT INTO orders VALUES (1002, 1, SYSDATE - 3, 'SHIPPED', 549.50, NULL, 'APP', SYSDATE, NULL);
INSERT INTO orders VALUES (1003, 2, SYSDATE - 1, 'PENDING', 129.99, 'Gift wrap', 'APP', SYSDATE, NULL);

INSERT INTO order_items VALUES (10001, 1001, 'Wireless Mouse', 2, 49.99);
INSERT INTO order_items VALUES (10002, 1001, 'USB-C Hub', 1, 89.99);
INSERT INTO order_items VALUES (10003, 1001, 'Laptop Sleeve', 1, 110.02);
INSERT INTO order_items VALUES (10004, 1002, 'Monitor 27"', 1, 349.99);
INSERT INTO order_items VALUES (10005, 1002, 'Keyboard', 1, 199.51);
INSERT INTO order_items VALUES (10006, 1003, 'Webcam HD', 1, 129.99);

INSERT INTO inventory VALUES ('Wireless Mouse', 50);
INSERT INTO inventory VALUES ('USB-C Hub', 30);
INSERT INTO inventory VALUES ('Laptop Sleeve', 25);
INSERT INTO inventory VALUES ('Monitor 27"', 10);
INSERT INTO inventory VALUES ('Keyboard', 20);
INSERT INTO inventory VALUES ('Webcam HD', 15);

COMMIT;

-- ---------------------------------------------------------------------
-- 3. MASTER QUERY (for Interactive Report)
-- ---------------------------------------------------------------------

SELECT
    o.order_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    o.order_date,
    o.status,
    o.total_amount,
    o.notes,
    (SELECT COUNT(*) FROM order_items oi WHERE oi.order_id = o.order_id) AS item_count
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
ORDER BY o.order_date DESC;

-- ---------------------------------------------------------------------
-- 4. DETAIL QUERY (for Interactive Grid)
-- ---------------------------------------------------------------------

SELECT
    oi.item_id,
    oi.order_id,
    oi.product_name,
    oi.quantity,
    oi.unit_price,
    oi.line_total
FROM order_items oi
WHERE oi.order_id = :P1_SELECTED_ORDER
ORDER BY oi.item_id;

-- ---------------------------------------------------------------------
-- 5. SUMMARY QUERY (for Classic Report region)
-- ---------------------------------------------------------------------

SELECT
    o.order_id,
    c.first_name || ' ' || c.last_name AS customer,
    o.order_date,
    o.status,
    o.total_amount,
    o.notes,
    COUNT(oi.item_id) AS total_items,
    SUM(oi.line_total) AS computed_total
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_id = :P1_SELECTED_ORDER
GROUP BY o.order_id, c.first_name, c.last_name, o.order_date,
         o.status, o.total_amount, o.notes;

-- ---------------------------------------------------------------------
-- 6. RECALCULATE ORDER TOTAL (Page Process after IG Save)
-- ---------------------------------------------------------------------

UPDATE orders o
SET o.total_amount = (
    SELECT NVL(SUM(oi.line_total), 0)
    FROM order_items oi
    WHERE oi.order_id = o.order_id
),
    o.updated_date = SYSDATE
WHERE o.order_id = :P1_SELECTED_ORDER;

-- ---------------------------------------------------------------------
-- 7. VALIDATION: QUANTITY > 0 (Page Validation)
-- ---------------------------------------------------------------------

DECLARE
    l_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO l_count
    FROM order_items
    WHERE order_id = :P1_SELECTED_ORDER
      AND quantity <= 0;
    IF l_count > 0 THEN
        RETURN 'Quantity must be greater than zero for all items.';
    END IF;
    RETURN NULL;
END;

-- ---------------------------------------------------------------------
-- 8. VALIDATION: INVENTORY CHECK (Page Validation)
-- ---------------------------------------------------------------------

DECLARE
    l_stock NUMBER;
    l_shortage VARCHAR2(4000);
BEGIN
    FOR item IN (
        SELECT product_name, quantity
        FROM order_items
        WHERE order_id = :P1_SELECTED_ORDER
    ) LOOP
        SELECT NVL(MAX(stock_quantity), 0) INTO l_stock
        FROM inventory WHERE product_name = item.product_name;

        IF l_stock < item.quantity THEN
            l_shortage := l_shortage || ', ' || item.product_name
                || ' (ordered: ' || item.quantity || ', available: ' || l_stock || ')';
        END IF;
    END LOOP;

    IF l_shortage IS NOT NULL THEN
        RETURN 'Insufficient inventory for: ' || LTRIM(l_shortage, ', ');
    END IF;
    RETURN NULL;
END;

-- ---------------------------------------------------------------------
-- 9. UPDATE ORDER STATUS WITH TRANSITION VALIDATION (DA PL/SQL)
-- ---------------------------------------------------------------------

DECLARE
    l_old_status VARCHAR2(20);
BEGIN
    SELECT status INTO l_old_status FROM orders WHERE order_id = :P1_SELECTED_ORDER;
    
    CASE
        WHEN l_old_status = 'SHIPPED' AND :P1_NEW_STATUS = 'PENDING' THEN
            RAISE_APPLICATION_ERROR(-20001, 'Cannot revert from SHIPPED to PENDING');
        WHEN l_old_status = 'DELIVERED' AND :P1_NEW_STATUS != 'CANCELLED' THEN
            RAISE_APPLICATION_ERROR(-20002, 'Only cancellation allowed after delivery');
        WHEN l_old_status = 'CANCELLED' AND :P1_NEW_STATUS != 'CANCELLED' THEN
            RAISE_APPLICATION_ERROR(-20003, 'Cannot change status of cancelled order');
        ELSE
            UPDATE orders
            SET status = :P1_NEW_STATUS,
                updated_date = SYSDATE
            WHERE order_id = :P1_SELECTED_ORDER;
    END CASE;
END;

-- ---------------------------------------------------------------------
-- 10. CLIENT-SIDE LINE TOTAL RECALCULATION (DA JavaScript)
-- ---------------------------------------------------------------------

/*
Dynamic Action: Change on QUANTITY, UNIT_PRICE columns in Interactive Grid
True Action: Execute JavaScript
*/

function recalcLineTotal(model, record) {
    var qty = parseFloat(model.getValue(record, 'QUANTITY')) || 0;
    var price = parseFloat(model.getValue(record, 'UNIT_PRICE')) || 0;
    model.setValue(record, 'LINE_TOTAL', qty * price);
}

// In DA: this.model and this.record are provided by APEX IG change event
recalcLineTotal(this.model, this.record);

-- ---------------------------------------------------------------------
-- 11. HIGHLIGHT SELECTED MASTER ROW (DA JavaScript)
-- ---------------------------------------------------------------------

/*
Dynamic Action: Click on .select-order-link
True Action: Execute JavaScript
*/

// Remove previous highlight
$('tr.highlight-row').removeClass('highlight-row');

// Highlight current row
$(this.triggeringElement).closest('tr').addClass('highlight-row');

// Optional: Update display item
$('#P1_SELECTED_ORDER_DISPLAY').text('Order #' + apex.item('P1_SELECTED_ORDER').getValue());

-- ---------------------------------------------------------------------
-- 12. RESTORE SELECTION ON PAGE LOAD (DA JavaScript)
-- ---------------------------------------------------------------------

/*
Dynamic Action: Page Load
Condition: P1_SELECTED_ORDER IS NOT NULL
True Actions: 
  1. Refresh "Order Items" region (Fire on Page Load = Yes)
  2. Refresh "Order Summary" region (Fire on Page Load = Yes)
  3. Execute JavaScript (below)
*/

var orderId = apex.item('P1_SELECTED_ORDER').getValue();
$('a.select-order-link').each(function() {
    if ($(this).text() == orderId) {
        $(this).closest('tr').addClass('highlight-row');
    }
});

-- ---------------------------------------------------------------------
-- 13. ADVANCED: RETRY LOGIC FOR EXTERNAL API (Reusable Procedure)
-- ---------------------------------------------------------------------

CREATE OR REPLACE PROCEDURE call_api_with_retry(
    p_url       IN VARCHAR2,
    p_response  OUT CLOB,
    p_retries   IN NUMBER DEFAULT 3
) IS
    l_last_error VARCHAR2(4000);
BEGIN
    FOR attempt IN 1..p_retries LOOP
        BEGIN
            p_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
                p_url => p_url,
                p_http_method => 'GET',
                p_credential_static_id => 'SHIPMENT_API_KEY',
                p_timeout => 5
            );
            RETURN; -- Success
        EXCEPTION
            WHEN OTHERS THEN
                l_last_error := SQLERRM;
                IF attempt < p_retries THEN
                    DBMS_LOCK.SLEEP(attempt * 2); -- Exponential backoff
                END IF;
        END;
    END LOOP;
    RAISE_APPLICATION_ERROR(-20001, 'API call failed after ' || p_retries ||
                                     ' retries: ' || l_last_error);
END call_api_with_retry;
/

-- ---------------------------------------------------------------------
-- 14. ADVANCED: BULK CSV PROCESSING (APEX_DATA_PARSER)
-- ---------------------------------------------------------------------

DECLARE
    l_data       APEX_DATA_PARSER.T_TABLE;
    l_track_nums APEX_T_VARCHAR2;
    l_response   CLOB;
    l_batch      CLOB;
    l_count      NUMBER := 0;
BEGIN
    -- Parse CSV file from APEX file item
    l_data := APEX_DATA_PARSER.PARSE(
        p_content   => APEX_FILE_MANAGER.GET_FILE_CONTENT(:P3_CSV_FILE),
        p_file_name => :P3_CSV_FILE,
        p_format    => 'CSV'
    );

    -- Collect tracking numbers from first column
    FOR i IN 1..l_data.COUNT LOOP
        l_track_nums.EXTEND;
        l_track_nums(l_track_nums.LAST) := l_data(i).COLUMN_01;
    END LOOP;

    -- Batch call to API (max 100 per batch)
    FOR batch_start IN 1..l_track_nums.COUNT BY 100 LOOP
        l_batch := '{"tracking_numbers": [';
        FOR j IN batch_start..LEAST(batch_start + 99, l_track_nums.COUNT) LOOP
            IF j > batch_start THEN l_batch := l_batch || ','; END IF;
            l_batch := l_batch || '"' || APEX_JSON.ESCAPE(l_track_nums(j)) || '"';
        END LOOP;
        l_batch := l_batch || ']}';

        l_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
            p_url        => 'https://api.mock-shipping.com/v2/track/batch',
            p_http_method => 'POST',
            p_body       => l_batch,
            p_credential_static_id => 'SHIPMENT_API_KEY'
        );

        -- Parse batch response and upsert shipments
        APEX_JSON.PARSE(l_response);
        FOR i IN 1..APEX_JSON.GET_COUNT('results') LOOP
            MERGE INTO shipments s
            USING (
                SELECT
                    APEX_JSON.GET_VARCHAR2('results[' || i || '].tracking_number') AS tracking_number,
                    APEX_JSON.GET_VARCHAR2('results[' || i || '].status') AS status,
                    APEX_JSON.GET_VARCHAR2('results[' || i || '].location') AS location
                FROM DUAL
            ) src ON (s.tracking_number = src.tracking_number)
            WHEN MATCHED THEN UPDATE SET
                s.status = INITCAP(REPLACE(src.status, '_', ' ')),
                s.last_api_sync = SYSDATE,
                s.updated_date = SYSDATE
            WHEN NOT MATCHED THEN INSERT (
                shipment_id, tracking_number, status, created_by, created_date
            ) VALUES (
                shipment_seq.NEXTVAL, src.tracking_number,
                INITCAP(REPLACE(src.status, '_', ' ')),
                :APP_USER, SYSDATE
            );
            l_count := l_count + 1;
        END LOOP;
    END LOOP;

    :P3_IMPORT_RESULT := l_count || ' shipments imported/updated.';
END;

-- ---------------------------------------------------------------------
-- 15. ADVANCED: ORDS REST SERVICE DEFINITION
-- ---------------------------------------------------------------------

BEGIN
    ORDS.DEFINE_MODULE(
        p_module_name    => 'orders.v1',
        p_base_path      => '/orders/v1/',
        p_items_per_page => 50
    );
    COMMIT;
END;
/

BEGIN
    ORDS.DEFINE_TEMPLATE(
        p_module_name    => 'orders.v1',
        p_pattern        => 'orders'
    );

    ORDS.DEFINE_HANDLER(
        p_module_name    => 'orders.v1',
        p_pattern        => 'orders',
        p_method         => 'GET',
        p_source_type    => 'json/collection',
        p_source         => q'[
            SELECT order_id, customer_name, order_date, status, total_amount
            FROM (
                SELECT o.order_id,
                       c.first_name || ' ' || c.last_name AS customer_name,
                       o.order_date,
                       o.status,
                       o.total_amount
                FROM orders o
                JOIN customers c ON c.customer_id = o.customer_id
                ORDER BY o.order_date DESC
            )
        ]'
    );
    COMMIT;
END;
/

BEGIN
    ORDS.DEFINE_TEMPLATE(
        p_module_name    => 'orders.v1',
        p_pattern        => 'orders/:id'
    );

    ORDS.DEFINE_HANDLER(
        p_module_name    => 'orders.v1',
        p_pattern        => 'orders/:id',
        p_method         => 'GET',
        p_source_type    => 'json/collection',
        p_source         => q'[
            SELECT o.*,
                   JSON_ARRAYAGG(
                       JSON_OBJECT(
                           'item_id' KEY oi.item_id,
                           'product_name' KEY oi.product_name,
                           'quantity' KEY oi.quantity,
                           'unit_price' KEY oi.unit_price,
                           'line_total' KEY oi.line_total
                       ) FORMAT JSON
                   ) AS items
            FROM orders o
            LEFT JOIN order_items oi ON oi.order_id = o.order_id
            WHERE o.order_id = :id
            GROUP BY o.order_id, o.customer_id, o.order_date, o.status,
                     o.total_amount, o.notes, o.created_date
        ]'
    );
    COMMIT;
END;
/

-- Enable ORDS for schema
BEGIN
    ORDS.ENABLE_SCHEMA(p_enabled => TRUE);
    COMMIT;
END;
/

-- ---------------------------------------------------------------------
-- 16. VERIFICATION QUERIES
-- ---------------------------------------------------------------------

-- Verify virtual column works
SELECT item_id, product_name, quantity, unit_price, line_total
FROM order_items
WHERE order_id = 1001;

-- Verify order totals match detail
SELECT o.order_id, o.total_amount, SUM(oi.line_total) AS computed_total
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, o.total_amount
HAVING o.total_amount != NVL(SUM(oi.line_total), 0);

-- Check foreign key cascade
DELETE FROM orders WHERE order_id = 1003;
SELECT * FROM order_items WHERE order_id = 1003; -- Should return 0 rows
ROLLBACK; -- Restore test data

-- ---------------------------------------------------------------------
-- END OF WORKED EXAMPLE
-- =====================================================================