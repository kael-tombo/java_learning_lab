# Mathematical Foundation — Queue Data Structure (Circular Queue)

## 1. Queue Abstract Data Type

A **queue** is a linear data structure following **FIFO** (First In, First Out) principle.

### Core Operations
| Operation | Description | Time Complexity |
|-----------|-------------|-----------------|
| `enQueue(x)` / `push(x)` | Add element to rear | O(1) |
| `deQueue()` / `pop()` | Remove and return front element | O(1) |
| `Front()` / `peek()` | Return front element without removing | O(1) |
| `Rear()` | Return rear element without removing | O(1) |
| `isEmpty()` | Check if queue is empty | O(1) |
| `isFull()` | Check if queue is at capacity | O(1) |

---

## 2. Circular Queue (Ring Buffer) — Array Implementation

### Structure
Fixed-size array with two pointers (or indices):

```
capacity = 8
indices:  0  1  2  3  4  5  6  7
data:    [E][F][G][H][A][B][C][D]
              ↑           ↑
            head        tail
size = 4
```

- `head`: Index of front element (oldest)
- `tail`: Index of **next insertion slot** (after rear)
- `size`: Current number of elements (0 ≤ size ≤ capacity)

### Empty/Full Ambiguity — Two Solutions

#### Solution 1: Track `size` Explicitly (Recommended)
```
Empty:  size == 0
Full:   size == capacity
head/tail can be equal in both cases — size disambiguates.
```

#### Solution 2: Waste One Slot
```
Empty:  head == tail
Full:   (tail + 1) % capacity == head
Actual capacity = array.length - 1
```

### Operations (Size-Based Approach)

```java
// Enqueue: add at tail, advance tail
boolean enQueue(int value) {
    if (isFull()) return false;
    data[tail] = value;
    tail = (tail + 1) % capacity;
    size++;
    return true;
}

// Dequeue: advance head, return old head
boolean deQueue() {
    if (isEmpty()) return false;
    head = (head + 1) % capacity;
    size--;
    return true;
}

// Front: element at head
int Front() {
    if (isEmpty()) return -1;
    return data[head];
}

// Rear: element before tail (with wrap)
int Rear() {
    if (isEmpty()) return -1;
    int rearIndex = (tail - 1 + capacity) % capacity;
    return data[rearIndex];
}
```

---

## 3. Complexity Analysis

### Time Complexity
| Operation | Array (Fixed) | Array (Dynamic) | Linked List | ArrayDeque |
|-----------|---------------|-----------------|-------------|------------|
| enQueue | O(1) | O(1)* | O(1) | O(1)* |
| deQueue | O(1) | O(1) | O(1) | O(1) |
| Front/Rear | O(1) | O(1) | O(1) | O(1) |
| isEmpty/isFull | O(1) | O(1) | O(1) | O(1) |

*Amortized for dynamic array / ArrayDeque

### Space Complexity
| Implementation | Space | Overhead |
|----------------|-------|----------|
| Fixed Array | O(capacity) | Minimal |
| Dynamic Array / ArrayDeque | O(n) | ~2× during resize |
| Linked List | O(n) | Pointer per node (~2-3×) |

---

## 4. Amortized Analysis — Dynamic Array / ArrayDeque

### Resize Strategy
When full, allocate new array of size `2 × capacity`, copy elements.

### Aggregate Analysis
For n enqueue operations starting from capacity 1:
- Capacities: 1, 2, 4, 8, ..., 2^k where 2^k ≥ n
- Copies per resize: 1 + 2 + 4 + ... + 2^(k-1) = 2^k - 1 < 2n
- Total operations: n enqueues + < 2n copies < 3n
- **Amortized O(1) per enqueue**

### Potential Function Method
Define potential Φ = 2 × size - capacity (after resize, Φ = 0).
- Normal enqueue: actual cost = 1, ΔΦ = +2 → amortized = 3
- Resize enqueue: actual cost = size + 1, ΔΦ = 2 - capacity = 2 - 2×size = 2(1-size) → amortized = 3
- Dequeue: actual cost = 1, ΔΦ = -2 → amortized = -1 (but never negative total)

---

## 5. ArrayDeque Internal Structure (Java)

### Circular Array Layout
```
Internal array: [ ][ ][C][D][E][A][B]
                  ↑       ↑
                head    tail
```

### Key Fields (simplified)
```java
transient Object[] elements;
transient int head;    // index of first element
transient int tail;    // index of next insertion slot
```

### Core Operations
```java
// push (addFirst)
public void push(E e) {
    if (head == 0) head = elements.length;
    elements[--head] = e;
    if (head == tail) doubleCapacity();
}

// pop (removeFirst)
public E pop() {
    int h = head;
    E result = (E) elements[h];
    elements[h] = null;
    head = (h + 1) & (elements.length - 1); // modulo power of 2
    return result;
}
```

### Power-of-2 Capacity Optimization
- Capacity always power of 2
- Modulo: `index & (capacity - 1)` instead of `% capacity`
- Bitwise AND is faster than modulo

---

## 6. Monotonic Queue — Advanced Applications

### Definition
A deque maintaining elements in **monotonic order** (increasing or decreasing).

### Sliding Window Maximum (LeetCode 239)
```java
Deque<Integer> deque = new ArrayDeque<>(); // stores indices
for (int i = 0; i < n; i++) {
    // Remove indices outside window
    while (!deque.isEmpty() && deque.peek() < i - k + 1)
        deque.poll();

    // Maintain decreasing order
    while (!deque.isEmpty() && nums[deque.peekLast()] < nums[i])
        deque.pollLast();

    deque.offer(i);

    if (i >= k - 1) result.add(nums[deque.peek()]);
}
```

### Time Complexity Proof
Each index enters and leaves deque at most once.
- Total `offer`: n
- Total `poll`/`pollLast`: ≤ n
- **Total: O(n)**

### Space Complexity
Deque holds at most k elements (window size).
- **O(k)** space

---

## 7. Queue from Two Stacks

### Structure
```
inStack:  [new] → [ ] → [old]     // push here
outStack: [old] → [ ] → [new]     // pop from here
```

### Transfer Operation
When outStack empty:
```
while (!inStack.isEmpty()) {
    outStack.push(inStack.pop());
}
```
Reverses order: FIFO behavior achieved.

### Amortized Analysis
Each element:
- Pushed to inStack: 1 time
- Popped from inStack: 1 time (during transfer)
- Pushed to outStack: 1 time (during transfer)
- Popped from outStack: 1 time

**4 stack operations per queue element → Amortized O(1)**

---

## 8. Priority Queue vs Regular Queue

| Aspect | Queue (FIFO) | Priority Queue |
|--------|--------------|----------------|
| Order | Insertion order | Priority order (min/max) |
| enQueue | O(1) | O(log n) |
| deQueue | O(1) | O(log n) |
| peek | O(1) | O(1) |
| Use case | BFS, buffering | Dijkstra, Huffman, scheduling |

---

## 9. Applications Summary

| Application | Queue Type | Why Queue? |
|-------------|------------|------------|
| BFS | Regular queue | Level-order traversal |
| Task Scheduling | Priority queue | Execute by priority |
| Print Spooler | Regular queue | Fairness (FIFO) |
| Rate Limiting | Circular queue | Fixed window, O(1) |
| Sliding Window Max | Monotonic deque | O(n) vs O(nk) |
| Recent Requests | Queue + timestamps | Auto-expire old entries |
| Buffering (I/O) | Circular queue | Fixed memory, overwrite old |

---

## 10. Java Best Practices

### Use `ArrayDeque` for Most Cases
```java
// Queue
Queue<Integer> q = new ArrayDeque<>();
q.offer(1); q.poll(); q.peek();

// Deque (both ends)
Deque<Integer> dq = new ArrayDeque<>();
dq.addFirst(1); dq.addLast(2);
dq.removeFirst(); dq.removeLast();
```

### Avoid
- `LinkedList` for queue/stack (poor cache, memory overhead)
- `Stack` class (legacy, synchronized)
- `Vector` (synchronized, legacy)

### Thread-Safe Alternative
```java
// For concurrent access
BlockingQueue<Integer> q = new ArrayBlockingQueue<>(capacity);
q.put(1); q.take(); // blocking
q.offer(1); q.poll(); // non-blocking
```