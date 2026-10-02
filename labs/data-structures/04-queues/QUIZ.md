# Quiz — Queue Data Structure (Circular Queue)

1. What are the seven operations required by LeetCode 622 (Design Circular Queue) and their time complexities?
2. How does a circular queue (ring buffer) differ from a linear queue?
3. What is the key challenge in distinguishing empty vs full state in a circular queue?
4. What are the two common approaches to handle the empty/full ambiguity?
5. In the array-based implementation, what do `head`, `tail`, and `size` represent?
6. Why is `ArrayDeque` a better choice than `LinkedList` for queue implementation in Java?
7. What is the amortized time complexity of `ArrayDeque` operations?
8. How would you implement a circular queue using a linked list?
9. What is the difference between a circular queue and a deque (double-ended queue)?
10. In the LeetCode 622 solution, why do we use `(tail + 1) % capacity` for enqueue and `(head + 1) % capacity` for dequeue?

---

## Answers

1. **enQueue(value)** O(1), **deQueue()** O(1), **Front()** O(1), **Rear()** O(1), **isEmpty()** O(1), **isFull()** O(1), **constructor** O(k). All O(1).
2. Circular queue wraps around when reaching end of array — no need to shift elements. Linear queue requires shifting or wastes space.
3. When `head == tail`, the queue could be empty OR full (if we just filled the last slot). Both states have same pointer positions.
4. **Approach 1**: Waste one slot — queue is full when `(tail + 1) % capacity == head`. **Approach 2**: Track `size` separately — full when `size == capacity`, empty when `size == 0`.
5. `head` = index of front element, `tail` = index of next insertion slot (after rear), `size` = current number of elements.
6. `ArrayDeque`: circular array, cache-friendly, no synchronization, no node allocation. `LinkedList`: node allocation per element, poor cache, more memory overhead.
7. **O(1) amortized** — resizing doubles capacity, total copies < 2n for n operations.
8. Maintain `head` and `tail` pointers to nodes. Enqueue adds after tail, dequeue removes head. No capacity limit but more memory per element.
9. Circular queue: fixed capacity, FIFO only. Deque: supports both ends, typically dynamic capacity (ArrayDeque).
10. Modulo arithmetic wraps indices around the array boundary, implementing the "circular" behavior without conditional branches for wrap-around.