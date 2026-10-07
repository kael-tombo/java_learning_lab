# Code Deep Dive - Records, Sealed Classes & Patterns (records-sealed-patterns)

Six topics, each with a short mechanism note, a complete snippet, the output observed when it was run, and one pitfall.

Every snippet is JDK-only. Each was extracted from this file, compiled with `javac --release 21 -proc:none` (no preview features), run on JDK 23, and the output pasted verbatim. Language features used and the release in which each became final: records (JEP 395, Java 16), `instanceof` patterns (JEP 394, Java 16), sealed classes (JEP 409, Java 17), pattern matching for `switch` (JEP 441, Java 21), record patterns (JEP 440, Java 21).

## Snippet 1: record canonical constructors

A record declares its components in the header, and the compiler derives a private final field and a public accessor per component, a canonical constructor taking all components in order, and `equals`, `hashCode` and `toString` (generated through the `ObjectMethods` bootstrap method). You may write the canonical constructor out in full, but then you must assign every field yourself; any other constructor has to start with `this(...)`, so all construction funnels through the canonical one.

The demo shows an extra delegating constructor, an explicit canonical constructor that copies a list, an overridden accessor, and the exact meaning of record `equals` for `double` and array components.

```java
import java.util.List;

public class RecordCanonicalDemo {

    record Point(int x, int y) {
        Point() {
            this(0, 0); // non-canonical constructors must delegate
        }
    }

    record Tags(String owner, List<String> values) {
        Tags(String owner, List<String> values) { // explicit canonical constructor
            this.owner = owner;
            this.values = List.copyOf(values);
        }

        @Override
        public String owner() { // accessor override: stored field is unchanged
            return owner.toUpperCase();
        }
    }

    record Measure(double value) {}

    record Samples(double[] data) {}

    public static void main(String[] args) {
        Point a = new Point(3, 4);
        Point b = new Point(3, 4);
        System.out.println(a + " equals " + b + " -> " + a.equals(b) + ", same hashCode -> " + (a.hashCode() == b.hashCode()));
        System.out.println("delegating constructor -> " + new Point());

        List<String> source = new java.util.ArrayList<>(List.of("x"));
        Tags tags = new Tags("ada", source);
        source.add("y");
        System.out.println("owner() -> " + tags.owner() + ", toString -> " + tags);

        System.out.println("0.0 vs -0.0 equal -> " + new Measure(0.0).equals(new Measure(-0.0)));
        System.out.println("NaN vs NaN equal -> " + new Measure(Double.NaN).equals(new Measure(Double.NaN)));

        Samples s1 = new Samples(new double[] {1.0, 2.0});
        Samples s2 = new Samples(new double[] {1.0, 2.0});
        System.out.println("arrays with same contents equal -> " + s1.equals(s2));
        System.out.println("same instance equal -> " + s1.equals(s1));
    }
}
```

Observed output (`java RecordCanonicalDemo`):

```text
Point[x=3, y=4] equals Point[x=3, y=4] -> true, same hashCode -> true
delegating constructor -> Point[x=0, y=0]
owner() -> ADA, toString -> Tags[owner=ada, values=[x]]
0.0 vs -0.0 equal -> false
NaN vs NaN equal -> true
arrays with same contents equal -> false
same instance equal -> true
```

**Pitfall:** record `equals` is component-wise but shallow. An array component is compared with the array's own `equals` (identity), so two `Samples` holding equal contents are not equal, `Set<Samples>` lookups fail, and `toString` prints `[D@...` rather than the contents. Use a `List<Double>` (copied with `List.copyOf`) or override `equals`, `hashCode` and `toString` using `Arrays.equals`/`Arrays.hashCode`/`Arrays.toString`. Also note that the `double` rule above (`Double.compare` semantics, so `0.0` and `-0.0` differ) differs from `==`.

## Snippet 2: compact constructors

A compact constructor omits the parameter list: its implicit parameters have the component names, and the compiler appends the field assignments after your body. That is why the body may validate and also reassign the parameters (`lo = hi`) to normalize them, but may not assign `this.lo` (a compile error). A throw inside the body prevents the instance from existing at all.

```java
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class CompactConstructorDemo {

    record Range(int lo, int hi) {
        Range {
            if (lo > hi) { // normalise by reassigning the parameters
                int tmp = lo;
                lo = hi;
                hi = tmp;
            }
        }
    }

    record Name(String value) {
        Name {
            Objects.requireNonNull(value, "value");
            value = value.strip();
            if (value.isEmpty()) {
                throw new IllegalArgumentException("blank name");
            }
        }
    }

    record Team(List<String> members) {
        Team {
            if (members.isEmpty()) {
                throw new IllegalArgumentException("no members");
            }
        }
    }

    record SafeTeam(List<String> members) {
        SafeTeam {
            members = List.copyOf(members); // copy first, then validate the copy
            if (members.isEmpty()) {
                throw new IllegalArgumentException("no members");
            }
        }
    }

    public static void main(String[] args) {
        System.out.println(new Range(5, 2));
        System.out.println(new Name("  Ada  "));

        try {
            new Name("   ");
        } catch (IllegalArgumentException e) {
            System.out.println("rejected: " + e.getMessage());
        }
        try {
            new Name(null);
        } catch (NullPointerException e) {
            System.out.println("rejected: NPE " + e.getMessage());
        }

        List<String> shared = new ArrayList<>(List.of("ann", "bob"));
        Team team = new Team(shared);
        SafeTeam safe = new SafeTeam(shared);
        shared.clear();
        System.out.println("Team after caller clears list     -> " + team);
        System.out.println("SafeTeam after caller clears list -> " + safe);
    }
}
```

Observed output (`java CompactConstructorDemo`):

```text
Range[lo=2, hi=5]
Name[value=Ada]
rejected: blank name
rejected: NPE value
Team after caller clears list     -> Team[members=[]]
SafeTeam after caller clears list -> SafeTeam[members=[ann, bob]]
```

**Pitfall:** the compact constructor checks the invariant once, at construction, and `final` only freezes the reference. `Team` accepted a non-empty list, the caller then cleared the same list, and the record now violates "has members" without any exception (see the `Team` line above). Copy mutable inputs with `List.copyOf`, `Set.copyOf`, `Map.copyOf` before validating, as `SafeTeam` does.

## Snippet 3: sealed permits

`sealed` restricts which classes may directly extend or implement a type. Each permitted subtype must declare exactly one of `final` (records and enums are implicitly final), `sealed` (continues the restriction) or `non-sealed` (explicitly reopens the branch). When all permitted subtypes live in the same compilation unit, the `permits` clause may be omitted and is inferred. The restriction is enforced by the JVM as well as `javac`, and is visible to reflection through `Class.isSealed()` and `Class.getPermittedSubclasses()`.

```java
import java.util.Arrays;

public class SealedHierarchyDemo {

    sealed interface Shape permits Circle, Rect, Polygon {}

    record Circle(double r) implements Shape {}

    record Rect(double w, double h) implements Shape {}

    non-sealed static class Polygon implements Shape {} // reopened: anyone may extend Polygon

    static final class Triangle extends Polygon {}

    sealed interface Result {} // permits inferred from the nested declarations below

    record Ok(int value) implements Result {}

    record Err(String message) implements Result {}

    static String names(Class<?>[] classes) {
        return Arrays.stream(classes).map(Class::getSimpleName).toList().toString();
    }

    public static void main(String[] args) {
        System.out.println("Shape sealed? " + Shape.class.isSealed());
        System.out.println("Shape permits " + names(Shape.class.getPermittedSubclasses()));
        System.out.println("Result sealed? " + Result.class.isSealed());
        System.out.println("Result permits " + names(Result.class.getPermittedSubclasses()));
        System.out.println("Polygon sealed? " + Polygon.class.isSealed());
        System.out.println("Polygon.getPermittedSubclasses() -> " + Polygon.class.getPermittedSubclasses());
        System.out.println("Circle is final? " + java.lang.reflect.Modifier.isFinal(Circle.class.getModifiers()));
        Shape s = new Triangle();
        System.out.println("Triangle is a Shape through non-sealed Polygon: " + (s instanceof Polygon));
    }
}
```

Observed output (`java SealedHierarchyDemo`):

```text
Shape sealed? true
Shape permits [Circle, Rect, Polygon]
Result sealed? true
Result permits [Ok, Err]
Polygon sealed? false
Polygon.getPermittedSubclasses() -> null
Circle is final? true
Triangle is a Shape through non-sealed Polygon: true
```

**Pitfall:** `non-sealed` silently gives up what `sealed` was bought for. A `switch` over `Shape` is still exhaustive when it lists `Circle`, `Rect` and `Polygon`, but `Polygon` now stands for an open-ended set, so code in `case Polygon p` must handle subclasses it has never seen. The compiler rejects the two usual mistakes (messages from `javac --release 21`): a permitted class with none of the three modifiers gives `error: sealed, non-sealed or final modifiers expected`, and a class that implements a sealed type without being listed gives `error: class is not allowed to extend sealed class: T (as it is not listed in its 'permits' clause)`.

## Snippet 4: pattern matching switch

A `switch` with type patterns (`case Integer i`) tests the selector's runtime class and binds a variable in one step. `javac` compiles such a switch to an `invokedynamic` call to `SwitchBootstraps.typeSwitch` that returns the index of the first matching label, followed by an ordinary `tableswitch` on that index. Over a sealed hierarchy with no `default`, the compiler checks that every permitted subtype is covered, and inserts a synthetic `default` branch that constructs and throws `MatchException` (it is visible in the `javap` output of `eval`) for the case where the hierarchy was later changed without recompiling the switch.

```java
public class PatternSwitchDemo {

    sealed interface Expr permits Num, Add, Mul, Neg {}

    record Num(int v) implements Expr {}

    record Add(Expr l, Expr r) implements Expr {}

    record Mul(Expr l, Expr r) implements Expr {}

    record Neg(Expr e) implements Expr {}

    static int eval(Expr e) {
        return switch (e) { // exhaustive over the sealed type: no default needed
            case Num n -> n.v();
            case Add a -> eval(a.l()) + eval(a.r());
            case Mul m -> eval(m.l()) * eval(m.r());
            case Neg n -> -eval(n.e());
        };
    }

    static String describe(Object o) {
        return switch (o) {
            case null -> "null selector";
            case Integer i -> "int " + i;
            case String s -> "string of length " + s.length();
            case int[] arr -> "int array of length " + arr.length;
            case Expr ex -> "expression evaluating to " + eval(ex);
            default -> "something else: " + o.getClass().getSimpleName();
        };
    }

    static String withoutNullCase(Object o) {
        return switch (o) {
            case String s -> "string";
            default -> "not a string";
        };
    }

    public static void main(String[] args) {
        Expr e = new Add(new Num(2), new Mul(new Num(3), new Neg(new Num(4))));
        System.out.println("eval -> " + eval(e));

        Object[] samples = {42, "hello", new int[3], e, 3.5, null};
        for (Object o : samples) {
            System.out.println(describe(o));
        }

        System.out.println(withoutNullCase("x"));
        try {
            withoutNullCase(null);
        } catch (NullPointerException ex) {
            System.out.println("no 'case null' -> NullPointerException");
        }
    }
}
```

Observed output (`java PatternSwitchDemo`):

```text
eval -> -10
int 42
string of length 5
int array of length 3
expression evaluating to -10
something else: Double
null selector
string
no 'case null' -> NullPointerException
```

Bytecode check, from `javap -c -p PatternSwitchDemo` (lines containing the bootstrap call):

```text
      11: invokedynamic #13,  0             // InvokeDynamic #0:typeSwitch:(Ljava/lang/Object;I)I
       6: invokedynamic #52,  0             // InvokeDynamic #1:typeSwitch:(Ljava/lang/Object;I)I
      11: invokedynamic #88,  0             // InvokeDynamic #7:typeSwitch:(Ljava/lang/Object;I)I
  0: #167 REF_invokeStatic java/lang/runtime/SwitchBootstraps.typeSwitch:(Ljava/lang/invoke/MethodHandles$Lookup;Ljava/lang/String;Ljava/lang/invoke/MethodType;[Ljava/lang/Object;)Ljava/lang/invoke/CallSite;
```

The three `typeSwitch` call sites correspond to the three switches in the class (`eval`, `describe`, `withoutNullCase`), and all three share one bootstrap method entry from `java.lang.runtime.SwitchBootstraps`.

**Pitfall:** a `switch` on a reference type throws `NullPointerException` for `null` unless it has `case null` (see `withoutNullCase`); migrating an old `if/else instanceof` chain, which treated `null` as "no match", into a pattern switch changes behaviour. Order matters too: a label that dominates a later one (for example `case CharSequence cs` before `case String s`) is a compile-time error, so put specific cases first. And if a sealed type gains a permitted subtype after a switch was compiled, running the old class file against the new hierarchy throws `MatchException` at runtime instead of failing at build time.

## Snippet 5: guarded patterns

A guard is a `when` clause after a pattern: `case Circle c when c.r() > 10`. The label matches only if the type pattern matches and the boolean guard is true, and labels are tried strictly from top to bottom, so a guarded label must precede the unguarded label for the same type. A guarded label does not count towards exhaustiveness, because the compiler cannot prove the guard is always true.

```java
public class GuardedPatternDemo {

    sealed interface Shape permits Circle, Square {}

    record Circle(double r) implements Shape {}

    record Square(double side) implements Shape {}

    static String classify(Shape s) {
        return switch (s) {
            case Circle c when c.r() > 10 -> "large circle";
            case Circle c when c.r() > 1 -> "medium circle";
            case Circle c -> "small circle";
            case Square q when q.side() == 0 -> "degenerate square";
            case Square q -> "square with side " + q.side();
        };
    }

    static int guardCalls = 0;

    static boolean expensiveCheck(int i) {
        guardCalls++;
        return i > 100;
    }

    static String bucket(Integer n) {
        return switch (n) {
            case Integer i when expensiveCheck(i) -> "big";
            case Integer i when i > 50 -> "mid";
            case Integer i -> "small";
        };
    }

    public static void main(String[] args) {
        Shape[] shapes = {new Circle(20), new Circle(5), new Circle(0.5), new Square(0), new Square(2)};
        for (Shape s : shapes) {
            System.out.println(s + " -> " + classify(s));
        }

        for (int n : new int[] {500, 60, 7}) {
            guardCalls = 0;
            System.out.println(n + " -> " + bucket(n) + " (expensiveCheck ran " + guardCalls + " time)");
        }
    }
}
```

Observed output (`java GuardedPatternDemo`):

```text
Circle[r=20.0] -> large circle
Circle[r=5.0] -> medium circle
Circle[r=0.5] -> small circle
Square[side=0.0] -> degenerate square
Square[side=2.0] -> square with side 2.0
500 -> big (expensiveCheck ran 1 time)
60 -> mid (expensiveCheck ran 1 time)
7 -> small (expensiveCheck ran 1 time)
```

**Pitfall:** deleting the unguarded fallback makes the switch non-exhaustive. If the final `case Square q -> ...` line of `classify` is deleted, leaving only `case Square q when q.side() == 0 -> ...`, `javac --release 21` rejects the switch with:

```text
GuardedPatternDemo.java:10: error: the switch expression does not cover all possible input values
        return switch (s) {
               ^
1 error
```

The error is helpful at build time; the real hazard is a guard with side effects (like `expensiveCheck`, which mutates a counter): guards run in source order and stop at the first true one, so reordering labels changes both the result and how often the side effect fires.

## Snippet 6: record patterns

A record pattern `Line(Point(var x1, var y1), var to)` tests that the value is a `Line`, calls the component accessors, and matches each result against a nested pattern, so one label can deconstruct several levels. The compiled code calls the ordinary public accessor methods with `invokevirtual`; there is no special deconstruction bytecode. A record pattern never matches `null`, while a `var` or type pattern that is total for the component type does.

```java
public class RecordPatternDemo {

    record Point(int x, int y) {}

    record Line(Point from, Point to) {}

    record Box<T>(T content) {}

    record Fragile(int v) {
        @Override
        public int v() {
            throw new IllegalStateException("accessor failed");
        }
    }

    static String describe(Object o) {
        return switch (o) {
            case Line(Point(var x1, var y1), Point(var x2, var y2)) ->
                    "line (" + x1 + "," + y1 + ") -> (" + x2 + "," + y2 + "), dx=" + (x2 - x1);
            case Line(var a, var b) -> "line with a=" + a + ", b=" + b;
            case Box<?>(String s) -> "box of string '" + s + "'";
            case Box<?>(Integer i) -> "box of int " + i;
            case Box<?>(var other) -> "box of " + other;
            case Fragile(int v) -> "fragile " + v;
            default -> "not matched: " + o;
        };
    }

    public static void main(String[] args) {
        System.out.println(describe(new Line(new Point(1, 2), new Point(4, 6))));
        System.out.println(describe(new Line(null, new Point(1, 1))));
        System.out.println(describe(new Box<>("hi")));
        System.out.println(describe(new Box<>(7)));
        System.out.println(describe(new Box<>(null)));
        System.out.println(describe("plain string"));

        Object p = new Point(5, 5);
        if (p instanceof Point(int x, int y) && x == y) {
            System.out.println("instanceof record pattern: diagonal point " + x);
        }

        try {
            describe(new Fragile(1));
        } catch (MatchException e) {
            System.out.println("MatchException, cause: " + e.getCause());
        }
    }
}
```

Observed output (`java RecordPatternDemo`):

```text
line (1,2) -> (4,6), dx=3
line with a=null, b=Point[x=1, y=1]
box of string 'hi'
box of int 7
box of null
not matched: plain string
instanceof record pattern: diagonal point 5
MatchException, cause: java.lang.IllegalStateException: accessor failed
```

Bytecode check, from `javap -c -p RecordPatternDemo` (accessor calls made by `describe`):

```text
      58: invokevirtual #19                 // Method RecordPatternDemo$Line.from:()LRecordPatternDemo$Point;
      76: invokevirtual #25                 // Method RecordPatternDemo$Line.to:()LRecordPatternDemo$Point;
      95: invokevirtual #28                 // Method RecordPatternDemo$Point.x:()I
     114: invokevirtual #32                 // Method RecordPatternDemo$Point.y:()I
     252: invokevirtual #50                 // Method RecordPatternDemo$Box.content:()Ljava/lang/Object;
     373: invokevirtual #66                 // Method RecordPatternDemo$Fragile.v:()I
     431: invokespecial #81                 // Method java/lang/MatchException."<init>":(Ljava/lang/String;Ljava/lang/Throwable;)V
```

Every component is read by an `invokevirtual` on the accessor, and `describe` contains the `MatchException` constructor call that wraps an accessor failure. Only the outer type test (`typeSwitch`, plus a nested one for `Box<?>`) uses `invokedynamic`.

**Pitfall:** the accessor is real code and may throw. When an accessor fails during matching, the exception is not propagated as-is: it is wrapped in a `MatchException` whose cause is the original (the `Fragile` case above), so a `catch (IllegalStateException e)` around the switch will not fire. Equally surprising is the `Line(null, ...)` case: it did not match the first label even though `from` is declared as `Point`, because nested record patterns reject `null`; it fell through to the `var` label, which accepts it.

## Verification notes

- Compiled and run (6 total): `RecordCanonicalDemo`, `CompactConstructorDemo`, `SealedHierarchyDemo`, `PatternSwitchDemo`, `GuardedPatternDemo`, `RecordPatternDemo`, all with `javac --release 21 -proc:none`.
- The two bytecode excerpts and the compiler error message were captured from `javap -c -p` and `javac --release 21` on the same sources.
- Nothing here depends on preview features; `javac` was never given `--enable-preview`.
