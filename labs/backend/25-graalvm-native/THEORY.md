# Theory: GraalVM Native Images

## What Native Image Changes

GraalVM's `native-image` Ahead-of-Time-compiles a closed Java application
into a native binary. Benefits: sub-second startup, tens-of-MB memory
footprint, instant horizontal scale-out, and smaller container images — why
serverless and CLI tools favor it. Costs: the binary is built for one
platform, peak throughput can lag JIT C2 after warmup, and some JVM features
(runtime bytecode generation, dynamic proxies, unrestricted reflection)
behave differently or fail.

## The Closed-World Assumption

The fundamental difference: JIT discovers classes and methods lazily at
runtime; AOT must know the entire reachable program graph at build time. Any
code reachable only through reflection, JNI, resource loading, or dynamic
proxying is invisible to the analysis and will fail at runtime with
`ClassNotFoundException`/`IllegalAccessError` unless declared. Spring's
`RuntimeHintsRegistrar`, `reflect-config.json`, and
`@RegisterReflectionForBinding` exist to declare what the analysis cannot
see.

## Spring Boot 3 AOT

Spring Boot 3 ships build-time AOT processing: bean definitions, configuration
classes, and `BeanFactory` methods are pre-computed into generated source
(`target/spring-aot`), so the native image does not scan/scan the classpath
at startup. This is what makes Spring's runtime DI fast in native mode.
Features like component scanning still work, but conditional evaluation and
profiles happen at build time — a bean missing from the native image cannot
be re-added at runtime.

## What Commonly Breaks

- **Jackson**: POJOs without a no-arg constructor or without
  `@JsonDeserialize` metadata fail; register hints with
  `RuntimeHintsRegisterer` for each DTO.
- **Java serialization** and **dynamic proxies**: declare `proxy-config.json`.
- **Native libraries** (JDBC drivers that ship `.so`/`.dll`): need JNI config;
  PostgreSQL/MySQL drivers generally work out of the box.
- **Thread-local-heavy code** and `SecurityManager`: different behavior;
  `SecurityManager` is deprecated/removed in native mode.
- **Classpath scanning** at runtime: must be replaced with build-time
  registration; Spring Boot does this, libraries that scan at runtime do not.

## Build vs Runtime Trade-off

Native build adds 2–10 minutes and 4–16 GB of RAM to CI; the artifact is
platform-specific (linux/amd64 ≠ macos/arm64) so a CI matrix per target is
needed. Throughput: modern GraalVM (22+) approaches HotSpot C2 for steady
state, but C2/JIT still wins for very long-running, allocation-heavy services
on large heaps. The right call: native for short-lived/scale-out/containerized
edge workloads; JVM for hot, long-lived services where peak throughput rules.

## Observability and Debugging

Thread dumps (`jstack`) do not exist in native images; use `jcmd`-equivalent
`process-api` + `--enable-monitoring`, `SIGQUIT` stack traces, or
`-H:+ReportExceptionStackTraces`. JFR works, but some events depend on
reachability metadata. Build with `--no-fallback` to guarantee a true native
binary rather than silently falling back to a JVM build; keep the fallback
for dev.

## Failure Modes in Production

- One missing reflection hint → the first user who hits that endpoint gets a
  500; no compile error. Test the native binary in CI, not just the JVM jar.
- A dependency update silently drops/renames a native-image config; the
  native build succeeds but runtime fails. Version the reachability metadata.
- Memory regression: native images sized without `-Xmx`/`-XX:MaxRAMPercentage`
  inherit container limits poorly; set explicit limits.
- Startup looks fast but first-payload JSON serialization is slow if
  Jackson needs runtime bytecode for a new feature — pre-warm in CI.

## References

- GraalVM Native Image documentation
- Spring Boot 3 AOT / "Efficient Development of Native Images" guide
