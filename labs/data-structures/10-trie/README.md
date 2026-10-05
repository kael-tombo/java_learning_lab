# Trie (Prefix Tree) — Lab

*Prefix search, autocomplete, IP routing.*

## What you will build
Core idea: A trie stores strings by sharing common prefixes: each edge is a character and each node marks end-of-word plus subtree counts.

Key operations:
- `insert(word)` — add a word, creating nodes as needed (O(L))
- `search(word)` — exact match incl. end-of-word flag (O(L))
- `startsWith(prefix)` — prefix existence check (O(P))
- `countWordsWithPrefix(p)` — subtree word count (O(P))
- `delete(word)` — unmark + prune dead nodes (O(L))
- `autocomplete(p,k)` — DFS top-k under prefix node (O(P + k*Sigma))

## Lab map
- `README.md`
- `THEORY.md`
- `EXERCISES.md`
- `QUIZ.md`
- `FLASHCARDS.md`
- `MATH_FOUNDATION.md`
- `CODE_DEEP_DIVE.md`
- `VISION.md`
- `MINI_PROJECT.md`
- `REAL_WORLD_PROJECT.md`

## Invariants to keep
- Every root-to-node path spells a prefix of some inserted key
- endOfWord flag distinguishes 'car' from prefix of 'cart'
- passCount/subtree counts stay consistent after insert/delete
- alphabet mapping (array vs HashMap) is fixed per implementation

## How to run (Java 17+)
```bash
javac -d out $(find src -name '*.java')
java -cp out Main
```

## Success criteria
- All unit tests green; benchmark notes recorded.
- Can explain every complexity in the table above.
