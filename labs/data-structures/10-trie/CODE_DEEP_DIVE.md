# CODE_DEEP_DIVE — Trie (Prefix Tree)

Java 17 implementation notes. Focus op: `insert(word)` (O(L)).

## 1. Reference skeleton
```java
public final class LabStructure {
    // Invariants: Every root-to-node path spells a prefix of some inserted key; endOfWord flag distinguishes 'car' from prefix of 'cart'
    // TODO core ops:
    //   - insert(word)  [O(L)]
    //   - search(word)  [O(L)]
    //   - startsWith(prefix)  [O(P)]
    //   - countWordsWithPrefix(p)  [O(P)]
    //   - delete(word)  [O(L)]
    //   - autocomplete(p,k)  [O(P + k*Sigma)]
    public void checkInvariants() { /* throw on violation */ }
    @Override public String toString() { /* ASCII dump */ return ""; }
}
```

## 2. Walkthrough
1. Construction sets the empty-state invariant (counts zeroed, sentinels linked).
2. Hot path follows exactly the contract table; no hidden scans.
3. Maintenance path (split/propagate/compress/rebuild) restores invariants before return.
4. Every public method ends with `assert checkInvariants()` in debug builds.

## 3. Pitfalls (Java-specific)
- `==` vs `.equals` on keys; missing `hashCode` contract.
- Integer overflow in mid/size math: use `lo + ((hi-lo)>>>1)` and `long` accumulators.
- 1-based vs 0-based index slips; half-open `[l, r)` discipline.
- Recursive depth on skewed input: prefer iterative or bounded depth.
- Mutation leaking through returned references; defensive copies or immutability.
- Forgetting to update auxiliary counts/tags on every path (esp. delete).

## 4. Testing plan (JUnit 5)
- Empty/singleton/boundary/duplicate/adversarial-order cases.
- Property test: random ops vs naive model (TreeMap/ArrayList) for 10k steps.
- Invariant fuzz: check after every op.
- Benchmark harness: `System.nanoTime` warmup + 5 measured runs.

## 5. Complexity audit
Map each method to its table cost; flag any loop that escapes the bound and justify or fix it.

## 6. Refactor prompts
- Extract the invariant checker into its own class.
- Swap array<->map children and re-measure.
- Add a `stats()` hook (height/size/counters) without changing asymptotics.
