# Step by Step - First Pipeline Pass

## Step 1. Land one batch

Take six order rows (PipeQuality's toy set: ids 1-6, two blank amounts).
Land them untouched in a staging structure - raw first, always.

## Step 2. Run the quality trio

Count rows (6), null rate (0.333), mean vs reference drift (9.375 vs
9.0 -> 0.375). Decide pass/quarantine by written thresholds before
transforming anything.

## Step 3. Sink with merge-by-key

Upsert each row into the serving map keyed by id (PipeIdem: after two
batches including a replay, rows = 3 with intact values). Assert the
replay changed nothing - that assertion is the idempotency test.

## Step 4. Check schema compatibility

Reader needs {id, amount}; writer adds currency -> COMPATIBLE, proceed.
Writer changes amount to string -> BREAKING, halt and version. Run both
branches of the demo and quote its verdicts.

## Step 5. Window the stream view

Compute width-3 tumbling averages (3.000, 5.333, 4.333 on demo data).
State event-time vs arrival-time choice for your windows - late data
policy written down, not discovered.

## Step 6. Wire the DAG order

extract -> validate -> transform -> serve with per-node retry. Draw it
(node names, no vendor features) and confirm acyclicity by inspection.

## Step 7. Log the run

Code version, input range, counts, check outcomes, decision. Re-run the
same input and diff outputs: identical means deterministic, promotable,
done.

## Checkpoint table

| Step | Artifact | Check |
|---|---|---|
| 1 landing | raw staged batch | untouched bytes |
| 2 quality trio | counts/nulls/drift | pass or quarantine |
| 3 keyed sink | serving map state | replay changes nothing |
| 4 compat | COMPATIBLE/BREAKING | verdicts quoted |
| 5 windows | tumbling avgs | event-time declared |
| 6 DAG | node order drawn | acyclic by inspection |
| 7 run log | version/range/counts | double-run identical |

An empty cell means the step was skipped; skipped compat review voids
the deploy.
