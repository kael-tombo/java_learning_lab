# EXERCISES: Architectural Decisions & ArchUnit Fitness Functions
## Lab 19 | Production Engineering Academy

---

## Exercise 1: Write an Architecture Decision Record (ADR)

### Scenario
Your team needs to choose a distributed caching solution for an active-active multi-region e-commerce catalog.
Options:
1. Multi-cluster Redis with manual replication.
2. Amazon DynamoDB Global Tables with DAX accelerator.
3. Hazelcast distributed in-memory data grid.

### Tasks
1. Identify 3 critical decision drivers (e.g. cross-region latency, cost, failover mechanics).
2. Author a complete ADR in Markdown using the Nygard template from `CODE_DEEP_DIVE.md`.
3. Fill out Context, Decision Drivers, Considered Options with pros/cons, Outcome, and Consequences.
4. Categorize as Type 1 or Type 2 decision.

---

## Exercise 2: Implement an ArchUnit Architectural Fitness Rule in JUnit

### Tasks
1. Add ArchUnit dependency to Maven `pom.xml`: `com.tngtech.archunit:archunit-junit5:1.3.0`.
2. Write an ArchRule enforcing that:
   - No class in `..controller..` directly calls `@Repository` methods.
   - All classes in `..service..` must be annotated with `@Service`.
   - Utility classes must have private constructors.
3. Introduce an intentional violation (e.g. inject repository directly into a controller).
4. Run `mvn test`: observe that the ArchUnit test fails and prints the exact offending class and line number in the console!
