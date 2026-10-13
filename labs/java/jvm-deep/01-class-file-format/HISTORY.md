# History: Class File Format

## Oak and the first portable binary (1991–1995)

James Gosling's Oak team needed one compiled artifact that ran on
consumer devices with different CPUs. The answer was a fixed binary
struct with a magic number (`0xCAFEBABE`, chosen by Gosling — the
hexspeak is his) and version bytes, so any JVM could accept or reject
a file in 8 bytes. Java 1.0 specified this in the first VM spec.

## JVMS §4 stabilizes the struct (1996–2004)

The major-version scheme (45 = 1.1, 46 = 1.2, 47 = 1.3, 48 = 1.4,
49 = 5, 50 = 6) let the platform evolve bytecode while keeping old
files loadable: the JVM rejects newer majors and runs older ones.
The constant-pool tag space assigned `Utf8=1` through `NameAndType=12`
in this era; `Long`/`Double` double-slots date to the original design.

## Split verification: JSR-202 and version 50 (Java 6)

Early verifiers inferred operand-stack types by iterating bytecode to
a fixed point — slow and version-sensitive. JSR-202 mandated
`StackMapTable` frames from version 50.0 on: `javac` pre-computes
types at merge points, the verifier checks them in one pass. Startup
verification of large applications got measurably faster, and this
lab's straight-vs-branchy probe still shows the emission rule.

## Dynamic linkage joins the pool (Java 7–8)

JSR 292 (Java 7) added `MethodHandle=15`, `MethodType=16`, and
`InvokeDynamic=18` pool tags plus the `BootstrapMethods` attribute.
Java 8 compiled every lambda through `invokedynamic` and
`LambdaMetafactory` (a later lab's subject), and string concatenation
followed in Java 9 via the same mechanism. The `Dynamic=17` constant
(Json-style condy) generalized the linkage in Java 11.

## Nests, records, sealed classes reshape attributes (11–17)

Project Valhalla-adjacent access work replaced synthetic accessor
bridges with `NestHost`/`NestMembers` (Java 11): nested classes
declare real nestmates. `Record` (finalized Java 16) and
`PermittedSubclasses` (Java 17) added declarative shape attributes
the access checker enforces. Each arrived as new attributes and pool
entries (`Module=19`, `Package=20` came with JPMS in 9) — the
header-first, attributes-last layout absorbed them without moves.

## Measured majors through 23

On JDK 23 with explicit `--release` flags this lab pins 8→52, 11→55,
17→61, 21→65, 23→67 (full run 45=1.1 … 67=23 in THEORY.md). The
forward-compatibility rule never changed: old bytecode runs, new
bytecode on old runtimes is `UnsupportedClassVersionError`.
