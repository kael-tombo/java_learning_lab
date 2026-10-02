# Code Deep Dive: Master-Detail with Dynamic Actions

## Dynamic Action Internals

### How APEX Processes a Click on an IR Link Column

```javascript
// 1. User clicks <a class="select-order-link" href="f?p=100:1:123::::P1_SELECTED_ORDER:1001">1001</a>
// 2. Browser navigates... BUT Dynamic Action intercepts if:
//    - Event: Click
//    - Selection Type: jQuery Selector
//    - Selector: .select-order-link
//    - Prevent Default: true (stops navigation)
```

### The `this.triggeringElement` Context

```javascript
// In Dynamic Action "Execute JavaScript" true action:
var clickedLink = this.triggeringElement;  // The <a> element
var orderId = apex.item('P1_SELECTED_ORDER').getValue();  // Already set by prior "Set Value" action

// DOM traversal to highlight row:
$(clickedLink).closest('tr').addClass('highlight-row');
```

### APEX JavaScript API for Page Items

```javascript
// Get value
var val = apex.item('P1_SELECTED_ORDER').getValue();

// Set value (triggers change event)
apex.item('P1_SELECTED_ORDER').setValue('1001');

// Set value silently (no change event)
apex.item('P1_SELECTED_ORDER').setValue('1001', null, true);

// Listen for changes
apex.item('P1_SELECTED_ORDER').on('change', function() {
    console.log('Order changed to:', this.getValue());
});
```

## Interactive Grid JavaScript Model

### Accessing the IG Model

```javascript
// Get the IG region's widget
var ig = apex.region('ORDER_ITEMS_IG').widget();  // Static ID: ORDER_ITEMS_IG
var model = ig.interactiveGrid('getViews').grid.model;

// Iterate records
model.forEach(function(record, index) {
    var qty = model.getValue(record, 'QUANTITY');
    var price = model.getValue(record, 'UNIT_PRICE');
    var total = (parseFloat(qty) || 0) * (parseFloat(price) || 0);
    model.setValue(record, 'LINE_TOTAL', total);
});
```

### IG Save Process Flow

```
User clicks "Save" in IG Toolbar
        │
        ▼
┌───────────────────┐
│  IG Save Process  │  (Type: Interactive Grid - Save Data)
│  - Validates      │
│  - Builds DML     │
│  - Executes       │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  After Processing │  (Page Process: PL/SQL)
│  UPDATE orders    │
│  SET total = ...  │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Dynamic Action   │  (Event: After Refresh on IG)
│  Refresh Summary  │
└───────────────────┘
```

### Customizing IG Save with PL/SQL

```sql
-- Instead of declarative IG Save, use custom process:
DECLARE
    l_ig_data APEX_DATA_PARSER.T_TABLE;
BEGIN
    -- Parse the IG change log
    FOR rec IN (
        SELECT * FROM APEX_COLLECTIONS
        WHERE collection_name = 'IG_CHANGES'
    ) LOOP
        -- Custom business logic per row
        IF rec.c001 = 'INSERT' THEN
            INSERT INTO order_items (...);
        ELSIF rec.c001 = 'UPDATE' THEN
            UPDATE order_items SET ... WHERE item_id = rec.n001;
        ELSIF rec.c001 = 'DELETE' THEN
            DELETE FROM order_items WHERE item_id = rec.n001;
        END IF;
    END LOOP;
END;
```

## APEX_WEB_SERVICE for External APIs (Preview)

While this lab focuses on internal master-detail, the same Dynamic Action pattern applies to external API calls:

```sql
-- In a Dynamic Action "Execute PL/SQL" true action:
DECLARE
    l_response CLOB;
BEGIN
    l_response := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
        p_url         => 'https://api.example.com/orders/' || :P1_SELECTED_ORDER,
        p_http_method => 'GET',
        p_timeout     => 5
    );
    
    -- Parse JSON and update page items
    APEX_JSON.PARSE(l_response);
    :P1_EXTERNAL_STATUS := APEX_JSON.GET_VARCHAR2('status');
    :P1_EXTERNAL_TOTAL := APEX_JSON.GET_NUMBER('total');
END;
```

## Virtual Column Implementation Details

### Database Definition
```sql
CREATE TABLE order_items (
    item_id     NUMBER PRIMARY KEY,
    order_id    NUMBER REFERENCES orders(order_id) ON DELETE CASCADE,
    product_name VARCHAR2(200),
    quantity    NUMBER CHECK (quantity > 0),
    unit_price  NUMBER(10,2),
    line_total  NUMBER(12,2) GENERATED ALWAYS AS (quantity * unit_price) VIRTUAL
);
```

### How APEX Handles Virtual Columns in IG
1. **Query includes `line_total`** → APEX sees it in result set
2. **Column Attribute: "Source Type" = Database Column** → Read-only by default
3. **No DML generated** for virtual columns during IG save
4. **JavaScript recalc** (client-side) provides instant feedback before save

### Client-Side Recalculation (Optional Enhancement)
```javascript
// Dynamic Action: Change on QUANTITY, UNIT_PRICE columns in IG
function recalcLineTotal(model, record) {
    var qty = parseFloat(model.getValue(record, 'QUANTITY')) || 0;
    var price = parseFloat(model.getValue(record, 'UNIT_PRICE')) || 0;
    model.setValue(record, 'LINE_TOTAL', qty * price);
}

// Attach to IG model change event
var model = apex.region('ORDER_ITEMS_IG').widget().interactiveGrid('getViews').grid.model;
model.on('change', function(event, record, field) {
    if (field === 'QUANTITY' || field === 'UNIT_PRICE') {
        recalcLineTotal(this, record);
    }
});
```

## Debugging Master-Detail Issues

### Common Issue: Detail Region Not Refreshing

**Diagnostic Steps:**
1. Check browser Network tab: Is AJAX request firing?
2. Check request payload: Does it include `p_request=APXWGT` and region ID?
3. Check response: HTML fragment for region?
4. Verify page item value: `apex.item('P1_SELECTED_ORDER').getValue()` in console

### Common Issue: IG Not Showing New Rows After Add

**Cause**: New row `ORDER_ID` not defaulted to `:P1_SELECTED_ORDER`

**Fix**: Set IG Column `ORDER_ID` Default Value:
- Type: `PL/SQL Expression`
- Value: `:P1_SELECTED_ORDER`

### Common Issue: Stale Data After Save

**Cause**: Region refresh happens before commit visible

**Fix**: Ensure process order:
1. IG Save Process (commits)
2. Recalculate Total Process (commits)
3. Dynamic Action Refresh (reads committed data)

## Performance: Tracing Dynamic Actions

```sql
-- Enable APEX debug for Dynamic Actions
-- In URL: &p_debug=YES&p_debug_level=9

-- Or programmatically:
BEGIN
    APEX_DEBUG.ENABLE(p_level => 9);
END;
/

-- Query debug messages:
SELECT message, timestamp
FROM apex_debug_messages
WHERE session_id = :APP_SESSION
AND message LIKE '%Dynamic Action%'
ORDER BY timestamp DESC;
```

## Custom Events for Cross-Component Communication

```javascript
// Publisher: After IG save completes
apex.event.trigger(document, 'order-items-saved', { orderId: 1001 });

// Subscriber: Dynamic Action on Page (Custom Event)
// Event: Custom
// Custom Event: order-items-saved
// True Action: Refresh "Order Summary" region
```

### Custom Event with Data
```javascript
// Publisher
apex.event.trigger(document, 'order-changed', {
    orderId: 1001,
    action: 'status-update',
    newStatus: 'SHIPPED'
});

// Subscriber (Execute JavaScript)
var data = this.data;  // { orderId: 1001, action: 'status-update', newStatus: 'SHIPPED' }
console.log('Order', data.orderId, 'changed to', data.newStatus);
```

## Security: Preventing IDOR (Insecure Direct Object References)

```sql
-- Always validate access in detail query:
SELECT oi.*
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
WHERE oi.order_id = :P1_SELECTED_ORDER
  AND o.customer_id = :APP_USER_CUSTOMER_ID  -- Or security check
  AND o.security_group_id = :G_SECURITY_GROUP_ID;
```

## Summary: Key Code Patterns

| Pattern | Code Location | Purpose |
|---------|---------------|---------|
| `GENERATED ALWAYS AS (...) VIRTUAL` | DDL | Computed column |
| `apex.item('P1_X').setValue()` | DA JS | Set page item |
| `apex.region('ID').widget()` | DA JS | Access IG model |
| `APEX_JSON.PARSE()` | PL/SQL | Parse API response |
| `apex.event.trigger()` | DA JS | Custom event pub/sub |
| `ON DELETE CASCADE` | DDL | Referential integrity |