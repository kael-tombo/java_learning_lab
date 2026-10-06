# Lab 06: Customization (OAF) — Exercises

## Exercise 1: MVC Layer Design
**Time**: 20 minutes | **Difficulty**: Beginner

### Objective
Document each OAF layer's single responsibility.

### Steps
1. Draw the View → Controller → AM → VO stack.
2. Write what each layer does and must not do.
3. Identify where transaction control belongs.
4. Locate where security context is established.

### Verification
- [ ] Dependency direction stated (upper depends on lower)
- [ ] "Must not" documented per layer
- [ ] Transaction boundary identified at the AM
- [ ] A layer violation example given

---

## Exercise 2: Extension vs Customisation Decision
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Decide the integration approach for a stated requirement.

### Steps
1. Check profile options for the requirement.
2. Check personalization applicability.
3. Check for a public API plus AM implementation.
4. Cost both options over five years and decide.

### Verification
- [ ] Configuration options checked and recorded
- [ ] Build and maintenance hours estimated for both
- [ ] Decision justified by total cost, not build speed

---

## Exercise 3: Layered VOs with Binds
**Time**: 30 minutes | **Difficulty**: Intermediate

### Objective
Build a four-layer VO stack with bind variables.

### Steps
1. Create SupplierVO with a `vendorId` bind.
2. Create InvoiceHeaderVO referencing the supplier layer.
3. Create InvoiceLineVO referencing the header bind.
4. Create AttachmentVO joined to `FND_ATTACHMENTS`.

### Verification
- [ ] No literals in any VO SQL
- [ ] Each layer references the one above rather than re-querying
- [ ] Attachment VO uses `fnd_attachment_generic` correctly

---

## Exercise 4: Prove Layering Saves Queries
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Quantify the query reduction from layering.

### Steps
1. Load an invoice with 20 lines.
2. Count queries with a flat design.
3. Count queries with the layered design.
4. Compute the reduction factor and time saved.

### Verification
- [ ] Both query counts measured
- [ ] Reduction factor computed (expect ~10×)
- [ ] Time saved expressed against the page budget

---

## Exercise 5: Per-Function Security
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Separate view, approve, and reject privileges.

### Steps
1. Create three functions.
2. Grant all three to a full approver responsibility.
3. Grant only VIEW to a read-only responsibility.
4. Attempt to approve as read-only; capture the denial.

### Verification
- [ ] Three functions created and grouped
- [ ] Read-only user denied by the controller check
- [ ] Over-privileged count reduced to zero

---

## Exercise 6: Workflow Completion
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Complete the approval through the API, not a status update.

### Steps
1. Query the open workflow item for an invoice.
2. Build a workflow context.
3. Complete the approve activity with a decision comment.
4. Verify no orphan item remains in `wf_item_activity_history`.

### Verification
- [ ] No `APPROVAL_STATUS` column set directly
- [ ] Workflow item marked complete by the workflow
- [ ] Orphan item query returns zero

---

## Exercise 7: Reason Code Enforcement
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Enforce structured reason codes with conditional comments.

### Steps
1. Create the reason code table with `requires_comment`.
2. Populate the LOV from the table.
3. Validate that the code exists in the table, not just in the request.
4. Enforce the comment only for codes that require it.

### Verification
- [ ] Invalid codes rejected even if injected via URL parameter
- [ ] Comment required only for flagged reasons
- [ ] Validation occurs before any state change

---

## Exercise 8: Image Strategy
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Quantify the thumbnail strategy.

### Steps
1. Attach a 300 DPI grayscale scan.
2. Measure its byte size.
3. Generate a 200 px thumbnail and measure it.
4. Compute the saving across a 25-invoice list.

### Verification
- [ ] Full and thumbnail sizes measured
- [ ] Ratio computed (expect ~250×)
- [ ] Served as a URL rather than streamed through the controller

---

## Exercise 9: Failure Path Testing
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Test the paths that actually cause incidents.

### Steps
1. Approve with the APPROVE function revoked.
2. Approve an invoice whose workflow item is closed.
3. Open an invoice with no attachment attached.
4. Run two concurrent approvals on one invoice.
5. Reject with a valid code but an invalid comment state.

### Verification
- [ ] Each failure produces a clear, specific message
- [ ] Concurrent approval: one success, one clean failure
- [ ] Missing attachment degrades gracefully without breaking approval

---

## Exercise 10: Rejection Analytics
**Time**: 20 minutes | **Difficulty**: Beginner

### Objective
Prove structured codes produce actionable data.

### Steps
1. Insert 150 rejection records across five reason codes.
2. Run the reason distribution query.
3. Identify the dominant theme.
4. State the process change the data supports.

### Verification
- [ ] Distribution computed with percentages
- [ ] Dominant theme quantified
- [ ] Recommended action stated from the data, not opinion