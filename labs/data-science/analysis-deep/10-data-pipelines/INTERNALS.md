# Internals - Pipeline Computations

## Keyed merge

LinkedHashMap.merge per record: amortized O(1), order-preserving for
deterministic prints and diffs. Memory O(keys); eviction policy (TTL by
event time) belongs in production sinks and is noted at the call site.

## Quality checks

Single pass accumulates row count, per-column null counts, and value
sums: O(rows * cols) time, O(cols) memory. Blank-vs-null distinguished
(isBlank check) so empty strings do not masquerade as values.

## Compat check

containsAll on key sets plus per-field type equality: O(fields). The
widening policy (int->long allowed) lives in an explicit allowlist map,
never in silent coercion - every exception to strictness is reviewable.

## Windows

Naive slice means O(w) per window; running-sum form O(1) amortized.
Lab uses the naive form for clarity with width 3; the running form is
specified in comments where w is a parameter.

## Determinism guards

LinkedHashMap/LinkedHashSet everywhere iteration order is observable;
no HashMap in output paths; no system clock in transforms (event time
only). Double-run equality asserted in exercises, not assumed.

## Edge cases

- Empty batch: zero rows with a valid schema passes trivially (nothing
  to corrupt) but logs a warning - silence hides upstream outages.
- All-null column: nullRate 1.0 quarantines unless the column is declared
  optional in the contract; declarations live in Schema, not in hope.
- Duplicate keys within one batch: last-write-wins with a logged count;
  silent first-wins vs last-wins divergence is a classic diff source.

## Why ordered maps

LinkedHashMap iteration order makes prints, diffs, and double-run
comparisons deterministic. HashMap order varies by JVM and key hash -
nondeterministic output poisons replay assertions, so it is banned here.
