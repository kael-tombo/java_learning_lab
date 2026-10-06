# Lab 06: Customization (OAF) — Theory

## The Scenario

A healthcare client's AP team needs a custom invoice approval page. The standard
APXINWKB invoice workbench does not support image attachments. Approvers want
to see the scanned invoice and approve or reject **without switching
applications**.

Requirements: display the invoice image from WebADI/attachments, show invoice
header and line details read-only, provide Approve/Reject with reason codes, log
all approval actions to a custom table, and integrate with Oracle Approval
Workflow.

## Principle 1: OAF is MVC with a strict dependency direction

```
Page (View Layer: .jsp / region metadata)
   ↓ depends on
Controller (Controller Layer: handles actions, validation, security)
   ↓ depends on
Application Module (AM: transaction boundary, security context)
   ↓ depends on
View Object (VO: SQL + mapping to Java)
   ↓ depends on
Database
```

The dependency direction matters: **upper layers depend on lower layers, never
the reverse.** A VO that calls controller logic is a design error that will
surface as a class-loading problem or a transaction bug.

Each layer has one job:

| Layer | Responsibility | Must not |
|-------|---------------|----------|
| View (page) | Render; forward user actions | Contain business logic |
| Controller | Interpret actions, validate, authorise | Query the database directly |
| AM | Transaction boundary, security context | Render anything |
| VO | SQL, row mapping, bind variables | Know about HTTP or page structure |

**Most OAF customisation bugs are a layer violation** — SQL in a controller, or
transaction logic in a VO.

## Principle 2: Extensions are cheap; customisations are not

OAF offers two integration options, and the difference is the whole cost model.

### Extension

```java
public class InvoiceImageRegion extends EOExtRowBaseImpl {
  // Registered against the standard region
  // Survives upgrades; certified by Oracle for supported combinations
}
```

**Cost**: low. Registered against standard metadata, so an upgrade replaces the
standard object and your extension rebinds automatically.

### Customisation

```sql
-- Copy APXINWKB's controller and modify it
```

**Cost**: high. You now own a copy of Oracle code. Every patch to the standard
controller is a merge you must perform manually, forever.

### Decision test

```
Can an extension satisfy the requirement?
  YES → extend. Always.
  NO  → before customising, ask:
          - Is there a profile option?
          - Is there a personalization?
          - Is there a public API + AM implementation?
        Only then → customise, and record the decision.
```

The expensive question is not "can I customise this" but "will I still be able to
maintain this in three years through four patches".

## Principle 3: The View Object is a query with a contract

A VO is more than SQL. It has:

1. **A query** — the SQL, with bind variables
2. **A mapping** — how columns become attributes
3. **A contract** — what callers may do (insert? update? delete?)

### Bind variables are mandatory, not optional

```sql
-- WRONG: literal header ID
SELECT * FROM ap_invoices_all WHERE invoice_id = 12345

-- RIGHT: bind variable, set from the request context
SELECT * FROM ap_invoices_all WHERE invoice_id = :invoiceId
```

A literal causes a **hard parse per invoice**. With 100 approvers working
concurrently, that is 100 separate cursors in the shared pool — a classic OAF
performance defect.

### View object layering

```
SupplierVO     (supplier data, cached across pages)
    ↓
InvoiceHeaderVO (header, uses SupplierVO for supplier fields)
    ↓
InvoiceLineVO   (lines, uses InvoiceHeaderVO for header fields)
    ↓
AttachmentVO    (image metadata, joins FND_ATTACHMENTS)
```

Layering means each level reuses the one above rather than re-querying. A flat
design re-fetches supplier data on every line row.

## Principle 4: The controller decides who may do what

Function security operates at **function** granularity, not page granularity.
Every action the approver can take is a function.

```sql
INSERT INTO fnd_functions
  (function_id, function_name, description)
VALUES (fnd_function_security_pvt.create_function(
  'XX_AP_INV_IMAGE_VIEW', 'View Invoice Image', 'Read invoice attachment'));
```

```sql
-- Grant: read-only role gets VIEW only, no APPROVE
```

Now the controller checks:

```java
public void approve() {
  if (! ADFContext.getCurrentInstance().getSecurityContext()
        .isAuthorized(SecurityConstants.VIEW_SENSITIVE_APPLICATION)) {
    throw new OAException(OracleExceptionBean...)  // reject
  }
  // proceed
}
```

**Without per-function security, granting access to the page grants everything
on it.** With 200 approvers and a mixed set of responsibilities, that is an
access-control finding.

## Principle 5: Approve/Reject is workflow, not a database flag

The visible requirement is a button. The real requirement is the **workflow
state machine**:

```
Invoice validated
    ↓
Approval workflow starts (workflow item created)
    ↓
Assigned to approver 1
    ├─ APPROVE ─► next approver / complete
    ├─ REJECT  ─► terminate with rejection reason
    └─ RETURN  ─► back to previous step
```

A custom button that sets `APPROVAL_STATUS = 'APPROVED'` bypasses the entire
chain and produces a workflow item still sitting in `WORKFLOW_ITEM_ACTIVITY`
waiting for a human. The document appears approved while the workflow believes
otherwise — and the next approver never sees it.

### Correct approach

```java
// Find the active workflow item
WorkflowItemKey itemKey = WorkflowWFQuery.queryOpenItemByEntity(
    "oracle.ap.apps.ar.ApprovalWorkflowEntity", invoiceKey, db);

WorkflowContext ctx = new WorkflowContext(itemKey, db);

// Complete the activity WITH a decision attribute
WorkflowResult result = ctx.getWorkflowTask() != null
  ? ctx.getWorkflowTask().completeApprove(taskId, decisionComment)
  : ctx.getWorkflowTask().completeReject(taskId, rejectionReason);
```

`APPROVAL_WORKFLOW_FLAG` and friends in `AP_INVOICES_ALL` are then updated by
**the workflow itself**, not by your code. Single source of truth.

## Principle 6: Reason codes must be structured, not free text

```sql
CREATE TABLE xx_ap_reject_reason (
  reason_code VARCHAR2(10) PRIMARY KEY,
  description VARCHAR2(200) NOT NULL,
  active_flag CHAR(1) DEFAULT 'Y',
  requires_comment CHAR(1) DEFAULT 'N'
);
```

Free-text rejection reasons are unanalysable. Structured codes let you report
*"63% of rejections are price disputes"* and act on it.

```
Structured:  'PRICE_VAR' → 63% of rejections → renegotiate contracts
Free text:   "price looks wrong to me" → unusable
```

## Principle 7: Log actions in the same transaction

The audit requirement is "log all approval actions". Two options:

| Approach | Assessment |
|----------|-----------|
| Separate transaction in the controller | ✗ Log survives a failed approval — worse than no log |
| **Same transaction via the AM** | ✓ Log and action commit or roll back together |

```java
// AM method — participates in the same request transaction
public void logApproval(ApprovalLog log) {
  getLogVO().insertRow(log);   // committed with the page transaction
}
```

A log that records an approval which then rolled back is worse than no log: it
makes the audit trail actively misleading.

## Principle 8: Image display has real costs

Rendering a scanned invoice is not "show a URL". Consider:

| Concern | Impact |
|---------|--------|
| Image size | A 300 DPI A4 scan is ~10–25 MB |
| Concurrent approvers | 20 concurrent viewers × 15 MB = 300 MB |
| Render time | Image generation on every request |
| Caching | Re-fetching per request defeats the purpose |

Mitigations:

1. **Thumbnail for the list, full image on demand** — render a 200px thumbnail
   for approval lists; fetch full resolution only when opened.
2. **Serve via a static content URL**, not a BLOB stream through the controller.
3. **Cache at the web tier**, keyed by attachment ID (immutable).
4. **Cap dimensions** on upload; reject 50 MB scans at ingestion.

```
Thumbnail:  ~30 KB   Full: ~15 MB   → 500× difference
```

## Principle 9: Register it properly or it does not exist

A deployed OAF page needs four registrations:

```
1. Deploy the EAR to the application server
2. Create an FND_FUNCTION and attach it to the page's root region
3. Add the function to a MENU and grant it to a RESPONSIBILITY
4. Optionally personalize the existing AP responsibility
```

Miss step 3 and the page builds fine, deploys fine, and returns
`FRM-40350: No responsibility defined` for every user. Test with a real
responsibility before declaring it done.

## Principle 10: Test the failure paths

For an approval page, the interesting tests are not the happy path:

```
✓ Approver lacks APPROVE function        → must be denied
✓ Invoice already approved by someone    → must be rejected (concurrency)
✓ Reason code missing on REJECT          → must fail validation
✓ Workflow item not found (bad key)      → must show a clean error
✓ Attachment missing for this invoice    → must degrade gracefully
✓ Two approvers acting simultaneously    → second must fail cleanly
```

**Concurrent approval is the one that bites.** Two approvers loading the same
invoice both see "pending", both click approve, and one of them silently
overwrites the other. Check the workflow item state again inside the transaction
before completing:

```java
if (WorkflowWFQuery.queryOpenItemByEntity(...) == null) {
  throw new OAException("This invoice was already actioned by another approver.");
}
```

## Design Order

1. Confirm no profile option or personalization satisfies the requirement.
2. Choose extension over customisation wherever possible.
3. Design the VO layer stack with bind variables from the start.
4. Add per-function security for every distinct action.
5. Route through the workflow API, not a status column.
6. Use structured reason codes.
7. Log in the AM so the log shares the transaction.
8. Plan image sizing and caching before writing the renderer.
9. Register all four steps, then test with a real responsibility.
10. Test the failure paths, especially concurrent approval.

## Anti-Patterns

- Copying a standard controller when an extension would work.
- Literal values in VO SQL, causing a hard parse per request.
- Flat VO design re-querying supplier data per line.
- Setting `APPROVAL_STATUS` directly and orphaning the workflow item.
- Free-text rejection reasons.
- Logging in a separate transaction from the action.
- Streaming full-resolution images through the controller on every request.
- Registering the function but forgetting the responsibility.
- Skipping the concurrent-approval race test.

## Summary

The page was straightforward; the design decisions were not. Extension over
customisation kept the upgrade cost low, VO layering with bind variables kept
the shared pool from collapsing, per-function security kept read-only users from
approving, routing through the workflow kept state in one place, structured
reason codes made rejection data analysable, same-transaction logging kept the
audit trail honest, and image caching kept a 15 MB scan from becoming a
performance incident.