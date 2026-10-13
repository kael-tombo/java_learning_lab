# Refactoring: Method Handles

## 1. Cache lookups in static finals

Before (lookup per call — reflection's cost profile with extras):

```java
int call(int a, int b) throws Throwable {
    var h = MethodHandles.lookup().findStatic(Fx.class, "add",
        MethodType.methodType(int.class, int.class, int.class));
    return (int) h.invokeExact(a, b);
}
```

After (lookup once in `<clinit>`, invoke freely):

```java
static final MethodHandle ADD;
static {
    try {
        ADD = MethodHandles.lookup().findStatic(Fx.class, "add",
            MethodType.methodType(int.class, int.class, int.class));
    } catch (ReflectiveOperationException e) { throw new ExceptionInInitializerError(e); }
}
int call(int a, int b) throws Throwable { return (int) ADD.invokeExact(a, b); }
```

Effect: access checks and type parsing leave the hot path.

## 2. Replace reflective field loops with handles

Before (per-call checks + boxing):

```java
for (Point p : points) sum += (int) xField.get(p);  // Field.get per element
```

After (offset baked at lookup, plain access per call):

```java
MethodHandle getX = lookup.findGetter(Point.class, "x", int.class);
for (Point p : points) sum += (int) getX.invokeExact(p);
```

Effect: no per-call access check, no boxing of `int`. Keep the
handle in a constant (item 1).

## 3. Use insertArguments for primitive currying

Before (bindTo on an int — fails the reference rule):

```java
MethodHandle add40 = add.bindTo(40);  // WRONG for (int,int)int
```

After (boxes the bound value, narrows the type):

```java
MethodHandle add40 = MethodHandles.insertArguments(add, 0, 40);  // (int)int
```

Effect: `add40(2) = 42` with the printed type stating the new
contract. Reserve `bindTo` for reference receivers.

## 4. Fuse if-else dispatch into guardWithTest

Before (branch + two call sites, split profiling):

```java
int pick(int x, int y) { return big(x) ? add(x, y) : mul(x, y); }
```

After (one handle, one optimizable unit):

```java
MethodHandle pick = MethodHandles.guardWithTest(isBig, add, mul);  // (int,int)int
int pick(int x, int y) throws Throwable { return (int) pick.invokeExact(x, y); }
```

Effect: test + arms inline together; both arms keep the full arg list.
