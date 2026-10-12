# Method Handles — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. Lookup Trio: Static, Virtual, Constructor (Correct Shapes)

```java
import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;
import java.util.ArrayList;

public class LookupTrio {
    public static void main(String[] args) throws Throwable {
        MethodHandles.Lookup lookup = MethodHandles.lookup();

        MethodHandle sqrt = lookup.findStatic(Math.class, "sqrt",
                MethodType.methodType(double.class, double.class));
        System.out.println("sqrt type: " + sqrt.type());
        System.out.println("sqrt(16.0) = " + (double) sqrt.invokeExact(16.0));

        MethodHandle sub = lookup.findVirtual(String.class, "substring",
                MethodType.methodType(String.class, int.class, int.class));
        System.out.println("substring type: " + sub.type());
        System.out.println("substring: " + (String) sub.invokeExact("hello", 1, 3));

        // constructor: MethodType return is void, ALWAYS (even for `new`)
        MethodHandle ctor = lookup.findConstructor(ArrayList.class,
                MethodType.methodType(void.class, int.class));
        System.out.println("ctor type: " + ctor.type());
        ArrayList<?> list = (ArrayList<?>) ctor.invokeExact(8);
        System.out.println("constructed, size = " + list.size());
        System.out.println("all three exact: " + ((double) sqrt.invokeExact(16.0) == 4.0
                && "el".equals((String) sub.invokeExact("hello", 1, 3))
                && list.size() == 0));
    }
}
```

Expected output:
```
sqrt type: (double)double
sqrt(16.0) = 4.0
substring type: (String,int,int)String
substring: el
ctor type: (int)ArrayList
constructed, size = 0
all three exact: true
```

The constructor's `(int)void` lookup descriptor becomes an
`(int)ArrayList` handle type — `findConstructor` adapts void to the
constructed type on return (a previous revision of this lab's THEORY showed
`methodType(ArrayList.class)` at lookup time — a descriptor no constructor
carries).

## 2. Field Handles: Getter/Setter Without Reflection

```java
import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;

public class FieldHandles {
    public static class Point {
        public int x;
        public final int y = 7;
        Point(int x) { this.x = x; }
    }

    public static void main(String[] args) throws Throwable {
        MethodHandles.Lookup lookup = MethodHandles.lookup();
        MethodHandle getX = lookup.findGetter(Point.class, "x", int.class);
        MethodHandle setX = lookup.findSetter(Point.class, "x", int.class);
        System.out.println("getter type: " + getX.type());
        System.out.println("setter type: " + setX.type());

        Point p = new Point(3);
        System.out.println("x = " + (int) getX.invokeExact(p));
        setX.invokeExact(p, 42);
        System.out.println("x after set = " + (int) getX.invokeExact(p));

        // final instance field: getter yes, setter no
        MethodHandle getY = lookup.findGetter(Point.class, "y", int.class);
        System.out.println("final field read: " + (int) getY.invokeExact(p));
        boolean setterRejected = false;
        try {
            lookup.findSetter(Point.class, "y", int.class);
        } catch (IllegalAccessException e) {
            setterRejected = true;
        }
        System.out.println("final field setter rejected: " + setterRejected);
    }
}
```

Expected output:
```
getter type: (Point)int
setter type: (Point,int)void
x = 3
x after set = 42
final field read: 7
final field setter rejected: true
```

Getter/setter handles bake the field offset at lookup; invocation is a
plain memory access (no per-call access check, no boxing for `int`). Final
fields expose reads only — the setter lookup fails fast at *creation*, the
security-check-once property from THEORY.

## 3. Combinators: bindTo, filterArguments, guardWithTest

```java
import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;

public class Combinators {
    static int add(int a, int b) { return a + b; }
    static int mul(int a, int b) { return a * b; }
    static boolean big(int x) { return x > 100; }

    public static void main(String[] args) throws Throwable {
        MethodHandles.Lookup lk = MethodHandles.lookup();
        MethodHandle add = lk.findStatic(Combinators.class, "add",
                MethodType.methodType(int.class, int.class, int.class));

        // bind the first argument (bindTo needs a reference receiver: use
        // insertArguments for primitives — it boxes the bound value)
        MethodHandle add40 = MethodHandles.insertArguments(add, 0, 40);
        System.out.println("add40 type: " + add40.type());
        System.out.println("add40(2) = " + (int) add40.invokeExact(2));

        // filterArguments: pre-process one argument (double it)
        MethodHandle dbl = lk.findStatic(Combinators.class, "dbl",
                MethodType.methodType(int.class, int.class));
        MethodHandle addDblFirst = MethodHandles.filterArguments(add, 0, dbl);
        System.out.println("addDblFirst(21, 0) = " + (int) addDblFirst.invokeExact(21, 0));

        // guardWithTest: test ? target : fallback — test takes a PREFIX of the
        // args; both branches take the FULL arg list. Composed type == branch type.
        MethodHandle isBig = lk.findStatic(Combinators.class, "big",
                MethodType.methodType(boolean.class, int.class));
        MethodHandle mul = lk.findStatic(Combinators.class, "mul",
                MethodType.methodType(int.class, int.class, int.class));
        MethodHandle guarded = MethodHandles.guardWithTest(isBig, add, mul);
        System.out.println("guarded type: " + guarded.type());
        System.out.println("guarded(200, 1) = " + (int) guarded.invokeExact(200, 1));
        System.out.println("guarded(1, 3) = " + (int) guarded.invokeExact(1, 3));
    }

    static int dbl(int x) { return x * 2; }
}
```

Expected output:
```
add40 type: (int)int
add40(2) = 42
addDblFirst(21, 0) = 42
guarded type: (int,int)int
guarded(200, 1) = 201
guarded(1, 3) = 3
```

`guardWithTest(test, target, fallback)` wires an if-else into one handle:
the test takes a leading prefix, both branches take the full list
(`big(200)`→`add(200,1)`; `big(1)` false→`mul(1,3)`). The guarded handle is
a single optimizable unit to the JIT — branching without bytecode.

## 4. CallSite Retargeting: Mutable vs Constant

```java
import java.lang.invoke.ConstantCallSite;
import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;
import java.lang.invoke.MutableCallSite;

public class Retarget {
    static String v1() { return "one"; }
    static String v2() { return "two"; }

    public static void main(String[] args) throws Throwable {
        MethodHandles.Lookup lk = MethodHandles.lookup();
        MethodHandle h1 = lk.findStatic(Retarget.class, "v1",
                MethodType.methodType(String.class));
        MethodHandle h2 = lk.findStatic(Retarget.class, "v2",
                MethodType.methodType(String.class));

        MutableCallSite mutable = new MutableCallSite(h1);
        MethodHandle invoker = mutable.dynamicInvoker();
        System.out.println("mutable before: " + (String) invoker.invokeExact());
        mutable.setTarget(h2);   // relink at runtime
        System.out.println("mutable after: " + (String) invoker.invokeExact());

        ConstantCallSite constant = new ConstantCallSite(h1);
        MethodHandle cInvoker = constant.dynamicInvoker();
        System.out.println("constant: " + (String) cInvoker.invokeExact());
        boolean relinkRejected = false;
        try {
            constant.setTarget(h2);   // may throw (never re-linkable)
        } catch (Throwable t) {
            relinkRejected = true;
        }
        System.out.println("constant still v1: "
                + "one".equals((String) cInvoker.invokeExact()));
        System.out.println("constant relink rejected-or-ignored: "
                + (relinkRejected || "one".equals((String) cInvoker.invokeExact())));
    }
}
```

Expected output:
```
mutable before: one
mutable after: two
constant: one
constant still v1: true
constant relink rejected-or-ignored: true
```

`MutableCallSite.setTarget` re-links all callers (volatile semantics —
suitable for guards, megamorphic caches, live code replacement);
`ConstantCallSite` folds to its target permanently (the JIT treats it as a
direct call — this is what lambda `invokedynamic` sites use). Same invoker
shape, opposite linkage contracts.

## 5. invokeExact Strictness vs invoke Adaptivity

```java
import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;
import java.lang.invoke.WrongMethodTypeException;

public class ExactVsLoose {
    public static void main(String[] args) throws Throwable {
        MethodHandles.Lookup lk = MethodHandles.lookup();
        MethodHandle concat = lk.findVirtual(String.class, "concat",
                MethodType.methodType(String.class, String.class));

        // invokeExact: static types must match the MethodType precisely
        String exact = (String) concat.invokeExact("a", "b");
        System.out.println("invokeExact: " + exact);
        boolean wmt = false;
        try {
            Object o = (Object) "a";
            concat.invokeExact(o, "b");   // receiver statically Object: REJECTED
            System.out.println("loose receiver accepted (unexpected)");
        } catch (WrongMethodTypeException | ClassCastException e) {
            wmt = true;
        }
        System.out.println("statically-wrong receiver rejected: " + wmt);

        // invoke: adapts (casts/unboxes) like an ordinary call
        Object flex = concat.invoke("a", "c");
        System.out.println("invoke adapts: " + flex);
        System.out.println("asType view: " + concat.asType(
                MethodType.methodType(Object.class, Object.class, Object.class)).type());
    }
}
```

Expected output:
```
invokeExact: ab
statically-wrong receiver rejected: true
invoke adapts: ac
asType view: (Object,Object)Object
```

`invokeExact` is signature-polymorphic: the *compiler* stamps the call site
with the static argument types, and mismatch fails at link time
(`WrongMethodTypeException` — never a `ClassCastException` from inside).
`invoke` inserts conversions (`asType` rules). Generics erase both to
`Object` at the source level, but the recorded types differ — which is why
`MethodHandle` behavior can surprise inside generic helper methods.

## Common Pitfalls Encountered Here

- **Constructor MethodType with a return type** — always `(params)V`
  (snippet 1; previously wrong in this lab's own THEORY).
- **Setting final fields via handles** — lookup-time rejection, not a
  runtime error (snippet 2).
- **`guardWithTest` arity confusion** — test takes the head args, branches
  take the tail (snippet 3 prints the composed type — read it).
- **Relinking a `ConstantCallSite`** — forbidden/ignored; mutability needs
  `MutableCallSite` (snippet 4).
- **`invokeExact` inside generic code** — erased static types mismatch the
  handle type; prefer `invoke` or explicit `asType` (snippet 5).
- **Assuming handles are reflection-speed** — cold handles link slowly;
  measure warm (THEORY table).
