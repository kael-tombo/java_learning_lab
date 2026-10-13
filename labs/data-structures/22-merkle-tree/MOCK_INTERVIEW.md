# Mock Interview: Merkle Trees

## Q1 — Root Hash Aggregation

**Problem.** Summarize a list of blocks with one tamper-evident digest.

**Key insight.** Hash leaves, then hash concatenated child pairs level by level. Any changed byte flips the root; equal roots mean equal content (up to hash collisions).

**Complexity.** Build O(n) hashes; root compare O(1).

```java
import java.security.MessageDigest;

public class MerkleQ1 {
    static String sha(String s) throws Exception {
        byte[] d = MessageDigest.getInstance("SHA-256").digest(s.getBytes("UTF-8"));
        StringBuilder sb = new StringBuilder();
        for (byte b : d) sb.append(String.format("%02x", b));
        return sb.toString();
    }

    public static void main(String[] args) throws Exception {
        String[] blocks = {"a", "b", "c", "d"};
        String[] level = new String[4];
        for (int i = 0; i < 4; i++) level[i] = sha(blocks[i]);
        while (level.length > 1) {
            String[] next = new String[level.length / 2];
            for (int i = 0; i < next.length; i++) {
                next[i] = sha(level[2 * i] + level[2 * i + 1]);
            }
            level = next;
        }
        System.out.println(level[0].substring(0, 16));
        System.out.println(level[0].length());
    }
}
```

Output:

```
58c89d709329eb37
64
```

## Q2 — Inclusion Proof in O(log n)

**Problem.** Prove block i belongs to a committed root without revealing all blocks.

**Key insight.** Reveal only the sibling hash at each level (log n hashes); the verifier re-hashes up to the root and compares. Used by package transparency logs and blockchains.

**Complexity.** Proof size and verify time O(log n).

```java
public class MerkleQ2 {
    public static void main(String[] args) {
        int leaves = 8, h = 0;
        for (int s = leaves; s > 1; s /= 2) h++;
        System.out.println(h);
        System.out.println("sibling-of-node-5-at-width-8");
    }
}
```

Output:

```
3
sibling-of-node-5-at-width-8
```

## Q3 — Tamper Detection

**Problem.** Show that flipping one block changes the root.

**Key insight.** The leaf hash changes, and since every ancestor hashes its children, the difference propagates to the root. Comparison of one digest detects corruption anywhere.

**Complexity.** O(1) detect via roots; O(log n) to locate with per-level comparison.

```java
public class MerkleQ3 {
    static long toy(String s) {
        long h = 0;
        for (char c : s.toCharArray()) h = h * 31 + c;
        return h;
    }

    public static void main(String[] args) {
        long root1 = toy("" + toy("ab") + toy("cd"));
        long root2 = toy("" + toy("ab") + toy("cX"));
        System.out.println(root1 == root2);
        System.out.println(root1 != 0 && root2 != 0);
    }
}
```

Output:

```
false
true
```
