# Flashcards — Hash Table (Design HashMap)

- Q: HashMap operations & avg time? → A: put/get/remove/size all O(1) avg, O(n) worst
- Q: Collision resolution in solution? → A: Separate chaining — linked list per bucket
- Q: Load factor default? → A: 0.75 — balances space vs collisions
- Q: Hash function used? → A: (h ^ (h >>> 16)) & (length - 1) — mixes high bits, power-of-2 masking
- Q: Resize trigger? → A: When size / capacity >= 0.75, double capacity and rehash
- Q: Resize time complexity? → A: O(n) to rehash all entries, amortized O(1) per put
- Q: Why XOR-shift in hash? → A: Power-of-2 capacity needs well-distributed low bits; mixes high bits down
- Q: HashMap vs Hashtable? → A: HashMap: unsynchronized, allows nulls, faster. Hashtable: synchronized, no nulls, legacy
- Q: Remove with separate chaining? → A: Traverse chain, relink prev.next = curr.next (or update bucket head)
- Q: Worst case time? → A: O(n) — all keys collide in one bucket
- Q: Null key handling? → A: Dedicated bucket (usually 0) or separate field
- Q: Separate chaining vs open addressing? → A: Chaining: simpler, handles high load, extra memory. Open addressing: cache-friendly, no pointers, complex deletion
- Q: Entry class fields? → A: key, value, next (for linked list)
- Q: Why power-of-2 capacity? → A: Bitmask (length-1) is faster than modulo
- Q: Java 8+ HashMap improvement? → A: Treeify bins when chain length > 8 (red-black tree) — O(log n) worst case