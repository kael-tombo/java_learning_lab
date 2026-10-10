# Flashcards: TreeMap / TreeSet

Q: What is `java.util.TreeMap / java.util.TreeSet` structurally?
A: red-black tree of Entry nodes (TreeSet = TreeMap<E,Boolean> with PRESENT sentinel).

Q: State the position rule.
A: color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1).

Q: What are the tree/growth thresholds?
A: identity is compareTo==0 (or comparator.compare==0), NOT equals().

Q: How does growth/rebalance work?
A: compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first.

Q: What are the null rules?
A: live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view.

Q: What is the default sizing / allocation behavior?
A: iteration ascending via on-the-fly successor links; fail-fast via modCount.

Q: Which ops form the hot path?
A: getEntry/put/fixAfterInsertion/fixAfterDeletion/getSuccessor.

Q: How do views/iterators behave?
A: NavigableSubMap view classes; unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them.

Q: Name one extra invariant from the source.
A: floor/ceiling/higher/lower + pollFirstEntry/pollLastEntry in O(log n).

Q: Where is the authoritative behavior defined?
A: `java.util.TreeMap` + THEORY.md / CODE_DEEP_DIVE.md in this lab.
