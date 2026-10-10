# Visual Guide: HashMap Internals

## Layout (`java.util.HashMap`)
```
store: [hash table with separate chaining over a Node[] table]
         |
 +-------+--------+------ ...
 | slot0 | slot1  | ...            <- position via spreader `h ^ (h >>> 16)` folds high bits down
 +---+---+---+----+------ ...
     |       |
   chain/  chain/
   links   tree                <- overflow per TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64
```

## Insert flow
```
key -> position (spreader `h ^ (h >>> 16)` folds high bits down)
        -> empty?  store directly (size++)
        -> taken?  resolve via TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64, splice in
        -> check TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64 -> maybe resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0
```

## Growth sketch
```
[resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0]
before: [a][b][ ][c]  size=3
after:  [a][ ][b][ ][c][ ][ ][ ]  (each entry re-decided once)
```

## Iteration sketch
```
entrySet().iterator() EntryIterator walks the LIVE store left-to-right (or ascending):
  view -> store[0] -> store[1] -> ...   (mutations visible mid-walk)
  rule: fail-fast via modCount, ConcurrentModificationException
```

## Null slot
```
null key allowed once, hash 0, bucket 0
```
