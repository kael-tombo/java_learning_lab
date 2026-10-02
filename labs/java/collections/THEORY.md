# THEORY — Java Collections Framework

## Overview

The Java Collections Framework (JCF) is a unified architecture for representing and manipulating collections of objects. It provides a set of interfaces, implementations, and algorithms for data structures commonly used in programming.

---

## 1. Collection Hierarchy

```
Collection (interface)
├── List (interface)
│   ├── ArrayList
│   ├── LinkedList
│   ├── Vector (legacy)
│   └── Stack (legacy)
├── Set (interface)
│   ├── HashSet
│   ├── LinkedHashSet
│   └── TreeSet (SortedSet)
├── Queue (interface)
│   ├── PriorityQueue
│   ├── ArrayDeque
│   └── LinkedList
└── Deque (interface)
    ├── ArrayDeque
    └── LinkedList

Map (interface) — separate hierarchy
├── HashMap
├── LinkedHashMap
├── TreeMap (SortedMap)
├── Hashtable (legacy)
└── ConcurrentHashMap
```

---

## 2. Core Interfaces

### Collection
Root interface for all collections (except Maps). Core methods:
- `add(E)`, `remove(Object)`, `contains(Object)`, `size()`, `isEmpty()`, `iterator()`

### List
Ordered collection with positional access. Allows duplicates.
- `get(int index)`, `set(int, E)`, `add(int, E)`, `remove(int)`

### Set
No duplicates. Mathematical set abstraction.
- `HashSet`: Hash table, O(1) ops, no order
- `LinkedHashSet`: Insertion order, hash table + linked list
- `TreeSet`: Sorted (NavigableSet), Red-Black tree, O(log n)

### Queue/Deque
- `Queue`: FIFO, `offer()`, `poll()`, `peek()`
- `Deque`: Double-ended, `addFirst()`, `addLast()`, `removeFirst()`, `removeLast()`

---

## 3. Map Interface

### Map Hierarchy
- **HashMap**: Hash table, O(1) avg, no order
- **LinkedHashMap**: Insertion/access order, hash table + linked list
- **TreeMap**: SortedMap, Red-Black tree, O(log n)
- **ConcurrentHashMap**: Thread-safe, segmented/striped locking
- **WeakHashMap**: Weak keys, auto-removal

### Key Methods
- `put(K, V)`, `get(Object)`, `remove(Object)`
- `containsKey()`, `containsValue()`, `keySet()`, `values()`, `entrySet()`

---

## 4. Performance Characteristics

| Collection | Add | Contains | Remove | Iteration | Order |
|------------|-----|----------|--------|-----------|-------|
| ArrayList | O(1)* | O(n) | O(n) | Fast | Index |
| LinkedList | O(1) | O(n) | O(1)* | Slow | Index |
| HashSet | O(1)* | O(1)* | O(1)* | Fast | None |
| LinkedHashSet | O(1)* | O(1)* | O(1)* | Fast | Insertion |
| TreeSet | O(log n) | O(log n) | O(log n) | Fast | Sorted |
| HashMap | O(1)* | O(1)* | O(1)* | Fast | None |
| LinkedHashMap | O(1)* | O(1)* | O(1)* | Fast | Insertion |
| TreeMap | O(log n) | O(log n) | O(log n) | Fast | Sorted |

* Amortized/average case

---

## 5. Choosing the Right Collection

| Requirement | Recommendation |
|-------------|----------------|
| Fast random access, frequent adds at end | ArrayList |
| Frequent inserts/deletes in middle | LinkedList |
| Unique elements, no order | HashSet |
| Unique elements, insertion order | LinkedHashSet |
| Unique elements, sorted | TreeSet |
| Key-value, fast lookup | HashMap |
| Key-value, insertion order | LinkedHashMap |
| Key-value, sorted keys | TreeMap |
| Thread-safe Map | ConcurrentHashMap |
| Thread-safe List | CopyOnWriteArrayList |
| Thread-safe Set | ConcurrentHashMap.newKeySet() |
| Producer-consumer queue | ArrayBlockingQueue / LinkedBlockingQueue |

---

## 5. Algorithms (Collections Utility)

```java
Collections.sort(list);                    // Natural order
Collections.sort(list, comparator);        // Custom order
Collections.shuffle(list);                 // Randomize
Collections.reverse(list);                 // Reverse
Collections.frequency(coll, obj);          // Count occurrences
Collections.max(coll); Collections.min(coll);
Collections.binarySearch(list, key);       // Sorted list only
Collections.synchronizedList(list);        // Thread-safe wrapper
Collections.unmodifiableList(list);        // Read-only view
```

---

## 6. Concurrent Collections

| Collection | Use Case |
|------------|----------|
| ConcurrentHashMap | High-concurrency Map |
| ConcurrentSkipListMap | Sorted concurrent Map |
| ConcurrentSkipListSet | Sorted concurrent Set |
| CopyOnWriteArrayList | Rare writes, frequent reads |
| CopyOnWriteArraySet | Thread-safe Set, copy-on-write |
| BlockingQueue implementations | Producer-consumer |
| CompletableFuture | Async composition |

---

## 6. Performance Tips

1. **Pre-size collections**: `new ArrayList<>(expectedSize)` avoids resizing
2. **Use interfaces**: `List<String> list = new ArrayList<>()` not `ArrayList<String>`
3. **Primitive collections**: Use Eclipse Collections / FastUtil for primitives (avoid boxing)
4. **Stream vs for-loop**: Streams have overhead; for-loops faster for simple loops
5. **Parallel streams**: Only for CPU-intensive, large datasets; overhead for small data