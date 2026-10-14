# Undo Timeline and Audit Ledger on Persistent Structures

Promise. A document store where every edit yields a new version and no
version ever mutates; an event-sourced ledger where auditors can replay
any prefix. Path copying gives O(log n) fresh nodes per update while
old roots keep working - sharing is the feature, mutation the bug.

Versioned map. Persistent balanced map (path-copied nodes) for document
fields: assoc returns a new root, dissoc returns a new root, lookup pins
a version id. Structural sharing ratio measured: nodes shared vs fresh
per 10k-edit script, quoted from instrumentation, not theory.

Undo caller. Editor timeline with branching: undo moves the pointer,
new edits from a past version fork a branch instead of destroying the
future. Branch integrity tested by interleaving edits across three
branches and verifying each tip reads back exactly.

Ledger caller. Append-only event log with per-version content hashes;
audit replay folds events from genesis to any version and must equal
the stored snapshot at that version on all 5k prefixes. Hash mismatch
fails the audit with the first divergent index.

Sharing audit. A debug walk counts reachable nodes per version and
shared nodes across versions; total allocation for 10k edits must sit
far below 10k times tree size, with the measured factor published.

Misuse drills. Lookup at a pruned version (typed error), unbounded
version growth (retention policy with pin API), hash tamper on one
snapshot (audit names the version), concurrent readers across versions
(no locks, no divergence).

Close. Store, ledger, sharing numbers, audit log, retention note.
Weighting: persistence guarantees 12, branch plus replay exactness 10,
sharing evidence and misuse handling 8.
## Retention sheet
- Pin API for audit holds.
- Default keeps 90 days.
- Sharing ratio re-measured monthly.
- Tamper drill each quarter.
- Branch-tips hashed nightly.
