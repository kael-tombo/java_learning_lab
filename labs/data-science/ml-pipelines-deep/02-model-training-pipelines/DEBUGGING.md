# Model Training Pipelines — Debugging

## Symptom: metrics change between identical reruns
Likely an unpinned seed or unversioned data. Check: compare the two
runs' seeds, code hashes, and data hashes field by field. The demo
shows seed discipline working (seed 42 repeats [2, 6, 3, 1, 4, 0, 7,
5]); a real rerun that diverges with equal seeds implicates data or
library versions instead. Fix: pin all three, rerun, confirm equality.

## Symptom: validation passes locally but fails in the pipeline
Likely the local check ran on a sample or a different snapshot. Check:
resolve the dataset version ids — local file vs pipeline snapshot —
and compare row counts and null rates. Fix: validate the pinned
snapshot, never a hand-exported sample.

## Symptom: pipeline trains despite bad data
Likely the gate is advisory (logs but does not halt) or a stage reads
around the gate. Check the runner's transition log for a pass record
on the validate stage. Fix: make gating structural — transform requires
a pass event, as the demo loop does — not a convention humans follow.

## Symptom: registry fills with unpromotable models
Likely trials register everything by default. Check promotion criteria:
every registered version needs a recorded evaluation plus a threshold
decision. Fix: register candidates with explicit status; garbage-collect
old unpromoted versions on schedule.

## Symptom: retrain metrics drift with no code change
Likely data drift, which is the retrain loop doing its job. Check the
tracked data hashes and validation histories across runs. Fix: treat
the delta as a data incident (page the data owner), not a training bug.

## Debugging checklist
1. Diff seeds, code hashes, data hashes across runs.
2. Confirm the failing check's numbers by recomputation.
3. Verify the gate is structural, not advisory.
4. Check promotion records before blaming training.
5. Read validation history before tuning hyperparameters.
