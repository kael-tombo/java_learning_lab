# Quiz — Stack Data Structure (Min Stack)

1. What are the four operations required by LeetCode 155 (Min Stack) and their time complexities?
2. How does the dual-stack approach track the minimum in O(1) time?
3. What is the space complexity of the dual-stack Min Stack implementation?
4. Why do we push `min(currentTop, val)` onto the minStack instead of just the new value?
5. What happens if we call `pop()` on an empty stack in a production implementation?
6. How would you implement Min Stack using only a single stack (space-optimized approach)?
7. Is the dual-stack Min Stack implementation stable for duplicate minimum values?
8. What Java collection class is ideal for implementing a stack and why?
9. How does `ArrayDeque` compare to `Stack` class in Java?
10. Can you implement a queue using two stacks? What would be the amortized time complexity?

---

## Answers

1. **push(val)** O(1), **pop()** O(1), **top()** O(1), **getMin()** O(1)
2. Main stack stores all elements. Auxiliary minStack stores the current minimum at each level. On push, push `min(val, minStack.peek())` onto minStack. `getMin()` just returns `minStack.peek()`.
3. **O(n)** — Both stacks store up to n elements (worst case: monotonically decreasing sequence).
4. This ensures minStack always has the same size as main stack, and `minStack.peek()` always reflects the minimum of all elements currently in the stack.
5. Should throw `NoSuchElementException` (or `EmptyStackException`) — never return a magic value like -1 as that could be a valid element.
6. Single stack storing pairs `(value, currentMin)` or store `(value - min)` with a separate min variable. More complex but saves ~50% space.
7. Yes — using `val <= minStack.peek()` (not `<`) ensures duplicates of the minimum are tracked correctly. Each duplicate gets its own entry in minStack.
8. **`ArrayDeque`** — Not synchronized (faster), implements `Deque` interface, no capacity limit, O(1) for push/pop/peek. `Stack` is legacy, synchronized, extends `Vector`.
9. `ArrayDeque`: no capacity limit, not synchronized, implements Deque, faster. `Stack`: synchronized, legacy, fixed initial capacity, only push/pop/peek.
10. Yes — use `inStack` for enqueue, `outStack` for dequeue. When `outStack` empty, transfer all from `inStack` (reversing order). Amortized O(1) for all operations.