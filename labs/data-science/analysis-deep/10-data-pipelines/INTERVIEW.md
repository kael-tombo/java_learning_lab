# Interview Q&A - Data Pipelines

Q: Batch or streaming for daily sales reports?
A: Batch: bounded, scheduled, replayable - streaming buys nothing when
decisions run daily, and sells complexity.

Q: Prove your sink is replay-safe.
A: Keyed merge with the fixed point m(m(S,b),b) = m(S,b), demonstrated
by replaying batch2 to an unchanged 3-row map. Appends cannot do this.

Q: At-least-once vs exactly-once?
A: At-least-once (common queue default) may duplicate; exactly-once is a
joint source-transport-sink property needing idempotent/transactional
sinks - never a queue feature alone.

Q: Additive vs breaking schema change?
A: New optional field flows (COMPATIBLE); type change or dropped/renamed
required field halts for versioned migration with dual reads.

Q: Backfill without double-counting?
A: Same code, explicit range, staging output, diff (counts, key overlap,
mismatches) vs production, promote on tolerances - never rerun live.

Q: Your quality trio?
A: Row counts vs source, null rates per column, drift vs reference -
fail loudly (quarantine) on breach, never silently serve.

Q: Late events in windows?
A: Declare event-time vs arrival-time, route lates to a lateness window
or side output - discovered policies corrupt history retroactively.

Q: DAG node keeps failing. Shape of the fix?
A: Per-node retry with backoff, quarantine its output, page with the
node name; downstream waits on contracts, never on partial writes.

Q: Source renames a column overnight. Walk me through it.
A: Landing quarantines on unknown-column strict mode; schema diff pages;
compat gate blocks deploy; v2 migration with dual reads ships on
schedule. No silent ignore, no midnight hotfix to readers.

Q: Backfill or live-fix for a logic bug affecting 30 days?
A: Backfill: same fixed code, explicit 30-day range, staging replay,
diff within tolerances, promote. Live-fixes on served tables compound
the original error with an unreviewed second one.
