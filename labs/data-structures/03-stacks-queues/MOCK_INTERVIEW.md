# Mock Interview: Stacks and Queues

## Q1 — Valid Parentheses (LC 20)

**Problem.** Decide whether a bracket string is correctly nested.
**Key insight.** Push openers; each closer must match the stack top; leftovers fail.
**Complexity.** Time O(n), space O(n).

```java
import java.util.ArrayDeque;
import java.util.Deque;
public class StacksQueuesQ1 {
    static boolean valid(String s) {
        Deque<Character> st = new ArrayDeque<>();
        for (char c : s.toCharArray()) {
            if (c == '(' || c == '[' || c == '{') st.push(c);
            else if (st.isEmpty()) return false;
            else { char o = st.pop();
                if ((c == ')' && o != '(') || (c == ']' && o != '[') || (c == '}' && o != '{')) return false; }
        }
        return st.isEmpty();
    }
    public static void main(String[] args) {
        System.out.println(valid("()[]{}"));
        System.out.println(valid("(]"));
    }
}
```

Output:

```
true
false
```

## Q2 — Min Stack (LC 155)

**Problem.** Stack with push/pop/top/getMin, each O(1).
**Key insight.** Parallel stack of running minima: push `min(x, current min)` alongside `x`.
**Complexity.** Time O(1) per op, space O(n).

```java
import java.util.ArrayDeque;
import java.util.Deque;
public class StacksQueuesQ2 {
    public static void main(String[] args) {
        Deque<Integer> st = new ArrayDeque<>(), mn = new ArrayDeque<>();
        int[] xs = {3, 1, 2};
        for (int x : xs) { st.push(x); mn.push(mn.isEmpty() ? x : Math.min(x, mn.peek())); }
        System.out.println(mn.peek());
        st.pop(); mn.pop(); st.pop(); mn.pop();
        System.out.println(mn.peek());
    }
}
```

Output:

```
1
3
```

## Q3 — Queue with Two Stacks (LC 232)

**Problem.** Implement FIFO with two LIFO stacks.
**Key insight.** Push to inbox; pop lazily drains inbox to outbox (reversing order). Each element moves at most twice per drain: amortized O(1).
**Complexity.** Amortized O(1) per op, space O(n).

```java
import java.util.ArrayDeque;
import java.util.Deque;
public class StacksQueuesQ3 {
    public static void main(String[] args) {
        Deque<Integer> in = new ArrayDeque<>(), out = new ArrayDeque<>();
        for (int x : new int[]{1, 2, 3}) in.push(x);
        for (int k = 0; k < 2; k++) {
            if (out.isEmpty()) while (!in.isEmpty()) out.push(in.pop());
            System.out.println(out.pop());
        }
    }
}
```

Output:

```
1
2
```
