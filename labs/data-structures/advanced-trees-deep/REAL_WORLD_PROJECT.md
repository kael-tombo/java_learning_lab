# Ordered Index Service with a Prefix Module: Deep Cut

Charter. A leaderboard and snapshot-query service over 1M scored entries
needs rank, range, and as-of-version reads; a prefix-search module adds
name completion. This deep lab layers balanced-tree fluency (AVL and
red-black behind one interface) with trie completion and a B-tree disk
note.

Index core. Both balanced variants serve put/get/delete/rank/select/
range with O(log n) worst-case behavior; a 60k-op fuzz vs TreeMap must
show zero mismatches. Sorted 100k ingest proves heights stay logarithmic
where the plain BST chained - height series attached.

Snapshot reads. Version-stamped queries answered from retained roots
(path copying in miniature); a read at version V must equal a rebuilt
map at V on 200 sampled versions. Retention cap with pin API documented.

Prefix module. Trie completion over 100k names with frequency ranking;
suggestion sets vs brute-force scan oracle. Longest-prefix spot checks
included for the routing-flavored demo.

Disk note. B-tree fan-out arithmetic for a 4 KB page (order, height at
10M keys, seeks per lookup) worked on paper and cited as the reason the
in-memory tree is not the on-disk answer.

Comparison close. AVL vs red-black read/write split at 200k keys with
rotation counts; trie memory per key; B-tree paper math. Scoring: fuzz
parity 12, snapshot exactness 10, comparison plus paper math 8.
## Deep-cut extras
- Sorted-100k height plot attached.
- 200 version samples verified.
- Rotation counts tabled.
- B-tree page math checked.
- Fuzz seed list published.
- Completion oracle log kept.
- Retention cap posted.
- Variant verdict dated.
