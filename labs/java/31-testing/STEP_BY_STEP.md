# Testing — Step-by-Step Tutorial

## Step 1: Set Up Your Project

Create a Maven project with JUnit 5 and Mockito dependencies:

`xml
<dependencies>
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.2</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-junit-jupiter</artifactId>
        <version>5.10.0</version>
        <scope>test</scope>
    </dependency>
</dependencies>
`

## Step 2: Write Your First Test

Create src/test/java/com/example/CalculatorTest.java:

`java
package com.example;
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {
    Calculator calc = new Calculator();

    @Test
    void add() {
        assertEquals(5, calc.add(2, 3));
    }
}
`

Run with: mvn test or click the green triangle in your IDE.

## Step 3: Use BeforeEach

Extract setup to avoid duplication:

`java
private Calculator calc;

@BeforeEach
void setUp() {
    calc = new Calculator();
}
`

## Step 4: Test for Exceptions

`java
@Test
void divideByZero() {
    assertThrows(ArithmeticException.class,
        () -> calc.divide(1, 0));
}
`

## Step 5: Add Parameterized Tests

`java
@ParameterizedTest
@CsvSource({"1,2,3", "10,20,30"})
void addTest(double a, double b, double expected) {
    assertEquals(expected, calc.add(a, b));
}
`

## Step 6: Mock External Dependencies

Add Mockito to test a service class:

`java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock UserRepository repo;
    @InjectMocks UserService service;

    @Test
    void findById() {
        when(repo.findById(1L)).thenReturn(Optional.of(new User(1L, "test@test.com", "Test")));
        Optional<User> result = service.findById(1L);
        assertTrue(result.isPresent());
    }
}
`

## Step 7: Follow TDD for a New Feature

1. **Write the test first** — it fails (RED)
2. **Implement the feature** — test passes (GREEN)
3. **Refactor** — test still passes (REFACTOR)

## Step 8: Run Tests in CI

Configure GitHub Actions or Jenkins to run mvn test on every push. Use JaCoCo for coverage reports.
