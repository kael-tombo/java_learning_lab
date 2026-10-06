# Lab 09: Security (SOD Remediation) — VISION

## Where this lab takes you
From 45 SOD violations discovered by audit to a closed finding with zero open
conflicts, a preventive control, and evidence an audit committee accepts.

## The Arc
1. **Understand the fraud** — SOD conflicts enable a chain, not a single act.
2. **Make it enforceable** — a risk matrix, not a vague principle.
3. **Detect correctly** — at the user-assignment level, not the responsibility.
4. **Sequence remediation** — by value at risk, removing only the conflict.
5. **Prevent recurrence** — block at grant time, not just report monthly.
6. **Except honestly** — time-bound, owned, with compensating controls.
7. **Certify** — attestation with evidence, not an unsigned report.
8. **Harden** — password visibility and dormancy close the escalation path.

## Milestones (checkable)
- [ ] M1: Write the SOD risk matrix enumerating duties and conflicts.
- [ ] M2: Build the detection query at user-assignment level and prove it.
- [ ] M3: Show why responsibility-level queries find nothing.
- [ ] M4: Risk-rank the 45 users by value at risk and remediate Tier 1 first.
- [ ] M5: Revoke only the conflicting responsibility and record the alternate path.
- [ ] M6: Implement the preventive control and prove a conflicting grant fails.
- [ ] M7: Create time-bound exceptions and report overdue ones.
- [ ] M8: Fix the password exposure and prove the scan returns clean.

## Anti-Goals
- Detecting conflicts between responsibilities instead of user assignments.
- Revoking whole roles rather than the one conflicting duty.
- Removing access without providing an alternate path.
- Treating "indefinite" as an acceptable exception expiry.
- Shipping a detective control only and finding new violations monthly.
- Generating a certification report nobody signs.
- Closing the SOD finding while leaving `FND_HIDE_DB_PASSWORD='N'`.
- Consuming the entire 30-day window with no verification phase.

## The one-sentence thesis
SOD is a missing control rather than 45 individual mistakes — enumerate the
conflicts, detect at the assignment level, remove only the conflicting duty, and
block the next one at grant time.