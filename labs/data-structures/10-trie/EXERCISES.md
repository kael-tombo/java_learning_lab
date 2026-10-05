# EXERCISES — Trie (Prefix Tree)

Implement from scratch in Java. No AI-written core logic; tests may assist. Trace each exercise on paper first.

## Ex1 — Build the minimal `insert` + `search` core and invariant checker (25–40 min)

Template:
```java
// Lab 10-trie: Trie (Prefix Tree)
// Goal: Build the minimal `insert` + `search` core and invariant checker
public class Exercise1 {
    // TODO: implement from scratch
    // TODO: picks: insert(word)
    static void check(boolean c) { if (!c) throw new AssertionError(); }
    public static void main(String[] a) { /* traces + asserts */ }
}
```

Acceptance: invariant checker passes; trace matches execution.

## Ex2 — Add the full operation set with edge cases (empty, single element, duplicates) (25–40 min)

Template:
```java
// Lab 10-trie: Trie (Prefix Tree)
// Goal: Add the full operation set with edge cases (empty, single element, duplicates)
public class Exercise2 {
    // TODO: implement from scratch
    // TODO: picks: search(word)
    static void check(boolean c) { if (!c) throw new AssertionError(); }
    public static void main(String[] a) { /* traces + asserts */ }
}
```

Acceptance: invariant checker passes; trace matches execution.

## Ex3 — Hand-trace two multi-step scenarios; commit the ASCII trace as a comment (25–40 min)

Template:
```java
// Lab 10-trie: Trie (Prefix Tree)
// Goal: Hand-trace two multi-step scenarios; commit the ASCII trace as a comment
public class Exercise3 {
    // TODO: implement from scratch
    // TODO: picks: startsWith(prefix)
    static void check(boolean c) { if (!c) throw new AssertionError(); }
    public static void main(String[] a) { /* traces + asserts */ }
}
```

Acceptance: invariant checker passes; trace matches execution.

## Ex4 — Write JUnit 5 tests: happy path, boundaries, adversarial order, invariant fuzz (25–40 min)

Template:
```java
// Lab 10-trie: Trie (Prefix Tree)
// Goal: Write JUnit 5 tests: happy path, boundaries, adversarial order, invariant fuzz
public class Exercise4 {
    // TODO: implement from scratch
    // TODO: picks: countWordsWithPrefix(p)
    static void check(boolean c) { if (!c) throw new AssertionError(); }
    public static void main(String[] a) { /* traces + asserts */ }
}
```

Acceptance: invariant checker passes; trace matches execution.

## Ex5 — Benchmark vs the naive baseline (HashMap/ArrayList/sort) at n=1k/10k/100k; record ns/op (25–40 min)

Template:
```java
// Lab 10-trie: Trie (Prefix Tree)
// Goal: Benchmark vs the naive baseline (HashMap/ArrayList/sort) at n=1k/10k/100k; record ns/op
public class Exercise5 {
    // TODO: implement from scratch
    // TODO: picks: delete(word)
    static void check(boolean c) { if (!c) throw new AssertionError(); }
    public static void main(String[] a) { /* traces + asserts */ }
}
```

Acceptance: invariant checker passes; trace matches execution.

## Ex6 — Break it on purpose: violate one invariant, observe the wrong answer, then fix (25–40 min)

Template:
```java
// Lab 10-trie: Trie (Prefix Tree)
// Goal: Break it on purpose: violate one invariant, observe the wrong answer, then fix
public class Exercise6 {
    // TODO: implement from scratch
    // TODO: picks: autocomplete(p,k)
    static void check(boolean c) { if (!c) throw new AssertionError(); }
    public static void main(String[] a) { /* traces + asserts */ }
}
```

Acceptance: invariant checker passes; trace matches execution.

## Ex7 — Add observability: size/height/counters + toString visualization (25–40 min)

Template:
```java
// Lab 10-trie: Trie (Prefix Tree)
// Goal: Add observability: size/height/counters + toString visualization
public class Exercise7 {
    // TODO: implement from scratch
    // TODO: picks: insert(word)
    static void check(boolean c) { if (!c) throw new AssertionError(); }
    public static void main(String[] a) { /* traces + asserts */ }
}
```

Acceptance: invariant checker passes; trace matches execution.

## Ex8 — Stretch: thread-safety review OR persistence/versioning spike (25–40 min)

Template:
```java
// Lab 10-trie: Trie (Prefix Tree)
// Goal: Stretch: thread-safety review OR persistence/versioning spike
public class Exercise8 {
    // TODO: implement from scratch
    // TODO: picks: search(word)
    static void check(boolean c) { if (!c) throw new AssertionError(); }
    public static void main(String[] a) { /* traces + asserts */ }
}
```

Acceptance: invariant checker passes; trace matches execution.

## Grading rubric
- Correctness 40 / Traces 20 / Tests 20 / Benchmark notes 20.
