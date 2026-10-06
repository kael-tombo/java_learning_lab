# History of Class Loading in Java

## Java 1.0 (1996): Basic Class Loading
Java included a simple ClassLoader with delegation. Applets could define custom ClassLoaders to load classes over the network. The `Class.forName()` method provided reflective class loading.

## Java 2 (1998): ClassLoader Hierarchy Formalized
The three-level hierarchy was formalized: Bootstrap → Extension (later Platform) → Application. `URLClassLoader` was introduced for loading from JARs and URLs. The delegation model was documented as part of the Java security architecture.

## Java 5 (2004): java.lang.instrument
The `java.lang.instrument` package (available since JDK 5, predating the JEP
process) introduced the `java.lang.instrument` package and `ClassFileTransformer`. This allowed Java agents to transform class bytecode at load time, enabling tools like profilers, AOP frameworks, and debuggers without modifying source code.

## Java 6 (2006): Pluggable Annotation Processing
JSR 269 introduced the annotation processing API, allowing compile-time code generation based on annotations.

## Java 7 (2011): invokedynamic (JSR 292)
JEP 276 introduced `invokedynamic` and `MethodHandle`. This was the foundation for the Nashorn JavaScript engine and Java 8's lambda expressions. The constant pool gained support for `CONSTANT_MethodHandle_info`, `CONSTANT_MethodType_info`, and `CONSTANT_InvokeDynamic_info`.

## Java 8 (2014): Lambda Metafactory
`LambdaMetafactory` used invokedynamic to implement lambda expressions. Each lambda site uses a bootstrap method that generates an anonymous class or method handle at runtime. String concatenation was also migrated to invokedynamic.

## Java 9 (2017): Module System
JEP 261 introduced the module system (Project Jigsaw). The Extension ClassLoader was renamed to Platform ClassLoader. Modular JARs could declare their dependencies, and the class loading architecture was updated to respect module boundaries.

## Java 14 (2020): CDS Archives
JEP 310: Application Class-Data Sharing allowed application classes to be archived for faster startup. JEP 350: Dynamic CDS Archives extended this to capture loaded classes at application exit.

## Java 21 (2023): Class Loading Enhancements
Continued improvements to CDS and class loading performance. The Platform ClassLoader no longer uses a flat class path.
