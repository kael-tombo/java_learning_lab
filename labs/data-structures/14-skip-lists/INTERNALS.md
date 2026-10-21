# Internals of Skip Lists

## Node Structure

`java
class SkipListNode<K, V> {
    K key;
    V value;
    SkipListNode<K, V>[] forward;
    int level;
}
`

## Level Selection

The expected number of nodes at each level follows a geometric distribution. For n elements:
- Level 0: n nodes
- Level 1: â‰ˆ n/2 nodes
- Level 2: â‰ˆ n/4 nodes
- Level k: â‰ˆ n/2^k nodes

MAX_LEVEL should be ceil(log2(n)).

## Memory Usage

Each node with level l stores l+1 forward pointers:
- 1 node at level 32: 33 references
- Expected average level: 2 (for large n)
- Average references per node: â‰ˆ 2

Total references: â‰ˆ 2n for large n.

## Update Array

During insert/delete, an array of size MAX_LEVEL stores the nodes that need their forward pointers updated.
