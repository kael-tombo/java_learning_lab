# Mental Models - Data Pipelines

## 1. Plumbing with receipts

Every batch is water through pipes, but each joint issues a receipt
(row counts, checks). Leaks (dropped rows) show where receipts disagree -
no receipt, no trust downstream.

## 2. Idempotence as an elevator button

Pressing twice calls the elevator once. Keyed merges are elevator
buttons; appends are ticket dispensers (press twice, two tickets).
Build elevators where retries press repeatedly.

## 3. Delivery semantics as mail

At-least-once is a persistent carrier (may redeliver); at-most-once is
a careless one (may lose); exactly-once is registered handoff with
signature (sink) - the signature, not the carrier, makes it exact.

## 4. Schemas as contracts, not suggestions

Reader and writer sign: required fields, types. Additive edits are
margin notes; breaking edits need re-signing (version + dual read).
Unsigned changes are breaches, however small.

## 5. Replay as time travel with quarantine

Backfills visit the past but stay in a clean suit (staging) until
decontaminated (diffed). Time travelers who touch live tables rewrite
history - quarantine first, always.

## 6. Quality gates as bouncers

Checks stand at the club door: counts, nulls, drift on the list or no
entry. A polite bouncer (warn-only) admits trouble; fail-loud keeps the
dance floor (dashboards) safe.

## 7. DAG as an assembly line

Stations in order, each with its own stop button and parts contract.
Lines never loop back (acyclic); a jammed station quarantines its tray
while the rest keep rhythm.

## 8. Staging as a clean room

Replay output lands in staging (clean room suits) before touching
production (the fab floor). Decontamination is the diff; promotion is
the airlock. No one walks onto the floor in street clothes.

## 9. Contracts as property lines

Schemas mark where your land ends and the neighbor's begins. Additive
edits are garden beds; breaking edits move the fence - surveyors
(compat checks) and signatures (versions) required, disputes otherwise.
