# Flashcards - Data Pipelines

Q: Batch vs streaming in one line?
A: Bounded inputs on schedule vs unbounded flows continuously; latency
need decides, each with its failure modes.

Q: Define idempotent sink.
A: m(m(S,b),b) = m(S,b): replays are no-ops (keyed upsert, not append).

Q: At-least-once means?
A: Every record arrives, duplicates possible - the common queue default,
stated generally here.

Q: At-most-once vs exactly-once?
A: Possible loss without duplicates vs each record effective once (joint
property of source, transport, and sink - never queue alone).

Q: Additive-compatible change?
A: New optional field; old readers unaffected (subset-with-types holds).

Q: Breaking change examples?
A: Type change, removed or renamed required field.

Q: Replay discipline?
A: Same code, explicit range, staging output, diff vs production, then
promote - never rerun against live tables.

Q: Quality trio?
A: Row counts vs source, null rates per column, drift vs reference.

Q: Demo quality numbers?
A: rows 6, nulls 2, nullRate 0.333, mean 9.375, drift 0.375 vs ref 9.0.

Q: DAG shape?
A: extract -> validate -> transform -> serve; acyclic, per-node retries,
data contracts on edges.

Q: Event time vs arrival time?
A: When it happened vs when it arrived; windows must declare which, with
a late-data policy.

Q: Tumbling window demo values?
A: Width 3 over {1,5,3,8,2}: 3.000, 5.333, 4.333.

Q: Compat demo verdicts?
A: Added currency COMPATIBLE; amount double->string BREAKING.

Q: Backfill promotion needs?
A: Row delta, key overlap, mismatch rate, checks green, version pin,
sign-off.
