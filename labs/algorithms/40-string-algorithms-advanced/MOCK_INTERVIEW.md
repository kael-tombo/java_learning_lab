# Mock Interview: Advanced String Algorithms
> Three questions on linear and near-linear pattern matching. Quote the bound before coding.
## Q1: KMP prefix function
Problem: build pi for ababaca and find it in abababacaba.
Key insight: pi[i] is the longest proper border of the prefix, so mismatches fall back without rescanning text characters; the single match starts at index 2.
Complexity: O(n + m) time, O(m) memory.
```java
import java.util.*;
public class L40Q1 {
    public static void main(String[] a){
        String p = "ababaca"; int[] pi = new int[p.length()];
        for (int i = 1; i < p.length(); i++){ int j = pi[i-1]; while (j > 0 && p.charAt(i) != p.charAt(j)) j = pi[j-1]; if (p.charAt(i) == p.charAt(j)) j++; pi[i] = j; }
        String t = "abababacaba"; List<Integer> hits = new ArrayList<>();
        int j = 0;
        for (int i = 0; i < t.length(); i++){ while (j > 0 && t.charAt(i) != p.charAt(j)) j = pi[j-1]; if (t.charAt(i) == p.charAt(j)) j++; if (j == p.length()){ hits.add(i-j+1); j = pi[j-1]; } }
        System.out.println("prefix=" + Arrays.toString(pi) + " matches=" + hits);
    }
}
```
Observed output:
```
prefix=[0, 0, 1, 2, 3, 0, 1] matches=[2]
```
Follow-up: where does the border chain appear in the fallback loop?
## Q2: Aho-Corasick multi-pattern
Problem: find {he, she, his} in ushers with trie plus failure links.
Key insight: failure links reuse the longest proper suffix that is also a trie prefix, and output inheritance reports she@1 and he@2 in one left-to-right pass.
Complexity: O(n + m + z) time for text n, patterns m, hits z.
```java
import java.util.*;
public class L40Q2 {
    static class Node { Map<Character,Node> next = new HashMap<>(); Node fail; List<String> out = new ArrayList<>(); }
    public static void main(String[] a){
        Node root = new Node();
        for (String w : new String[]{"he","she","his"}){ Node c = root; for (char ch : w.toCharArray()) c = c.next.computeIfAbsent(ch, k -> new Node()); c.out.add(w); }
        Queue<Node> q = new ArrayDeque<>();
        for (Node c : root.next.values()){ c.fail = root; q.add(c); }
        while (!q.isEmpty()){ Node c = q.poll(); for (Map.Entry<Character,Node> e : c.next.entrySet()){ Node f = c.fail; while (f != null && !f.next.containsKey(e.getKey())) f = f.fail; e.getValue().fail = (f == null) ? root : f.next.get(e.getKey()); e.getValue().out.addAll(e.getValue().fail.out); q.add(e.getValue()); } }
        Node c = root; List<String> hits = new ArrayList<>(); String t = "ushers";
        for (int i = 0; i < t.length(); i++){ char ch = t.charAt(i); while (c != root && !c.next.containsKey(ch)) c = c.fail; c = c.next.getOrDefault(ch, root); for (String w : c.out) hits.add(w + "@" + (i-w.length()+1)); }
        System.out.println("hits=" + hits);
    }
}
```
Observed output:
```
hits=[she@1, he@2]
```
Follow-up: how do output links (or dict-suffix links) avoid walking the full chain per position?
## Q3: suffix array plus LCP
Problem: sort the suffixes of banana and compute adjacent longest common prefixes.
Key insight: the sorted order [5,3,1,0,4,2] groups shared prefixes (lcp 3 for ana/anana), which is the basis for substring search and distinct-substring counting.
Complexity: O(n^2 log n) with substring keys here; production builds use doubling or linear methods.
```java
import java.util.*;
public class L40Q3 {
    public static void main(String[] a){
        String s = "banana"; Integer[] sa = {0,1,2,3,4,5};
        Arrays.sort(sa, (x,y) -> s.substring(x).compareTo(s.substring(y)));
        int[] lcp = new int[6];
        for (int i = 1; i < 6; i++){ String p = s.substring(sa[i-1]), q = s.substring(sa[i]); int k = 0; while (k < p.length() && k < q.length() && p.charAt(k)==q.charAt(k)) k++; lcp[i] = k; }
        System.out.println("sa=" + Arrays.toString(sa) + " lcp=" + Arrays.toString(lcp));
    }
}
```
Observed output:
```
sa=[5, 3, 1, 0, 4, 2] lcp=[0, 1, 3, 0, 0, 2]
```
Follow-up: how does binary search over the suffix array answer pattern queries?
## Pass checklist
- [ ] Recompute pi[4] = 3 from the borders of ababa by hand.
- [ ] Trace why position 2 in ushers reports he but not she.
- [ ] Explain the lcp value 3 from the pair ana/anana.
