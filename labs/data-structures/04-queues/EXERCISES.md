# Exercises — Queue Data Structure (Circular Queue)

## Beginner

1. **Implement Circular Queue with Array (Fixed Capacity)**
   - Implement all 7 operations: `enQueue`, `deQueue`, `Front`, `Rear`, `isEmpty`, `isFull`, constructor.
   - Use the `size` variable approach to distinguish empty/full.
   - Test wrap-around behavior.

2. **Implement Circular Queue — Wasted Slot Approach**
   - Implement without `size` variable; waste one array slot.
   - Full when `(tail + 1) % capacity == head`.
   - Compare code simplicity with size-based approach.

3. **Implement Queue using Two Stacks (LeetCode 232)**
   - Implement `MyQueue` with `push`, `pop`, `peek`, `empty`.
   - Amortized O(1) for all operations.

## Intermediate

4. **Design Circular Deque (LeetCode 641)**
   - Support insert/delete at both front and rear.
   - Operations: `insertFront`, `insertLast`, `deleteFront`, `deleteLast`, `getFront`, `getRear`, `isEmpty`, `isFull`.

5. **Sliding Window Maximum (LeetCode 239)**
   - Given array and window size k, find max in each window.
   - Use monotonic decreasing deque (store indices).
   - O(n) time, O(k) space.

6. **Implement Circular Queue with Linked List**
   - No fixed capacity. Nodes with `next` pointers.
   - Compare memory/performance with array version.

## Advanced

7. **Max Queue (LeetCode Offer II 041 / 剑指 Offer II 041)**
   - Design queue supporting `max_value`, `push_back`, `pop_front` all in O(1) amortized.
   - Use main queue + monotonic decreasing deque for max tracking.

8. **Number of Recent Calls (LeetCode 933)**
   - `RecentCounter` class: `ping(t)` returns calls in [t-3000, t].
   - Use queue to maintain sliding window of timestamps.

9. **Shortest Subarray with Sum at Least K (LeetCode 862)**
   - Given array (can have negatives), find shortest subarray with sum ≥ K.
   - Use prefix sums + monotonic increasing deque.
   - O(n) time.

10. **Circular Queue with Dynamic Resizing**
    - Implement circular queue that doubles capacity when full.
    - Maintain O(1) amortized enqueue.
    - Handle head/tail repositioning during resize.