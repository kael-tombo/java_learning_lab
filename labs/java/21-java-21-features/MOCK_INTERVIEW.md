# Mock Interview Transcript: Java 21 Features

## Interviewer: Staff Engineer, Oracle
## Candidate: Senior Java developer
## Time: 45 minutes
## Focus: All Java 21 features, preview features, migration

---

**Q1: What are the main features delivered in Java 21?**

**Candidate**: Java 21 (LTS, September 2023) includes: Virtual Threads (JEP 444, final), Record Patterns (JEP 440, final), Pattern Matching for switch (JEP 441, final), Sequenced Collections (JEP 431), String Templates (JEP 430, preview), Structured Concurrency (JEP 453, preview), Scoped Values (JEP 446, preview), Unnamed Patterns and Variables (JEP 443, preview), Unnamed Classes and Instance Main Methods (JEP 445, preview).

**Interviewer**: What are Sequenced Collections? Why were they needed?

**Candidate**: Before Java 21, there was no unified interface for collections with a defined encounter order. List has get(index), Deque has getFirst/getLast, LinkedHashMap has no standard first/last access. SequencedCollection (and SequencedSet, SequencedMap) provides: `addFirst()`, `addLast()`, `getFirst()`, `getLast()`, `removeFirst()`, `removeLast()`, `reversed()`. This unifies ordered collection access.

**Interviewer**: Write an example of record pattern matching.

**Candidate**:
```java
record Location(double lat, double lon) {}
record Place(String name, Location loc) {}

void printLocation(Object obj) {
    if (obj instanceof Place(var name, Location(var lat, var lon))) {
        System.out.println(name + " at " + lat + ", " + lon);
    }
}
```

**Interviewer**: What about nested record patterns?

**Candidate**: Record patterns can be nested arbitrarily:
```java
void process(Order order) {
    if (order instanceof Order(String id, 
            Customer(var name, var tier), 
            Address(_, var city))) {  // _ is unnamed pattern
        System.out.println(name + " in " + city);
    }
}
```

**Interviewer**: What are unnamed patterns and variables (JEP 443)?

**Candidate**: You can use `_` instead of a variable name when you don't need the value:
```java
try { int x = Integer.parseInt(s); }
catch (NumberFormatException _) { System.out.println("Bad number"); }

if (obj instanceof Point(int x, _)) { System.out.println("x=" + x); }
```

**Interviewer**: Explain String Templates (preview in Java 21).

**Candidate**: String templates let you embed expressions in strings using `\{...}`:
```java
int x = 10, y = 20;
String s = STR."The sum of \{x} and \{y} is \{x + y}";
```
The `STR` template processor handles interpolation. Custom template processors can be created. This is more readable than concatenation or String.format.

**Interviewer**: Migration path from Java 17 to 21 — what are the risks?

**Candidate**: (1) Sealed class/interface migration — check all permits. (2) Records interacting with JPA/Hibernate — need tuning. (3) Virtual threads — replace synchronized with ReentrantLock. (4) Pattern matching — switch expressions exhaustiveness checked. (5) Remove `--illegal-access=permit` (removed in Java 17+). (6) JVM flags change — some GC flags deprecated. (7) Test all reflective access for module system compliance.

**Interviewer**: How do you enable preview features?

**Candidate**: `--enable-preview` both at compile time and runtime: `javac --release 21 --enable-preview`, `java --enable-preview -jar app.jar`. Preview features are subject to change and may be removed.

**Interviewer**: Final: Which of these features would you use in production immediately?

**Candidate**: Virtual Threads (final), Record Patterns (final), Pattern Matching for switch (final), Sequenced Collections (final) — all safe for production. String Templates (preview), Structured Concurrency (preview), Scoped Values (preview) — evaluate carefully. Unnamed patterns — use immediately as a convention (even if preview, it's non-breaking).

---

## Feedback

**Strengths**:
- Comprehensive knowledge of all Java 21 features
- Correct record pattern and unnamed pattern usage
- Practical migration concerns identified
- Understands preview vs final distinction

**Areas for Improvement**:
- Could discuss `Vector API` (incubator) status
- Might mention performance improvements in GC (ZGC on small heaps)

**Score**: 5/5 — Ready for Java 21 migration leadership
