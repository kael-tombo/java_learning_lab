# Exercises: Java 21 Features

## Exercise 1: Virtual Thread Web Crawler

Build a web crawler that fetches pages concurrently using virtual threads. Each URL fetch should run in its own virtual thread. Limit the total number of concurrent fetches using a semaphore.

```java
// TODO: Implement a web crawler that:
// 1. Takes a list of URLs
// 2. Fetches each URL in a virtual thread
// 3. Extracts links from the HTML
// 4. Continues crawling discovered links
// 5. Stops after discovering 1000 unique URLs
// 6. Uses StructuredTaskScope for error handling
```

## Exercise 2: Pattern Matching Expression Evaluator

Extend the expression evaluator from the code deep dive with more operations and simplification rules:

```java
// Add support for:
// 1. Subtract operation
// 2. Divide operation
// 3. Variable expression (evaluate with a Map<String, Integer>)
// 4. Simplify: a + 0 = a, a * 0 = 0, a * 1 = a
// 5. Simplify: -(a + b) = -a + -b
```

## Exercise 3: Sequenced Collection Task Scheduler

```java
// Build a task scheduler using SequencedCollection:
// 1. Tasks can be added with priorities (HIGH, MEDIUM, LOW)
// 2. HIGH tasks are processed first (added to front)
// 3. LOW tasks are processed last (added to end)
// 4. MEDIUM tasks are processed in order
// 5. Implement getNext(), addTask(), and reversed() for audit log
```

## Exercise 4: Safe SQL Builder after the String Templates Withdrawal

> **Status**: String Templates were previewed in JDK 21/22 and withdrawn before JDK 23 — the exercise is reframed to what compiles today.

```java
// Historically this exercise asked for a custom StringTemplate processor for SQL.
// Without that (withdrawn) API, build the same safety yourself:
// 1. Build parameterized queries with PreparedStatement (executeUpdate/executeQuery)
// 2. Support IN clauses with variable-length parameters (dynamic ? placeholders)
// 3. Prevent SQL injection — never concatenate user values into the SQL string
// 4. Support WHERE, JOIN, and subquery patterns
// 5. Log the generated SQL and parameters for debugging

// Bonus: Support type-safe queries where column types are validated
```

## Exercise 5: Structured Concurrency Service Aggregator

```java
// Build a service aggregator that:
// 1. Fetches data from 3 microservices concurrently
// 2. Has a 2-second timeout for the entire operation
// 3. If any service fails, cancels the others and returns a partial result
// 4. Logs which services succeeded and which failed
// 5. Uses ShutdownOnFailure policy
```

## Exercise 6: Pattern Matching JSON Parser

```java
// Given a sealed hierarchy for JSON values:
sealed interface JsonValue permits JsonNull, JsonString, JsonNumber, JsonObject, JsonArray {}

// Write a formatter using pattern matching switch that:
// 1. Formats JsonNull as "null"
// 2. Formats JsonString with escaped quotes
// 3. Formats JsonNumber with proper decimal formatting
// 4. Formats JsonObject with indented key-value pairs
// 5. Formats JsonArray with elements separated by commas
```

## Exercise 7: Virtual Thread Rate Limiter

```java
// Implement a rate limiter for virtual thread execution:
// 1. Allow at most 100 requests per second
// 2. Use a token bucket algorithm
// 3. Queue excess requests (don't reject)
// 4. Measure actual throughput vs. virtual thread count
// 5. Compare with a platform-thread-based implementation
```

## Exercise 8: Comprehensive Review

Build a chat server that combines all Java 21 features:

```java
// Requirements:
// 1. Each client connection handled by a virtual thread
// 2. Messages are parsed using pattern matching switch
// 3. Chat rooms are managed using SequencedCollection
// 4. Message formatting uses String.formatted (String Templates were withdrawn before JDK 23)
// 5. User authentication runs in a StructuredTaskScope
// 6. Handle at least 10,000 concurrent connections
// 7. Handle disconnection with proper cleanup
```

## Solutions

Solutions should be placed in a `solutions/` subdirectory. Try to solve each exercise yourself before looking at the reference implementations. The exercises build on each other — completing them in order provides the most learning benefit.
