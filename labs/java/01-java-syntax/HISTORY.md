# Java Syntax — Evolution Across Versions

## Java 1.0 (1996)

The original syntax: classes, methods, primitives, `if`/`for`/`while`, exceptions, packages. Everything was verbose by modern standards. No generics, no autoboxing, no enhanced for-loop. Inner classes existed but were a compiler trick — no `.class` file support.

**Example pattern (pre-generics):**
```java
List names = new ArrayList();
names.add("Hello");
String name = (String) names.get(0); // Manual cast required
```

## Java 1.1 (1997)

Inner classes (including anonymous inner classes), JAR files, and the `assert` keyword (though not yet enabled by default).

## Java 1.2 (1998) — "Playground"

The `strictfp` keyword introduced to ensure consistent floating-point behavior across platforms.

## Java 1.4 (2002)

The `assert` keyword became fully functional (had to be enabled with `-ea`).

## Java 5 (2004) — Major Syntax Overhaul

The single biggest expansion of Java syntax:

| Feature | Syntax |
|---------|--------|
| Generics | `List<String>`, `Map<K, V>` |
| Enhanced for-loop | `for (T item : collection)` |
| Autoboxing/unboxing | `Integer x = 42;` |
| Varargs | `void method(String... args)` |
| Annotations | `@Override`, `@Deprecated` |
| Static import | `import static Math.PI;` |
| Enumerations | `enum Color { RED, GREEN, BLUE }` |
| Covariant return types | Subtype can return subtype |

## Java 7 (2011)

- Diamond operator: `List<String> list = new ArrayList<>();`
- Strings in `switch`: `switch (str) { case "hello": ... }`
- Binary literals: `int x = 0b1010;`
- Underscores in numeric literals: `int million = 1_000_000;`
- Multi-catch: `catch (IOException | SQLException e)`
- Try-with-resources: `try (Resource r = new Resource()) { ... }`

## Java 8 (2014) — Lambda Revolution

- Lambda expressions: `(x, y) -> x + y`
- Functional interfaces: `@FunctionalInterface`
- Method references: `String::length`, `System.out::println`
- Default methods in interfaces: `default void method() { }`
- Static methods in interfaces: `static void helper() { }`
- Optional type: `Optional<String>`

## Java 9 (2017)

- Private methods in interfaces
- Diamond operator with anonymous classes (refinement)
- Underscore `_` can no longer be used as an identifier

## Java 10 (2018)

- Local variable type inference: `var list = new ArrayList<String>();`
- `var` for local variables only (not fields, method params, or return types)

## Java 11 (2018) — LTS

- `var` in lambda parameters (implicit typing)
- `_` removed as an identifier (compilation error)

## Java 13/14 (2019-2020)

- Switch expressions (preview → standard in Java 14):
  ```java
  int days = switch (month) {
      case JAN, MAR, MAY, JUL, AUG, OCT, DEC -> 31;
      case FEB -> 28;
      default -> 30;
  };
  ```

## Java 14 (2020)

- Records (preview): `record Point(int x, int y) { }`
- Pattern matching for `instanceof` (preview):
  ```java
  if (obj instanceof String s) { System.out.println(s.length()); }
  ```
- Text blocks (preview → standard in Java 15): `""" ... """`

## Java 15 (2020)

- Text blocks (standard): multi-line string literals
- Sealed classes (preview): `sealed`, `non-sealed`, `permits`

## Java 16 (2021)

- Records (standard)
- Pattern matching for `instanceof` (standard)

## Java 17 (2021) — LTS

- Sealed classes (standard)
- Pattern matching for `switch` (preview)
- Enhanced pseudo-random number generators

## Java 21 (2023) — LTS

- Pattern matching for `switch` (standard)
- Record patterns (standard)
- String templates (preview): `STR."Hello \{name}"` — previewed in Java 21/22, withdrawn before Java 23 (no shipping JDK has it)
- Unnamed patterns and variables (preview): `case _ ->`
- Sequenced collections

## Syntax Stability Principle

Despite all these additions, code written in Java 1.0 syntax still compiles and runs on Java 21. All new features are *additive* — they never remove or change existing syntax rules. This backward compatibility is a cornerstone of Java's enterprise adoption.
