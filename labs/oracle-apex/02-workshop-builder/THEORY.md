# Theory: Master-Detail Patterns in Oracle APEX

## What is Master-Detail?

A **master-detail** relationship displays a parent record (master) alongside its child records (detail). When the user selects a different master record, the detail region automatically updates to show the corresponding children.

### Real-World Analogies
| Domain | Master | Detail |
|--------|--------|--------|
| E-commerce | Order | Line Items |
| HR | Employee | Dependents |
| Finance | Invoice | Invoice Lines |
| Supply Chain | Shipment | Packages |

## APEX Master-Detail Implementation Approaches

### 1. Classic: Page Navigation (Pre-APEX 5.0)
```
Page 1 (Master IR) ──click link──► Page 2 (Detail IR with :P2_MASTER_ID)
```
- **Pros**: Simple, bookmarkable URLs
- **Cons**: Full page reload, loses master context, poor UX

### 2. Modal Dialog (APEX 5.0+)
```
Page 1 (Master IR) ──click──► Modal Dialog (Detail Form/IR)
```
- **Pros**: Maintains master context, modern UX
- **Cons**: Still requires navigation, limited to one detail at a time

### 3. Single-Page AJAX Refresh (This Lab) ⭐
```
Single Page: Master IR + Detail IG
Click master row → Set P1_MASTER_ID → Refresh Detail Region (AJAX)
```
- **Pros**: Instant feedback, no navigation, multiple details possible, preserves scroll position
- **Cons**: More complex Dynamic Actions, state management via page items

## The Shared State Pattern

The key insight: **a page item holds the "currently selected master key"**

```
┌─────────────────────────────────────────────────────┐
│ Page Item: P1_SELECTED_ORDER (Hidden, Protected)    │
│ Value: 1001 (set when user clicks Order #1001)      │
└─────────────────┬───────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│ Master Region │   │ Detail Region │
│ (IR on orders)│   │ (IG on items) │
│               │   │ WHERE order_id│
│ Click → sets  │   │ = :P1_SELECTED│
│ P1_SELECTED   │   │ _ORDER        │
└───────────────┘   └───────────────┘
```

### Why This Works
1. **Declarative binding**: Detail region SQL references `:P1_SELECTED_ORDER`
2. **Automatic requery**: When page item changes, region refresh re-executes query
3. **Zero custom code** for the basic pattern

## Dynamic Actions Deep Dive

### Event Types for Master-Detail
| Event | Use Case |
|-------|----------|
| `Click` on link column | User selects master row |
| `Change` on select list | User picks from dropdown |
| `Page Load` | Restore selection from session |
| `Custom Event` | Cross-region communication |

### True Actions for Synchronization
```javascript
// Standard pattern: Set Value → Refresh Region → Refresh Region
True Action 1: Set Value (P1_SELECTED_ORDER = #ORDER_ID#)
True Action 2: Refresh (Region "Order Items")
True Action 3: Refresh (Region "Order Summary")
True Action 4: Execute JS (Highlight row, update UI)
```

### Critical: Fire on Page Load
- **Set Value** actions: `Fire on Page Load = No` (only on trigger)
- **Refresh** actions: `Fire on Page Load = Yes` (if item has value)

## Interactive Grid vs Interactive Report for Details

| Feature | Interactive Report | Interactive Grid |
|---------|-------------------|------------------|
| Inline Edit | No | **Yes** |
| Add Row | No | **Yes** |
| Multi-row Delete | No | **Yes** |
| Toolbar Actions | Limited | **Full** |
| Save Processing | Manual | **Declarative** |
| Virtual Columns | Display only | **Editable source** |

**Rule of thumb**: Use IG for details when users need to edit children.

## Virtual Columns for Calculated Fields

```sql
-- Database-level virtual column (computed on read)
line_total NUMBER(12,2) GENERATED ALWAYS AS (quantity * unit_price) VIRTUAL
```

Benefits:
- **Consistency**: Same calculation in DB and APEX
- **Performance**: No PL/SQL function call overhead
- **Queryability**: Can index, filter, sort on `line_total`
- **Declarative**: IG displays it automatically as read-only

## State Persistence Across Navigation

### Problem
User selects Order #1001 → navigates to Page 5 → returns to Page 1 → selection lost.

### Solutions
| Approach | Implementation |
|----------|----------------|
| **Browser History** | Use `f?p=&APP_ID.:1:&SESSION.:::P1_SELECTED_ORDER:1001` URLs |
| **Session State** | Page item `P1_SELECTED_ORDER` persists in APEX session |
| **Local Storage** | JavaScript `localStorage.setItem('selectedOrder', '1001')` |
| **URL Synchronization** | PushState API to update URL without reload |

### Recommended: URL + Session State
```sql
-- Master IR Link Column Target:
f?p=&APP_ID.:1:&SESSION.:::P1_SELECTED_ORDER:#ORDER_ID#
```
- Bookmarkable, shareable, browser back/forward works

## Performance Considerations

### For 100K+ Master Records
1. **Server-side pagination** on IR (default 15 rows)
2. **Indexes** on foreign keys: `CREATE INDEX idx_items_order ON order_items(order_id)`
3. **Limit detail query**: `WHERE order_id = :P1_SELECTED_ORDER` (single value = index range scan)

### For 500K+ Detail Records
1. **Pagination on IG** (50 rows default)
2. **Virtual column** avoids computation per row
3. **Consider materialized view** for aggregated summaries

## Error Handling Patterns

### Validation in Detail IG
```sql
-- Validation: Quantity > 0 (server-side)
DECLARE
    l_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO l_count
    FROM order_items
    WHERE order_id = :P1_SELECTED_ORDER
      AND quantity <= 0;
    IF l_count > 0 THEN
        RETURN 'Quantity must be greater than zero.';
    END IF;
    RETURN NULL;
END;
```

### Referential Integrity
```sql
-- ON DELETE CASCADE ensures detail cleanup
CREATE TABLE order_items (
    ...
    order_id NUMBER REFERENCES orders(order_id) ON DELETE CASCADE
);
```

## Advanced: Multi-Level Master-Detail

```
Order (Master) 
  └── Order Items (Detail 1)
        └── Item Serial Numbers (Detail 2)
```

Implementation: Chain page items `P1_ORDER_ID` → `P1_ITEM_ID` with separate Dynamic Actions.

## Summary

| Pattern | Best For | Complexity |
|---------|----------|------------|
| Page Navigation | Simple apps, bookmarking needed | Low |
| Modal Dialog | Form-based detail, occasional use | Medium |
| **AJAX Single-Page** | **Dashboards, frequent switching, editing** | **Medium-High** |

**This lab teaches the AJAX Single-Page pattern** — the gold standard for modern APEX dashboards.