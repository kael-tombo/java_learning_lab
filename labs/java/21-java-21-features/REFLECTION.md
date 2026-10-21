# Reflection: Java 21 Features

## Self-Assessment Questions

1. **Virtual threads**: Can you explain how virtual threads achieve scalability without changing the familiar `Thread` API? How would you identify a workload where virtual threads provide no benefit?

2. **Pattern matching**: Think about your last three Java projects. How many `instanceof`-cast patterns did they contain? How would converting them to pattern matching change the code's readability and safety?

3. **Sequenced Collections**: Before Java 21, how did you access the last element of a `LinkedHashSet`? How many different approaches did the codebase use for different collection types?

4. **String Templates**: Consider a codebase that builds SQL queries, HTML, or JSON by string concatenation. How many security vulnerabilities might be present? A template processor was designed to prevent them — but the feature was previewed in JDK 21/22 and withdrawn before JDK 23. How would you close the same gap with `PreparedStatement` and escaping today?

5. **Structured Concurrency**: In your experience with multithreaded code, how often have you encountered orphaned threads, leaked executors, or race conditions from missed task coordination? Would structured concurrency have prevented these?

## Code Quality Reflection

Compare the following:

**Before (Java 8-17 style)**:
```java
if (obj instanceof String) {
    String s = (String) obj;
    if (s.length() > 5) {
        // process
    }
}
```

**After (Java 21 style)**:
```java
if (obj instanceof String s && s.length() > 5) {
    // process
}
```

The second version combines type check, cast, variable binding, and condition into a single expression. Reflection question: Does this conciseness improve or reduce comprehension for developers unfamiliar with pattern matching?

## Adoption Considerations

Consider a real-world migration to Java 21:
- What training would your team need?
- Which features would provide the most immediate value?
- What legacy patterns (e.g., Visitor pattern, reactive streams) could you deprecate?
- How would you convince management to invest in the migration?

## Personal Learning

1. **Most surprising insight**: What aspect of virtual threads or pattern matching was most counterintuitive?
2. **Most practical feature**: Which feature would you apply first in your daily work?
3. **Most challenging concept**: Which feature requires the most mental model adjustment?

## Learning Progress

Rate your understanding from 1 (novice) to 5 (expert) on each:
- [ ] Virtual threads: creating, executing, and managing
- [ ] Pinning detection and mitigation
- [ ] Pattern matching for instanceof
- [ ] Switch expressions with type patterns
- [ ] Record patterns and nested deconstruction
- [ ] Sequenced Collections API
- [ ] String Templates history (JEP 430/459, withdrawn before JDK 23) and `String.formatted` substitutes
- [ ] StructuredTaskScope lifecycle management
- [ ] Combining features in a single application

Areas where you rated below 3 should be revisited. Focus your study on these areas before moving to the next lab.
