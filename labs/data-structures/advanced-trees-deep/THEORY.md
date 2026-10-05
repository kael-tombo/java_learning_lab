# THEORY — Advanced Trees (Deep)

## 1. Why trees
An ordered set should answer search/insert/delete in O(log n) worst case, and a B-tree should also minimize block transfers. All advanced trees trade strictness, constants, and complexity for that.

## 2. Red-Black Tree
Invariants: every node red/black; root black; red nodes have black children; every root-to-leaf path has equal black count. Height ≤ 2 log(n+1). Insert: recolor up, at most two rotations. Delete: more cases, but same flavor. Java: TreeMap/TreeSet.

## 3. AVL
Strict height balance: |h(L)−h(R)| ≤ 1. Rotations LL/RR/LR/RL. Height ~ 1.44 log n. Stricter than RB → faster lookups, more rotations on write-heavy loads.

## 4. Splay
No balance stored; access moves a node to the root via zig/zig-zig/zig-zag. Amortized O(log n); great for skewed/frequent access; poor worst case per op.

## 5. Treap
BST on key + max-heap on random priority. Rotations fix heap order; expected O(log n). Split/merge form lets you express insert/erase/join in O(log n).

## 6. B-tree/B+
Nodes hold many keys; minimize disk/block trips. B+ pushes data to leaves and links leaves. Fanout B chosen from block size. Height ~ log_B n.

## 7. RedBlackTreeMap (JDK TreeMap)
Uses red-black tree; comparator or natural ordering; navigable API (floor/ceiling/subMap). Fail-fast iterators.

## 8. Trie
Path encodes prefix; children map char→node; marked end-of-word nodes. O(L) search for length L. Compressed tries (radix) reduce node count.

## 9. Invariants to memorize
RB: equal black-height, no red-red edge. AVL: |balance| ≤ 1. Treap: heap on priority. B-tree: full nodes except leaves rules, min fill. Trie: path prefix = node content.

## 10. Choosing in practice
Read-heavy, strict latency → AVL; general purpose ordered map → RB (TreeMap); skewed hot keys → splay; randomized simplicity → treap; disk → B-tree/B+; prefix matching → trie.
