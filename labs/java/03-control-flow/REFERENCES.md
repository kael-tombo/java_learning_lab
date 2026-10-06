# Control Flow — References

## Official Documentation
- [Java Language Specification — Chapter 14: Blocks and Statements](https://docs.oracle.com/javase/specs/jls/se21/html/jls-14.html)
- [Oracle Tutorial — Control Flow Statements](https://docs.oracle.com/javase/tutorial/java/nutsandbolts/flow.html)
- [Oracle Tutorial — Branching Statements](https://docs.oracle.com/javase/tutorial/java/nutsandbolts/branch.html)

## Books
- *Core Java Volume I* — Cay S. Horstmann (Chapter 3: Control Flow)
- *Effective Java* — Joshua Bloch
- *Clean Code* — Robert C. Martin (Chapter 3: Functions — control flow structure)

## JEPs
- JEP 325: Switch Expressions (Preview) — Java 12
- JEP 354: Switch Expressions (Second Preview) — Java 13
- JEP 361: Switch Expressions — Java 14 (Standard)
- JEP 406: Pattern Matching for switch (Preview) — Java 17
- JEP 427: Pattern Matching for switch (Third Preview) — Java 19
- JEP 433: Pattern Matching for switch (Fourth Preview) — Java 20
- JEP 441: Pattern Matching for switch — Java 21
- JEP 440: Record Patterns — Java 21

## Deep Dive References
- [JVMS §3 — Compiling Java Control Flow](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-3.html) — How if/switch/loops compile to bytecode
- [JEP 441: Pattern Matching for switch](https://openjdk.org/jeps/441) — Pattern matching in switch (Java 21)
- [C2 Branch Prediction Heuristics](https://wiki.openjdk.org/display/HotSpot/BranchPrediction) — OpenJDK Wiki on branch prediction
- [Aleksey Shipilëv: Loop Optimization](https://shipilev.net/jvm/anatomy-quarks/5-loop-optimization/) — JVM loop optimization techniques
- [Branch Prediction in Modern CPUs](https://en.wikipedia.org/wiki/Branch_predictor) — Branch predictor overview

## Tools
- [SpotBugs](https://spotbugs.github.io/) — Detects switch fall-through, unreachable code
- [PMD](https://pmd.github.io/) — Control flow analysis
- [Checkstyle](https://checkstyle.org/) — Coding standard enforcement
