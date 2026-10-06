# Tests: LRU Cache

## Test Files

Unit tests live in `src/test/java/`.

## Test Coverage

- get/put correctness on known sequences
- Eviction order: tail is the least-recently-used key
- move-to-front on hit and on update
- Capacity boundary (exactly at, one over)
- Resize semantics: drain tail, never exceed capacity
- Hit/miss accounting
- Invariant check after every operation: map size == list size

## Run with

```bash
# Using Maven
mvn test

# Using Gradle
gradle test

# Using javac directly
javac -d out src/test/java/**/*.java src/main/java/**/*.java
java -cp out org.junit.platform.console.ConsoleLauncher --scan-classpath
```
