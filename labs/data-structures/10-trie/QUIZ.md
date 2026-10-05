# QUIZ — Trie (Prefix Tree)

15 questions. Answer from memory, then check. Target: 12+/15.

1. What is the core idea of Trie (Prefix Tree) in one sentence?
2. Name all operations in the contract table and their costs.
3. State invariant #1 and give a concrete violation example.
4. What workload makes this structure beat its naive baseline?
5. Which operation is the hot path, and what is its cost O(L)?
6. What breaks if the invariant checker is skipped after updates?
7. Best vs average vs worst case: which applies here and why?
8. How does memory scale with n? Name the auxiliary overhead.
9. Give an adversarial input and the mitigation.
10. How would you test this with 5 focused unit tests?
11. Where does Java's stdlib already cover this, and why build it anyway?
12. Which two production systems use this, and what metric do they gain?
13. Sketch the structure for n=7 on paper: what lands where?
14. What is the single most common bug, and how do you detect it?
15. One-line interview pitch for this structure?

## Answers
1. A trie stores strings by sharing common prefixes: each edge is a character and each node marks end-of-word plus subtree counts.
2. insert(word) O(L); search(word) O(L); startsWith(prefix) O(P); countWordsWithPrefix(p) O(P); delete(word) O(L); autocomplete(p,k) O(P + k*Sigma)
3. Every root-to-node path spells a prefix of some inserted key
4. search-engine autocomplete + IP longest-prefix match
5. insert(word) at O(L)
6. Stale auxiliary state causes silently wrong answers.
7. See THEORY section 5; randomized/amortized bounds need the qualifier.
8. Linear in n plus documented auxiliary factor; measure with a profiler.
9. Sorted/adversarial keys or collisions; randomize / rehash / rebalance.
10. Empty, singleton, boundary, duplicate/adversarial, invariant fuzz.
11. Stdlib covers the common case; this lab teaches the mechanism + limits.
12. search-engine autocomplete + IP longest-prefix match; contact-list prefix search in a mobile app.
13. Paper sketch matching the invariant list in THEORY.
14. Stale bookkeeping (alphabet mapping (array vs hashmap) is fixed per implementation); catch with a checker.
15. 'Trie (Prefix Tree) for prefix search, autocomplete, ip routing.'

