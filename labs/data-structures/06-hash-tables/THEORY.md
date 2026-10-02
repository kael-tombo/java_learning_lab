# Theory: Hash Tables

## Hash Table Concept

A hash table is a data structure that maps **keys to values** using a **hash function** to compute an index into an array of buckets.

### Components

1. **Key**: the input to the hash function (must have `hashCode()`)
2. **Value**: the data associated with the key
3. **Hash function**: maps a key to an integer
4. **Compression**: maps hash to array index (modulo, bit masking)
5. **Bucket array**: stores the key-value pairs
6. **Collision resolution**: handles multiple keys mapping to the same index

## Hash Functions

### Properties of a Good Hash Function

- **Deterministic**: same key always produces same hash
- **Uniform**: distributes keys evenly across the table
- **Fast**: O(1) computation
- **Non-invertible**: hard to recover key from hash

### Java's hashCode Contract

```java
// If a.equals(b), then a.hashCode() == b.hashCode()
// If a.hashCode() == b.hashCode(), a.equals(b) is NOT required (collision)
// HashCode should be consistent during one execution
```

## Collision Resolution

### Separate Chaining

Each bucket is a linked list (or tree) of entries. Insert: compute index, append to list. Search: compute index, scan list.

### Open Addressing

All entries stored directly in the array. On collision, probe for next empty slot:

- **Linear probing**: `index = (hash + i) % capacity`
- **Quadratic probing**: `index = (hash + c₁i + c₂i²) % capacity`
- **Double hashing**: `index = (hash + i × hash₂(key)) % capacity`

## Load Factor and Resizing

```
load factor = number of entries / capacity
```

- Typical threshold: 0.75
- When exceeded: **rehash** (double capacity, reinsert all entries)
- Higher load factor: less memory, more collisions
- Lower load factor: more memory, fewer collisions

## Time Complexity

| Operation | Average | Worst Case |
|-----------|---------|------------|
| Get | O(1) | O(n) |
| Put | O(1)* | O(n) |
| Remove | O(1) | O(n) |
| Contains | O(1) | O(n) |

\*Amortized — includes occasional rehashing

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Swiss Tables Design Notes", Abseil / Google — https://abseil.io/about/design/swisstables — production open-addressing design: splits each 64-bit hash into H1 (57 bits, bucket index) + H2 (7 bits stored in a dense metadata byte array); lookup builds a mask from H2 and uses SSE to winnow 16 candidates in a few instructions — concrete industrial counterpart to the lab's linear/quadratic/double-hash probing section.
- Same source, overhead number — 1 byte of metadata per entry, and deleted slots keep probing (only empty slots terminate a probe) — ties directly to the lab's load-factor/rehash exercise: higher occupancy means longer probe chains, hence the 0.75-style resize threshold.
- Same source, flat vs node tables — flat_hash_map stores values inline (no pointer stability across rehash); node_hash_map keeps pointer stability at the cost of an extra allocation — useful framing for the lab's separate-chaining vs open-addressing tradeoff discussion.
- Same source, allocation optimization — emplace()/insert() avoid heap-allocating the value when the key is already present (std::unordered_map would allocate then free) — example of why average-O(1) put has very different constant factors across implementations; verify against the lab's benchmark exercise before quoting.
