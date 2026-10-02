# Quiz — Hash Table (Design HashMap)

1. What are the four operations required by LeetCode 706 (Design HashMap) and their average time complexities?
2. What collision resolution strategy does the provided solution use?
3. What is the load factor, and why is 0.75 a common default?
4. How does the `hash(int key)` function work in the solution?
5. What happens during `resize()` and what is its time complexity?
6. Why do we use `(h ^ (h >>> 16)) & (length - 1)` instead of just `key % length`?
7. What is the difference between `HashMap` and `Hashtable` in Java?
8. How does the `remove` operation work with separate chaining?
9. What is the worst-case time complexity for hash table operations, and when does it occur?
10. How would you handle null keys in a hash map implementation?

---

## Answers

1. **put(key, value)** O(1) avg, **get(key)** O(1) avg, **remove(key)** O(1) avg, **size()** O(1). Worst case O(n).
2. **Separate chaining** — Each bucket is a linked list of Entry nodes. Collisions are resolved by adding to the list.
3. **Load factor** = size / capacity. 0.75 balances space utilization (lower = more empty buckets) vs collision rate (higher = longer chains).
4. `hash(key) = (h ^ (h >>> 16)) & (length - 1)` where `h = key.hashCode()`. Mixes high bits into low bits, then masks with power-of-2 length.
5. `resize()` creates new array of double size, rehashes all entries. Time: O(n) where n = current size. Amortized O(1) per put.
6. `key % length` only works well when length is prime. With power-of-2 length, `& (length-1)` is faster, but low bits must be well-distributed. The XOR-shift mixes high bits down.
7. `HashMap`: non-synchronized, allows null key/value, faster. `Hashtable`: synchronized (thread-safe), no nulls allowed, legacy.
8. Traverse the chain at the bucket. If found, relink: `prev.next = curr.next` (or `bucket = curr.next` if head). Decrement size.
9. **Worst case: O(n)** — All keys hash to same bucket (poor hash function or adversarial input). Chain becomes a linked list.
10. Special case: store null key in a dedicated bucket (e.g., bucket 0) or use a separate `nullKeyValue` field. Java's HashMap uses bucket 0.