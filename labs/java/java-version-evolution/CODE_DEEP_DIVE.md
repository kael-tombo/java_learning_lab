# Code Deep Dive — Version Evolution

## 1. Source Tour
- `java.lang.Record` (16+), `java.lang.Thread::ofVirtual` (21).
- `java.util.SequencedCollection` (21), `java.util.stream.Gatherer` (22+ preview→stable path).
- JEP index: openjdk.org/jeps.

## 2. Bytecode Deltas
- Records: `Record` attribute (17). `javap -v` diff 8 vs 17 class.
- Switch patterns: `tableswitch` on type ordinal + `checkcast` (21).
- Lambdas unchanged since 8 (`invokedynamic`), but JIT better.

## 3. Strong Encapsulation (17)
`--illegal-access=permit` removed; reflective JDK access → `InaccessibleObjectException`.
Fix audit: `jdeprscan --release 17 app.jar`, replace with `--add-opens` only interim.

## 4. Virtual Threads Internals
Carrier pool (ForkJoin) + continuations; blocking parks (unmount), no OS thread held.
Inspect: `jcmd <pid> Thread.dump_to_file threads.json`, `jfr jdk.VirtualThreadStart`.

## 5. ZGC Generational (21+)
`-XX:+UseZGC` defaults generational; colored pointers + load barriers.
Logs: `-Xlog:gc*` shows minor/major cycles sub-ms.

## 6. Compile/Release
```bash
javac --release 8 App.java   # old API
javac --release 21 App.java   # new APIs (records/patterns)
jdeps --release 21 --jdk-internals app.jar
```

## 7. Perf Flags by Era
- 8: `-XX:+UseG1GC` new; 11: ZGC exp; 17: strong encap; 21: `-Djdk.virtualThreadScheduler.*`.
- Always: `-Xlog:gc* -XX:+HeapDumpOnOutOfMemoryError`.

## 8. Refs
JEP 395/409/441/444 (records/sealed/patterns/vthreads), `java.lang.Thread` (21) javadoc.
