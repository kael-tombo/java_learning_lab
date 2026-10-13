# Mock Interview: Circular Buffers

## Q1 — Ring Buffer with Full/Empty Disambiguation

**Problem.** Fixed-capacity FIFO where head == tail is ambiguous.
**Key insight.** Keep an explicit `size`: empty iff 0, full iff capacity. Indices wrap with modulo.
**Complexity.** O(1) offer/poll, O(capacity) space.

```java
public class CircularQ1 {
    static int[] a = new int[3];
    static int head, size;
    static boolean offer(int x) {
        if (size == a.length) return false;
        a[(head + size++) % a.length] = x;
        return true;
    }
    static int poll() { int x = a[head]; head = (head + 1) % a.length; size--; return x; }
    public static void main(String[] args) {
        offer(1); offer(2); offer(3);
        System.out.println(offer(4));
        System.out.println("" + poll() + poll());
        offer(5);
        System.out.println("" + poll() + poll());
    }
}
```

Output:

```
false
12
35
```

## Q2 — Overwrite-Oldest Telemetry Ring

**Problem.** Keep the last N sensor readings, overwriting the oldest.
**Key insight.** Offer on a full buffer advances head instead of failing; read order is head..head+size-1 mod capacity.
**Complexity.** O(1) record, O(N) snapshot.

```java
public class CircularQ2 {
    public static void main(String[] args) {
        int cap = 3, head = 0, size = 0;
        int[] a = new int[cap];
        for (int x : new int[]{10, 20, 30, 40}) {
            if (size < cap) a[(head + size++) % cap] = x;
            else { a[head] = x; head = (head + 1) % cap; }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < size; i++) sb.append(a[(head + i) % cap]).append(" ");
        System.out.print(sb.toString().trim());
        System.out.println();
    }
}
```

Output:

```
20 30 40
```

## Q3 — Sliding-Window Moving Average

**Problem.** Maintain the mean of the last k stream values.
**Key insight.** Running sum plus ring: subtract the evicted value, add the new one. No re-summing.
**Complexity.** O(1) per value, O(k) space.

```java
public class CircularQ3 {
    public static void main(String[] args) {
        int k = 3, idx = 0, n = 0;
        int[] buf = new int[k];
        long sum = 0;
        for (int x : new int[]{1, 10, 3, 5}) {
            if (n == k) sum -= buf[idx]; else n++;
            buf[idx] = x; idx = (idx + 1) % k; sum += x;
            System.out.printf("%.2f%n", sum / (double) n);
        }
    }
}
```

Output:

```
1.00
5.50
4.67
6.00
```
