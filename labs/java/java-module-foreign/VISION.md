# Vision — Foreign Function & Memory

## Direction (2026+)
- FFM is stable (JDK 22+); JNI relegated to legacy.
- Vector API + FFM unlock Java for ML/native codecs without C++ glue.
- jextract auto-generates bindings from headers — manual descriptors fade.

## 5-Year Bets
1. Most new native libs ship jextract bindings, not JNI.
2. Off-heap columnar stores (Arrow) accessed via segments.
3. Safe native sandboxing via arenas + restricted access.

## Constants
- Ownership discipline (who closes arena) stays critical.
- Descriptor correctness: one wrong layout = crash/garbage.

## Signals
- Panama project page, jextract releases, Vector API JEPs.
- Libraries: Lucene, Netty, Arrow FFM backends.

## Career
FFM + perf skills → infra, DB, ML-systems roles. Build the codec service.

## Anti-Vision
Don't wrap everything native "for speed" — JNI/FFM crossing still costs.
Profile; prefer pure-Java unless native wins 2×+.

## 30/60/90
- 30d: arenas + strlen/struct labs.
- 60d: upcall + mapped-file grep.
- 90d: production codec with NMT-verified zero leaks.
