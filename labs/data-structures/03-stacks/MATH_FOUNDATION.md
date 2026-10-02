# Mathematical Foundation — Stack Data Structure

## 1. Stack Abstract Data Type

A **stack** is a linear data structure following **LIFO** (Last In, First Out) principle.

### Core Operations
| Operation | Description | Time Complexity |
|-----------|-------------|-----------------|
| `push(x)` | Add element x to top | O(1) |
| `pop()` | Remove and return top element | O(1) |
| `top()` / `peek()` | Return top element without removing | O(1) |
| `isEmpty()` | Check if stack is empty | O(1) |
| `size()` | Return number of elements | O(1) |

---

## 2. Implementation Analysis

### Array-Based Stack (Dynamic Array / ArrayDeque)

**Structure**: Contiguous memory with `top` index.

```
[ ][ ][ ][A][B][C]  top=5
     ↑           ↑
   bottom      top
```

**Operations**:
- `push`: `data[top++] = x` — O(1) amortized (resize when full)
- `pop`: `return data[--top]` — O(1)
- `peek`: `return data[top-1]` — O(1)

**Space**: O(n) where n = current size. Capacity may be larger (typically 2× when resizing).

**Amortized Analysis of Push**:
- Resize doubles capacity: 1 → 2 → 4 → 8 → ... → n
- Total copies for n pushes: n + n/2 + n/4 + ... < 2n
- **Amortized O(1)** per push

### Linked List Stack

**Structure**: Head pointer to top node.

```
top → [C] → [B] → [A] → null
```

**Operations**: All O(1) worst-case (no resizing).
**Space**: O(n) + pointer overhead (~2× array).

---

## 3. Min Stack — Mathematical Analysis

### Dual-Stack Approach

Let `S` be the main stack, `M` be the minStack.

**Invariant**: After each operation, `M.peek() = min(S)`.

**Push(x)**:
```
S.push(x)
if M.isEmpty() or x ≤ M.peek():
    M.push(x)
else:
    M.push(M.peek())
```

**Proof of Correctness**:
By induction on number of operations.
- Base: Empty stacks, invariant holds vacuously.
- Push(x): New min is `min(x, old_min)`. We push exactly this value to M.
- Pop: Both stacks pop together, invariant preserved for remaining elements.

**Space Complexity**: O(n) — M has exactly same size as S.
- Worst case (monotonically decreasing): M stores all elements
- Best case (monotonically increasing): M stores all elements (all equal to first)
- Average: M stores ~n elements

### Single-Stack Space-Optimized Approach

Store pairs `(value, currentMin)` or use encoding:

**Pair Approach**:
```
Stack<Pair<Integer, Integer>> stack;
push(x): stack.push(new Pair(x, stack.isEmpty() ? x : Math.min(x, stack.peek().second)));
getMin(): return stack.peek().second;
```

**Space**: O(n) pairs = 2n integers. Same asymptotic, ~2× memory of dual-stack.

**Delta Encoding** (theoretical):
Store `x - min` when new min encountered.
```
min = INF
push(x):
    if x < min:
        stack.push(x - min)  // negative value signals new min
        min = x
    else:
        stack.push(x)
```
Complex to implement correctly with all operations. Rarely used in practice.

---

## 4. Monotonic Stack — Advanced Applications

### Definition
A **monotonic stack** maintains elements in strictly increasing or decreasing order.

### Increasing Monotonic Stack (Next Smaller Element)
```java
Deque<Integer> stack = new ArrayDeque<>(); // stores indices
for (int i = 0; i < n; i++) {
    while (!stack.isEmpty() && arr[stack.peek()] > arr[i]) {
        int idx = stack.pop();
        // arr[i] is next smaller element to the right of arr[idx]
    }
    stack.push(i);
}
```

### Decreasing Monotonic Stack (Next Greater Element)
```java
while (!stack.isEmpty() && arr[stack.peek()] < arr[i]) {
    int idx = stack.pop();
    // arr[i] is next greater element to the right
}
```

### Complexity
**Time**: O(n) — Each element pushed and popped at most once.
**Space**: O(n) — Stack size ≤ n.

### Classic Problems

| Problem | Stack Type | Key Insight |
|---------|------------|-------------|
| Next Greater Element | Decreasing | Pop when current > stack top |
| Next Smaller Element | Increasing | Pop when current < stack top |
| Largest Rectangle in Histogram | Increasing | Width = right_smaller - left_smaller - 1 |
| Trapping Rain Water | Decreasing | Water trapped between walls |
| Daily Temperatures | Decreasing (indices) | Distance to next warmer day |

---

## 5. Stack in Algorithm Design

### Recursion → Stack Conversion
Every recursive algorithm can be converted to iterative using explicit stack.

**Recursion**:
```java
void dfs(node) {
    visit(node);
    for (child : node.children) dfs(child);
}
```

**Iterative with Stack**:
```java
Stack<Node> stack = new Stack<>();
stack.push(root);
while (!stack.isEmpty()) {
    Node n = stack.pop();
    visit(n);
    for (child : n.children) stack.push(child);
}
```

**Space Equivalence**: Both use O(depth) space. Iterative avoids call stack limits.

### Expression Evaluation
**Infix → Postfix (Shunting Yard)**:
- Operands → output
- Operators → stack (by precedence)
- Parentheses control grouping

**Postfix Evaluation**:
- Operands → push
- Operator → pop 2, compute, push result

---

## 6. Queue from Two Stacks

### Structure
```
inStack:  [newest] → [older] → [oldest]   (push here)
outStack: [oldest] → [older] → [newest]   (pop from here)
```

### Operations
```java
void push(int x) {
    inStack.push(x);
}

int pop() {
    if (outStack.isEmpty()) {
        while (!inStack.isEmpty()) {
            outStack.push(inStack.pop());
        }
    }
    return outStack.pop();
}
```

### Amortized Analysis
- Each element moved from inStack to outStack **at most once**.
- n operations: n pushes + n pops + n transfers = 3n stack operations.
- **Amortized O(1)** per queue operation.

---

## 7. Complexity Summary

| Implementation | push | pop | peek | space | notes |
|----------------|------|-----|------|-------|-------|
| ArrayDeque (Java) | O(1)* | O(1) | O(1) | O(n) | *amortized, cache-friendly |
| LinkedList | O(1) | O(1) | O(1) | O(n) | pointer overhead |
| Array (fixed) | O(1) | O(1) | O(1) | O(cap) | capacity limit |
| Dual Min Stack | O(1) | O(1) | O(1) | O(n) | getMin O(1) |
| Pair Min Stack | O(1) | O(1) | O(1) | O(n) | single stack |

---

## 8. Real-World Applications

1. **Call Stack**: Function call management (return addresses, local variables)
2. **Undo/Redo**: Command pattern with history stacks
3. **Browser History**: Back/forward navigation
4. **Expression Parsing**: Compiler syntax analysis
5. **Backtracking**: DFS, maze solving, N-Queens
6. **Memory Management**: Stack allocation in runtime systems
7. **Matching Algorithms**: Parentheses, HTML tags, regex

---

## 9. Java Implementation Notes

### ArrayDeque vs Stack vs LinkedList
```java
// Recommended: ArrayDeque
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);
stack.pop();
stack.peek();

// Legacy: Stack (extends Vector, synchronized)
Stack<Integer> legacy = new Stack<>();
legacy.push(1);

// Not recommended for stack: LinkedList
// Implements Deque but higher overhead
```

### Performance Characteristics
- **ArrayDeque**: Circular array, no synchronization, cache-friendly, O(1) amortized
- **Stack**: Synchronized (thread-safe but slower), extends Vector (legacy)
- **LinkedList**: Node allocation per element, poor cache locality, implements Deque

**Best Practice**: Use `ArrayDeque` for stack/queue in single-threaded code.