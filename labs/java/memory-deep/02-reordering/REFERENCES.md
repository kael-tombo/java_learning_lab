# References: Reordering

## Normative and architectural sources

- JLS 17.4 (Memory Model): the hb rules and DRF guarantee that define
  which litmus outcomes are *forbidden* (Dekker (0,0) under SC) vs
  *allowed* (anything unordered) — the verdict side of every snippet.
- Doug Lea, *JSR-133 Cookbook for Compiler Writers*: barrier placement
  per hb edge per platform — why volatile closes Dekker and
  release/acquire does not (lab 03's taxonomy in full).
- Sewell, Sarkar, Owens, Nardelli, Myreen, "x86-TSO: A Rigorous and
  Usable Programmer's Model for x86 Multiprocessors" (CACM 2010): the
  three-pairs-preserved, StoreLoad-free formalization; SPARC TSO
  heritage discussed therein.
- Tomasulo, "An Efficient Algorithm for Exploiting Multiple Arithmetic
  Units" (IBM JRD 1967): reservation stations and in-order commit for
  the 360/91 — the OoO execution layer.

## ARM / POWER architecture (qualitative references)

- ARM Architecture Reference Manual (ARMv8): `LDAPR`/`STLR` acquire/
  release semantics, `DMB` full barrier, multi-copy-atomicity of ARMv8.
- POWER ISA: `lwsync` vs `sync` (lightweight vs full cumulative) —
  the weakest-shipping-model exhibit (IRIW/WRC litmus in the research
  literature, e.g., Sarkar et al. on POWER semantics).
- Preshing, "Memory Ordering at Compile Time" and "Acquire and Release
  Semantics": practitioner-grade treatment of compiler/CPU reorderings
  with litmus examples matching this lab's shapes.

## JVM and testing

- Aleksey Shipilev, "Java Memory Model Pragmatics" (talk + notes):
  rendezvous design for litmus tests and why barriers phase badly —
  the methodology behind snippets 1-3 and 5.
- OpenJDK jcstress (`github.com/openjdk/jcstress`): the standard
  harness for promoting hand-rolled Dekker drivers to histograms.
- `src/java.base/share/classes/java/lang/invoke/VarHandle.java`
  (OpenJDK): `getAcquire`/`setRelease`/`getOpaque` specifications used
  in snippet 4 and lab 03's snippet 5.
- `src/java.base/share/classes/java/util/concurrent/locks/LockSupport.java`
  (OpenJDK): `parkNanos`/`onSpinWait` mechanics behind the drain test
  and the rendezvous spins.
