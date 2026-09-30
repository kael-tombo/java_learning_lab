# Core Java Learning Path

A practical, hands-on curriculum for learning Java from fundamentals to modern Java 21+ features. This section is designed to help you build strong programming foundations, improve code quality, and gain confidence with real-world Java exercises.

## Overview

This directory groups the foundational Java modules for the learning lab. It is intended to be used as a guided progression from beginner topics to advanced concepts such as concurrency, generics, reflection, and modern language features.

The goal is not only to understand syntax, but to develop good habits around:

- clean and readable code
- object-oriented design
- testing and debugging
- performance awareness
- practical Java tooling

## How to use this section

1. Start with the basics and complete each module in order.
2. Read the module README before writing code.
3. Practice the examples and complete the exercises.
4. Revisit advanced topics after you feel comfortable with the fundamentals.
5. Use the project folders and lab exercises to reinforce what you learn.

## Prerequisites

Before starting, make sure you have:

- Java 21 LTS or newer installed
- Maven 3.8+ or Gradle 7+ available
- An IDE such as IntelliJ IDEA, VS Code, or Eclipse
- Git for version control and project tracking

## Recommended learning path

### Beginner path
1. [01-java-basics](./01-java-basics)
2. [02-oop-concepts](./02-oop-concepts)
3. [03-collections-framework](./03-collections-framework)
4. [10-lambda-expressions](./10-lambda-expressions)

### Intermediate path
1. [04-streams-api](./04-streams-api)
2. [06-exception-handling](./06-exception-handling)
3. [07-file-io](./07-file-io)
4. [08-generics](./08-generics)
5. [09-annotations](./09-annotations)

### Advanced path
1. [05-concurrency](./05-concurrency)
2. [11-design-patterns](./11-design-patterns)
3. [12-java-21-features](./12-java-21-features)
4. [14-reflection-introspection](./14-reflection-introspection)
5. [15-jvm-internals](./15-jvm-internals)

> Use the folders inside this section as the source of truth. Some subfolders in this curriculum are exploratory or advanced extensions and may not follow the exact numbering in older materials.

## Module map

| Module | Folder | Focus | Difficulty |
| --- | --- | --- | --- |
| Java Basics | [01-java-basics](./01-java-basics) | Syntax, variables, control flow, methods | Beginner |
| OOP Concepts | [02-oop-concepts](./02-oop-concepts) | Classes, objects, inheritance, polymorphism | Beginner |
| Collections | [03-collections-framework](./03-collections-framework) | Lists, sets, maps, iteration | Intermediate |
| Streams API | [04-streams-api](./04-streams-api) | Functional processing and pipelines | Intermediate |
| Exception Handling | [06-exception-handling](./06-exception-handling) | Errors, try-catch, custom exceptions | Intermediate |
| File I/O | [07-file-io](./07-file-io) | Reading, writing, and managing files | Intermediate |
| Generics | [08-generics](./08-generics) | Reusable, type-safe code | Intermediate |
| Annotations | [09-annotations](./09-annotations) | Metadata and framework usage | Intermediate |
| Lambda Expressions | [10-lambda-expressions](./10-lambda-expressions) | Functional interfaces and lambdas | Intermediate |
| Design Patterns | [11-design-patterns](./11-design-patterns) | Reusable solutions to common problems | Advanced |
| Concurrency | [05-concurrency](./05-concurrency) | Threads, synchronization, executors | Advanced |
| Java 21 Features | [12-java-21-features](./12-java-21-features) | Virtual threads, pattern matching, modern APIs | Advanced |
| Reflection | [14-reflection-introspection](./14-reflection-introspection) | Runtime inspection and metadata-driven code | Advanced |
| JVM Internals | [15-jvm-internals](./15-jvm-internals) | Memory, bytecode, garbage collection basics | Advanced |

## Quick start

Use the commands below as a general pattern when working in a module folder:

```bash
# Confirm Java is installed
java -version

# Navigate to a module
cd 01-core-java/01-java-basics

# If the module uses Maven
mvn clean test

# If the module uses Gradle
./gradlew test
```

If a specific module contains its own instructions, follow that module's README before running commands.

## Learning outcomes

By the end of this section, you should be able to:

- write clean Java programs using core language syntax
- design classes and apply object-oriented principles
- use collection types appropriately
- work with streams and functional programming concepts
- handle exceptions and file operations safely
- apply generics and annotations effectively
- reason about concurrency and thread safety
- leverage modern Java 21+ capabilities with confidence

## Progress tracker

- [x] [Java Basics](./01-java-basics)
- [x] [OOP Concepts](./02-oop-concepts)
- [x] [Collections Framework](./03-collections-framework)
- [x] [Streams API](./04-streams-api)
- [x] [Concurrency](./05-concurrency)
- [x] [Exception Handling](./06-exception-handling)
- [x] [File I/O](./07-file-io)
- [x] [Generics](./08-generics)
- [x] [Annotations](./09-annotations)
- [x] [Lambda Expressions](./10-lambda-expressions)
- [x] [Design Patterns](./11-design-patterns)
- [x] [Java 21 Features](./12-java-21-features)
- [x] [Reflection & Introspection](./14-reflection-introspection)
- [x] [JVM Internals](./15-jvm-internals)

## Best practices for this learning path

- Prefer understanding concepts before copying code.
- Rebuild examples from memory to reinforce learning.
- Use small, focused exercises instead of large, vague ones.
- Keep code readable and well named.
- Practice debugging with a clear mental model of execution flow.
- Review Java documentation when a concept feels unclear.

## Useful references

- [Oracle Java Tutorials](https://docs.oracle.com/javase/tutorial/)
- [Java SE Documentation](https://docs.oracle.com/en/java/)
- [Baeldung Java Tutorials](https://www.baeldung.com/)
- [LeetCode Java Track](https://leetcode.com/)
- [Exercism Java Track](https://exercism.org/tracks/java)

## Next step

Start with [01-java-basics](./01-java-basics) and work through the modules in sequence. If you already know the basics, jump to the advanced topics after completing the foundational exercises.
