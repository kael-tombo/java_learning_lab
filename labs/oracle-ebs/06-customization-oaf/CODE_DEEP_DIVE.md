# Lab 06: Customization (OAF) — Code Deep Dive

## 1. Reject Reason Structure

```sql
CREATE TABLE xx_ap_reject_reason (
  reason_code       VARCHAR2(10) PRIMARY KEY,
  description       VARCHAR2(200) NOT NULL,
  requires_comment  CHAR(1) DEFAULT 'N' NOT NULL,
  active_flag       CHAR(1) DEFAULT 'Y' NOT NULL
);

INSERT INTO xx_ap_reject_reason VALUES
  ('PRICE_VAR', 'Price variance beyond tolerance',       'N', 'Y'),
  ('DUPLICATE', 'Duplicate invoice suspected',            'N', 'Y'),
  ('QTY_VAR',   'Quantity does not match receipt',        'N', 'Y'),
  ('INVALID',   'Invoice not valid - not a legal claim', 'Y', 'Y'),
  ('OTHER',     'Other (comment required)',                'Y', 'Y');
```

## 2. Approval Audit Table

```sql
CREATE TABLE xx_ap_approval_log (
  log_id          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  invoice_id      NUMBER NOT NULL,
  invoice_number  VARCHAR2(50) NOT NULL,
  action          VARCHAR2(10) NOT NULL,   -- APPROVE / REJECT / VIEW / RETURN
  reason_code     VARCHAR2(10),
  comment_text    VARCHAR2(1000),
  workflow_item_key VARCHAR2(80),
  actor           VARCHAR2(64) NOT NULL,
  action_date     TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  CONSTRAINT xx_al_action_ck CHECK (action IN
    ('APPROVE','REJECT','VIEW','RETURN'))
);
CREATE INDEX xx_al_inv_idx ON xx_ap_approval_log (invoice_id, action_date);
```

## 3. View Object Layering

### SupplierVO — base layer
```sql
-- SupplierVO.sql (supplier data, cached across the request)
SELECT pv.vendor_id,
       pv.segment1            AS vendor_number,
       pv.vendor_name,
       pv.vendor_id_1         AS tax_id
  FROM po_vendors pv
 WHERE pv.vendor_id = :vendorId     -- BIND VARIABLE, never a literal
```

### InvoiceHeaderVO — reuses SupplierVO
```sql
SELECT ai.invoice_id,
       ai.invoice_number,
       ai.invoice_amount,
       ai.invoice_date,
       ai.invoice_currency_code,
       ai.vendor_id,                 -- feeds the SupplierVO reference
       ai.approval_status,
       ai.invoice_total            AS invoice_total
  FROM ap_invoices_all ai
 WHERE ai.invoice_id = :invoiceId
```

### InvoiceLineVO — reuses the header for supplier fields
```sql
SELECT ail.invoice_distribution_id,
       ail.invoice_line_number,
       ail.amount,
       ail.quantity,
       ail.unit_price,
       ail.account_segment1,
       ail.description
  FROM ap_invoice_distributions_all ail
 WHERE ail.invoice_id = :invoiceId    -- inherited from header bind
 ORDER BY ail.invoice_line_number
```

### AttachmentVO — joins FND_ATTACHMENTS for the image
```sql
SELECT fad.attachment_id,
       fad.entity_name1,
       fa.file_name,
       fa.mime_type,
       fa.db_file_name,
       fdat.contents
  FROM fnd_attachment_generic fad
  JOIN fnd_attachments fa ON fa.attachment_id = fad.attachment_id
  LEFT JOIN fnd_lobs fdat ON fdat.entity_id = fa.entity_id
                        AND fdat.entity_name = fa.entity_name
 WHERE fad.entity_name1 = 'AP_INVOICES'
   AND fad.pk1_value      = TO_CHAR(:invoiceId)   -- entity/pk join pattern
```

> `fnd_attachment_generic` uses the generic attachment pattern: `entity_name1`
> is the table name and `pk1_value` is the key as a **string**.

## 4. Application Module

```java
package xx.ap.invoice;

import oracle.apps.fnd.ext.webui.OAApplicationModule;

public class XXApInvoiceAM extends OAApplicationModule {

  public void init() {
    super.init();
    // Bind the invoice ID from the request context exactly once
    BigDecimal invoiceId = new BigDecimal(
        (String) OAContext.getPageContext().getParameter("invoiceId"));
    getInvoiceHeaderVO().setBindVariableValue("invoiceId", invoiceId);
    getAttachmentVO().setBindVariableValue("invoiceId", invoiceId);
    getSupplierVO().executeQuery();   // supplier layer first
    getInvoiceHeaderVO().executeQuery();
    getInvoiceLineVO().executeQuery();
    getAttachmentVO().executeQuery();
  }

  /** Approval log written in the SAME transaction as the approval action. */
  public void logApproval(String action, String reasonCode, String comment) {
    OracleBindings bindings = new OracleBindings();
    bindings.setValue("action",     action);
    bindings.setValue("reasonCode", reasonCode);
    bindings.setValue("comment",    comment);
    bindings.setValue("invoiceId",  getInvoiceHeaderVO()
                                       .getCurrentRow().getAttributeValue("InvoiceId"));
    bindings.setValue("actor",      OAContext.getPageContext().getUserName());
    getSqlStatement().execute();   // commits with the page transaction
  }
}
```

**Note**: logging via the AM means the log row commits or rolls back **with the
approval**. A log that survives a failed approval is worse than no log.

## 5. Controller — Approve / Reject

```java
package xx.ap.invoice;

import oracle.apps.fnd.ext.webui.OAControllerImpl;
import oracle.apps.fnd.ext.webui.OAPageContext;
import oracle.apps.fnd.ext.webui.beans.OAWebBean;
import oracle.apps.fnd.framework.webui.OAException;
import oracle.apps.fnd.framework.webui.OAWebException;
import oracle.apps.fnd.framework.webui.server.OAApplicationModule;

public class XXApInvoiceController extends OAControllerImpl {

  public void approve() {
    OAWebBean approveButton = getWebBean("ApproveButton");
    approveButton.setRequiredErrorMessage(null);
    OAPageContext pageContext = getPageContext();

    // 1. AUTHORISATION — per-function security
    if (! ADFContext.getCurrentInstance()
          .getSecurityContext()
          .isAuthorized("XX_AP_INV_APPROVE")) {
      throw new OAException(OracleExceptionBean
        .bundle(1, "You are not authorized to approve invoices."));
    }

    // 2. CONCURRENCY — re-check the workflow item inside this transaction
    String invoiceKey = getInvoiceKey();
    WorkflowItemKey itemKey =
        WorkflowWFQuery.queryOpenItemByEntity(
          "oracle.ap.apps.ar.ApprovalWorkflowEntity",
          new KeyBuilder(invoiceKey), pageContext.getDatabaseConnection());
    if (itemKey == null) {
      throw new OAException(
        "This invoice was already actioned by another approver.");
    }

    try {
      // 3. WORKFLOW — complete the activity, do NOT set status directly
      WorkflowContext ctx = new WorkflowContext(itemKey,
                          pageContext.getDatabaseConnection());
      String taskId = ctx.getWorkflowTask() == null ? null
                      : ctx.getWorkflowTask().getTaskId();

      WorkflowResult result = taskId == null
        ? ctx.getWorkflowTask().completeApprove(taskId, "Approved via custom page")
        : ctx.getWorkflowTask().completeReject(taskId,
              getReasonCodeValue(pageContext));

      // 4. LOG — same transaction
      OAApplicationModule am = pageContext.getApplicationModule(pageContext);
      XXApInvoiceAM xxam = (XXApInvoiceAM) am;
      xxam.logApproval(result.isApprove() ? "APPROVE" : "REJECT",
                       getReasonCodeValue(pageContext),
                       getCommentValue(pageContext));

      OAFrameworkUtil.setSuccessMessage(pageContext,
        "Invoice " + getInvoiceNumber() + " actioned successfully.");
      am.invokeMethod("refreshPage");   // or forward to the workbench

    } catch (OAException e) {
      throw new OAWebException(e.getMessage());
    } catch (Exception e) {
      throw new OAWebException("Workflow error: " + e.getMessage());
    }
  }

  public void reject() {
    // 1. Reason code is MANDATORY on reject
    OAPageContext pageContext = getPageContext();
    String reasonCode = getReasonCodeValue(pageContext);
    if (reasonCode == null || reasonCode.trim().length() == 0) {
      throw new OAException("A reason code is required to reject an invoice.");
    }

    // 2. Comment required for reasons flagged requires_comment
    String comment = getCommentValue(pageContext);
    if (requiresComment(reasonCode) &&
        (comment == null || comment.trim().length() == 0)) {
      throw new OAException("A comment is required for reason " + reasonCode + ".");
    }

    // then delegate to the shared action path
    reject_internal(reasonCode, comment);
  }

  private String getReasonCodeValue(OAPageContext ctx) {
    return ctx.getParameter("xxReasonCode");
  }
}
```

**Critical**: the reject path validates the reason code *before* any state
change. Validating after would leave a rejected invoice with no reason.

## 6. Reason Code Query and Validation

```sql
SELECT reason_code, description, requires_comment
  FROM xx_ap_reject_reason
 WHERE active_flag = 'Y'
 ORDER BY reason_code
```

Bind into the page item with `pSubmitDependent`/`LOV` or a simple `SELECT`
populated region, so an invalid code cannot be injected by URL manipulation:

```java
// Never trust a value that came in as a request parameter
private boolean reasonCodeIsValid(String code) {
  if (code == null) return false;
  return (Boolean) OAApplicationModule.invokeSQLQuery(
    "SELECT COUNT(1) FROM xx_ap_reject_reason " +
    "WHERE reason_code = :code AND active_flag = 'Y'",
    new OracleBindings(){{ setValue("code", code); }});
}
```

## 7. Image Renderer with Thumbnail Strategy

```java
public class InvoiceImageRenderer extends OAImageRenderer {

  @Override
  protected void processImage(
      OAWebBean webBean, OAWebBean tableRow, ImageField imageField,
      OAWebLink link) {

    // 1. THUMBNAIL for list views (cheap)
    if (! isFullView()) {
      imageField.setImageUrl(buildThumbnailUrl());
      imageField.setWidth(200);
      imageField.setHeight(280);
      imageField.setAlternateText("Invoice scan thumbnail");
      return;
    }

    // 2. FULL image on demand, served as a static URL
    //    NOT streamed through the controller
    imageField.setImageUrl(buildAttachmentUrl());
    imageField.setAlternateText("Scanned invoice");
  }

  private String buildThumbnailUrl() {
    return getPageContext().getOracleHome()
             + "/nls/../XX_AP_THUMB?attachmentId=" + getAttachmentId();
  }
}
```

**Why a URL, not a byte stream**: streaming a 15 MB BLOB through the controller
holds the view thread for the full transfer and blocks a shared pool thread.
A static URL lets the web server handle it and the browser cache it.

## 8. Function Security Setup

```sql
-- Functions: one per distinct action
DECLARE
  l_view    NUMBER := fnd_function_security_pvt.create_function(
    'XX_AP_INV_IMAGE_VIEW',   'View Invoice Image',   'Read invoice and attachment');
  l_approve NUMBER := fnd_function_security_pvt.create_function(
    'XX_AP_INV_APPROVE',      'Approve Invoice',      'Complete approval activity');
  l_reject  NUMBER := fnd_function_security_pvt.create_function(
    'XX_AP_INV_REJECT',       'Reject Invoice',       'Reject with reason code');
  l_menu    NUMBER := fnd_function_security_pvt.create_menu(
    'XX_AP_INVOICE_MENU', 'Invoice Approval (Custom)', NULL, NULL);

BEGIN
  fnd_function_security_pvt.add_to_group(
    l_menu, l_view,    'Single Web Application');
  fnd_function_security_pvt.add_to_group(
    l_menu, l_approve, 'Single Web Application');
  fnd_function_security_pvt.add_to_group(
    l_menu, l_reject,  'Single Web Application');
END;
/

-- Responsibility roles
-- FULL_APPROVER: all three functions
-- READ_ONLY_APPROVER: VIEW only → the controller's authorization check
--                    blocks APPROVE and REJECT
```

**This is the control that makes read-only access safe.** Without it, granting
the page to a read-only responsibility grants approval too.

## 9. Deployment

```bash
# 1. Build the EAR in JDeveloper
#    Project → Deploy → Deploy to EAR

# 2. Copy to the application tier
scp xx_ap_invoice.ear apps@apps01:/u01/install/APPS/fs1/FMW-INF/ear/

# 3. Restart or let the managed server pick it up
$ADMIN_SCRIPTS_HOME/adstrtal.sh -apps
```

## 10. Error Reporting to the Approver

```java
// Distinguish "you cannot" from "it failed"
private void reportError(OAPageContext ctx, String message, boolean fatal) {
  if (fatal) {
    throw new OAWebException(message);   // full page error
  } else {
    // Non-fatal: degrade gracefully — e.g. missing attachment
    OAFrameworkUtil.setErrorMessage(ctx, message);
  }
}

// Graceful degradation for a missing attachment
if (getAttachmentVO().getRowCount() == 0) {
  reportError(pageContext,
    "No scanned document is attached to this invoice.", false);
  hideImageRegion();
  return;   // the page still works for approval
}
```

## 11. Logging and Monitoring

```sql
-- Approval throughput by reason — the reason structured codes exist
SELECT reason_code, COUNT(*) rejections,
       ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) pct
  FROM xx_ap_approval_log
 WHERE action = 'REJECT'
   AND action_date >= ADD_MONTHS(TRUNC(SYSDATE), -3)
 GROUP BY reason_code
 ORDER BY rejections DESC;
```

```sql
-- OAF performance: check for missing binds (literal SQL)
SELECT sql_id, executions, elapsed_time/1e6 elapsed_sec,
       SUBSTR(sql_text, 1, 120) sql_text
  FROM v$sql
 WHERE sql_text LIKE '%AP_INVOICES_ALL%'
   AND sql_text NOT LIKE '%:invoiceId%'
 ORDER BY executions DESC;
```

Rows here indicate a VO built with a literal instead of a bind variable — the
hard-parse-per-request defect.

## 12. Concurrent Approval Test

```sql
-- Two approvers, one invoice: second must fail cleanly
-- Test:
--   Session A: queryOpenItemByEntity → itemKey
--   Session B: queryOpenItemByEntity → itemKey   (still open)
--   Session A: completeApprove → succeeds
--   Session B: completeApprove → must fail, not silently succeed
```

```sql
-- Verify no orphan workflow items after the test
SELECT COUNT(*) orphan_items
  FROM wf_item_activity_history h
 WHERE h.item_key IN (SELECT item_key FROM wf_items WHERE item_type = 'APPROVAL')
   AND h.activity_name = 'APPROVE'
   AND NOT EXISTS (SELECT 1 FROM wf_items i
                    WHERE i.item_key = h.item_key
                      AND i.status = 'COMPLETE');
```