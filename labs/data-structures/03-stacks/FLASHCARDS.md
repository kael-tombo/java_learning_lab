# Flashcards — Stack Data Structure (Min Stack)

- Q: Min Stack operations & time? → A: push/pop/top/getMin all O(1)
- Q: Dual-stack min tracking? → A: Main stack + minStack storing min at each level
- Q: Min Stack space? → A: O(n) — both stacks up to n elements
- Q: Why min(currentMin, val)? → A: Keeps minStack same size, peek() always returns global min
- Q: Empty stack pop? → A: Throw NoSuchElementException
- Q: Single-stack Min Stack? → A: Store (value, currentMin) pairs or (value - min) with separate min var
- Q: Duplicate minima handled? → A: Yes, use <= when pushing to minStack
- Q: Best Java stack implementation? → A: ArrayDeque — unsynchronized, Deque interface, no capacity limit
- Q: ArrayDeque vs Stack? → A: ArrayDeque faster, not synchronized, no legacy baggage
- Q: Queue from two stacks? → A: inStack for enqueue, outStack for dequeue; amortized O(1)
- Q: Stack LIFO principle? → A: Last In, First Out — last pushed, first popped
- Q: Stack use cases? → A: Function calls, undo/redo, expression evaluation, backtracking, syntax parsing
- Q: Min Stack getMin() implementation? → A: return minStack.peek()
- Q: When to use ArrayDeque over LinkedList for stack? → A: ArrayDeque has better cache locality, lower memory overhead