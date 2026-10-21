# Testing — Exercises

## Exercise 1: Write Tests First (TDD)

Implement a StringUtils class with these methods. Write the test FIRST for each method:

1. String reverse(String input) — reverses a string
2. oolean isPalindrome(String input) — checks if input reads same forward/backward
3. int countVowels(String input) — counts vowels (a, e, i, o, u)

**Starter test:**
`java
@Test void reverseBasic() { assertEquals("cba", StringUtils.reverse("abc")); }
`

## Exercise 2: Mock a Repository

Given a ProductRepository interface with indById, indAll, and save methods, create:
1. ProductService that uses the repository
2. Mock-based tests for the service covering success and failure paths

## Exercise 3: Parameterized Tests

Write parameterized tests for a TemperatureConverter:
- celsiusToFahrenheit(double celsius) — formula: F = C * 9/5 + 32
- ahrenheitToCelsius(double fahrenheit) — formula: C = (F - 32) * 5/9

Test at least: 0°C, 100°C, -40°C, 37°C (body temperature)

## Exercise 4: Testing Exceptions

For the Calculator class, write tests that verify:
- Division by zero throws ArithmeticException
- Factorial of negative throws IllegalArgumentException
- sqrt of negative throws IllegalArgumentException

## Exercise 5: Verify Interactions

Create a LoggerService that delegates to a LogWriter. Write tests that verify:
- log("msg") calls logWriter.write("msg")
- When write throws, the exception is caught and logged via errorHandler

## Exercise 6: Integration Test

Write an integration test that:
1. Creates a temporary file
2. Writes data to it
3. Reads it back
4. Verifies the content
5. Cleans up the file

## Exercise 7: Test Coverage

Use JaCoCo to measure coverage on the Calculator class. Write additional tests until you reach 100% line and 100% branch coverage.
