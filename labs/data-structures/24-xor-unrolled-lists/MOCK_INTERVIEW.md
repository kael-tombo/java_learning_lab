# Mock Interview: XOR and Unrolled Linked Lists

## Q1 — Unrolled List Blocking

**Problem.** Store a list in fixed-capacity blocks (nodes holding up to B elements).

**Key insight.** Blocking cuts pointer overhead to one per B elements and makes scans cache-friendly: sequential elements sit contiguously. Insert shifts within one block, splitting it when full.

**Complexity.** Index O(n/B) blocks; scan O(n) with far fewer cache misses; insert O(B) shifts.

```java
import java.util.ArrayList;
import java.util.List;

public class XorListQ1 {
    public static void main(String[] args) {
        int B = 4;
        List<List<Integer>> blocks = new ArrayList<>();
        int[] data = {1, 2, 3, 4, 5, 6};
        for (int x : data) {
            if (blocks.isEmpty() || blocks.get(blocks.size() - 1).size() == B) {
                blocks.add(new ArrayList<>());
            }
            blocks.get(blocks.size() - 1).add(x);
        }
        System.out.println("blocks=" + blocks.size());
        System.out.println(blocks.get(0).size() + "," + blocks.get(1).size());
    }
}
```

Output:

```
blocks=2
4,2
```

## Q2 — XOR Link Traversal Idea

**Problem.** How can a doubly linked list store one pointer per node instead of two?

**Key insight.** Store `prev XOR next` in a single field. Traversing with the previous address recovers next as `link XOR prev`. It saves memory but defeats garbage collectors and debuggers, which is why it stays a C-level trick.

**Complexity.** Same O(1)/O(n) asymptotics as a doubly linked list; traversal is strictly sequential from a known endpoint.

```java
public class XorListQ2 {
    public static void main(String[] args) {
        int[] addr = {1000, 2000, 3000};
        int[] link = new int[3];
        link[0] = 0 ^ addr[1];
        link[1] = addr[0] ^ addr[2];
        link[2] = addr[1] ^ 0;
        int prev = 0, cur = addr[0];
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 3; i++) {
            sb.append(cur).append(" ");
            int nxt = link[i] ^ prev;
            prev = cur;
            cur = nxt;
        }
        System.out.print(sb.toString().trim());
        System.out.println();
    }
}
```

Output:

```
1000 2000 3000
```

## Q3 — Cache Locality Comparison

**Problem.** Why does an unrolled list scan faster than a pointer-chased list despite identical big-O?

**Key insight.** Each cache line fetched for an unrolled block yields B usable elements; a node-per-element list wastes most of each fetched line on pointers and may jump lines per element. Constants matter between equal big-Os.

**Complexity.** Both O(n) scan; unrolled does ~n/B pointer hops vs n.

```java
public class XorListQ3 {
    public static void main(String[] args) {
        int n = 1000, B = 16;
        System.out.println("plain-hops=" + n);
        System.out.println("unrolled-hops=" + (n + B - 1) / B);
    }
}
```

Output:

```
plain-hops=1000
unrolled-hops=63
```
