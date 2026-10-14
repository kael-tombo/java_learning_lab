# Rollout: Autocomplete plus Longest-Prefix Match on a Trie

Phase 0 - scope. One trie library serving two callers: a search-box
autocomplete API and an IP longest-prefix-match table. Shared node code,
separate edge profiles, one conformance suite.

Phase 1 - core. Alphabet-indexed or map-based children (decision logged
with memory numbers for both), terminal flags, prefix counts, insert /
search / startsWith / delete with node pruning. All ops O(L) in key
length; the report shows timing vs key length, not vs key count.

Phase 2 - autocomplete. Top-8 suggestions per prefix ranked by stored
frequency, with update-on-select reweighting. Suggestion sets verified
against a brute-force prefix scan on a 60k-word lexicon; order must
match the ranking rule exactly.

Phase 3 - prefix match. Binary trie over address bits for longest-prefix
lookup; verified against a linear table scan on 20k prefixes plus 50k
lookups. Default-route behavior specified and tested.

Phase 4 - memory. Per-key byte cost from heap deltas at 10k/50k/200k
keys for both child layouts; compressed single-child chains evaluated
as a stretch note with measured savings.

Phase 5 - edges. Empty prefix (top overall), missing prefix (typed miss),
delete of a shared-prefix word (siblings survive), duplicate insert
(frequency policy documented), unicode entries (byte vs char policy).

Phase 6 - launch proof. Lexicon fixture, query trace with latencies,
memory table, oracle agreement logs for both callers, rollback note
(HashMap scan fallback behind a flag). Bar: caller parity 12, prefix
semantics 10, memory plus edge evidence 8.
## Launch gates
- Both oracle logs green.
- Memory table reviewed.
- Rollback flag exercised once.
- Lexicon version pinned.
