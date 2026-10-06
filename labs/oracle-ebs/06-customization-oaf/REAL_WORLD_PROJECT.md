# Lab 06: Customization (OAF) — Real World Project

## Scenario
A healthcare provider's AP department processes 800 invoices a day across 200
approvers. The standard APXINWKB invoice workbench cannot display scanned
invoice images, so approvers switch to a separate document system to view the
claim and back to EBS to approve — doubling handling time and producing a 4%
mismatch rate between what was viewed and what was approved. The client wants a
single page showing the image beside the invoice data, with Approve/Reject,
reason codes, full audit logging, and Oracle Approval Workflow integration, on
EBS 12.2.10.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS customization)
- https://docs.oracle.com/database/121/BOAWN/ (Oracle Application Framework)
- https://docs.oracle.com/database/121/APUG/ (Application Development Guide)

## Architecture
```
JDeveloper project (MVC)
   │
   ├─ View: InvoiceApprovalPage
   │     ├─ InvoiceHeader region   (read-only, AP_INVOICES_ALL)
   │     ├─ InvoiceLine region     (read-only, AP_INVOICE_DISTRIBUTIONS_ALL)
   │     ├─ Image region           (thumbnail; full on demand)
   │     ├─ Reason code LOV
   │     └─ Approve / Reject buttons (function-secured)
   │
   ├─ Controller: XXApInvoiceController
   │     ├─ authorize()      → per-function security
   │     ├─ concurrency()    → re-check workflow item
   │     └─ workflow()       → complete activity via API
   │
   ├─ AM: XXApInvoiceAM
   │     ├─ init()           → bind variables, execute layers in order
   │     └─ logApproval()    → SAME transaction as the action
   │
   └─ VOs (layered, bind variables only)
         SupplierVO ← InvoiceHeaderVO ← InvoiceLineVO
                                   └─── AttachmentVO (FND_ATTACHMENTS)
```

## Implementation sketch
```java
// The control that makes read-only access safe
if (! ADFContext.getCurrentInstance().getSecurityContext()
      .isAuthorized("XX_AP_INV_APPROVE")) {
  throw new OAException(OracleExceptionBean.bundle(1,
    "You are not authorized to approve invoices."));
}

// Never set the status directly — complete the workflow activity
WorkflowItemKey itemKey = WorkflowWFQuery.queryOpenItemByEntity(
  "oracle.ap.apps.ar.ApprovalWorkflowEntity",
  new KeyBuilder(invoiceKey), db);
if (itemKey == null) {
  throw new OAException("This invoice was already actioned by another approver.");
}
ctx.getWorkflowTask().completeApprove(taskId, decisionComment);
```

## Requirements
- F1: OAF page extending APXINWKB with image and invoice data side by side.
- F2: Four-layer VO stack with bind variables throughout.
- F3: Per-function security separating VIEW, APPROVE, and REJECT.
- F4: Workflow API completion with concurrency re-check.
- F5: Structured reject reason codes with mandatory-comment enforcement.
- F6: Audit logging in the same transaction as the approval action.
- F7: Thumbnail-for-list, full-on-demand image strategy with caching.
- F8: Graceful degradation when an attachment is missing.
- F9: Rejection analytics by reason code.
- F10: AOL registration: function, menu, and responsibility assignment.
- NF1: Handling time per invoice reduced by at least 40%.
- NF2: View/approve mismatch rate below 0.5% (from 4%).
- NF3: p95 page response under 3 seconds.
- NF4: Zero over-privileged approvers — 40 approvers, 160 read-only.
- NF5: Security baseline — no direct SQL in the controller, all via VOs.
- NF6: Documented rollback for every deployment and configuration change.

## Milestones
- Week 1: Extension-vs-customisation analysis; MVC design; security model.
- Week 2: VOs, AM, and page built in JDeveloper.
- Week 3: Controller with authorization and workflow completion.
- Week 4: Image strategy and attachment degradation handling.
- Week 5: Registration, responsibility setup, and pilot with 5 approvers.
- Week 6: Full rollout with rejection analytics and monitoring.

## Verification
- Fault injection: missing attachment, invalid reason code, closed workflow item.
- Concurrent approval test proving the second action fails cleanly.
- Orphan workflow item check after a full day of approvals.
- Performance test: p95 response with 10 concurrent approvers.
- Security review confirming read-only users cannot approve.

## Rollback
The page is additive — the standard workbench remains available until cutover.
Deployment is a file copy plus EAR redeploy; function grants are reversible by
responsibility. Document rollback steps for every change.