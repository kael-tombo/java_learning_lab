# FLASHCARDS — Lists Deep

| # | Front | Back |
|---|---|---|
| 1 | ArrayList backing? | Object[] |
| 2 | ArrayList get? | O(1) |
| 3 | ArrayList middle insert? | O(n) |
| 4 | ArrayList add amortized? | O(1) via doubling |
| 5 | ArrayList growth? | ×2 (OpenJDK ~1.5× on grow) |
| 6 | LinkedList nodes? | doubly-linked |
| 7 | LinkedList addFirst? | O(1) |
| 8 | LinkedList get? | O(n) |
| 9 | Vector default growth? | ×2 |
| 10 | Vector methods? | synchronized |
| 11 | ArrayDeque vs LinkedList? | ArrayDeque faster |
| 12 | Fail-fast via? | modCount check |
| 13 | LRU with? | LinkedHashMap or DL+HashMap |
| 14 | Reverse list iteratively? | prev/curr/next |
| 15 | Floyd detects? | cycle |
| 16 | Cycle entry via? | Floyd + entry step |
| 17 | Memory per LinkedList node? | ~24–48B |
| 18 | CopyOnWriteArrayList mutation? | copy array |
| 19 | Best list for iteration-removal? | usually ArrayDeque/iterator |
| 20 | Queue via LinkedList front? | O(1) |
| 21 | ArrayList trimToSize effect? | shrink cap |
| 22 | ensureCapacity purpose? | preallocate |
| 23 | LinkedList iterator remove? | O(1) once positioned |
| 24 | Vector replaced by? | ArrayList/Collections.syncList |
| 25 | ArrayDeque can hold nulls? | no |
| 26 | LinkedList can hold null? | yes |
| 27 | ArrayList null slots? | yes |
| 28 | ArrayList serializable? | yes |
| 29 | RandomAccess interface marks? | O(1) positional access |
| 30 | ArrayList implements RandomAccess? | yes |
| 31 | LinkedList implements RandomAccess? | no |
| 32 | ArrayList capacity property? | `elementData.length` |
| 33 | Iterator.remove relation to CME? | legal after next |
| 34 | subList view live? | yes |
| 35 | ArrayList sublist O(1) view? | yes |
| 36 | LinkedList sublist O(n) get? | yes |
| 37 | ArrayList sort? | TimSort |
| 38 | LinkedList sort via merge? | yes |
| 39 | Stack extends Vector? | yes (legacy) |
| 40 | ArrayDeque as Stack? | yes, drop-in |
| 41 | LinkedList as Deque? | yes |
| 42 | ArrayDeque vs LinkedList iteration? | ArrayDeque fewer allocs |
| 43 | ArrayList constructor with capacity? | yes |
| 44 | ArrayList trim on remove? | no |
| 45 | LinkedList peek/pop/push? | offerFirst/pollFirst |
| 46 | LRU capacity-triggered eviction? | removeEldest |
| 47 | ArrayList clone? | shallow copy |
| 48 | LinkedList clone? | copy of nodes |
| 49 | Concurrent list choices? | CopyOnWriteArrayList |
| 50 | Snapshot iterators? | CopyOnWriteArrayList |
| 51 | Fail-fast vs weakly consistent? | fail-fast: throw |
| 52 | Iterator.next after remove? | IllegalStateException |
| 53 | ArrayList batch ops O? | O(n·m) worst |
| 54 | LinkedList batch removeAll? | O(n·m) |
| 55 | ArrayList buffer compaction? | arraycopy |
| 56 | ArrayDeque ring buffer? | yes, circular |
| 57 | LinkedList vs ArrayDeque stack? | ArrayDeque wins |
| 58 | ArrayList for binary search? | yes |
| 59 | LinkedList for binary search? | no, O(n) |
| 60 | Why LinkedList rarely wins? | cache locality + node overhead |
