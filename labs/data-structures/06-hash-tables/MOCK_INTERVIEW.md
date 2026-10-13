# Mock Interview: Hash Tables

## Q1 — Frequency Count and First Unique Character (LC 387)

**Problem.** Find the index of the first non-repeating character in a string.

**Key insight.** Two passes: count frequencies in a hash map, then return the first character with count 1.

**Complexity.** Time O(n), space O(1) for a fixed alphabet (O(k) distinct symbols generally).

```java
import java.util.HashMap;
import java.util.Map;

public class HashTablesQ1 {
    public static int firstUnique(String s) {
        Map<Character, Integer> freq = new HashMap<>();
        for (char c : s.toCharArray()) freq.put(c, freq.getOrDefault(c, 0) + 1);
        for (int i = 0; i < s.length(); i++) {
            if (freq.get(s.charAt(i)) == 1) return i;
        }
        return -1;
    }

    public static void main(String[] args) {
        System.out.println(firstUnique("leetcode"));
        System.out.println(firstUnique("aabb"));
    }
}
```

Output:

```
0
-1
```

## Q2 — Load Factor and Resizing

**Problem.** Explain why hash table inserts stay O(1) amortized even though resizes cost O(n).

**Key insight.** Doubling on resize means resize costs form a geometric series n + n/2 + n/4 + ... < 2n, so the average insert cost is constant. Keep load factor below ~0.75 to bound collisions.

**Complexity.** Amortized O(1) insert, O(n) worst-case resize, space O(n).

```java
public class HashTablesQ2 {
    public static void main(String[] args) {
        int cap = 4, n = 0, resizes = 0;
        for (int i = 0; i < 20; i++) {
            if ((double) n / cap > 0.75) { cap *= 2; resizes++; }
            n++;
        }
        System.out.println("cap=" + cap + " resizes=" + resizes);
    }
}
```

Output:

```
cap=32 resizes=3
```

## Q3 — Group Anagrams (LC 49)

**Problem.** Group strings that are anagrams of each other.

**Key insight.** Anagrams share a canonical key: the sorted characters (or a 26-count signature). Hash by that key.

**Complexity.** Time O(n * k log k) with sorting, space O(n * k).

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class HashTablesQ3 {
    public static void main(String[] args) {
        String[] words = {"eat", "tea", "tan", "ate", "nat", "bat"};
        Map<String, List<String>> groups = new HashMap<>();
        for (String w : words) {
            char[] c = w.toCharArray();
            Arrays.sort(c);
            groups.computeIfAbsent(new String(c), k -> new ArrayList<>()).add(w);
        }
        System.out.println(groups.size());
        System.out.println(groups.get("abt"));
    }
}
```

Output:

```
3
[bat]
```
