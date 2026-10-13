# References: Class Loading

## Specifications

- JVMS SE 23, §5 — *Loading, Linking, and Initializing*: the phase
  definitions this lab measures (loading → verify/prepare/resolve →
  `<clinit>`).
- JLS 17, §12.2–12.4 — loading, linking, and initialization triggers
  (active uses; constants never initialize).
- JLS 17, §15.29 — constant expressions (which `static final` fields
  become `ConstantValue` and inline).

## JSRs and JEPs

- JSR-133 — *Java Memory Model* (finalized `<clinit>` locking and
  exactly-once semantics, Java 5).
- JSR-202 — split verification at link time (the verify sub-step's
  single-pass check, Java 6).
- JEP 220 — *Modular Run-Time Images* (removed the extension loader
  and `rt.jar`/`lib/ext`, Java 9).
- JEP 261 — *Module System* (`open`/`opens`, reflective access gates,
  `InaccessibleObjectException`, Java 9).

## Tools and source

- `java -Xlog:class+load,class+init` — HotSpot unified logging for
  loads and initializations in startup order.
- OpenJDK source: `src/java.base/share/classes/java/lang/ClassLoader.java`
  (`loadClass`/`findClass`/`defineClass` delegation),
  `src/hotspot/share/oops/instanceKlass.cpp` (link + init lock),
  `src/java.base/share/classes/java/lang/Class.java` (`forName` variants).
- `javap -c -p` on the use site — proves `ConstantValue` inlining
  (lab 01's stale-constant mechanism) without a debugger.

## Reading order

JVMS §5.3–5.5 first (the three phases), then JLS §12.4 (triggers),
then JEP 220 (why the tree has three rungs, not four). The five
CODE_DEEP_DIVE probes map one-to-one onto those pages.
