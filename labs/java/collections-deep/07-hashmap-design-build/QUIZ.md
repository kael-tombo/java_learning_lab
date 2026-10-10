# Quiz: Open-Addressing HashMap

## Q1. Why spread (`h ^ (h >>> 16)`) before masking?

**A.** `h & (n-1)` keeps only low bits; hashes varying in high bits would
collide systematically. Folding high into low makes all bits influence the
index.

## Q2. Why can't remove just null the slot?

**A.** Later probes reaching the slot would stop at EMPTY and miss keys
placed beyond it — phantom misses. Tombstones say "keep walking".

## Q3. Why must the load trigger count tombstones?

**A.** Tombstones occupy probe steps. A table half-live + half-tombstone
probes like a full one; `size/n` alone hides the real α.

## Q4. Hit vs miss probes at α = 0.5, 0.7, 0.9?

**A.** Hit ≈ 1.5 / 2.2 / 5.5; miss ≈ 2.5 / 6 / 50. Miss cost squares —
that knee is why caps sit at 0.5–0.7.

## Q5. What does resize do with tombstones and positions?

**A.** Rehashes live entries only through the new mask (runs dissolve),
recounts `size`, zeroes tombstones. Not a slot copy.

## Q6. Linear vs quadratic probing vs double hashing?

**A.** Linear: best locality, clustering. Quadratic: breaks clusters,
needs full-cycle guarantees. Double hashing: uniform, two hashes per
probe, poor locality.

## Q7. How does HashMap avoid everything above?

**A.** Chaining: collisions extend per-bucket lists/trees, unlinking is
local (no tombstones), α > 1 survivable, collide-all degrades to O(log n)
via treeified bins.
