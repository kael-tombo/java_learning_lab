# PriorityQueue & Heap Operations — Exercises

## Exercise 1: Min-Heap from Scratch
Implement a `MinHeap<T extends Comparable<T>>` class backed by an `ArrayList<T>` with:
- `offer(T item)` — O(log n) sift-up
- `poll()` — O(log n) sift-down, returns min
- `peek()` — O(1)
- `size()`, `isEmpty()`
- Dynamic resizing (grow by 1.5×)

**Test**: Insert 1000 random integers, poll all, verify sorted order.

---

## Exercise 2: Merge K Sorted Lists (LeetCode 23)
Implement `mergeKLists(ListNode[] lists)` using a `PriorityQueue<ListNode>`:
- `ListNode` has `int val` and `ListNode next`
- Comparator: `(a, b) -> Integer.compare(a.val, b.val)`
- Handle null/empty lists
- Return merged sorted list

**Test cases**:
- `[[1,4,5],[1,3,4],[2,6]]` → `[1,1,2,3,4,4,5,6]`
- `[]` → `null`
- `[[], [1]]` → `[1]`
- 5 lists of 1000 elements each

---

## Exercise 3: Top K Frequent Elements
Given an integer array `nums` and integer `k`, return the `k` most frequent elements.
- Use `HashMap<Integer, Integer>` to count frequencies
- Use `PriorityQueue<Map.Entry<Integer, Integer>>` with min-heap of size k
- For each entry: if heap size < k, offer; else if entry freq > heap peek freq, poll and offer

**Time**: O(n log k) | **Space**: O(n + k)

**Test**: `nums = [1,1,1,2,2,3], k = 2` → `[1,2]`

---

## Exercise 4: PriorityQueue with Custom Objects
Create a `Task` class with fields: `String name`, `int priority`, `long timestamp`.
- Implement `Comparable<Task>`: higher priority first; if equal, earlier timestamp first (FIFO)
- Create `PriorityQueue<Task>` and submit 20 tasks with random priorities (1-5) and timestamps
- Poll all tasks and verify ordering: priority desc, then timestamp asc

**Challenge**: Modify to use a `Comparator<Task>` instead of `Comparable` — compare both approaches.

---

## Exercise 5: Heap Sort Implementation
Implement in-place heap sort on an `int[]` array using the sift-down procedure:
1. **Heapify**: Build max-heap from array in O(n) by sifting down from last parent to root
2. **Sort**: Repeatedly swap root (max) with last element, reduce heap size, sift down new root

**Signature**: `void heapSort(int[] arr)`

**Test**: Sort arrays of sizes 10, 100, 10000 with random, sorted, reverse-sorted, duplicate-heavy data.
Verify correctness and measure time vs `Arrays.sort()`.

---

## Starter Code Snippets

```java
// ListNode for merge k lists
class ListNode {
    int val;
    ListNode next;
    ListNode() {}
    ListNode(int val) { this.val = val; }
    ListNode(int val, ListNode next) { this.val = val; this.next = next; }
}

// Task for custom comparator
class Task implements Comparable<Task> {
    String name;
    int priority;      // higher = more urgent
    long timestamp;    // lower = earlier

    public Task(String name, int priority, long timestamp) {
        this.name = name; this.priority = priority; this.timestamp = timestamp;
    }

    @Override
    public int compareTo(Task other) {
        int cmp = Integer.compare(other.priority, this.priority); // desc priority
        if (cmp != 0) return cmp;
        return Long.compare(this.timestamp, other.timestamp);     // asc timestamp (FIFO)
    }
}
```

```xml
<!-- JMH for benchmarking heap sort vs Arrays.sort -->
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-core</artifactId>
    <version>1.37</version>
</dependency>
```

---

## Reflection Questions
1. Why is `PriorityQueue` not suitable for "decrease-key" operations (e.g., Dijkstra)? What alternative?
2. How does `PriorityQueue`'s array-based heap avoid memory fragmentation vs. pointer-based trees?
3. In merge k lists, why not just collect all N values, sort, and rebuild? (Time/space tradeoff)
4. What happens if you mutate a `Task`'s priority while it's in the queue?