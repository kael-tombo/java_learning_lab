# Flashcards: ConcurrentHashMap

Q: What is `java.util.concurrent.ConcurrentHashMap` structurally?
A: lock-striped hash table: buckets (not the map) are the locking unit.

Q: State the position rule.
A: putVal rejects null key/value with NullPointerException.

Q: What are the tree/growth thresholds?
A: spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative.

Q: How does growth/rebalance work?
A: sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer.

Q: What are the null rules?
A: counting via baseCount + CounterCell[] (LongAdder-style); sumCount() snapshot.

Q: What is the default sizing / allocation behavior?
A: writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt).

Q: Which ops form the hot path?
A: putVal/merge/compute/putIfAbsent.

Q: How do views/iterators behave?
A: weakly-consistent iterators (never throw CME); volatile tabAt/casTabAt reads; Node.val/next volatile.

Q: Name one extra invariant from the source.
A: TreeBin root locking; TREEIFY 8 / MIN 64 / UNTREEIFY 6 shared with HashMap.

Q: Where is the authoritative behavior defined?
A: `java.util.concurrent.ConcurrentHashMap` + THEORY.md / CODE_DEEP_DIVE.md in this lab.
