# Testing — Evolution Across Versions

## JUnit Timeline

| Version | Year | Key Features |
|---------|------|-------------|
| JUnit 1 | 1997 | Framework by Kent Beck and Erich Gamma, simple test runner |
| JUnit 3 | 2000 | Test by inheritance (extends TestCase), naming conventions |
| JUnit 4 | 2006 | Annotations (@Test, @Before, @After), runners, assumptions |
| JUnit 5 | 2017 | Modular architecture, Jupiter API, extensions, lambdas |

## Mockito Timeline

| Version | Year | Key Features |
|---------|------|-------------|
| Mockito 1 | 2008 | Simple mocking with when/thenReturn |
| Mockito 2 | 2017 | Improved stub behavior, lenient mode, Java 8+ |
| Mockito 3 | 2019 | Java 11+, Android, new inline mock maker |
| Mockito 4 | 2020 | Java 8 baseline, API cleanup |
| Mockito 5 | 2022 | Java 11 baseline, enhanced mocking |

## Build Tool Integration

- **Maven Surefire Plugin** (2004): Runs JUnit tests in Maven builds
- **Gradle Test Task** (2012): First-class test support in Gradle
- **JaCoCo** (2011): De facto standard code coverage tool
- **ArchUnit** (2017): Tests architectural constraints

## JUnit Jupiter vs Vintage

JUnit 5 introduced the Jupiter programming model while retaining backward compatibility via the Vintage engine:
`xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.2</version>
</dependency>
`

## Modern Testing (2020s)

- **Testcontainers**: Integration tests with throwaway Docker containers
- **WireMock**: HTTP stub server for API testing
- **Awaitility**: Async testing with fluent wait conditions
- **Selenide**: Concise Selenium wrapper for UI testing
