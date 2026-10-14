# Editor Backend and Log Viewer on Ropes

Desk. A collaborative editor holds 5 MB documents with heavy middle
edits; a log viewer concatenates chunk streams and slices windows. Flat
strings shift O(n) per middle edit; ropes split, concat, and slice in
O(log n) with rebalancing. Both callers ship on one rope core.

Rope core. Weight-balanced leaves (1-4 KB chunks), concat nodes with
cached total length, split by index, rebalance when height exceeds
4 * log2(leaves). Index, split, concat each O(log n); iteration streams
leaves without materializing the string.

Editor caller. Insert/delete at cursor, undo via retained roots
(bonus tie to lab 20), render visible window by double split. A 20k-edit
script with cursor jumps must produce exactly the StringBuilder oracle
text, verified by hash after every 500 edits.

Document-store caller. Concat-heavy assembly of 10k chunks plus random
window reads; total time vs StringBuilder and vs StringBuffer, quoted
per mix (append-heavy, middle-heavy, read-heavy). Each mix names its
winner with margins.

Rebalance proof. Adversarial concat chain (always append right) drives
height up; the audit triggers rebalancing and shows height returning
near logarithmic with before/after numbers. Leaf-size sweep (512 B to
16 KB) picks the default with data.

Rotten edits. Split at 0 and at length, delete past the end (clamped,
flagged), empty-document ops, 100k-char paste (chunked, timed).

Deliver. Rope, editor CLI, store bench, rebalance log, sweep table.
Scoring: oracle parity 12, mix-by-mix verdicts 10, rebalance plus edge
evidence 8.
## Edit corpus
- Middle-heavy script versioned.
- Hash check every 500 edits.
- Leaf sweep rerun yearly.
- Rebalance log archived.
- Paste case timed.
