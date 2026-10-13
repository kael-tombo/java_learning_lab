# Why It Exists: Class Loading

Untrusted code was the founding constraint. The 1995 applet model ran
foreign classes inside the browser; without namespace discipline, an
applet shipping its own `java.lang.String` could intercept every
string operation. Parent-first delegation answered structurally: the
trusted core always resolves first, so hostile shadowing never loads.
Loading/linking/initialization split so untrusted bytes could be
verified (link) before any of their logic ran (init).

The three-loader shape tracked deployment reality. Bootstrap held the
runtime core; extension (`lib/ext`) let vendors share add-ons without
touching every classpath; app held user code. When modules arrived
(Java 9, JEP 220), `rt.jar` and `lib/ext` dissolved into modules and
the platform loader took the middle rung — same delegation contract,
one fewer directory convention.

`loadClass`-without-init exists because frameworks need to inspect
before committing: annotation scanners, dependency injectors, and
persistence providers enumerate classes (load + link) and initialize
only the instantiated subset. `Class.forName(name, false, loader)`
is that need in API form.

Identity-as-(name, loader) exists because isolation is a feature.
Containers must run two apps with conflicting library versions in one
JVM; the only sound way is distinct runtime types per loader. The
`ClassCastException` on identical names is the type system telling
the truth about that isolation — collapsing it would corrupt both apps.

The context loader exists because strict hierarchy backfires on
frameworks: high-layer generic code (JNDI, JDBC, XML parsers) must
instantiate low-layer app classes its own loader cannot see. The
thread-bound down-channel (Java 1.2) threads that needle without
breaking delegation's security ordering.

Linking's lazy resolution exists for startup and optionality: resolve
every reference eagerly and hello-world links the world; resolve on
first use and unused paths cost nothing — with version-skew errors
deferred to first execution as the accepted trade.
