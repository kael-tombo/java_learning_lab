# MINI_PROJECT — Advanced String Algorithms
> Build a pattern-matching toolkit (KMP, Aho-Corasick, suffix array + LCP) validated on fixed strings and one real log file.

## Inputs
- Fixed checks: pattern ababaca in text abababacaba (prefix table + match at 2); patterns {he,she,his} in ushers (she@1, he@2); banana SA/LCP.
- One real log file (>= 1 MB) plus 20 literal alert patterns for the throughput test.

## Build steps
1. Implement KMP (prefix function + search); verify prefix [0,0,1,2,3,0,1] and matches [2].
2. Implement Aho-Corasick (trie, failure links, output inheritance); verify hits [she@1, he@2].
3. Implement suffix array by sorting plus adjacent LCP; verify sa [5,3,1,0,4,2] and lcp [0,1,3,0,0,2].
4. Add a cross-check mode: KMP and Aho must agree on single-pattern inputs; naive search arbitrates disputes in tests.
5. Run the 20-pattern scan over the log file; report matches per pattern and MB/s (measured, machine noted).

## Acceptance criteria
1. All three fixed checks reproduce exactly as listed.
2. Cross-check mode passes on 50 random (text, pattern) pairs against naive search (seeded).
3. Log scan reports per-pattern counts plus measured MB/s with machine/JDK noted.
4. Overlapping matches (e.g. he inside she at shared end positions) are both reported, proven by the ushers case.
5. Empty pattern, empty text, and pattern-longer-than-text are handled with documented behavior and tests.
6. Memory note states the per-character structure cost for each method as implemented.

## Analysis prompts
1. Where does Aho-Corasick beat 20x KMP on the log file, and where would it not?
2. Which suffix pairs produce the lcp value 3, and why does sorting group them?
3. What input shape most stresses the failure-link walk, and how do output links help?

## Non-goals
- Regex engines, approximate matching (edit distance), and linear-time SA construction (doubling named only).

## Worked reference (verified outputs)
- KMP prints prefix=[0, 0, 1, 2, 3, 0, 1] matches=[2]; Aho prints hits=[she@1, he@2].
- Suffix job prints sa=[5, 3, 1, 0, 4, 2] lcp=[0, 1, 3, 0, 0, 2] for banana.

## Stretch
- Add Z-algorithm search and cross-check it against KMP on the 50 random pairs.
- Add suffix-array binary search for pattern queries and time it against Aho on the log file.
