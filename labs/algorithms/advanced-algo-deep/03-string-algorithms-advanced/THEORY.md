# Theory — String Algorithms Advanced

String algorithms exploit the *overlap structure* of strings: a partial match
already tells you something about the next position. KMP, Z, and the suffix
automaton are three progressively more refined exploitations of that idea.

## The naive scan, and what it wastes

Matching pattern p (length m) against text t (length n) by trying every
alignment costs Θ(n·m): for each of n-m+1 alignments, compare up to m
characters. The waste is that after a mismatch at offset k, the naive scan
restarts comparison at the beginning of p over a region of t it has already
read. KMP's insight is that the k characters of t we just compared are a
*known prefix* of p — so we do not need to re-read them.

## KMP and the failure function

Define `π[i]` on the pattern as the length of the longest proper prefix of
`p[0..i]` that is also a suffix of `p[0..i]`. When a mismatch occurs after
matching j characters of the pattern, the next candidate alignment corresponds
to `j ← π[j-1]` — the longest prefix of p that could still match ending at
the same text position. This never *shortens* the text pointer; it only moves
j backwards along already-matched territory.

**Running time.** Let the matched length be j. Each comparison either
increases j by 1 or decreases it via π (which costs one step per unit
decrease). Since j increases at most n times and each π-application decreases
j by at least 1, the total number of decreases is at most n. Hence the total
work is Θ(n) — the potential argument is that j is a potential that is spent
at most once per text character.

## Rabin–Karp rolling hash

Hash the pattern, and hash each length-m window of the text with a rolling
update: `H(i+1) = (H(i) - t[i]·B^(m-1))·B + t[i+m]`. Each window compares
in Θ(1) on the hash and Θ(m) on a confirm. A false positive is a hash
collision; with a uniform hash mod a large prime q, the expected number is
O(n·m/q)-bounded, so a double modulus or a 64-bit splitmix-style hash makes
collisions negligible. The rolling update is the whole trick: it reuses m-1
of the m multiplications.

## Z-function

`Z[i]` = length of the longest substring starting at i that matches a prefix
of the whole string. For i=0 define Z[0]=0. Maintain the rightmost window
`[l, r]` that lies inside a prefix-match; for i ≤ r reuse `Z[i-l]` clamped
to the remaining window, otherwise scan forward. Because r only moves right
and each comparison either advances r or stops, the total is Θ(n). Pattern
matching is `Z` on `p + '#' + t` and scanning for entries ≥ m.

## Manacher's algorithm

Longest palindrome in Θ(n): expand around each centre, but reuse the
palindrome radii of earlier centres reflected about the current mirror. The
mirror is the centre of the last palindrome whose right edge is farthest
right; a position i inside that palindrome inherits the radius of its
reflection, clamped. Linear by the same "right edge never moves left"
argument as KMP/Z.

## Suffix automaton (overview)

A suffix automaton recognises exactly the suffixes of a string. Each new
character adds at most two states and at most ... transitions; the
incremental construction is Θ(n) with a small alphabet. It is the basis of
linear-time longest-common-substring and substring-counting queries. The
important structural facts: states are equivalence classes of substrings with
the same endpos set, and a path of length k from the initial state reaches a
state accepting that substring.

## Choosing between them

| Task | Tool | Time |
|------|------|------|
| Single pattern in text | KMP or Rabin–Karp | Θ(n+m) |
| All alignments / LPS array | KMP | Θ(n+m) |
| Multi-pattern | Aho–Corasick | Θ(n + matches) |
| Longest palindrome | Manacher | Θ(n) |
| Many substring queries | Suffix automaton | Θ(n) build |
| Occurrences count | Z-array / KMP | Θ(n+m) |

## Pitfalls

- KMP: resetting the text pointer on mismatch silently restores the Θ(n·m)
  blow-up; the whole point is that the text pointer never moves back.
- Off-by-one in π: `π[i]` is indexed on the *pattern*, and a full match at
  text position pos means the pattern matched ending at pos+m-1.
- Rabin–Karp: comparing only hashes returns false positives; confirm on a
  match. Java's `String.hashCode` is not a rolling hash.
- Z/Manacher use 0-based inclusive windows; mixing in 1-based CLR pseudocode
  causes an off-by-one at the window edges.
