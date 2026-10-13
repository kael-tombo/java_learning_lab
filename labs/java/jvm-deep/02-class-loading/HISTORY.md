# History: Class Loading

## Classpath and the three loaders (1995–1998)

Java 1.0 shipped bootstrap (VM built-ins), extension (`lib/ext`,
shareable add-ons), and application (`CLASSPATH`) loaders with
parent-first delegation. Delegation's motive was security from day
one: untrusted applet classes could never replace `java.*` because
bootstrap always answered first.

## JSR-133 fixes initialization (Java 5, 2004)

The revised Java Memory Model nailed down `<clinit>` semantics the
earlier spec left loose: initialization holds a JVM-managed lock,
runs exactly once, and has defined visibility to all threads.
Circular static initializers across classes deadlock or observe
defaults under this lock — the puzzle behavior this lab's theory
section documents.

## Containers break delegation deliberately (2000s)

Servlet containers (Tomcat), OSGi, and application servers inverted
lookup for webapp isolation: check self before parent so two apps
ship different versions of one library. The price — sibling
namespaces where identical names refuse to cast — became the
industry's standard `ClassCastException: X cannot be cast to X`.
The `SplitIdentity` probe is that incident in miniature.

## JEP 220 removes the extension loader (Java 9, 2017)

Modularizing the JDK replaced `rt.jar`/`lib/ext` with modules and
the platform loader. `java.ext.dirs` is ignored; upgrade paths that
dropped jars into `lib/ext` silently stop loading. `java.sql`,
`java.xml`, and CORBA leftovers moved under platform. Any current
document diagramming bootstrap→extension→application is eight years
stale — `LoaderTree` prints the two-hop chain that replaced it.

## Context loaders and frameworks (1998–present)

`Thread.getContextClassLoader` (Java 1.2) gave high-layer framework
code (JNDI, JDBC drivers, JAXB, logging) a down-channel to app
classes delegation hides. Every "resource not found though it's on
the classpath" incident since is a missing or wrong context loader —
unmanaged threads and pool workers inherit or replace it
unpredictably.

## Modules gate reflection (Java 9+)

JPMS added `open`/`opens` directives and `Module.getResourceAsStream`;
`InaccessibleObjectException` is the new enforcement face of the old
access rules. Custom loaders kept their contract (`findClass` +
`defineClass` + verification) unchanged through all of it — the
hierarchy above them is what moved.
