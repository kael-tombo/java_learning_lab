# Flashcards: HashMap Internals

Q: What is `java.util.HashMap` structurally?
A: hash table with separate chaining over a Node[] table.

Q: State the position rule.
A: spreader `h ^ (h >>> 16)` folds high bits down.

Q: What are the tree/growth thresholds?
A: TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64.

Q: How does growth/rebalance work?
A: resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0.

Q: What are the null rules?
A: null key allowed once, hash 0, bucket 0.

Q: What is the default sizing / allocation behavior?
A: default capacity 16, load factor 0.75.

Q: Which ops form the hot path?
A: put(k,v)/get(k)/remove(k).

Q: How do views/iterators behave?
A: entrySet().iterator() EntryIterator; fail-fast via modCount, ConcurrentModificationException.

Q: Name one extra invariant from the source.
A: TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties.

Q: Where is the authoritative behavior defined?
A: `java.util.HashMap` + THEORY.md / CODE_DEEP_DIVE.md in this lab.
