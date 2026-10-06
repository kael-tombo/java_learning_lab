# History of JIT Compilation in Java

## Java 1.0 (1996): Pure Interpreter
The first JVM had no JIT compiler — all bytecode was interpreted. Performance was approximately 10x slower than C++.

## Java 1.1 (1997): Symantec JIT
Symantec contributed a JIT compiler that improved performance to approximately 2-3x slower than C++. This was a simple JIT with minimal optimization.

## Java 1.3 (2000): HotSpot JVM
Sun acquired HotSpot from Longview Technologies. HotSpot featured adaptive optimization: the JVM profiles running code and only JIT-compiles hot methods. This is where "HotSpot" gets its name.

## Java 1.4 (2002): Server/Client Compilers
HotSpot offered two configurations:
- Client compiler (C1): fast startup, basic optimizations
- Server compiler (C2): slower startup, aggressive optimizations (developed by Sun's JVM team)

## Java 6 (2006): Tiered Compilation (Experimental)
Tiered compilation was introduced experimentally, allowing the VM to start with C1 and transition to C2 as code warmed up. It was not enabled by default until later.

## Java 7 (2011): Tiered Compilation (Default)
Tiered compilation (improved by JEP 163, and on by default since 8) on server-class machines. The JVM now uses C1 for fast startup and transitions to C2 for peak performance.

## Java 8 (2014): Lambda Inlining
Lambda expressions introduced new inlining challenges. The JIT had to inline through invokedynamic call sites and function interface wrappers.

## Java 9 (2017): Ahead-of-Time Compilation (Experimental)
JEP 295 introduced `jaotc`, an experimental AOT compiler using the Graal compiler. This added AOT support for reduced warmup time.

## Java 17 (2021): C2 Deprecation Warnings
GraalVM's JIT compiler was proposed as a replacement for C2, though this didn't happen. C2 remains the primary production compiler.

## Java 21 (2023): Continued Optimizations
Ongoing improvements to escape analysis, inlining heuristics, and vectorization (Project Panama / Vector API).
