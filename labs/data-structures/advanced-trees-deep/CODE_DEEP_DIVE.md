# CODE_DEEP_DIVE — Advanced Trees (Deep)

## TreeMap internals
- TreeMap<K,V> implements SortedMap/NavigableMap on a red-black tree.
- Entry nodes store left, right, parent, and a `color` boolean.
- put() is a BST descent; fixup via rotateLeft/rotateRight + recolor.
- Comparators: if the key's natural order or comparator returns 0, keys are considered equal — collision of equal keys overwrites value.

Pitfall: `subMap(k1,k2)` views are live; modifying the map structure elsewhere may invalidate the view's iteration.

## ArrayDeque vs LinkedList in maps
Not a map, but LinkedHashMap vs TreeMap: LinkedHashMap keeps doubly-linked access order; iteration is O(n) regardless of capacity; random-access get is still O(1) via HashMap base.

## Trie in Java
Use HashMap<Character, Node> for children unless sigma is tiny (array[26] faster). For large alphabet use CompressedTrie with edge labels.

## B-tree / B+ in practice
Java rarely uses B-trees directly; databases do. If you need cache-efficient search, look at MemoryMapped indexes / ChronicleMap style or B-link trees for concurrency.

## Splay in Java
No JDK class; write your own. Remember the node `parent` pointer and the zig/zig-zig/zig-zag recursion. Easy to get wrong when the parent is null mid-splay.

## Treap
Random priority with `new Random().nextInt()`; on collisions, tiebreak by a secondary key or use split-by-priority that reuses. Watch for stack overflow on deep recursion for very large n; iterative insert helps.

## Red-black vs AVL in JDK
JDK TreeMap chose RB because insert rotations are bounded (≤2) and recoloring is cheap; AVL delete restores more strictly. Read-heavy AVL in-memory would be slightly better, but the trade is usually acceptable.

## Common Java pitfalls
- Forgetting `parent` updates on rotations.
- Coloring bugs: red-red parent/child after color flip; fix by rotate at grandparent.
- Using HashMap children in trie with null values (HashMap permits nulls as values).
- Lazy color bool after clone.

## Micro-benchmark note
Use JMH; ArrayDeque-style amortization removes outliers. Watch memory: RB tree node overhead (~32–48 bytes) dwarfs the payload for small keys.
