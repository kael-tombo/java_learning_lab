# Step by Step: HashMap Internals

Trace `put(k,v)/get(k)/remove(k)` on `java.util.HashMap` with keys K1..K3 (empty start).

## Step 1 — Allocate (lazy)
- State per default capacity 16, load factor 0.75: no backing array / first==last==null / root==null.
- First insert triggers the single initial allocation (or root creation).

## Step 2 — Position K1
- Apply spreader `h ^ (h >>> 16)` folds high bits down → slot/walk target. Store entry; size 0→1.

## Step 3 — Position K2 (distinct)
- Resolves elsewhere; link per TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties. size 1→2.

## Step 4 — Position K3 colliding with K1
- Same slot/neighborhood: chain/tree/link splice; identity per TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64.

## Step 5 — Threshold check
- Compare against TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64; if tripped run resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0, else return.

## Step 6 — Remove K2
- Locate, unlink, clear slot (TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties); views (entrySet().iterator() EntryIterator) see it at once.

## Step 7 — Iterate
- Walk via entrySet().iterator() EntryIterator; fail-fast via modCount, ConcurrentModificationException.

## Self-check
- After each step assert size and the invariant in spreader `h ^ (h >>> 16)` folds high bits down.
- Lab note (01-hashmap-internals/STEP_BY_STEP.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
- Lab note (01-hashmap-internals/STEP_BY_STEP.md): TreeBin with tieBreakOrder (class name, identityHashCode) on hash ties
