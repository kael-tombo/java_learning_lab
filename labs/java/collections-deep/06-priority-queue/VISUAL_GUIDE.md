# Visual Guide: the Array-Tree

Heap `[1, 3, 2, 5, 9, 8, 7]` drawn as a tree (index in parens):

```
            1(0)
          /      \
       3(1)      2(2)
       / \        / \
    5(3) 9(4)  8(5) 7(6)
```

Read each row left to right and you get the array back — that flatness is
the point. There are no pointers; "left child" means "index 2k+1".

## SiftUp trace: offer(0) → index 7

```
  before:        1
               / \
              3   2        append 0 at index 7 (child of 5)
             / \ / \
            5 9 8 7
           /
          0?              k=7, parent(7)=3 (value 5): 5>0, pull down
```

Two more hops (past 3, past 1) and 0 lands at the root. Path length 3 =
floor(log2 8).

## SiftDown trace: poll() moves 7 to root

```
  7               3               2
 / \    →       / \      →      / \
3   2          5   2            5   7 ...
```

7 sinks one level (swapping with smaller child 2... in the real code the
child is pulled up and 7 drops). Depth of sinking ≤ tree height.

## Growth ruler (measured by reflection)

```
cap: 11 → 24 → 50 → 102 → 153 → 229 → 343
        +2 rule      |      1.5x rule
     (oldCap + 2)   64 boundary   (oldCap >> 1)
```

The kink at 64 is the only non-obvious mark: tiny heaps roughly double,
large ones grow by half.
