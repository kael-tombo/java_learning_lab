# Model Monitoring - Step by Step

1. Instrument serving to log predictions, versions, features, and timestamps.
   - Async emission only; monitoring must never block the prediction path.
2. Pin a reference window representing known-good behavior.
   - Record why it was chosen; refreshes are deliberate and reviewed.
3. Build hourly and daily rollups: score mix, null rates, volume, errors.
   - Rollups power both dashboards and alerts; raw events stay short-term.
4. Add distribution checks (PSI/KS-style) per key feature and score.
   - Track them as trends first; page only on validated high-precision rules.
5. Define a small set of high-precision paging alerts, each with a runbook link.
   - Every page names the slice, the signal, and the first three triage steps.
6. Join ground truth by key as it arrives; mark fresh windows provisional.
   - Official quality numbers come from mature windows only.
7. On alert, check pipeline health first, then slice breakdowns, then model causes.
   - Most overnight jumps are pipeline changes, not world changes.
8. Turn confirmed incidents into pinned evaluation cases.
    - The evaluation set grows with production experience, not just offline ideas.
9. Add per-slice monitors for every segment that matters, with owners.
    - Aggregates stay for orientation; slices carry the paging responsibility.
10. Alert on telemetry absence with the same seriousness as bad values.
    - Volume and last-received timestamps page when the pipeline goes quiet.
11. Version the reference snapshot and require review for refreshes.
    - Each refresh records reason, owner, and back-comparison numbers.
12. Schedule the monthly alert-precision review with demotion authority.
    - Rules below the bar leave paging; proven ones stay with runbooks attached.
13. Quarantine model-influenced labels from default retraining inputs.
    - The loop is labeled explicitly and validated before any round uses it.
14. Pin one confirmed incident per quarter into the evaluation set.
    - Production experience compounds only when it is written down as cases.

## Operating checklist
- Pipeline healthy, slices covered, references pinned, pages precise, labels mature.
- Walk the checklist after every deploy and every reference refresh.
- A red item blocks retraining promotion until it clears with an owner.
- File each walk with the run record for the audit trail.
   - The evaluation set grows with production experience, not just offline ideas.

## Done when
- Dashboards, a few trusted pages, and mature-window metrics all agree on health.
