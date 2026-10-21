# SOLUTION — Exercise Solutions

## Exercise 1: StringUtils TDD

`java
public class StringUtils {
    public static String reverse(String input) {
        if (input == null) return null;
        return new StringBuilder(input).reverse().toString();
    }
    public static boolean isPalindrome(String input) {
        if (input == null) return false;
        String cleaned = input.replaceAll("\\s+", "").toLowerCase();
        return cleaned.equals(reverse(cleaned));
    }
    public static int countVowels(String input) {
        if (input == null) return 0;
        return (int) input.toLowerCase().chars()
            .filter(c -> "aeiou".indexOf(c) >= 0)
            .count();
    }
}
`

## Exercise 2: ProductService Mock

See source files in src/test/java/... for the full Mockito-based test suite.

## Exercise 3: TemperatureConverter

`java
@ParameterizedTest
@CsvSource({
    "0, 32",
    "100, 212",
    "-40, -40",
    "37, 98.6"
})
void celsiusToFahrenheit(double c, double expectedF) {
    assertEquals(expectedF, converter.celsiusToFahrenheit(c), 0.1);
}
`

Solutions for remaining exercises follow the same pattern.
