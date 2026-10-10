# Refactoring: Toward a Sound Probing Table

## Add the spread before the mask

Before — raw mask, high-bit collisions:

```java
int i = key.hashCode() & (n - 1);
```

After — JDK spread first:

```java
int h = key.hashCode();
int i = (h ^ (h >>> 16)) & (n - 1);
```

## Replace null-on-delete with tombstones

Before — phantom misses past the hole:

```java
table[i] = null; size--;
```

After — chain-preserving delete:

```java
table[i].state = DELETED; table[i].key = null; table[i].value = null;
size--; tombstones++;
```

## Fix the load trigger

Before — `if (size > n * 0.75) resize();` (blind to tombstones). After —
`if (size + tombstones > n * LOAD) resize();` so delete-heavy tables
still rebuild.

## Replace slot-copy resize with rehash

Before — `System.arraycopy(old, 0, nt, 0, n)`. After — fresh table,
re-`put` live entries through the new mask, recount `size`. Runs dissolve
instead of transferring.

## Replace `% n` stepping with mask stepping

Before — `(i + 1) % n` (division per probe). After — `(i + 1) & (n - 1)`
with enforced power-of-two capacity. Identical sequence, cheaper step.
