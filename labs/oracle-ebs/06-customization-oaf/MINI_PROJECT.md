# Lab 06: Customization (OAF) — Mini Project

## Goal
Build a custom invoice approval page with image display, Approve/Reject,
structured reason codes, and audit logging in 90 minutes.

## Requirements
- R1: MVC layer design with each layer's responsibility documented.
- R2: Four-layer VO stack: Supplier, Header, Line, Attachment.
- R3: Bind variables in all VO SQL — no literals.
- R4: Controller with Approve and Reject handlers.
- R5: Authorization check against a named function.
- R6: Workflow API call for completion, not a status update.
- R7: Structured reject reasons with mandatory-comment validation.
- R8: Audit log written in the same transaction as the action.

## Steps
1. Document the MVC responsibilities and dependency direction.
2. Create the reject reason and approval log tables.
3. Write the four VOs with bind variables.
4. Wire the AM to execute layers in order and expose `logApproval`.
5. Implement `approve` — authorize, re-check the workflow item, complete.
6. Implement `reject` — validate reason and comment **before** any change.
7. Add the per-function security check.
8. Log through the AM so it shares the transaction.
9. Test: approve, reject without a reason (must fail), reject with a reason.
10. Test the concurrent approval conflict.

## Acceptance criteria
- Rejecting without a reason code fails before any state changes.
- The workflow item is completed via the API; no status column is set directly.
- A read-only user is denied by the controller's authorization check.
- The audit log row commits and rolls back with the action.
- Two simultaneous approvals produce one success and one clean failure.

## Stretch
- Count VO queries before and after layering; show the reduction.
- Add a thumbnail-vs-full-resolution strategy and quantify the byte saving.