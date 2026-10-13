# References: Class File Format

## Specifications

- JVMS for Java SE 23, §4 — *The class File Format*: header, pool,
  field/method/attribute tables. The normative struct this lab reads.
- JVMS SE 23, §4.4.5 — *Long/Double double-slot rule* (the `#12→#14`
  gap); §4.7.3–4.7.4 — `Code` and `StackMapTable` attributes.
- JVMS SE 23, §4.7 — attribute inventory (`ConstantValue`,
  `BootstrapMethods`, `NestHost`/`NestMembers`, `Record`,
  `PermittedSubclasses`, `SourceFile`, `LineNumberTable`).
- JLS 17, §13.1 — binary compatibility rules for `static final`
  constants (the stale-constant mechanism behind `ConstantValue`).

## JSRs and JEPs

- JSR-202 — *Class File Update* (split verification, `StackMapTable`,
  version 50.0 / Java 6).
- JSR 292 — *Supporting Dynamically Typed Languages* (pool tags
  `MethodHandle=15`, `MethodType=16`, `InvokeDynamic=18`, Java 7).
- JEP 220 — modularized the JDK (pool tags `Module=19`, `Package=20`,
  Java 9); JEP 181 (nestmates, Java 11), JEP 395/409 (`Record`,
  sealed classes, 16/17).

## Tools and source

- `javap` (JDK tool reference) — flags `-v -c -p -s` used in every
  probe of this lab.
- OpenJDK source: `src/java.base/share/classes/java/lang/ClassLoader.java`
  (version enforcement path), `src/hotspot/share/classfile/classFileParser.cpp`
  (header/pool parsing, `ClassFormatError` origins).
- `java.lang.classfile.ClassFile` (JDK 22+, preview JEP 457/466) —
  the programmatic reader for the same struct (lab 04's subject).

## Reading order

Start with JVMS §4.1–4.4 (header + pool), then §4.7.3 (Code), then
JSR-202's `StackMapTable` section. Everything else in this lab is a
measurement of those pages.
