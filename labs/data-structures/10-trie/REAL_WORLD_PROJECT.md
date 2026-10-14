# Search-Engine Prefix Service, Told End to End

The setting is a small search engine whose box must suggest completions
as each character lands, backed by a second life as a contact-list
prefix search in the companion mobile demo. One prefix tree serves both.

Ingest starts with 80k head queries plus 40k contacts, each carrying a
weight from historical clicks or call frequency. Insertion order is
shuffled to prove the structure does not depend on it; a timing note
records the build rate.

Lookup is two verbs. Complete(prefix) returns the top completions with
weights; longestMatch(address) walks address bits for the routing demo.
Both run in O(L) key length, and the narrative pauses on the consequence:
doubling the lexicon barely moves latency while lengthening keys does.

Ranking gets its own chapter. Frequencies decay weekly so stale queries
sink; the decay job is idempotent and the writeup shows one query
falling out of the top eight across two decay passes. Ties break by
recency, documented with an example.

Deletion is a quiet hero. Removing a word prunes only orphaned nodes;
shared prefixes stay intact. A 5k-delete script runs against a brute
force oracle that rescans the lexicon after every batch.

The memory chapter compares child layouts honestly: map children vs
array children at three lexicon sizes with heap deltas quoted. The
cheaper layout wins the default, the dearer stays behind a flag.

The closing drill corrupts inputs: empty string, emoji prefix, 2k-char
paste, address with no matching prefix. Each returns the specified miss
answer. Scoring: completion parity 12, decay plus delete behavior 10,
memory candor and miss handling 8.
## Demo script
- Type p-r-e live; show top eight.
- Delete a shared-prefix word.
- Paste the 2k-char edge case.
- Show decay across two passes.
