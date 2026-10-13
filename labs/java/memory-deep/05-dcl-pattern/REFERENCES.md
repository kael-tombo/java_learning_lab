# References: DCL Pattern

## Normative sources

- JLS 12.4.2 (class initialization): the exactly-once, JVM-locked
  procedure behind the holder idiom — lazy on first active use.
- JLS 17.4/17.5: volatile write/read ordering (the DCL publication edge)
  and the final-field freeze (why `value == 42` is visible through it).
- JSR-133 (Java Memory Model revision, Java 5, 2004): the expert-group
  report that made volatile DCL correct and documented why the
  pre-2004 shape was broken.

## Books

- Joshua Bloch, *Effective Java*: Item 3 (enum singletons), the holder
  idiom, and the local-variable single-read DCL shape used throughout
  this lab.
- Brian Goetz et al., *Java Concurrency in Practice*: DCL correctness
  (chapter on safe publication/initialization), holder vs DCL guidance,
  and the synchronized-accessor baseline framing.
- Jeremy Manson and William Pugh, "The Java Memory Model" (POPL 2005):
  formal basis of the volatile edges DCL relies on.

## OpenJDK implementation paths

- `src/hotspot/share/opto/memnode.cpp`, `library_call.cpp`: volatile
  access and fence emission (the fast-path acquire / publication
  release).
- `src/hotspot/share/oops/instanceKlass.cpp`: class-initialization
  locking behind `LazyHolder`.
- `src/java.base/share/classes/java/lang/Enum.java` and
  `src/java.base/share/classes/java/io/ObjectInputStream.java`
  (enum handling): reflection/serialization identity for singletons.

## Further reading

- Shipilev's JMM/concurrency writings (openjdk.org, shipilev.net):
  volatile costs, DCL stress methodology (start gates, construction
  counters), and x86-vs-weak-hardware caution matching this lab's
  no-observable-reorder lesson.
- Martin, Ulf, et al., "Double-Checked Locking is Broken" declaration
  (2004-era): the pre-fix consensus statement for historical context.
