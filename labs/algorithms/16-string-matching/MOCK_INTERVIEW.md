# Mock Interview: String Matching: Naive Counts, KMP, Rabin-Karp
> Three worked questions on exact pattern search. Each answer is complete runnable Java; outputs below were observed.

## Q1: Count character comparisons of naive search on a repetitive input.
Key insight: Naive search rechecks the pattern from scratch after each mismatch; on text aaaaab and pattern aaab every alignment matches 3 characters before failing, so the comparison count (not just big-O) shows the quadratic behavior.
Complexity: Time O(n*m) worst case; space O(1).
```java
public class L16Q1NaiveCount {
    public static void main(String[] args) {
        String t = "aaaaab", p = "aaab";
        int cmp = 0, hits = 0;
        for (int i = 0; i + p.length() <= t.length(); i++) {
            int j = 0;
            while (j < p.length()) { cmp++; if (t.charAt(i + j) != p.charAt(j)) break; j++; }
            if (j == p.length()) hits++;
        }
        System.out.println("hits=" + hits + " cmp=" + cmp);
    }
}
```
Observed output: `hits=1 cmp=12`
Follow-up: Generalize this input family to length parameters n, m and derive the exact Theta(n*m) comparison count.

## Q2: Find all occurrences of abcab in abcababcab with KMP.
Key insight: The prefix function lets the pattern slide forward without rechecking known-matching text: after the match at 0, the fallback resumes mid-pattern and finds the overlapping occurrence at 5. Each text character is examined at most twice.
Complexity: Time O(n + m); space O(m).
```java
import java.util.ArrayList;
public class L16Q2Kmp {
    public static void main(String[] args) {
        String t = "abcababcab", p = "abcab";
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
Observed output: `kmp=[0, 5]`
Follow-up: What is pi for abcab, and how does its last value produce the overlap at position 5?

## Q3: Search with Rabin-Karp rolling hash (mod 101, verified by direct check).
Key insight: The window hash updates in O(1) by dropping the leading character and shifting: th = (26*(th - lead*h) + next) mod q. Hash equality is only a candidate - the direct comparison confirms it - so collisions cost time but never correctness.
Complexity: Expected time O(n + m); worst case O(n*m) under collisions; space O(1).
```java
public class L16Q3RK {
    public static void main(String[] args) {
        String t = "ababa", p = "aba";
        int q = 101, ph = 0, th = 0, h = 1;
        for (int i = 0; i < p.length() - 1; i++) h = (h * 26) % q;
        for (int i = 0; i < p.length(); i++) { ph = (26 * ph + p.charAt(i)) % q; th = (26 * th + t.charAt(i)) % q; }
        String hits = "";
        for (int i = 0; i + p.length() <= t.length(); i++) {
            if (ph == th && t.startsWith(p, i)) hits += i + " ";
            th = (26 * (th - t.charAt(i) * h) + (i + p.length() < t.length() ? t.charAt(i + p.length()) : 0)) % q;
            if (th < 0) th += q;
        }
        System.out.println("rk=" + hits.trim());
    }
}
```
Observed output: `rk=0 2`
Follow-up: Why must a negative intermediate hash be adjusted, and what failure does skipping that cause?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
