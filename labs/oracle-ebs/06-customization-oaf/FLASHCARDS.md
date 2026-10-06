# Lab 06: Customization (OAF) — Flashcards

## Architecture

---
**Q**: OAF MVC stack order?
**A**: Page (View) → Controller → AM → VO → Database.

---
**Q**: Dependency direction?
**A**: Upper depends on lower. Never VO → Controller.

---
**Q**: Layer responsibilities?
**A**: View renders · Controller acts/authorises · AM owns the transaction · VO queries.

---
**Q**: Transaction boundary?
**A**: The Application Module. VOs and controllers must never commit.

---
**Q**: BC4J role?
**A**: The Java layer between the page and the database implementing VO/AM.

---

## Extension vs Customisation

---
**Q**: Extension vs customisation, over 5 years?
**A**: Extension 40 build + 4 upgrade = 44 hrs. Customisation 30 + 60 = 90 hrs.

---
**Q**: Why is customisation faster to build yet worse to own?
**A**: You save 10 build hours and pay 56 maintenance hours. Build speed is the
smallest term in the total.

---
**Q**: Decision order?
**A**: Profile option → personalization → public API + AM → only then customise.

---
**Q**: What does an extension bind against?
**A**: Registered standard region metadata. Upgrades replace the standard object
and your extension rebinds.

---

## View Objects

---
**Q**: Three parts of a VO?
**A**: Query (SQL + binds) · mapping (columns → attributes) · contract
(insert? update? delete?).

---
**Q**: Why bind variables mandatory?
**A**: Literals create a distinct statement per value → hard parse per request,
plus library cache latch contention.

---
**Q**: Literal cost in the lab?
**A**: ~50,000 annual hard parses, ~1 ms CPU each, latch risk is the real hazard.

---
**Q**: Layering example?
**A**: SupplierVO ← InvoiceHeaderVO ← InvoiceLineVO; AttachmentVO off the header.

---
**Q**: Query saving from layering?
**A**: 41 queries → 4 for a 20-line invoice. ~10×, ~740 ms saved.

---
**Q**: Invoice image query pattern?
**A**: `FND_ATTACHMENT_GENERIC` where `ENTITY_NAME1='AP_INVOICES'` and
`PK1_VALUE = TO_CHAR(:invoiceId)`.

---

## Controller

---
**Q**: What does the controller decide?
**A**: Who may act (function security), what action means, which workflow call to make.

---
**Q**: Can a controller contain SQL?
**A**: No. It goes through a VO. Direct SQL is a layer violation.

---
**Q**: Order of operations in approve()?
**A**: Authorise → re-check concurrency → complete workflow → log → refresh.

---
**Q**: Why validate the reason code before any state change?
**A**: Validating after leaves a rejected invoice with no reason.

---

## Security

---
**Q**: Function granularity?
**A**: One function per distinct action: VIEW, APPROVE, REJECT.

---
**Q**: Over-provisioning without it?
**A**: 200 users granted the page, only 40 should approve → 80% over-provisioning.

---
**Q**: Controller check?
**A**: `SecurityContext.isAuthorized("XX_AP_INV_APPROVE")`.

---
**Q**: Registration steps?
**A**: Deploy EAR → create function → add to menu → grant to responsibility.
Miss step 4 and every user gets FRM-40350.

---

## Workflow

---
**Q**: Why not set APPROVAL_STATUS directly?
**A**: It orphans the workflow item. The document looks approved; the workflow still
waits and the next approver never sees it.

---
**Q**: Correct completion path?
**A**: `WorkflowWFQuery.queryOpenItemByEntity` → `WorkflowContext` →
`completeApprove` / `completeReject`.

---
**Q**: Concurrency re-check — why?
**A**: 4,000 annual conflicts in the lab. Without it, one approval silently
overwrites the other.

---
**Q**: Where should the re-check live?
**A**: Inside the transaction, immediately before completing.

---

## Reject Reasons

---
**Q**: Structured or free text?
**A**: Structured. 63% concentration on `PRICE_VAR` identifies the highest-value
process fix.

---
**Q**: `requires_comment` flag?
**A**: Some reasons (INVALID, OTHER) require a comment; most do not.

---
**Q**: Can a reason code be trusted from the URL parameter?
**A**: No. Validate it exists in `XX_AP_REJECT_REASON` with `active_flag='Y'`.

---

## Audit Logging

---
**Q**: Which transaction?
**A**: The AM's — the same one as the approval action.

---
**Q**: Why?
**A**: A log surviving a rolled-back approval makes the audit trail actively
misleading. Worse than no log.

---
**Q**: What to log?
**A**: invoice, action, reason code, comment, workflow item key, actor, timestamp.

---

## Images

---
**Q**: 300 DPI grayscale scan size?
**A**: ~8 MB. Full resolution render is ~1,600 ms over 5 MB/s.

---
**Q**: Thumbnail size?
**A**: ~30 KB for 200 px. ~267× reduction, 99.6% less payload on a list.

---
**Q**: Serve how?
**A**: Static URL, not streamed through the controller. Avoids holding view threads
and enables browser caching.

---
**Q**: Peak concurrent load, 10 approvers, thumbnails?
**A**: 300 KB in-flight. Trivial.

---
**Q**: What if an attachment is missing?
**A**: Degrade gracefully — hide the region, show a message, keep approval working.

---

## Quick Reference

| Task | Object / Call |
|------|---------------|
| Attachment query | `FND_ATTACHMENT_GENERIC` + `FND_ATTACHMENTS` |
| File metadata | `FND_ATTACHMENTS.db_file_name` |
| Open workflow item | `WorkflowWFQuery.queryOpenItemByEntity` |
| Complete activity | `ctx.getWorkflowTask().completeApprove/Reject` |
| Function create | `fnd_function_security_pvt.create_function` |
| Function to menu | `fnd_function_security_pvt.add_to_group` |
| Log line | `FND_FILE.PUT_LINE(FND_FILE.OUTPUT, ...)` |
| MOAC read | `fnd_global_apps_pr.get_org_id` |

---

## Numbers to Remember

| Metric | Value |
|--------|-------|
| Page response target | < 3,000 ms p95 |
| Layering query reduction | 41 → 4 (~10×) |
| VO budget | 800 ms |
| Image ratio (full vs thumb) | 267× |
| Full 300 DPI scan | ~8 MB |
| Over-provisioning without functions | 80% |
| Concurrent approval conflicts | ~4,000/yr |
| Extension vs customisation (5 yr) | 44 vs 90 hrs |

---

## Failure Paths Worth Testing

1. APPROVE function revoked → denied
2. Workflow item already closed → "already actioned"
3. No attachment → degrade, don't break
4. Two approvers, one invoice → one clean failure
5. Reject without reason → fail before state change
6. Injected reason code → rejected by lookup

---

## Anti-Patterns

1. Copied standard controller.
2. SQL in a controller.
3. Commit in a VO.
4. Literal values in VO SQL.
5. Direct `APPROVAL_STATUS` update.
6. Free-text rejection reasons.
7. Audit log in a separate transaction.
8. Full-res images on list pages.
9. Function registered without responsibility.

---

## Study Tips
1. Recall the extension vs customisation totals and explain the inversion.
2. Explain why literals cause latch contention, not just CPU cost.
3. Trace the approve() order from memory.
4. State the four registration steps and which one gets forgotten.