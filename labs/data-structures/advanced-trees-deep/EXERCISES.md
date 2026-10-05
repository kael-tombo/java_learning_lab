# EXERCISES — Advanced Trees (Deep)

1. Insert 1..31 into a red-black tree; draw and count rotations.
2. Prove equal black-height for your tree above.
3. Implement AVL balanceFactor update on insert (recursive version).
4. Trace LR rotation on node with left-heavy inner child.
5. Splay: access 3, then 8, then 5 on a 7-node BST; draw each zig/zig-zig.
6. Build a treap by inserting with random priorities; show expected rotations.
7. Split a treap at k; merge it back; verify inorder.
8. Design a B-tree of order 3; insert 1,2,3,4,5; split root.
9. Compare TreeMap vs ConcurrentHashMap for ordered iteration.
10. Implement trie insert with a HashMap children.
11. Add prefix counting to your trie (pass-through counts).
12. Benchmark TreeMap put vs HashMap put at n=100k; note factors.
13. Find and fix a rotation bug: suspect parent recolor after RB delete.
14. Explain why splay is amortized O(log n) with the potential function.
15. Pick an ordered-set replacement for each workload: heavy reads, heavy writes, disk, prefix.
