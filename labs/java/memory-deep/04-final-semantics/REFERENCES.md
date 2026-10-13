# References: Final Field Semantics

## Normative sources

- JLS 17.5, "final Field Semantics": the freeze rule (`w ->hb f ->hb a
  ->mc r1 ->dc r2`), transitivity through finals, and the `this`-escape
  exclusion. The authoritative statement of everything this lab
  demonstrates.
- JSR-133 (Java Memory Model revision, Java 5, 2004): the expert group
  report and FAQ that introduced the final-field guarantee alongside the
  redefined `volatile` semantics.

## Books

- Joshua Bloch, *Effective Java*: immutable-class design (final fields,
  defensive copies) and the constructor discipline (no overridable calls,
  no premature publication) that the freeze presupposes.
- Brian Goetz et al., *Java Concurrency in Practice*: safe publication,
  immutability, and the escape hazards (chapter 3 material) in
  practitioner form.

## OpenJDK implementation paths

- `src/hotspot/share/opto/parse.cpp` (`Parse::do_field_store`): JIT
  handling of final stores and freeze barriers.
- `src/hotspot/share/opto/memnode.cpp`: memory-ordering nodes the freeze
  constrains (StoreStore handling on weak platforms).
- `src/java.base/share/classes/java/lang/String.java`: `final byte[]
  value` + `final byte coder`, the largest-scale consumer of 17.5.
- `src/java.base/share/classes/java/lang/Record.java` and
  `java.util.ImmutableCollections`: final-component snapshots relying on
  the same rule.

## Further reading

- Jeremy Manson and William Pugh, "The Java Memory Model" (POPL 2005):
  the formal underpinning of JSR-133, including the freeze formalization.
- Aleksey Shipilev's JMM writings (openjdk.org, shipilev.net): freeze
  pragmatics, safe-publication tests, and x86-vs-weak-hardware contrasts
  matching this lab's mutable-twin lesson.
