# THEORY — Collections Deep Dive

## Overview

The Collections Framework is the cornerstone of Java data manipulation. Understanding its internals enables writing efficient, correct code.

---

## 1. Hierarchy & Design

### Core Interfaces

```
Collection
├── List          → ordered, duplicates allowed
│   ├── ArrayList     → array-backed, O(1) random access
│   ├── LinkedList    → doubly-linked, O(1) insert/remove at ends
│   └── Vector        → synchronized, legacy
├── Set             → no duplicates
│   ├── HashSet       → hash table, O(1) avg
│   ├── LinkedHashSet → insertion order
│   └── TreeSet       → sorted, Red-Black tree
└── Queue/Deque
    ├── PriorityQueue → heap, O(log n)
    ├── ArrayDeque    → array-based deque
    └── LinkedList    → also implements Deque

Map (separate hierarchy)
├── HashMap       → hash table, O(1) avg
├── LinkedHashMap → insertion/access order
├── TreeMap       → sorted, Red-Black tree
├── ConcurrentHashMap → thread-safe, segmented/striped
└── WeakHashMap   → weak keys, auto-cleanup
```

---

## 2. ArrayList vs LinkedList

| Operation | ArrayList | LinkedList |
|-----------|-----------|------------|
| get(index) | O(1) | O(n) |
| add(E) | O(1)* | O(1) |
| add(i, e) | O(n) | O(n) |
| remove(i) | O(n) | O(1)* |
| iterate | Fast (cache-friendly) | Slow |
| Memory | Compact | 2x overhead |

*Amortized

---

## 2. HashMap Internals

### Structure (JDK 8+)

```
HashMap<K,V>
├── Node<K,V>[] table (power of 2)
├── size
├── threshold = size * loadFactor (0.75)
└── modCount
```

### Node Structure (JDK 8+)

```java
static class Node<K,V> implements Entry<K,V> {
    final int hash;
    final K key;
    V value;
    Node<K,V> next;        // linked list or tree
}
```

**Treeify**: When bucket size ≥ 8 (TREEIFY_THRESHOLD) → Red-Black tree
**Untreeify**: When bucket size ≤ 6 (UNTREEIFY_THRESHOLD)

---

## 2. HashMap Deep Dive

### Hash Function

```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

- **Why shift 16?** Mix high bits into low bits for better distribution
- Power-of-2 table size → `hash & (n-1)` for index

### Resize & Transfer

```java
void resize() {
    Node[] newTab = new Node[oldCap << 1];
    for (Node e : oldTable) {
        if (e != null) {
            if (e.next == null)
                newTab[e.hash & (newCap - 1)] = e;
            else if (e instanceof TreeNode)
                ((TreeNode)e).split(this, newTab, oldCap);
            else { // linked list
                // split into lo/hi lists
            }
        }
    }
}
```

---

## 3. ConcurrentHashMap (JDK 8+)

### Segmented → CAS + Synchronized

```java
// JDK 7: Segments (16 locks)
// JDK 8+: CAS + synchronized on first node per bin

static final class Node<K,V> implements Map.Entry<K,V> {
    final int hash;
    final K key;
    volatile V val;
    volatile Node<K,V> next;
}
```

### Key Operations

| Operation | Mechanism |
|-----------|-----------|
| `get` | volatile read, no lock |
| `put` | CAS on head, else synchronized on first node |
| `computeIfAbsent` | CAS loop |
| `compute` | synchronized on bin head |

### Size Counter

```java
// LongAdder-style striped counter
static final class CounterCell {
    volatile long value;
}
long[] counterCells; // striped counter
```

---

## 3. ConcurrentHashMap Deep Dive

### Segment-Free Design (JDK 8+)

```
table[0] → Node → Node (linked list) or TreeNode (tree)
table[1] → null
table[2] → TreeNode (Red-Black tree)
...
```

### Key Operations

| Operation | Mechanism |
|-----------|-----------|
| `get(key)` | volatile read, no lock |
| `put(key, val)` | CAS on bin head → synchronized on bin head |
| `computeIfAbsent` | CAS loop on bin head |
| `size()` | Sum of `baseCount` + sum of `counterCells[]` |

---

## 3. ConcurrentHashMap Internals

### Bin Structure

```
table[0] → Node → Node (linked list)     // size < 8
table[1] → TreeNode (Red-Black tree)     // size ≥ 8, treeified
table[2] → null
```

### Treeification Thresholds

| Threshold | Value |
|-----------|-------|
| TREEIFY_THRESHOLD | 8 |
| UNTREEIFY_THRESHOLD | 6 |

---

## 3. Concurrent Collections

| Collection | Use Case | Mechanism |
|------------|----------|-----------|
| `ConcurrentHashMap` | High-concurrency Map | CAS + synchronized bins |
| `ConcurrentSkipListMap` | Sorted concurrent Map | Skip list |
| `CopyOnWriteArrayList` | Read-heavy, rare writes | Copy-on-write |
| `CopyOnWriteArraySet` | Thread-safe Set | Copy-on-write |
| `ConcurrentLinkedQueue` | Non-blocking queue | CAS on head/tail |
| `BlockingQueue` impls | Producer-consumer | Locks/CAS |
| `LongAdder`/`LongAdder` | High-contention counters | Striped counters |

---

## 4. CopyOnWriteArrayList

### Mechanism

```java
// Write: copy array
public boolean add(E e) {
    final ReentrantLock lock = lock;
    lock.lock();
    try {
        Object[] elements = getArray();
        int len = elements.length;
        Object[] newElements = Arrays.copyOf(elements, len + 1);
        newElements[len] = e;
        setArray(newElements);
        return true;
    } finally {
        lock.unlock();
    }
}

// Read: no lock, volatile array reference
public E get(int index) {
    return getArray()[index];
}
```

### Trade-offs

| Aspect | CopyOnWriteArrayList | ArrayList |
|--------|---------------------|-----------|
| Read | Fast (no lock) | Fast |
| Write | Slow (copy array) | Fast (amortized) |
| Iterator | Snapshot (safe) | Fail-fast |
| Memory | 2x on write | Efficient |

---

## 5. Queue Implementations

| Queue | Ordering | Blocking | Use Case |
|----------|----------|----------|----------|
| `ArrayDeque` | FIFO/LIFO | No | Fast deque |
| `LinkedBlockingQueue` | FIFO | Yes | Producer-consumer |
| `ArrayBlockingQueue` | FIFO | Yes | Bounded buffer |
| `PriorityBlockingQueue` | Priority | Yes | Priority tasks |
| `DelayQueue` | Delay order | Yes | Delayed tasks |
| `SynchronousQueue` | Direct handoff | Yes | Handoff |

---

## 5. BlockingQueue Patterns

### Producer-Consumer

```java
BlockingQueue<Task> queue = new LinkedBlockingQueue<>(100);

// Producer
queue.put(task); // blocks if full

// Consumer
Task task = queue.take(); // blocks if empty
```

### CompletionService

```java
ExecutorCompletionService<Result> ecs = new ExecutorCompletionService<>(executor);
for (Task t : tasks) ecs.submit(t);
for (int i = 0; i < n; i++) {
    Result r = ecs.take().get(); // blocks until next completes
}
```

---

## 5. BlockingQueue Implementations

| Queue | Ordering | Blocking | Use Case |
|--------|----------|----------|----------|
| `ArrayBlockingQueue` | FIFO | Yes | Bounded buffer |
| `LinkedBlockingQueue` | FIFO | Yes | Unbounded (configurable) |
| `PriorityBlockingQueue` | Priority | Yes | Priority tasks |
| `DelayQueue` | Delay order | Yes | Scheduled tasks |
| `SynchronousQueue` | Direct handoff | Yes | Direct handoff |
| `LinkedTransferQueue` | FIFO | Yes | High throughput |