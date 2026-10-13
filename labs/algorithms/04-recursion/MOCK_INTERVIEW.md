# Mock Interview: Recursion: Base Cases, Traces, Depth Limits
> Three worked questions on recursive thinking. Each answer is complete runnable Java; outputs below were observed.

## Q1: Compute a factorial recursively and count the calls.
Key insight: Every recursive function needs a base case that shrinks the argument: fact(n) = n * fact(n-1) with fact(1) = 1. Counting calls makes the linear call depth visible.
Complexity: Time O(n); stack space O(n).
```java
public class L04Q1Fact {
    static int calls = 0;
    static long fact(int n) { calls++; return n <= 1 ? 1 : n * fact(n - 1); }
    public static void main(String[] args) {
        System.out.println("fact(6)=" + fact(6) + " calls=" + calls);
    }
}
```
Observed output: `fact(6)=720 calls=6`
Follow-up: At what n does fact overflow a long, and how would you detect it instead of wrapping?

## Q2: Compute x^n with binary (divide-and-conquer) recursion.
Key insight: Halving the exponent - x^n = (x^2)^(n/2) for even n - turns n multiplications into log n. The recursion tree has one path of length log n, not n levels.
Complexity: Time O(log n) multiplications; stack O(log n).
```java
public class L04Q2Pow {
    static long pw(long x, long n) {
        return n == 0 ? 1 : (n % 2 == 0 ? pw(x * x, n / 2) : x * pw(x, n - 1));
    }
    public static void main(String[] args) {
        System.out.println("2^16=" + pw(2, 16) + " 3^5=" + pw(3, 5));
    }
}
```
Observed output: `2^16=65536 3^5=243`
Follow-up: Why is the odd case x * pw(x, n-1) still O(log n) overall rather than O(n)?

## Q3: Count Tower of Hanoi moves for 3 disks without printing every move.
Key insight: Moving n disks needs the top n-1 moved away, the big disk moved once, then n-1 moved back: M(n) = 2*M(n-1) + 1, so M(n) = 2^n - 1. The recurrence itself is the proof of exponential cost.
Complexity: Time and moves Theta(2^n); stack O(n).
```java
public class L04Q3Hanoi {
    static int moves = 0;
    static void h(int n, char a, char b, char c) {
        if (n == 0) return;
        h(n - 1, a, c, b);
        moves++;
        h(n - 1, b, a, c);
    }
    public static void main(String[] args) {
        h(3, 'A', 'C', 'B');
        System.out.println("hanoi(3) moves=" + moves);
    }
}
```
Observed output: `hanoi(3) moves=7`
Follow-up: Solve M(n) = 2*M(n-1) + 1 with M(0) = 0 by unrolling three levels to guess the closed form.

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
