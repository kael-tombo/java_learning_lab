# EBS Upgrade and Migration — Vision

## Where this lab takes you
From "we need a new version" to a rehearsed cutover — the method, the order
operations happen in, and the point at which rollback stops being possible.

## The Arc
1. **Method** — assess, plan, test, rehearse, cut over, verify.
2. **Paths** — which R12.2 upgrade path applies and what it assumes.
3. **ADOP** — the five phases and the dual file system behind them.
4. **Online patching** — what users experience during a cutover.
5. **Downtime patching** — when online is not available and why.
6. **Bundles and CPU** — patch bundles and security patches separately.
7. **Cloud Manager** — automated lifecycle for EBS environments.
8. **Lift and shift** — moving to OCI without changing the application.

## Milestones (checkable)
- [ ] M1: Write an upgrade assessment capturing version, patches, and custom code.
- [ ] M2: Choose the correct R12.2 path and justify the choice.
- [ ] M3: Execute the `ADOP` phases and state what each one changed.
- [ ] M4: Perform a rolling cutover with a written rollback for each phase.
- [ ] M5: Apply a patch bundle and explain the ordering constraint.
- [ ] M6: Apply a CPU security patch and identify the RUP path it uses.
- [ ] M7: Set up Cloud Manager and run a lifecycle operation.
- [ ] M8: Plan a lift-and-shift to OCI with a stated downtime budget.

## Anti-Goals
- Scheduling the first production cutover before the second rehearsal.
- Treating a CPU patch as a bundle patch, or the reverse.
- Assuming ADOP rollback is available after `cleanup` has run.
- Promising zero downtime when the change is a downtime patch.

## The one-sentence thesis
The upgrade method is the deliverable, not the cutover — anyone can follow a
runbook, but only a method survives a surprise at 2am.