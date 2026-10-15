| # | Front | Back |
|---|-------|------|
| 1 | Sizes of Java int, long, double? | int 4 bytes, long 8, double 8; all fixed by the JLS on every platform. |
| 2 | Sizes of byte, short, char, float? | byte 1, short 2, char 2 (UTF-16 unit), float 4. |
| 3 | How big is a boolean in Java? | JLS leaves it undefined; boolean[] stores one byte per element. |
| 4 | Why does `long x = 10000000000;` fail? | Literal exceeds int range; write 10000000000L. |
| 5 | Value of `7 / 2` vs `7 / 2.0`? | 3 (truncation) vs 3.5; one double operand widens the whole expression. |
| 6 | Value of `Integer.MAX_VALUE + 1`? | -2147483648; int arithmetic wraps silently, no exception. |
| 7 | How to detect int overflow safely? | Widen to long first, or use Math.addExact which throws on overflow. |
| 8 | Value of `'A' + 1`? | 66 as int; char widens to int in arithmetic. |
| 9 | Why does `b += 1` compile but `b = b + 1` fail for byte b? | Compound assignment includes an implicit cast; plain + widens to int. |
| 10 | `==` vs equals for Strings? | == compares references; equals compares content. Never use == for content. |
| 11 | When is `var x = 5;` legal? | Always with an initializer; `var x;` fails because nothing is inferable. |
| 12 | Can `var` change type later? | No; inferred type is fixed, `x = "s"` after `var x = 5` fails. |
| 13 | Precedence trap: `1 + 2 * 3`? | 7; * binds tighter. Parenthesize when unsure. |
| 14 | Short-circuit `&&` vs `&`? | && skips the right side when false; & always evaluates both. |
| 15 | What does `%` do with negatives: `-7 % 3`? | -1; sign follows the dividend in Java. |
| 16 | Integer vs floating division by zero? | 1/0 throws ArithmeticException; 1.0/0.0 gives Infinity. |
| 17 | What is stderr vs stdout in a CLI? | Results go to stdout; diagnostics to stderr so pipes stay clean. |
| 18 | How to read an int CLI arg safely? | Integer.parseInt inside try/catch NumberFormatException with a default. |
| 19 | Arrow switch expression syntax? | `switch (s/10) { case 10, 9 -> "A"; default -> "F"; }` yields a value. |
| 20 | Old switch fall-through pitfall? | Colon cases without break fall through; prefer arrow arms or explicit break. |
| 21 | Enhanced for over int[]? | `for (int s : scores)` reads each element; no index available. |
| 22 | When to use while vs for? | for for counted/indexed loops; while for condition-driven loops. |
| 23 | What does `break` vs `continue` do? | break exits the loop; continue skips to the next iteration. |
| 24 | instanceof pattern matching form? | `if (o instanceof String s)` binds s; stable since Java 16. |
| 25 | Four OOP pillars? | Encapsulation, inheritance, polymorphism, abstraction. |
| 26 | Encapsulation in one line? | Private state, public behavior; validate at the boundary. |
| 27 | Overriding vs overloading? | Overriding redefines an inherited method (runtime dispatch); overloading reuses a name with new params. |
| 28 | What does @Override buy you? | Compile-time check that a superclass method with that signature exists. |
| 29 | Single inheritance rule? | A class extends at most one superclass; interfaces are unlimited via implements. |
| 30 | Abstract class vs interface? | Abstract holds shared state/code; interface defines a capability with default/static helpers. |
| 31 | Interface fields are implicitly? | public static final constants; put behavior, not state, in interfaces. |
| 32 | First statement of a constructor? | super(...) or this(...); the compiler inserts super() otherwise. |
| 33 | private constructor use? | Utility classes and factories; blocks instantiation from outside. |
| 34 | Record Point(int x, int y) gives? | Final carrier with accessors, equals, hashCode, toString; immutable by convention. |
| 35 | Checked vs unchecked exceptions? | Checked (IOException) must be caught/declared; unchecked (RuntimeException) need not be. |
| 36 | NumberFormatException hierarchy? | Extends IllegalArgumentException extends RuntimeException: unchecked. |
| 37 | try-with-resources requirement? | Resource must implement AutoCloseable; close() runs automatically. |
| 38 | Multi-catch syntax? | `catch (IOException \| NumberFormatException e)`; alternatives must be unrelated types. |
| 39 | Does finally always run? | Yes after try/catch, barring System.exit or JVM crash; use for cleanup without resources API. |
| 40 | Catching Error (e.g. OutOfMemoryError)? | Do not catch in app code; fix the cause instead of swallowing JVM failures. |
| 41 | What is type erasure? | One Box class at runtime; `Box<String>` vs `Box<Integer>` share getClass. |
| 42 | Diamond operator purpose? | `new ArrayList<>()` infers from the left side; avoids repeating type args. |
| 43 | Raw type hazard? | `List xs = new ArrayList<String>()` compiles with warnings, fails later at runtime. |
| 44 | PECS mnemonic? | Producer extends, consumer super: `List<? extends Shape>` to read, `<? super Circle>` to write. |
| 45 | Can you `new T()` or `instanceof T`? | No; erasure removes T at runtime. Pass Class<T> or a factory instead. |
| 46 | Generic method syntax? | `<T> T first(List<T> xs)`; type param precedes the return type. |
| 47 | ArrayList.get(i) cost? | O(1); array-backed index access. |
| 48 | ArrayList add cost? | Amortized O(1); occasional O(n) resize copy. |
| 49 | HashMap get/put average cost? | O(1) average with a good hashCode; O(n) worst case on collision chains. |
| 50 | HashMap null handling? | One null key and null values allowed; TreeMap rejects null keys. |
| 51 | List.of(...) mutability? | Immutable; add throws UnsupportedOperationException. Use new ArrayList<>(...) to copy. |
| 52 | equals/hashCode contract? | Equal objects must share hashCode; violate it and HashMap lookups break. |
| 53 | Stream pipeline result for filter-even then x10 over 1..5? | [20, 40]; filter then map then toList. |
| 54 | Lazy vs eager stream ops? | Intermediate ops (filter/map) are lazy; terminal ops (toList/count) trigger work. |
| 55 | Can a stream be reused? | No; reusing a consumed stream throws IllegalStateException. Build a new one. |
| 56 | Lambda variable capture rule? | Captured locals must be final or effectively final. |
| 57 | Comparator lambda for sort by length? | `(x, y) -> Integer.compare(x.length(), y.length())`; stable: pear stays before kiwi. |
| 58 | Compile for release 21? | `javac --release 21 -encoding UTF-8 -d out Main.java`. |
| 59 | Run with classpath out and arg hi? | `java -cp out Main hi`; -cp sets where classes load from. |
| 60 | Classpath separator Windows vs Linux? | Semicolon on Windows, colon on Linux/macOS. |
