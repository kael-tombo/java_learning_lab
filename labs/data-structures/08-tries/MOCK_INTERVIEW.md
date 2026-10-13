# Mock Interview: Tries

## Q1 — Implement a Trie (LC 208)

**Problem.** Support insert, exact search, and prefix check on lowercase words.
**Key insight.** One node per shared prefix; an end-of-word flag separates "app" from "apple". Cost scales with word length, not dictionary size. **Complexity.** O(L) per op.

```java
public class TriesQ1 {
    static class Node {
        Node[] next = new Node[26];
        boolean word;
    }
    static Node root = new Node();
    static void insert(String w) {
        Node c = root;
        for (char ch : w.toCharArray()) { int i = ch - 'a'; if (c.next[i] == null) c.next[i] = new Node(); c = c.next[i]; }
        c.word = true;
    }
    static Node walk(String s) {
        Node c = root;
        for (char ch : s.toCharArray()) { c = c.next[ch - 'a']; if (c == null) return null; }
        return c;
    }
    public static void main(String[] args) {
        insert("apple");
        Node a = walk("apple"), b = walk("app");
        System.out.println(a.word + " / " + b.word + " / " + (walk("ax") != null));
    }
}
```

Output:

```
true / false / false
```

## Q2 — Longest Common Prefix via Trie

**Problem.** Find the longest common prefix of a set of strings.
**Key insight.** Insert all strings; walk down while the node has exactly one child and is not a word end. **Complexity.** O(total length) time and space.

```java
public class TriesQ2 {
    static class Node {
        Node[] next = new Node[26];
        int kids;
        boolean word;
    }
    public static void main(String[] args) {
        Node root = new Node();
        for (String w : new String[]{"flower", "flow", "flight"}) {
            Node c = root;
            for (char ch : w.toCharArray()) { int i = ch - 'a'; if (c.next[i] == null) { c.next[i] = new Node(); c.kids++; } c = c.next[i]; }
            c.word = true;
        }
        StringBuilder sb = new StringBuilder();
        Node c = root;
        while (c.kids == 1 && !c.word)
            for (int i = 0; i < 26; i++) if (c.next[i] != null) { sb.append((char) ('a' + i)); c = c.next[i]; break; }
        System.out.println(sb);
    }
}
```

Output:

```
fl
```

## Q3 — Prefix-Set Pruning

**Problem.** Why does a trie beat a hash set when searching many words on a board (LC 212)?
**Key insight.** Board DFS abandons a path the moment the prefix is absent, pruning whole subtrees a flat word set cannot rule out early. **Complexity.** O(L) per word search.

```java
public class TriesQ3 {
    public static void main(String[] args) {
        java.util.Set<String> pre = new java.util.HashSet<>();
        for (String w : new String[]{"oath", "pea", "eat", "rain"})
            for (int i = 1; i <= w.length(); i++) pre.add(w.substring(0, i));
        System.out.println(pre.contains("oat") + " / " + pre.contains("oax") + " / " + pre.size());
    }
}
```

Output:

```
true / false / 14
```
