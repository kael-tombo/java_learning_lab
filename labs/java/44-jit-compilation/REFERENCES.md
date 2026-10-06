# References: JIT Compilation

- **Tiered Compilation in HotSpot** (OpenJDK) - https://wiki.openjdk.org/display/HotSpot/TieredCompilation
- **JIT Compiler Overview** - https://docs.oracle.com/en/java/javase/21/vm/compiler-overview.html
- **C2 Sea-of-Nodes IR** (Cliff Click) - https://www.oracle.com/technetwork/java/javase/tech/c2-ir-20062024.html
- **JITWatch** (AdoptOpenJDK) - https://github.com/AdoptOpenJDK/jitwatch
- **Deoptimization in HotSpot** - https://wiki.openjdk.org/display/HotSpot/Deoptimization
- **Intrinsic Methods in HotSpot** - https://github.com/openjdk/jdk/blob/master/src/hotspot/share/classfile/vmIntrinsics.hpp
- **On-Stack Replacement (OSR)** - https://wiki.openjdk.org/display/HotSpot/OnStackReplacement
- **PrintCompilation Output Explained** - https://blogs.oracle.com/johnomics/post/java-printcompilation-output-explained: JIT Compilation

## Official Documentation
- [JIT Compilation in HotSpot](https://docs.oracle.com/en/java/javase/21/vm/java-virtual-machine-guide.pdf)
- [HotSpot Compilation Flags Reference](https://docs.oracle.com/en/java/javase/21/docs/specs/man/java.html)
- [Java Performance Tuning Guide](https://docs.oracle.com/en/java/javase/21/gc/tuning.html)

## JEPs
- JEP 163: Improve Tiered Compilation
- JEP 295: Ahead-of-Time Compilation
- JEP 317: Experimental Java-Based JIT Compiler (Graal)
- JEP 165: Compiler Control

## Books
- *Java Performance: The Definitive Guide* by Scott Oaks
- *Optimizing Java* by Ben Evans and Chris Newland
- *Java Performance Companion* by Charlie Hunt

## Articles
- [HotSpot Architecture](https://www.infoq.com/articles/OpenJDK-HotSpot-Architecture/)
- [JIT Inlining Deep Dive](https://www.baeldung.com/jvm-method-inlining)
- [Escape Analysis in Java](https://www.baeldung.com/java-escape-analysis)

## Tools
- `-XX:+PrintCompilation` — compilation event log
- `-XX:+PrintInlining` — inlining decisions
- `-XX:+PrintAssembly` — disassembled native code
- `-XX:+PrintIntrinsics` — intrinsic replacement log
- `async-profiler` — CPU profiling with JIT information
- `JITWatch` — GUI for analyzing JIT compilation logs

## Source Code
- `src/hotspot/share/opto/` (C2 compiler)
- `src/hotspot/share/c1/` (C1 compiler)
- `src/hotspot/share/runtime/` (compilation broker, MDO, nmethod)
