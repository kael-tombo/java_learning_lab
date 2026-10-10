# Visual Guide: LinkedList

## Chain layout
```
first                          last
  |                              |
  v                              v
+---+    +---+    +---+
| a |<-->| x |<-->| b |   each Node: {prev, item, next}, 24 bytes
+---+    +---+    +---+
prev=null                  next=null   (null-terminated, never circular)
```

## node(index): nearer end wins
```
index:  0 ..... size>>1 ..... size-1
        |<-- from first -->|<-- from last -->|
        forward if i < size>>1 else backward
get(75000) in n=100000: 25000 hops back, not 75000 forward
```

## linkBefore(x, succ) splice
```
before:  [a] <-> [b]          (succ = b)
after:   [a] <-> [x] <-> [b]  (4 pointer writes, O(1) once positioned)
```

## unlinkFirst / unlinkLast
```
unlinkFirst: first = f.next; first.prev = null; clear f (GC); size--
unlinkLast:  last = l.prev;  last.next = null;  clear l (GC); size--
every path flows through link*/unlink* (size + modCount updated there)
```

## Deque face
```
push/pop    = addFirst/removeFirst   (stack)
offer/poll  = add/offerLast + pollFirst (queue)
nulls allowed (unlike ArrayDeque); get(i) still O(n/2) — not O(1)
```
