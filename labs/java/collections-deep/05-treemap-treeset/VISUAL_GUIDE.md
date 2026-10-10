# Visual Guide: TreeMap / TreeSet

## Red-black tree (B = black=true, R = red=false)
```
        5(B)                      root always black
       /    \
     3(R)    7(R)                 no red-red adjacency
    /
  1(R) -> violation under red 3 -> fixAfterInsertion: recolor + <=2 rotations
black-height equal on every root-to-leaf path -> height <= 2*log2(n+1)
```

## Lookup = BST walk on compareTo, not equals
```
key -> cmp vs root -> left if <0, right if >0, MATCH iff cmp == 0
"a" vs "A" (CASE_INSENSITIVE_ORDER): cmp == 0 -> same element, add returns false
```

## Live bounded views (no copies)
```
tree:  [1][3][5][7][9]
subMap(2,true,6,false) -> window [3,5]: writes hit the tree, tree writes show
descendingMap() -> reversed window; tailMap(c).headMap(d) composes intervals
bounds checked against the PARENT view at call time — cannot escape range
```

## Iteration via successor links
```
first = leftmost (1); next = successor(p): down-right-once then leftmost,
  else climb until coming from a left child — O(n) total, O(log n) per step
fail-fast: captures modCount, throws ConcurrentModificationException on drift
```

## TreeSet = thin skin
```
TreeSet.add(e) -> map.put(e, PRESENT); PRESENT is one shared sentinel object
add returns false on compareTo==0 (silent); TreeMap.put would REPLACE the value
```
