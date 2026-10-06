# Flashcards — String Algorithms Advanced

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | π[i] on the pattern | length of longest proper prefix of p[0..i] that is also a suffix of it |
| 2 | KMP time | Θ(n+m) |
| 3 | KMP space | Θ(m) |
| 4 | On mismatch KMP moves | j ← π[j-1]; text pointer stays |
| 5 | KMP potential argument | j increases ≤n, decreases ≤ increases |
| 6 | Rabin–Karp core | rolling hash of length-m windows |
| 7 | False positive source in RK | hash collision |
| 8 | Hash confirm on hit | compare characters |
| 9 | Z[i] | longest substring at i matching a prefix of the string |
| 10 | Z build time | Θ(n) |
| 11 | Z matching construction | p + "#" + t, entries ≥ m are hits |
| 12 | Manacher output | radii of palindromes at each centre |
| 13 | Manacher time | Θ(n) |
| 14 | Mirror trick in Manacher | reuse radius of reflected centre, clamped to right edge |
| 15 | Suffix automaton states ≤ | 2n-1 |
| 16 | Suffix automaton recognises | the suffixes of its string |
| 17 | Naive match worst case | Θ(n·m) |
| 18 | Aho–Corasick | multi-pattern KMP via trie + failure links |
| 19 | Rolling update formula | H = (H - t[i]·B^(m-1))·B + t[i+m] |
| 20 | Hash window reuse | m-1 of m multiplications |
| 21 | Sentinel in Z match | blocks matches spanning the p/t boundary |
| 22 | π of "ababaca" | [0,0,1,2,3,0,1] |
| 23 | KMP on "aaaa" with p="aaab" | Θ(n·m) for naive, Θ(n) for KMP |
| 24 | Longest palindrome in "babad" | 3 |
| 25 | Rolling hash modulus | large prime; double modulus for safety |
| 26 | Java String.hashCode | not a rolling hash |
| 27 | LPS array | longest proper prefix that is also a suffix — the π table |
| 28 | Z[0] convention | 0 (no self-overlap) |
| 29 | Manacher centres | each gap between characters and each character |
| 30 | Suffix automaton use | longest common substring in Θ(n) |
| 31 | Suffix automaton transitions | ≤ 3n-4 |
| 32 | KMP fallback loop | while j > 0 and p[j] != t[i]: j = π[j-1] |
| 33 | Z window [l,r] meaning | rightmost prefix-match region used for reuse |
| 34 | Total RK expected time | Θ(n + m) |
| 35 | Total Manacher time | Θ(n) |
| 36 | KMP matches all occurrences in | Θ(n+m) |
| 37 | Multiple pattern matching | Aho–Corasick |
| 38 | Pattern period from π | period = m - π[m-1] for the border |
| 39 | String borders via π | follow π[m-1], π[π[m-1]-1], … |
| 40 | Z used for LPS of all prefixes | with a reverse pass |
| 41 | The border of "ababaca" | "a" (length 1) |
| 42 | KMP failure on "aaaab" | stays large then falls to 0 at the b |
| 43 | Why rolling hash is Θ(1) per window | one multiply-subtract-add replaces m work |
| 44 | False positive then confirm | RK reports candidate; confirm prevents wrong hits |
| 45 | Manacher right edge invariant | R only moves right |
| 46 | Z window right edge invariant | r only moves right |
| 47 | KMP potential invariant | j never exceeds i+1 and never below 0 |
| 48 | Suffix automaton path = substring | every substring is a path from the root |
| 49 | Edge-labelled DAG | suffix automaton is a DAG of states+transitions |
| 50 | KMP prefix function build | Θ(m) with the same fallback loop |
| 51 | Z-array build pseudocode core | if i ≤ r: Z[i] = min(r-i+1, Z[i-l]) |
| 52 | Rolling hash base choice | B > alphabet size; reduce mod q each step |
| 53 | KMP never rescans text | text pointer i increases monotonically |
| 54 | Palindrome radius r at centre c | length of the palindrome centred at c, halved per side |
| 55 | Z[i] ≤ m check in matching | entry ≥ m is a full match |
| 56 | Match end positions from Z | i + m in the concatenated string |
| 57 | Border of a string | a proper prefix that is also a suffix |
| 58 | Longest border via π | π[m-1] |
| 59 | Period of string = m - border | border length b ⇒ period m-b |
| 60 | KMP border use | find all borders in Θ(m) |
| 61 | RK mod arithmetic trap | subtract can go negative — renormalise |
| 62 | Rolling hash for "abc" vs "bca" | different windows, different hashes generally |
| 63 | Multi-pattern via one trie | Aho–Corasick adds failure links like KMP |
| 64 | KMP matched length as potential | spent at most once per character |
| 65 | Z on p#t for each hit | Z[i] ≥ m ⇒ t[i-m-1..] starts with p |
| 66 | Manacher on "cbbd" | 2 — "bb" |
| 67 | Suffix automaton for "abcab" | accepts abcab, bcab, cab, ab, b |
| 68 | Linear substring count | suffix automaton: Σ (len(s)-len(link(s))) |
| 69 | KMP fallback j=π[j-1] when j=0 | stop, move i |
