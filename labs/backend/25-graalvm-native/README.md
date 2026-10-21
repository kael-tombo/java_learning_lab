# Lab 25: GraalVM Native Images

## Overview
GraalVM Native Images compile Java applications ahead-of-time (AOT) into native executables. Learn reflection configuration, resource bundles, GraalVM reachability, and building native images with Spring Boot.

## Topics Covered
- GraalVM architecture (SubstrateVM, Truffle)
- AOT compilation vs JIT
- Spring Boot AOT engine
- Native image building with Maven/Gradle
- Reflection configuration (reachability metadata)
- Resource and resource bundle config
- Serialization config
- Dynamic proxy config
- Native image testing
- Performance characteristics

## Prerequisites
- Java 21+
- Spring Boot 3.3+
- GraalVM SDK installed (optional)

## Getting Started
`ash
mvn -Pnative native:compile
./target/backend25  # Native executable
`

## Key Dependencies
`xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.3.0</version>
</dependency>
<plugin>
    <groupId>org.graalvm.buildtools</groupId>
    <artifactId>native-maven-plugin</artifactId>
</plugin>
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\25-graalvm-native "THEORY.md") @"
# Theory: GraalVM Native Images

## 1. AOT vs JIT Compilation

- **JIT (Just-in-Time)**: Code compiled at runtime. Advantages: adaptive optimization, profile-guided. Disadvantages: warmup time, larger memory.
- **AOT (Ahead-of-Time)**: Code compiled before runtime. Advantages: instant startup, lower memory, smaller deployable. Disadvantages: fewer optimizations, no adaptive deoptimization.

## 2. Closed World Assumption

Native images assume all code is known at build time:
- No dynamic class loading
- No runtime bytecode generation
- Reflection must be declared
- Resources must be declared
- Serialization must be declared

## 3. SubstrateVM

The native image runtime:
- Minimal VM (no JIT compiler)
- Custom GC (low-pause, small footprint)
- Direct compilation to machine code
- Optional: PGO (Profile-Guided Optimization) for better performance

## 4. Spring Boot AOT Engine

Spring Boot 3.x includes an AOT engine that:
- Processes Spring configuration at build time
- Generates reflection configuration for beans
- Processes conditionals (@ConditionalOnClass, etc.)
- Prepares Hibernate proxies
- Optimizes Spring AOP
- Generates native-image.properties

## 5. Reachability Metadata

GraalVM uses reachability metadata:
- reflect-config.json: Reflection declarations
- resource-config.json: Resource declarations
- serialization-config.json: Serialization declarations
- proxy-config.json: Dynamic proxy declarations
- jni-config.json: JNI declarations
- predefine-classes-config.json: Class predefinition
