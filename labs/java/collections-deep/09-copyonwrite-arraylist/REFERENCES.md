# References: CopyOnWriteArrayList

- OpenJDK source:
  `src/java.base/share/classes/java/util/concurrent/CopyOnWriteArrayList.java`
  — copy-publish paths, COWIterator, addIfAbsent/remove revalidation.
- Goetz et al., *Java Concurrency in Practice* (2006), §5.2 + §11.4 —
  copy-on-write collections, listener notification, publication safety.
- JLS §17.4 (memory model) + JSR 133 (Java 5 memory-model revision;
  Manson, Pugh, Adve) — volatile synchronizes-with / happens-before edges
  the design rests on.
- Lea, JSR 166 (Java 5, 2004) — the concurrency package shipping COW
  collections.
- Okasaki, *Purely Functional Data Structures* (1998) — persistent
  version chains, the functional cousin of copy-publish.
- Bloch, *Effective Java* (Item 17–18, immutability; Item 82, thread
  safety documentation) — why frozen arrays + fresh publication compose.
## Javadoc and source entry points

- `java.util.concurrent.CopyOnWriteArrayList` — snapshot-iterator clause,
  addIfAbsent/remove semantics, subList/spliterator notes.
- `java.util.concurrent.CopyOnWriteArraySet` — the addIfAbsent-backed
  wrapper and its O(n) set costs.
- JLS §17.4 / §17.7 — happens-before on volatile access, atomic reference
  reads/writes: the two rules making lock-free reads sound.

## Further reading

- *Java Concurrency in Practice*, §5.2 — COW collections and the listener
  pattern; §16 — the Java memory model in practice.
- JSR 133 (Manson/Pugh/Adve) — the memory-model revision COW relies on.
- Okasaki, *Purely Functional Data Structures* — version chains without
  O(n) copies (the O(log n) path-copying alternative).
