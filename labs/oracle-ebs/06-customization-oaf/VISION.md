# Lab 06: Customization (OAF) — VISION

## Where this lab takes you
From "approvers want to see the invoice and approve in one place" to a page that
respects the framework, survives upgrades, respects authorisation, and does not
become a workflow-consistency incident.

## The Arc
1. **Framework** — OAF MVC and the strict dependency direction.
2. **Extension vs customisation** — the upgrade cost inversion.
3. **VO design** — layering and mandatory bind variables.
4. **Controller** — action handling and per-function authorisation.
5. **Workflow** — complete the activity, never set a status flag.
6. **Reason codes** — structured so rejection data is analysable.
7. **Audit** — same transaction as the action.
8. **Images and failure paths** — the parts that actually cause incidents.

## Milestones (checkable)
- [ ] M1: Draw the OAF MVC stack with each layer's single responsibility.
- [ ] M2: Evaluate extension vs customisation for one requirement and decide.
- [ ] M3: Build a four-layer VO stack with bind variables throughout.
- [ ] M4: Prove layering reduces query count with a before/after count.
- [ ] M5: Implement per-function security and prove a read-only user is denied.
- [ ] M6: Route approval through the workflow API and verify no orphan items.
- [ ] M7: Enforce mandatory reason codes before any state change.
- [ ] M8: Test concurrent approval and confirm the second action fails cleanly.

## Anti-Goals
- Copying a standard controller when an extension would work.
- Putting SQL in a controller or transaction logic in a VO.
- Using literals in VO SQL.
- Setting `APPROVAL_STATUS` directly and orphaning the workflow item.
- Free-text rejection reasons.
- Logging approvals in a separate transaction from the action.
- Streaming full-resolution images on list pages.
- Registering the function and forgetting the responsibility.

## The one-sentence thesis
Most OAF defects are layer violations, and most OAF incidents are state
inconsistency — respect the MVC boundaries and let the workflow own the state.