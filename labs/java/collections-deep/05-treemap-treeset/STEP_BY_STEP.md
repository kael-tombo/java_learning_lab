# Step by Step: TreeMap / TreeSet

Trace `put(5,a); put(3,b); put(7,c); put(1,d)` (natural Integer ordering).

## Step 1 — addEntryToEmptyMap(5)
- `compare(5, 5)` runs FIRST (type/null pre-check), then root = black Entry(5).
  size 0->1. New root forced BLACK.

## Step 2 — put(3): BST descend + red insert
- 3 < 5 -> left child of root, inserted RED. Parent black -> no violation,
  no fix. size 1->2.

## Step 3 — put(7): mirror
- 7 > 5 -> right child, RED, parent black -> no fix. Tree: 5(B) with 3(R),7(R).

## Step 4 — put(1): red-red violation + fix
- 1 < 5, 1 < 3 -> left child of 3, RED under RED parent -> fixAfterInsertion:
  recolor 3's subtree / rotate at 5 so root stays black and black-heights match.
  (Exact case depends on uncle color; JDK does <= 2 rotations here.)

## Step 5 — TreeSet face
- `set.add(3)` on TreeSet{1,3,5,7}: `compareTo == 0` with existing 3 -> returns
  false, no PRESENT overwrite, size unchanged.

## Step 6 — Views and iteration
- `subMap(2, true, 6, false)` is a live view holding [3,5]; `pollFirstEntry`
  removes 1 in O(log n); `keySet().iterator()` walks 3->5->7 via successor().

## Step 7 — Neighbor and reverse probes
- `ceilingKey(4)` returns 5, `floorKey(4)` returns 3, `higherKey(5)` returns 7
  — each one O(log n) descent, impossible on HashMap without a full sort.
- `descendingMap().firstKey()` returns 7 with no copy; assert the reverse walk
  yields 7->5->3.
