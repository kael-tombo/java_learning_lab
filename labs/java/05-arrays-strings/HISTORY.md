# Arrays & Strings — Evolution Across Java Versions

## Java 1.0 (1996)

Arrays: single and multi-dimensional, `length` field, bounds checking, covariant type system. `String`: immutable, UTF-16, String pool, `StringBuffer` (synchronized mutable strings). No `StringBuilder`. `+` concatenation compiled to `StringBuffer.append()`.

## Java 5 (2004)

- **Enhanced for-loop**: `for (String s : array)` — cleaner iteration over arrays and Iterables
- **Varargs**: `String...` internally creates array
- **`StringBuilder`**: Non-synchronized alternative to `StringBuffer` (faster for single-threaded use)

## Java 6 (2006)

- **`String` optimization**: `-XX:+UseStringCache` for hash code caching
- **`isEmpty()`** method added to `String`

## Java 7 (2011)

- **String in switch**: `switch(str) { case "hello": ... }`
- **String pool moved**: From PermGen to heap (enables GC of interned strings)
- **`Objects.toString()`, `Objects.equals()`**: Null-safe string utilities

## Java 8 (2014)

- **`String.join()`**: `String.join(", ", "a", "b", "c")` → "a, b, c"
- **`StringJoiner`** class: More flexible joining with prefix/suffix
- **Stream API**: `Arrays.stream(array)` creates streams from arrays
- **`String.chars()`**: IntStream of character codes

## Java 9 (2017)

- **Compact Strings**: `String` uses `byte[]` instead of `char[]` — Latin-1 stored as single byte per char, UTF-16 only when needed. Reduces heap memory by ~50% for Latin-1 strings.

## Java 10 (2018)

- **`List.copyOf()`, `Set.copyOf()`, `Map.copyOf()`**: Create immutable copies from arrays (via `Arrays.asList()`)

## Java 11 (2018) — LTS

- **`String.repeat(n)`**: `"ha".repeat(3)` → "hahaha"
- **`String.isBlank()`**: Checks if string is empty or whitespace-only
- **`String.strip()`, `stripLeading()`, `stripTrailing()`**: Unicode-aware whitespace removal
- **`String.lines()`**: Stream of lines from multi-line string
- **`String.indent(n)`**: Adjusts indentation

## Java 12 (2019)

- **`String.transform(Function)`**: Applies function to string

## Java 13 (2019)

- **`String.stripIndent()`** and **`String.translateEscapes()`**: Used internally for text blocks

## Java 15 (2020)

- **Text blocks**: `""" ... """` — multi-line string literals with indentation preservation
- **`String.formatted(args)`**: Instance method equivalent to `String.format()`

## Java 16 (2021)

- **`Stream.toList()`**: Creates unmodifiable list from stream — common pattern with array-originated streams
- **Records**: `record` classes can be used as array elements

## Java 21 (2023)

- **String templates** (preview): `STR."Hello \{name}"` — string interpolation with safety; previewed in Java 21/22, withdrawn before Java 23
- **Sequenced collections**: `SequencedCollection`, `SequencedSet`, `SequencedMap`

## Performance Trends

String optimizations have been a major focus: compact strings (Java 9) reduced memory, text blocks (Java 15) improved readability, and string templates (Java 21, previewed and then withdrawn before Java 23) targeted concatenation boilerplate — a gap `String.formatted` still fills.
