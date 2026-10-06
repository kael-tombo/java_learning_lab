# Lab 07: APEX Advanced Components — Code Deep Dive

## 1. Interactive Grid — Order Line Entry

```
Region: Order Lines (Interactive Grid)
  Source (SQL):
```

```sql
SELECT ol.line_id,
       ol.order_id,
       ol.item_code,
       i.description,
       ol.quantity,
       ol.unit_price,
       ol.discount_pct,
       -- RECALCULATED, never stored: a consequence of the columns
       ROUND(ol.quantity * ol.unit_price * (1 - ol.discount_pct/100), 2) line_total,
       ol.status
  FROM order_line ol
  JOIN item i ON i.item_code = ol.item_code
 WHERE ol.order_id = :P1_ORDER_ID          -- REQUIRED: bound to the parent
 ORDER BY ol.line_id;

  Edit:
    Type:              Update, Insert, Delete
    Primary Key:       LINE_ID       ← REQUIRED for editing
    Allowed Operations: insert row, update, delete row
```

**`LINE_ID` is the primary key configuration.** Without it, editing is not
addressable and Save cannot target rows.

## 2. Column Configuration

| Column | Type | Editable | Validation |
|--------|------|----------|------------|
| `LINE_ID` | Number | No (hidden or read-only) | System |
| `ORDER_ID` | Number | No | System |
| `ITEM_CODE` | Popup LOV | **Yes** | Item must be active |
| `DESCRIPTION` | Text | No | — |
| `QUANTITY` | Number | **Yes** | `> 0` |
| `UNIT_PRICE` | Number | **Yes** | `> 0` |
| `DISCOUNT_PCT` | Number | **Yes** | `0` to `100` |
| `LINE_TOTAL` | Number | **No** (computed) | — |
| `STATUS` | Select list | **Yes** | Constrained list |

```
Popup LOV on ITEM_CODE — shared component:
  SELECT item_code, description, unit_price, uom
    FROM item
   WHERE active_flag = 'Y'
   AND (:P_ORDER_ID IS NULL OR item_code NOT IN
        (SELECT item_code FROM order_line WHERE order_id = :P_ORDER_ID
          AND item_code NOT LIKE 'RETURN%'))
   ORDER BY item_code

  Extra column shown on select: UNIT_PRICE
  → the user sees the standard price when choosing, which reduces price errors.
```

## 3. Cell Validation — Immediate Feedback

```sql
-- Validation 1: quantity must be positive
--   Applies to: QUANTITY
--   Condition:  WHEN LENGTH(:Q1) > 0 AND TO_NUMBER(:Q1) <= 0
--   Message:    'Quantity must be greater than zero. You entered: ' || :Q1

-- Validation 2: unit price must be positive
--   Applies to: UNIT_PRICE
--   Condition:  WHEN LENGTH(:P1) > 0 AND TO_NUMBER(:P1) <= 0
--   Message:    'Unit price must be greater than zero. You entered: ' || :P1

-- Validation 3: discount within range
--   Applies to: DISCOUNT_PCT
--   Condition:  WHEN LENGTH(:D1) > 0
--                AND (TO_NUMBER(:D1) < 0 OR TO_NUMBER(:D1) > 100)
--   Message:    'Discount must be between 0 and 100 percent. You entered: ' || :D1
```

Cell validation fires **during editing**, so the user is corrected at the point of
mistake. Every message names the value entered.

## 4. Recalculating the Computed Column on Edit

```javascript
// Dynamic Action: "Recalculate line total"
apex.jq(function () {
  var grid$  = apex.jQuery("#order-lines-grid");
  var model   = grid$.igGrid("getGridAPEx").grid.rowSorter$.model;

  $(document).on('cellchanged', function (e, extra) {
    if (extra.cellData.colId === 'QUANTITY'
     || extra.cellData.colId === 'UNIT_PRICE'
     || extra.cellData.colId === 'DISCOUNT_PCT') {
      recompute(extra);
    }
  });

  function recompute(extra) {
    var rec   = extra.rowData.row;
    var qty   = parseFloat(rec.getValue('QUANTITY') || 0);
    var price = parseFloat(rec.getValue('UNIT_PRICE') || 0);
    var disc  = parseFloat(rec.getValue('DISCOUNT_PCT') || 0);
    var total = qty * price * (1 - disc / 100);
    extra.cellData.cell.setValueAndStash(total.toFixed(2));
  }
});
```

**Cell validation does not reliably fire on programmatic `setValue`**, so the
computed column is recalculated explicitly. Handle new rows too:

```javascript
// New-row handling (Add Row)
apex.jQuery(document).on('iggridcelladded', function (e, extra) {
  var rec = extra.rowData.row;
  rec.setValue('ORDER_ID', apex.item('P1_ORDER_ID').getValue());
  rec.setValue('DISCOUNT_PCT', 0);
});
```

## 5. Row Validation — Rules That Span Rows

```sql
-- Validation: "Total discount on the order must not exceed 20%"
--   This cannot be a cell rule — it sums across rows.
--   Fires on SAVE, not during editing.

DECLARE
  l_total_discount NUMBER;
  l_limit          CONSTANT NUMBER := 20;
BEGIN
  SELECT SUM(NVL(discount_pct, 0)) INTO l_total_discount
    FROM order_line
   WHERE order_id = :P1_ORDER_ID;

  IF l_total_discount > l_limit THEN
    RAISE_APPLICATION_ERROR(-20200,
      'Total discount for this order is ' || l_total_discount ||
      '%, exceeding the ' || l_limit || '% limit. Reduce a line discount.');
  END IF;
END;
/
```

```sql
-- Validation: "Line total cannot exceed the order credit limit"
DECLARE
  l_line_total NUMBER;
  l_credit     NUMBER;
BEGIN
  SELECT quantity * unit_price * (1 - discount_pct/100) INTO l_line_total
    FROM order_line WHERE line_id = :P2_LINE_ID;
  SELECT credit_limit INTO l_credit FROM customer_order WHERE order_id = :P1_ORDER_ID;

  IF l_line_total > l_credit THEN
    RAISE_APPLICATION_ERROR(-20201,
      'Line total ' || TO_CHAR(l_line_total,'FM999,999,990.00') ||
      ' exceeds the credit limit of ' || TO_CHAR(l_credit,'FM999,999,990.00') || '.');
  END IF;
END;
/
```

## 6. Save with a Row Guard

```sql
-- Page Process: "Save order lines"
--   Condition: When Page Item P1_SAVE is not null   (the Save button)

DECLARE
  l_row_count NUMBER;
  l_limit     CONSTANT NUMBER := 500;
BEGIN
  -- Count changed rows in the submitted collection
  SELECT COUNT(*) INTO l_row_count
    FROM APEX_COLLECTION
   WHERE collection_name = 'ORDER_LINES'     -- the IG's internal collection
     AND c001 IN ('U','I','D');              -- update / insert / delete flags

  IF l_row_count > l_limit THEN
    RAISE_APPLICATION_ERROR(-20202,
      'You have ' || l_row_count || ' unsaved changes. The limit is ' ||
      l_limit || ' — please save in smaller batches.');
  END IF;

  APEX_APPLICATION.PROCESS(
    p_start_row => 1, p_end_row => GREATEST(l_row_count,1),
    p_processed => 0, p_total => GREATEST(l_row_count,1), p_error => 0);
END;
/
```

## 7. Aggregations and Control Breaks

```
Region attributes:
  Control Break:  GROUP BY → CATEGORY_NAME
  Aggregations:   SUM on LINE_TOTAL · COUNT on LINE_ID
  Sort:           CATEGORY_NAME, then LINE_ID
  Chart View:     enabled, type = Bar, sum = LINE_TOTAL, group = CATEGORY_NAME
```

```
Exploration:  user changes the grouping from category to item in one click,
              no page round trip — this is what control breaks are for.
```

## 8. Master-Detail Grid Pair

### Master IG

```sql
SELECT o.order_id,
       o.order_number,
       o.order_date,
       c.customer_name,
       ROUND(SUM(ol.quantity * ol.unit_price * (1 - ol.discount_pct/100)), 2) net_amount
  FROM customer_order o
  JOIN customer c ON c.customer_id = o.customer_id
  LEFT JOIN order_line ol ON ol.order_id = o.order_id
 WHERE (:P1_CUSTOMER_ID IS NULL OR o.customer_id = :P1_CUSTOMER_ID)
 GROUP BY o.order_id, o.order_number, o.order_date, c.customer_name
 ORDER BY o.order_date DESC;
```

### Dynamic Action: master selection drives the detail

```
Dynamic Action: "Load order lines"
  Event:    Region → Order Summary (Interactive Grid), Condition = Selection
  True Action 1: Set Value on P1_ORDER_ID
                  Source Type = JavaScript Expression
                  Source     = "function(){ return this.triggeringElement.value[0] }"
  True Action 2: Refresh → Order Lines (Interactive Grid)
```

### Detail IG

```sql
SELECT ol.line_id, ol.order_id, ol.item_code, i.description,
       ol.quantity, ol.unit_price, ol.discount_pct,
       ROUND(ol.quantity * ol.unit_price * (1 - ol.discount_pct/100), 2) line_total
  FROM order_line ol
  JOIN item i ON i.item_code = ol.item_code
 WHERE ol.order_id = :P1_ORDER_ID
 ORDER BY ol.line_id;
```

## 9. Per-User State, Tidying, and Reset

```
Region attributes:
  Save State:              Yes
  Session State Group:     ORDER_ENTRY      ← used by APEX_REGION_CACHE / tidying
  Reset Selection on Reload: No              ← preserve the user's selected row

Shared Components → Page Defaults:
  Named region defaults: layouts
```

```sql
-- Provide a Reset action so a user can recover from a drifted layout
-- Dynamic Action: "Reset grid layout"
apex.jQuery(function () {
  $("#order-lines-grid").igGrid("getGridAPEx").grid.resetColumnState();
});
```

```sql
-- State size monitoring
SELECT c_name AS ig_name, COUNT(DISTINCT c_session_id) sessions
  FROM apex_collection
 WHERE c_collection_name LIKE '%IG_STATE%'
 GROUP BY c_name
 ORDER BY 2 DESC;
```

```sql
-- Scheduled tidying (a light job, not something to do at save time)
DELETE FROM apex_collection
 WHERE collection_name LIKE '%IG_STATE%'
   AND last_update_date < SYSDATE - 30;
COMMIT;
```

## 10. Saved Filters with a Cap

```
Region attributes:
  Saved Filters:    Yes
  Enable Facets:   Yes
```

```sql
-- Limit saved filters per user to prevent state growth
-- APEX enforces a per-region limit; set it low (5) and document it
```

## 11. Oracle JET Chart Configuration

```
Region: Revenue by Category (Oracle JET)
  Type: Oracle JET
  Series Type:       Pie
  Series Name:       CATEGORY_NAME
  Point Name:        CATEGORY_NAME
  Point Value:       SUM(NET_AMOUNT)
  Height:            350px
  Layout Options:    Show legend right, data labels on
```

```sql
-- Chart data: aggregate to a readable point count
SELECT c.category_name, ROUND(SUM(o.net_amount), 2) revenue
  FROM customer_order o
  JOIN category c ON c.category_id = o.category_id
 WHERE o.order_date >= :P1_FROM_DATE
   AND o.order_date <  :P1_TO_DATE + 1
   AND (:P1_CUSTOMER_ID IS NULL OR o.customer_id = :P1_CUSTOMER_ID)
 GROUP BY c.category_name
 HAVING SUM(o.net_amount) > 0
 ORDER BY 2 DESC
 FETCH FIRST 12 ROWS ONLY;    -- READABLE LIMIT, enforced in SQL
```

### Combination chart — bar plus line

```
Region: Revenue and Target (Oracle JET)
  Series 1: Type = Bar,    Name = MONTH, Value = ACTUAL_REVENUE
  Series 2: Type = Line,   Name = MONTH, Value = TARGET_REVENUE
  Y-axis:   Revenue
  X-axis:   Month
```

## 12. Plugin — Item Type (Map Picker)

```sql
-- Create: Custom Item Type plugin "XX_MAP_PICKER"
-- Files packaged via APEX_APPLICATION.CREATE_PLUGIN

-- JavaScript renderer (simplified)
(function ($) {
  "use strict";
  var NAME = "xxMapPicker", KEY = "xxMapPicker";

  apex.widget.registerWidget(KEY, {
    widgetNamespace: NAME,
    $el: null,
    defaults: { latitude: 0, longitude: 0, zoom: 12, onChange: null },

    init: function (options) {
      this.$el = options.el;
      this.mapEl = apex.jQuery('<div class="xx-map" style="height:240px"></div>')
                     .appendTo(this.$el);
      this.render();
      this.listenForChange();
    },

    render: function () {
      this.mapEl.text("[" +
        this.latitude().toFixed(4) + ", " +
        this.longitude().toFixed(4) + "]");
      var lat = this.latitude(), lon = this.longitude(), zoom = this.zoom();
      this.mapEl.append(
        apex.jQuery('<div class="xx-map-note">Map at zoom ' + zoom + '</div>'));
    },

    latitude: function (value) {
      if (arguments.length) {
        this.options.latitude = value;
        this.render();
        return this;
      }
      return this.options.latitude;
    },

    longitude: function (value) {
      if (arguments.length) {
        this.options.longitude = value;
        this.render();
        return this;
      }
      return this.options.longitude;
    },

    zoom: function () {
      return this.options.zoom;
    },

    update: function () { this.render(); },

    destroy: function () {
      this.mapEl.remove();
    },

    listener: function (event, context) {
      this.triggerEvent(event, context);
    }
  });
})(apex.jQuery);
```

```sql
-- Server-side: the plugin's region/process source reads the item values
-- APEX invokes the JS with the item values; no framework code is copied.
```

```sql
-- Package and install the plugin
BEGIN
  APEX_APPLICATION.CREATE_PLUGIN(
    p_type            => 'ITEM',
    p_name            => 'XX Map Picker',
    p_display_name    => 'XX Map Picker',
    p_description     => 'Coordinate picker for delivery locations',
    p_version         => '1.0.0',
    p_application_id  => 100);
END;
/
```

## 13. Support Model Check for a Plugin

Plugins are the supported extension point, so verify none of your changes require
framework edits:

```sql
-- Were any APEX internal tables modified? That is the real upgrade test.
SELECT table_name, num_rows, last_analyzed
  FROM user_tab_updates
 WHERE table_name LIKE 'APEX_%'
   AND num_rows > 0
 ORDER BY table_name;
```

```
If APEX internal tables have been modified directly, that is an upgrade risk
regardless of how well the code works today.
```

## 14. Grid Health Check

```sql
SELECT
  (SELECT COUNT(DISTINCT collection_name) FROM apex_collection
    WHERE collection_name LIKE '%IG_%') open_grid_collections,
  (SELECT ROUND(AVG(c001)/1024, 1) FROM apex_collection
    WHERE collection_name LIKE '%IG_STATE%') avg_state_kb,
  (SELECT COUNT(*) FROM apex_collection
    WHERE collection_name LIKE '%IG_STATE%'
      AND last_update_date < SYSDATE - 30) stale_state_rows,
  CASE WHEN (SELECT COUNT(*) FROM apex_collection
              WHERE collection_name LIKE '%IG_STATE%'
                AND last_update_date < SYSDATE - 30) > 1000
       THEN 'STATE GROWTH — schedule tidying' ELSE 'Healthy' END status
FROM dual;
```