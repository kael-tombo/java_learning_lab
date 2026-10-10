# Visual Guide: ConcurrentHashMap

## Table + cells layout
```
table (Node[], power of two)        counter cells (LongAdder-style)
+---+---+---+---+                        baseCount
| 0 | 1 | 2 |..|  <- (n-1) & spread(h)     +  [c0][c1][c2][c3]
+---+---+---+---+                        sumCount = base + sum(cells)
  |   |   |
 Node CAS  TreeBin(sync)  ForwardingNode(MOVED -> new table)
(empty bin (tree bin     (moved bucket:
 pure CAS)  root lock)    follow, don't block)
```

## putVal decision flow
```
key,value -> null check (NPE) -> i = (n-1) & spread(h) -> f = tabAt(i)
  f == null      -> casTabAt install (no lock)
  f.hash==MOVED  -> helpTransfer (join resize)
  else           -> synchronized (f): append / replace / treeify at 8
  -> addCount -> sumCount >= sizeCtl ? start cooperative transfer
```

## Resize sketch (16 -> 32)
```
old: [a][FWD][b][FWD]...   FWD = ForwardingNode -> new table
new: [a][..][b][..  ]...   readers follow FWD; writers move stride chunks
each entry: stays at i or moves to i+16 by one hash bit
```

## Visibility edges
```
write val/next (volatile) --happens-before--> read via tabAt (volatile)
no monitor on reads: get/replace(k,old,new) proceed lock-free
iterators: weakly consistent, never throw ConcurrentModificationException
```
