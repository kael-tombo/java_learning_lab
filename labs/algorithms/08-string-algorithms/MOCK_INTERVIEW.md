# Mock Interview: String Algorithms: Naive Search, Prefix Function, KMP
> Three worked questions on exact string matching. Each answer is complete runnable Java; outputs below were observed.

## Q1: Count occurrences of a pattern with naive search.
Key insight: Naive search tests every alignment; it is simple and fine for short patterns, but on text a^n and pattern a^(m-1)b it rescans the same characters, giving Theta(n*m) worst case. That failure motivates KMP.
Complexity: Time O(n*m) worst case; space O(1).
```java
public class L08Q1Naive {
    public static void main(String[] args) {
        String t = "ababa", p = "aba";
        int n = 0;
        for (int i = 0; i + p.length() <= t.length(); i++)
            if (t.startsWith(p, i)) n++;
        System.out.println("occurrences=" + n);
    }
}
```
Observed output: `occurrences=2`
Follow-up: Construct the text/pattern pair that forces naive search into Theta(n*m) character comparisons.

## Q2: Compute the KMP prefix function for a fixed pattern.
Key insight: pi[i] = length of the longest proper prefix of p[0..i] that is also a suffix. When a mismatch happens, pi tells how far the pattern can shift without rechecking known-matching characters - the core of KMP.
Complexity: Time O(m); space O(m).
```java
import java.util.Arrays;
public class L08Q2Prefix {
    public static void main(String[] args) {
        String p = "ababaca";
        int[] pi = new int[p.length()];
        for (int i = 1; i < p.length(); i++) {
            int j = pi[i - 1];
            while (j > 0 && p.charAt(i) != p.charAt(j)) j = pi[j - 1];
            if (p.charAt(i) == p.charAt(j)) j++;
            pi[i] = j;
        }
        System.out.println("pi=" + Arrays.toString(pi));
    }
}
```
Observed output: `pi=[0, 0, 1, 2, 3, 0, 1]`
Follow-up: Why is the total work of all the inner while-loops O(m) rather than O(m^2)?

## Q3: Find all pattern occurrences with KMP search.
Key insight: The search reuses the same fallback logic as the prefix construction: on mismatch, fall back along pi instead of restarting at the next text position. Each text character is examined at most twice, giving linear time.
Complexity: Time O(n + m); space O(m).
```java
import java.util.ArrayList;
public class L08Q3Kmp {
    public static void main(String[] args) {
        String t = "ababa", p = "aba";
        int[] pi = new int[p.length()];
        for (int i = 1; i < p.length(); i++) {
            int j = pi[i - 1];
            while (j > 0 && p.charAt(i) != p.charAt(j)) j = pi[j - 1];
            if (p.charAt(i) == p.charAt(j)) j++;
            pi[i] = j;
        }
        ArrayList<Integer> hits = new ArrayList<>();
        int j = 0;
        for (int i = 0; i < t.length(); i++) {
            while (j > 0 && t.charAt(i) != p.charAt(j)) j = pi[j - 1];
            if (t.charAt(i) == p.charAt(j)) j++;
            if (j == p.length()) { hits.add(i - j + 1); j = pi[j - 1]; }
        }
        System.out.println("kmp=" + hits);
    }
}
```
Observed output: `kmp=[0, 2]`
Follow-up: After reporting a match at i, why must j fall back to pi[j-1] instead of 0?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
