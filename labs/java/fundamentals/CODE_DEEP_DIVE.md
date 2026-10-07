# Code Deep Dive — Java Fundamentals (fundamentals)

Six runnable snippets on the parts of the language where the compiler accepts code that does not behave the way it reads: numeric types, control flow, OOP dispatch, exceptions, generics erasure and class files.

How to use this file: each snippet is a complete single-file program. Save it as `<ClassName>.java`, compile with `javac --release 21 -proc:none <ClassName>.java`, then run the command shown under it. Every snippet targets Java 21 without preview features and uses only the JDK. The "Observed output" blocks were produced by compiling and running the snippets on JDK 23.0.1 (Windows), with `--release 21`.

## Snippet 1: types & operators

Java's primitive arithmetic is defined by fixed-width two's-complement rules, not by mathematical rules. `int` addition wraps around on overflow, `/` truncates toward zero, `%` takes the sign of the dividend, and a compound assignment such as `b += 10` silently inserts a narrowing cast back to the left-hand type. Boxed types add one more layer: `Integer` values from -128 to 127 come from a shared cache, so `==` on boxes compares references that happen to be identical only inside that range.

```java
public class TypesAndOperators {
    public static void main(String[] args) {
        int big = Integer.MAX_VALUE;
        System.out.println("MAX_VALUE + 1 = " + (big + 1));
        try {
            Math.addExact(big, 1);
        } catch (ArithmeticException e) {
            System.out.println("addExact: " + e.getMessage());
        }

        System.out.println("-7 / 2 = " + (-7 / 2)
                + ", -7 % 2 = " + (-7 % 2)
                + ", floorMod(-7, 2) = " + Math.floorMod(-7, 2));

        byte b = 120;
        b += 10; // compiles: means b = (byte) (b + 10)
        System.out.println("byte 120 += 10 -> " + b);

        System.out.println("0.1 + 0.2 = " + (0.1 + 0.2)
                + ", equals 0.3? " + (0.1 + 0.2 == 0.3));

        char c = 'a';
        c++;
        System.out.println("char after ++: " + c + ", 'a' + 1 = " + ('a' + 1));

        System.out.println("-16 >> 2 = " + (-16 >> 2)
                + ", -16 >>> 28 = " + (-16 >>> 28));

        Integer x1 = 127, x2 = 127, y1 = 128, y2 = 128;
        System.out.println("127 == 127: " + (x1 == x2)
                + ", 128 == 128: " + (y1 == y2)
                + ", 128 equals 128: " + y1.equals(y2));
    }
}
```

Run: `java TypesAndOperators`

Observed output:
```text
MAX_VALUE + 1 = -2147483648
addExact: integer overflow
-7 / 2 = -3, -7 % 2 = -1, floorMod(-7, 2) = 1
byte 120 += 10 -> -126
0.1 + 0.2 = 0.30000000000000004, equals 0.3? false
char after ++: b, 'a' + 1 = 98
-16 >> 2 = -4, -16 >>> 28 = 15
127 == 127: true, 128 == 128: false, 128 equals 128: true
```

Run: `java -XX:AutoBoxCacheMax=1000 TypesAndOperators`

Observed output with the box cache widened to 1000 (same program, only the last line changes):
```text
MAX_VALUE + 1 = -2147483648
addExact: integer overflow
-7 / 2 = -3, -7 % 2 = -1, floorMod(-7, 2) = 1
byte 120 += 10 -> -126
0.1 + 0.2 = 0.30000000000000004, equals 0.3? false
char after ++: b, 'a' + 1 = 98
-16 >> 2 = -4, -16 >>> 28 = 15
127 == 127: true, 128 == 128: true, 128 equals 128: true
```

**Pitfall:** `==` on `Integer` passes every unit test that uses small ids and then fails in production when an id reaches 128. The second run shows the result is not even a property of the code: `-XX:AutoBoxCacheMax` changes what `128 == 128` evaluates to. Compare boxes with `equals`, `Objects.equals`, or unbox first.

## Snippet 2: control flow

The old `switch` statement jumps to a label and then keeps executing every following statement until it meets `break`, so a missing `break` runs the next case too. The arrow form (`case X ->`) never falls through and, as a `switch` expression, must be exhaustive: for a sealed interface the compiler checks that every permitted subtype is covered, so adding a new record makes callers fail to compile instead of failing at run time. Java 21 also allows type patterns, record deconstruction patterns and `when` guards in `case` labels; a labeled `break` leaves an outer loop in one step.

```java
public class ControlFlow {
    sealed interface Shape permits Circle, Square, Rect {}
    record Circle(double r) implements Shape {}
    record Square(double side) implements Shape {}
    record Rect(double w, double h) implements Shape {}

    @SuppressWarnings("fallthrough")
    static String oldSwitch(int n) {
        StringBuilder sb = new StringBuilder();
        switch (n) {
            case 1: sb.append("one ");
            case 2: sb.append("two ");
            case 3: sb.append("three "); break;
            default: sb.append("other ");
        }
        return sb.toString().trim();
    }

    static String arrowSwitch(int n) {
        return switch (n) {
            case 1 -> "one";
            case 2 -> "two";
            case 3 -> {
                String prefix = "thr";
                yield prefix + "ee";
            }
            default -> "other";
        };
    }

    static double area(Shape s) {
        return switch (s) {
            case Circle c -> Math.PI * c.r() * c.r();
            case Square q -> q.side() * q.side();
            case Rect(double w, double h) -> w * h;
        };
    }

    static String describe(Object o) {
        return switch (o) {
            case null -> "null";
            case Integer i when i > 100 -> "big int " + i;
            case Integer i -> "int " + i;
            case String s -> "string of length " + s.length();
            default -> o.getClass().getSimpleName();
        };
    }

    public static void main(String[] args) {
        for (int n = 1; n <= 4; n++) {
            System.out.println("n=" + n + "  old: '" + oldSwitch(n) + "'  arrow: '" + arrowSwitch(n) + "'");
        }

        System.out.printf("circle(1)=%.4f square(3)=%.1f rect(2,5)=%.1f%n",
                area(new Circle(1)), area(new Square(3)), area(new Rect(2, 5)));

        for (Object o : new Object[] {7, 500, "hello", 2.5, null}) {
            System.out.println("describe -> " + describe(o));
        }

        int foundI = -1, foundJ = -1;
        search:
        for (int i = 1; i <= 5; i++) {
            for (int j = i; j <= 5; j++) {
                if (i * j == 12) {
                    foundI = i;
                    foundJ = j;
                    break search;
                }
            }
        }
        System.out.println("first pair with product 12: " + foundI + " x " + foundJ);
    }
}
```

Run: `java ControlFlow`

Observed output:
```text
n=1  old: 'one two three'  arrow: 'one'
n=2  old: 'two three'  arrow: 'two'
n=3  old: 'three'  arrow: 'three'
n=4  old: 'other'  arrow: 'other'
circle(1)=3.1416 square(3)=9.0 rect(2,5)=10.0
describe -> int 7
describe -> big int 500
describe -> string of length 5
describe -> Double
describe -> null
first pair with product 12: 3 x 4
```

**Pitfall:** the `n=1` line shows `oldSwitch(1)` returning `one two three`: the case for 1 never says `break`, so execution slides into cases 2 and 3. The compiler accepts it, and only `javac -Xlint:fallthrough` points at it (this snippet silences it with `@SuppressWarnings("fallthrough")` to keep the demonstration quiet). Prefer arrow cases; a `default` branch on a sealed-type switch is also a trap, because it hides the compile error you would otherwise get when a new subtype is added.

## Snippet 3: OOP pillars

Encapsulation (a private field behind methods), inheritance, polymorphism and abstraction come together in one rule: instance method calls are dispatched on the runtime class of the object, while field accesses are resolved on the static type of the reference. A constructor runs the superclass constructor first, and during that call the object already has its final runtime class, so an overridden method can run before the subclass's field initializers have executed.

```java
public class OopPillars {
    abstract static class Account {
        private long balanceCents;          // encapsulated: only reachable through methods
        protected final String id;

        Account(String id, long openingCents) {
            this.id = id;
            this.balanceCents = openingCents;
            audit("opened");                // calls an overridable method from the constructor
        }

        void audit(String what) {
            System.out.println("  [" + kind() + "] " + id + " " + what);
        }

        abstract String kind();             // abstraction: subclasses must supply it

        abstract long fee(long amountCents);

        final void withdraw(long amountCents) {
            long total = amountCents + fee(amountCents);
            if (total > balanceCents) {
                throw new IllegalStateException(
                        "insufficient funds: need " + total + ", have " + balanceCents);
            }
            balanceCents -= total;
        }

        long balance() {
            return balanceCents;
        }
    }

    static class Checking extends Account {
        private String label = "main";      // assigned only AFTER super(...) returns

        Checking(String id, long openingCents) {
            super(id, openingCents);
        }

        @Override String kind() { return "checking/" + label; }
        @Override long fee(long amountCents) { return 25; }
    }

    static class Premium extends Checking {
        Premium(String id, long openingCents) {
            super(id, openingCents);
        }

        @Override String kind() { return "premium"; }
        @Override long fee(long amountCents) { return 0; }
    }

    static class Parent {
        String name = "parent-field";
        String who() { return "parent-method"; }
    }

    static class Child extends Parent {
        String name = "child-field";        // hides, does not override
        @Override String who() { return "child-method"; }
    }

    public static void main(String[] args) {
        System.out.println("constructing:");
        Account[] accounts = {new Checking("C-1", 1000), new Premium("P-1", 1000)};

        for (Account a : accounts) {
            a.withdraw(500);
            System.out.println(a.id + " (" + a.kind() + ") balance after withdraw(500) = " + a.balance());
        }

        try {
            accounts[0].withdraw(10_000);
        } catch (IllegalStateException e) {
            System.out.println("rejected: " + e.getMessage());
        }

        Parent p = new Child();
        System.out.println("p.who() = " + p.who());
        System.out.println("p.name  = " + p.name);
        System.out.println("((Child) p).name = " + ((Child) p).name);
    }
}
```

Run: `java OopPillars`

Observed output:
```text
constructing:
  [checking/null] C-1 opened
  [premium] P-1 opened
C-1 (checking/main) balance after withdraw(500) = 475
P-1 (premium) balance after withdraw(500) = 500
rejected: insufficient funds: need 10025, have 475
p.who() = child-method
p.name  = parent-field
((Child) p).name = child-field
```

**Pitfall:** in the output the first audit line reads `[checking/null]`, not `[checking/main]`. `Account`'s constructor called `kind()`, dispatch went to `Checking.kind()`, and `label` still held its default `null` because the subclass initializer had not run. Never call overridable methods from a constructor; make the method `final`/`private` or move the call out of construction. The last three lines show the other half of the rule: `p.name` is resolved against `Parent`, so the hidden field wins even though `p.who()` reaches `Child`.

## Snippet 4: exceptions

`try`-with-resources closes resources in reverse order of declaration and runs before any `catch` block. When both the body and a `close()` throw, the body's exception is the primary one and the `close()` failures are attached to it via `addSuppressed`. A `finally` block always runs, and a `return` inside it replaces both a pending return value and a pending exception.

```java
public class Exceptions {
    static class Res implements AutoCloseable {
        final String name;
        final boolean failOnClose;

        Res(String name, boolean failOnClose) {
            this.name = name;
            this.failOnClose = failOnClose;
            System.out.println("  open " + name);
        }

        @Override
        public void close() {
            System.out.println("  close " + name);
            if (failOnClose) {
                throw new IllegalStateException("close failed: " + name);
            }
        }
    }

    @SuppressWarnings("finally")
    static int finallyReturnSwallows() {
        try {
            throw new RuntimeException("this exception is lost");
        } finally {
            return 42;
        }
    }

    static int finallyCannotChangeReturnValue() {
        int x = 1;
        try {
            return x;       // the value 1 is already saved
        } finally {
            x = 99;         // too late to affect it
        }
    }

    static void loadConfig(String text) {
        try {
            Integer.parseInt(text);
        } catch (NumberFormatException e) {
            throw new IllegalStateException("config value is not a number: '" + text + "'", e);
        }
    }

    @SuppressWarnings("try")
    public static void main(String[] args) {
        System.out.println("try-with-resources:");
        try (Res a = new Res("A", true); Res b = new Res("B", true)) {
            System.out.println("  body runs");
            throw new IllegalArgumentException("body failed");
        } catch (Exception e) {
            System.out.println("caught: " + e);
            for (Throwable s : e.getSuppressed()) {
                System.out.println("  suppressed: " + s);
            }
        }

        System.out.println("finallyReturnSwallows() = " + finallyReturnSwallows());
        System.out.println("finallyCannotChangeReturnValue() = " + finallyCannotChangeReturnValue());

        try {
            loadConfig("12x");
        } catch (IllegalStateException e) {
            System.out.println("caught: " + e.getMessage());
            System.out.println("cause : " + e.getCause());
        }

        for (String s : new String[] {"7", null, "seven"}) {
            try {
                System.out.println("parsed " + Integer.parseInt(s));
            } catch (NumberFormatException | NullPointerException e) {
                System.out.println("multi-catch: " + e.getClass().getSimpleName());
            }
        }
    }
}
```

Run: `java Exceptions`

Observed output:
```text
try-with-resources:
  open A
  open B
  body runs
  close B
  close A
caught: java.lang.IllegalArgumentException: body failed
  suppressed: java.lang.IllegalStateException: close failed: B
  suppressed: java.lang.IllegalStateException: close failed: A
finallyReturnSwallows() = 42
finallyCannotChangeReturnValue() = 1
caught: config value is not a number: '12x'
cause : java.lang.NumberFormatException: For input string: "12x"
parsed 7
multi-catch: NumberFormatException
multi-catch: NumberFormatException
```

**Pitfall:** `finallyReturnSwallows()` returned 42 and the `RuntimeException` vanished without a trace, no log line and no stack trace. A `return`, `break` or `continue` in `finally` discards the in-flight exception; javac warns about it only under `-Xlint:finally`. Keep `finally` for cleanup that cannot complete abruptly, and use try-with-resources so close failures end up as suppressed exceptions rather than replacing the real error.

## Snippet 5: generics intro

Generics are checked by the compiler and then erased: `List<String>` and `List<Integer>` are the same class at run time, and the compiler inserts a `checkcast` wherever a generic return value is assigned to a concrete type. A raw type switches the compile-time check off for the call, so a wrong element can enter the list unnoticed and the failure shows up later, at a different line, on the reading side.

```java
import java.util.ArrayList;
import java.util.List;

public class GenericsIntro {
    static class Box<T> {
        private T value;

        Box(T value) { this.value = value; }
        T get() { return value; }
        void set(T value) { this.value = value; }
    }

    @SuppressWarnings({"rawtypes", "unchecked"})
    static void sneakIn(List strings) {
        strings.add(42);                      // no check: the parameter is a raw List
    }

    static <T extends Comparable<T>> T largest(List<T> items) {
        T best = items.get(0);
        for (T item : items) {
            if (item.compareTo(best) > 0) {
                best = item;
            }
        }
        return best;
    }

    public static void main(String[] args) {
        List<String> names = new ArrayList<>();
        names.add("ann");
        sneakIn(names);
        System.out.println("size after sneakIn = " + names.size() + " (no error so far)");

        try {
            String second = names.get(1);     // compiler-inserted checkcast String fails here
            System.out.println("second = " + second);
        } catch (ClassCastException e) {
            System.out.println("ClassCastException at the read site: " + e.getMessage());
        }

        List<Integer> ints = new ArrayList<>();
        System.out.println("same runtime class? " + (names.getClass() == ints.getClass()));

        Box<Integer> box = new Box<>(10);
        box.set(box.get() + 5);
        System.out.println("box = " + box.get());

        System.out.println("largest(3, 9, 4) = " + largest(List.of(3, 9, 4)));
        System.out.println("largest(pear, apple) = " + largest(List.of("pear", "apple")));
    }
}
```

Run: `java GenericsIntro`

Observed output:
```text
size after sneakIn = 2 (no error so far)
ClassCastException at the read site: class java.lang.Integer cannot be cast to class java.lang.String (java.lang.Integer and java.lang.String are in module java.base of loader 'bootstrap')
same runtime class? true
box = 15
largest(3, 9, 4) = 9
largest(pear, apple) = pear
```

**Pitfall:** the corrupting call (`sneakIn`) and the exception (`names.get(1)`) are in different places, and the stack trace only points at the reader. This is heap pollution, and it is what raw types and unchecked casts cause. Treat every `unchecked`/`rawtypes` warning as a place where the type system stopped protecting you, and confine them to one small method with a justified `@SuppressWarnings`.

## Snippet 6: JVM & bytecode

`javac` turns each class into a `.class` file that starts with the magic number `0xCAFEBABE`, a minor/major version pair (major 65 means Java 21, and `--release` controls it), a constant pool, and then methods as bytecode for a stack machine. The JVM only loads class files whose major version it knows. The snippet reads its own helper class from the class path and decodes the header, and `javap -c -p` then shows the instructions `javac` emitted for two small methods, including the `invokedynamic` that Java 9+ uses for string concatenation.

```java
import java.io.DataInputStream;
import java.io.IOException;

public class JvmBytecode {
    public static void main(String[] args) throws IOException {
        try (DataInputStream in = new DataInputStream(
                JvmBytecode.class.getResourceAsStream("Calc.class"))) {
            int magic = in.readInt();
            int minor = in.readUnsignedShort();
            int major = in.readUnsignedShort();
            int constantPoolCount = in.readUnsignedShort();
            System.out.printf("magic=0x%08X minor=%d major=%d (Java %d) constant_pool_count=%d%n",
                    magic, minor, major, major - 44, constantPoolCount);
        }
        System.out.println("Calc.sum(2, 3) = " + Calc.sum(2, 3));
        System.out.println("Calc.greet(\"jvm\") = " + Calc.greet("jvm"));
    }
}

class Calc {
    static int sum(int a, int b) {
        int t = a + b;
        return t * 2;
    }

    static String greet(String name) {
        return "hi " + name;
    }
}
```

Run: `java JvmBytecode`

Observed output:
```text
magic=0xCAFEBABE minor=0 major=65 (Java 21) constant_pool_count=35
Calc.sum(2, 3) = 10
Calc.greet("jvm") = hi jvm
```

Run: `javap -c -p Calc`

Observed output (bytecode of `Calc`):
```text
Compiled from "JvmBytecode.java"
class Calc {
  Calc();
    Code:
       0: aload_0
       1: invokespecial #1                  // Method java/lang/Object."<init>":()V
       4: return

  static int sum(int, int);
    Code:
       0: iload_0
       1: iload_1
       2: iadd
       3: istore_2
       4: iload_2
       5: iconst_2
       6: imul
       7: ireturn

  static java.lang.String greet(java.lang.String);
    Code:
       0: aload_0
       1: invokedynamic #7,  0              // InvokeDynamic #0:makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;
       6: areturn
}
```

**Pitfall:** a class file is only as portable as its major version. A JVM refuses a class whose major version is newer than it supports with `UnsupportedClassVersionError`, which is what happens when a build server runs a newer JDK without `--release` and the result is deployed to an older runtime. To see the exact failure without installing another JDK, patch the major-version bytes of `Calc.class` to 99 and load it:
```text
magic=0xCAFEBABE minor=0 major=99 (Java 55) constant_pool_count=35
Exception in thread "main" java.lang.UnsupportedClassVersionError: Calc has been compiled by a more recent version of the Java Runtime (class file version 99.0), this version of the Java Runtime only recognizes class file versions up to 67.0
	at java.base/java.lang.ClassLoader.defineClass1(Native Method)
	at java.base/java.lang.ClassLoader.defineClass(ClassLoader.java:1026)
```
(Produced by overwriting bytes 6-7 of `Calc.class` with `0x0063`. Compile with `--release N` for the oldest runtime you deploy to, not just `-source`/`-target`.)

## Pitfalls summary

| Topic | Concrete failure | How to catch it |
|---|---|---|
| types & operators | `Integer == Integer` is true up to 127 and false at 128 | compare with `equals`; use `Math.addExact` where wrapping is a bug |
| control flow | missing `break` makes `oldSwitch(1)` return `one two three` | arrow cases; `-Xlint:fallthrough` |
| OOP pillars | overridable method in a constructor sees `label == null` | call only `final`/`private` methods from constructors |
| exceptions | `return` in `finally` erases the exception | `-Xlint:finally`; try-with-resources |
| generics intro | raw `List` lets an `Integer` into a `List<String>`; failure appears at `get` | no raw types; read `unchecked` warnings |
| JVM & bytecode | class file major version newer than the runtime fails to load | `javac --release <oldest deployed Java>` |
