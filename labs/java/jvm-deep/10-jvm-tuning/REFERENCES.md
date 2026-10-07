# JVM Tuning — References

## Official Documentation
- [Java Collections Framework Overview](https://docs.oracle.com/javase/tutorial/collections/)
- [HashMap JavaDoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html)
- [Java Language Specification, Chapter 17](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [JEP Index](https://openjdk.org/jeps/0)

## Books
- **Effective Java, 4th Edition** — Joshua Bloch
- **Java Concurrency in Practice** — Brian Goetz
- **Modern Java in Action** — Raoul-Gabriel Urma
- **Core Java, 12th Edition** — Cay S. Horstmann
- **Algorithm Design Manual** — Steven Skiena
- **Introduction to Algorithms (CLRS)** — Cormen, Leiserson, Rivest, Stein

## Research Papers
- "The Java Memory Model" — Manson, Pugh, Adve (POPL 2005)
- "Simple, Fast, and Practical Non-Blocking and Blocking Concurrent Queue Algorithms" — Michael, Scott (1996)
- "A Scalable Lock-Free Hash Table" — Triplett, McKenney, Walpole, Wienand (2010)

## Blog Posts and Articles
- [Baeldung: Java Collections Guide](https://www.baeldung.com/java-collections)
- Inside Java: Collections Framework
- [Shipilev: Java Memory Model Pragmatics](https://shipilev.net/blog/2016/close-encounters-of-jmm-kind/)
- [Mechanical Sympathy](https://mechanical-sympathy.blogspot.com/)

## Tools
- [JMH (Java Microbenchmark Harness)](https://github.com/openjdk/jmh)
- [JOL (Java Object Layout)](https://openjdk.org/projects/code-tools/jol/)
- [async-profiler](https://github.com/async-profiler/async-profiler)
- [VisualVM](https://visualvm.github.io/)
- [Eclipse MAT](https://eclipse.dev/mat/)
- [GCeasy](https://gceasy.io/)

## Related Labs
- Previous lab in module
- Next lab in module
- Performance Deep Dive labs
- Concurrency Deep Dive labs
- JVM Deep Dive labs


## Further Exploration

### Additional Reading
- Review the companion files in this micro-lab for deeper understanding
- Complete the exercises in EXERCISES.md to apply your knowledge
- Build the MINI_PROJECT to cement the concepts
- Test yourself with QUIZ.md and FLASHCARDS.md
- Practice with INTERVIEW.md questions for job preparation

### Related Concepts
- equals() and hashCode() contracts in Java
- Comparable and Comparator interfaces for ordering
- Iterator and Iterable patterns for traversal
- Stream API for functional-style operations
- Serialization for object persistence
- Cloning and defensive copying

### Best Practices
1. Always choose the right data structure for your use case
2. Consider initial capacity for large datasets
3. Use immutable objects as keys in hash-based collections
4. Synchronize externally or use concurrent variants for thread safety
5. Profile before optimizing - don't guess about performance
6. Document ordering guarantees your code depends on
7. Use interfaces (Map, List, Set) for variable declarations
8. Prefer composition over inheritance for custom collections
9. Override toString() for meaningful debug output
10. Consider memory implications of your collection choices

### Common Pitfalls to Avoid
- Using mutable objects as keys in HashMap/HashSet
- Iterating and modifying without using iterator methods
- Assuming iteration order without checking documentation
- Using LinkedList when random access is needed
- Ignoring initial capacity for large collections
- Forgetting to override both equals() and hashCode()
- Using == instead of equals() for key comparison
- Not handling ConcurrentModificationException properly

### Next Steps
1. Implement a custom version of this data structure from scratch
2. Benchmark against the standard Java implementation
3. Analyze memory usage with JOL (Java Object Layout)
4. Profile performance with async-profiler
5. Write comprehensive unit tests covering all edge cases
6. Design a thread-safe variant for concurrent use cases
7. Research alternative implementations in other languages
8. Apply the concept to a real-world project

### Key Takeaways Summary
- Understand the internal mechanics and algorithmic complexity
- Know the performance characteristics and memory footprint
- Recognize appropriate use cases and selection criteria
- Master common patterns and anti-patterns
- Develop debugging intuition for related issues
- Build mental models that transfer to other concepts

### Discussion Questions
1. How would you design this differently if starting from scratch?
2. What are the limits of this approach in terms of scale?
3. How does this concept interact with modern hardware (CPU caches, NUMA)?
4. What alternatives exist in other programming languages?
5. How would you implement this for a distributed system?

### Code Review Checklist
- [ ] Correct equals() and hashCode() implementations for keys
- [ ] Appropriate initial capacity and load factor selection
- [ ] Proper synchronization or concurrent variant for shared state
- [ ] No concurrent modification during iteration
- [ ] Immutable or effectively immutable key objects
- [ ] Consistent use of interface types for declarations
- [ ] Proper null handling (or documentation of non-null requirement)
- [ ] toString() implementation for debugging
- [ ] Serializable implementation if needed
- [ ] Performance considerations documented
