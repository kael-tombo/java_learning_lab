# Mini Project: File And Batch Processing

## The assignment

This file and batch processing mini build produces a working payroll CSV import job you can run locally.
Scope stays deliberately small so every behavior remains observable.
Budget roughly one focused evening for the payroll CSV import job implementation.
Success means demonstrating its judgment, not just compiling code.
Keep a lab journal noting each surprise encountered.
The acceptance checks cap the work; features beyond them wait.

## Parts you will wire

- Chunk-oriented reading concept.
- Restart from last checkpoint.
- Skip versus retry on bad rows.
- Idempotent write handling.
- Run-level metrics.

## Build order

1. Import a 5000-row payroll CSV in bounded chunks for the service.
2. Checkpoint progress so a kill resumes mid-file.
3. Quarantine malformed rows without aborting the run.
4. Make reruns safe against double-posting salaries.
5. Emit per-run counts of read, written, and skipped rows.

## Acceptance checks

- [ ] 5000-row file imports fully in bounded memory in the solution.
- [ ] Mid-file kill resumes and finishes with zero duplicates in the platform.
- [ ] 25 malformed rows quarantined with reasons.
- [ ] Rerun of a completed file changes nothing.
- [ ] Run metrics reconcile exactly with the file contents.

## Stretch

The project gains exactly one realistic complication, chosen by you.
Write the two-paragraph retro: which decision proved hardest.
Show the system to a peer armed with nothing but the acceptance checks.
