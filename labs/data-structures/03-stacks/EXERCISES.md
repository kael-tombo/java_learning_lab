# Exercises — Stack Data Structure (Min Stack)

## Beginner

1. **Implement basic Stack using ArrayDeque**
   - Implement `push`, `pop`, `peek`, `isEmpty`, `size`.
   - Write tests for LIFO behavior.

2. **Implement Min Stack (dual-stack approach)**
   - Implement all four operations: `push`, `pop`, `top`, `getMin`.
   - Handle edge cases: empty stack exceptions, duplicate minimums.

3. **Valid Parentheses (LeetCode 20)**
   - Given a string of parentheses `()[]{}`, determine if valid.
   - Use stack to match opening/closing brackets.

## Intermediate

4. **Min Stack — Space-Optimized (Single Stack)**
   - Implement Min Stack using only one stack storing `(value, currentMin)` pairs.
   - Compare memory usage with dual-stack approach.

5. **Evaluate Reverse Polish Notation (LeetCode 150)**
   - Evaluate arithmetic expression in postfix notation.
   - Operators: `+`, `-`, `*`, `/`. Operands: integers.

6. **Daily Temperatures (LeetCode 739)**
   - Given daily temperatures, return days until warmer temperature.
   - Use monotonic decreasing stack (store indices).

## Advanced

7. **Largest Rectangle in Histogram (LeetCode 84)**
   - Given bar heights, find area of largest rectangle.
   - Use monotonic increasing stack to find next smaller element on left/right.

8. **Trapping Rain Water (LeetCode 42)**
   - Given elevation map, compute trapped water.
   - Use two-pointer or stack approach.

9. **Implement Queue using Two Stacks (LeetCode 232)**
   - Implement `MyQueue` with `push`, `pop`, `peek`, `empty`.
   - Amortized O(1) for all operations.

10. **Max Stack (LeetCode 716)**
    - Design stack supporting `push`, `pop`, `top`, `peekMax`, `popMax`.
    - `popMax` removes and returns the maximum element.
    - Use double-linked list + tree map or two stacks.