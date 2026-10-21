# Mental Models

## 1. The Versioned Document Model
Think of a document where each edit creates a new version. Old versions remain accessible. Most content is shared between versions (structural sharing). This is exactly how Git works.

## 2. The Copy-on-Write Model
When you modify data, the system copies only the parts that changed. The rest is shared. This is like a lazy copy: the copy happens only when someone writes.

## 3. The Tree Path Model
In a persistent tree, modifying a leaf copies the nodes along the path from root to that leaf. The unchanged branches are shared. This limits copying to O(height) instead of O(size).

## 4. The Snapshot Model
Every operation takes a snapshot of the current state and returns it. The snapshot is immutable and safe to share. Old snapshots remain valid.
