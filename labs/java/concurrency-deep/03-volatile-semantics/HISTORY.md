# History: Volatile Semantics

## From broken DCL to a specified memory model
- **Late 1990s:** double-checked locking idiom circulates; developers discover it is broken under the original Java memory model (publication before initialization becomes visible).
- **2004, JSR-133 (Bill Pugh, Jeremy Manson, Brian Goetz and others) with Java 5:** memory-model rewrite; volatile write->read becomes a happens-before edge (JLS 17.4.5); DCL becomes correct *only* with a volatile field.
- **2004, JSR-166 (Doug Lea):** `java.util.concurrent` documents an edge per action (submit->execute, etc.), extending the same happens-before vocabulary.
- **2006, Brian Goetz et al., *Java Concurrency in Practice*:** codifies safe publication, piggybacking, and the volatile-array trap for working engineers.
- **2014-2017, Java 8-9:** `LongAdder` (Java 8) relieves volatile-counter abuse; `VarHandle` (Java 9, JEP 193) exposes acquire/release/opaque modes beneath the volatile bundle.

## What changed and what did not
- The *specification* of volatile (visibility + access atomicity, no compound atomicity) has been stable since 2004; hardware costs shifted (x86 TSO vs ARM barriers) without changing the contract.

## Dates to remember (confident facts only)
- JSR-133 memory-model rewrite: 2004 (Java 5). JSR-166 concurrency utilities: 2004 (Java 5).
- `LongAdder`: Java 8. `VarHandle`: Java 9. Biased locking off by default: JDK 15 (JEP 374); removed: JDK 18.
- Virtual threads: Java 21 (JEP 444). *Java Concurrency in Practice* (Goetz et al.): 2006.

## Sources
- REFERENCES.md entries for JLS 17.4/17.5/17.7, JSR-133 FAQ (Pugh), JSR-166, OpenJDK source paths.

## Why the pre-2004 model broke DCL
- The original Java memory model permitted publication-before-initialization visibility: `helper = new Helper()` could show the reference before the constructor's field stores became visible — no edge forbade the reorder.
- Developers "fixed" it with more synchronization in the wrong place (synchronizing only the write side, or re-checking without a read edge), which narrowed the race without closing it — testing passed, production published half-built objects.
- The failure was unreproducible on demand by construction: it needed a specific JIT/CPU reorder plus a racing reader, so bug reports read as hardware flakiness rather than model violations.

## Mechanism depth on the dated entries
- JSR-133 (2004, Pugh/Manson/Goetz and others): rewrote JLS 17.4 around happens-before; volatile write -> later read became an edge (17.4.5), and program-order plus transitivity turned one flag into a publication channel for whole object graphs.
- JSR-166 (2004, Doug Lea): extended the same vocabulary with one documented edge per concurrent action (submit -> execute, unlock -> lock, countDown -> await return) — message-passing built from chained edges, as snippet 5 demonstrates.
- JCIP (Goetz et al., 2006): translated the model into working rules — safe-publication catalog, piggybacking idiom, volatile-array trap — the bridge most engineers actually learned from.
- Java 8 (2014): `LongAdder`/`LongAccumulator` removed the main excuse for volatile counters — RMW contention got its own striped tool instead of abusing a visibility keyword.
- Java 9 (JEP 193): `VarHandle` unbundled volatile into modes (volatile/acquire-release/opaque/plain) plus CAS primitives — experts can now buy exactly the edge they need, while everyone else stays on `volatile`.

## How to read old volatile advice
- Pre-2004 writing about volatile ("flush", "main memory", DCL without the keyword) predates the edge vocabulary — translate or discard; never merge it with JLS 17.4 reasoning.
- "Volatile is expensive, avoid it" benchmarks from the early 2000s measured un-fenced implementations on hardware the model later priced differently — re-measure per architecture (x86 TSO vs ARM fences) instead of inheriting the fear.
- Any DCL sample without `volatile` (or holder/enum) is a bug exhibit regardless of its date — the keyword is the correctness condition, not a style choice.
- Post-2004 "volatile means thread-safe" simplifications conflate visibility with atomicity — check every such claim against `volatile++` before quoting it.
