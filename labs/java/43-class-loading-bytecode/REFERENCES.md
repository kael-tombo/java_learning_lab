# References: Class Loading & Bytecode

- **JVM Specification Chapter 4 (Class File Format)** - https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-4.html
- **ASM 9.x User Guide** - https://asm.ow2.io/asm4-guide.pdf
- **MethodHandle API** (Oracle) - https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/invoke/package-summary.html
- **JSR 292: invokedynamic** - https://jcp.org/en/jsr/detail?id=292
- **Nest-Based Access (JEP 181)** - https://openjdk.org/jeps/181
- **LambdaMetafactory Internals** - https://cr.openjdk.org/~briangoetz/lambda/lambda-translation.html
- **Bytecode Wrangling with ASM** (InfoQ) - (link removed)
- **Invokedynamic 101** (Brian Goetz) - (link removed) Class Loading & Bytecode

## Official Documentation
- [ClassLoader Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ClassLoader.html)
- [JVM Specification — Class File Format](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-4.html)
- [JVM Specification — Bytecode Instruction Set](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-6.html)
- [ASM Library Homepage](https://asm.ow2.io/)
- [MethodHandle Javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/invoke/MethodHandle.html)

## JEPs
- JEP 276: Dynamic Linking of Language-Defined Methods (invokedynamic)
- JEP 140: Limited Privileges for Reflection
- JEP 261: Module System
- JEP 350: Dynamic CDS Archives

## Books
- *The Java Virtual Machine Specification* (Java SE Edition)
- *Java Bytecode: A Comprehensive Guide* by Kaushik Sathupadi
- *Pro Java 9 Module Systems* by Paul Deitel
- *ASM 4.0: A Java Bytecode Engineering Library* by Eric Bruneton

## Tools
- `javap`: Java class file disassembler
- `jclasslib`: Class file viewer
- `Bytecode Viewer`: Multi-tool bytecode viewer
- `javassist`: Bytecode manipulation library

## Source Code
- `java.base/java/lang/ClassLoader.java`
- `java.base/java/lang/invoke/LambdaMetafactory.java`
- ASM: `org.objectweb.asm:*`
