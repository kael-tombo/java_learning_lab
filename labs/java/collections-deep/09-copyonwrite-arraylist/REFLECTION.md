# Reflection: CopyOnWriteArrayList

## What surprised you?

The "wasteful" structure — copying everything per write — is optimal for
its niche. Write down the workload ratio where waste becomes wisdom, and
why your instinct initially priced copies above locks.

## Check your model

1. An iterator pins V2 while writes publish V3, V4. List every version
   each actor sees (old iterator, new iterator, indexed `get`). When is
   V2 collectible?
2. Why does `remove` bother with a lock-free pre-scan if it must lock to
   mutate anyway? Which call pattern does the pre-scan accelerate?
3. `set(i, sameValue)` copies and publishes. Argue both sides: wasteful
   vs necessary — then state what "necessary" means in memory-model terms.

## Connect

- Which notification/config/reread loop in your code iterates under a
  lock or clones per read? What is its read:write ratio — does COW fit?
- Where do you hold iterators or snapshots across writes today? What do
  they pin?

## The one-line takeaway

One volatile array reference, never mutated in place: readers surf
versions for free, writers pay per version. If your summary names the
field, the snapshot rule, and the workload ratio, it is complete.
