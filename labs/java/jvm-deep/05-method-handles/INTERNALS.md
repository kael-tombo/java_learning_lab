# Internals: Method Handles

## Lookup methods and their checks

```text
findStatic(cls, name, type)        exact static, accessible to caller
findVirtual(cls, name, type)       receiver type checked; dispatches virtually
findConstructor(cls, (params)V)    void return REQUIRED; handle adapts to (params)Class
findGetter(cls, field, ftype)      read handle (Point)int; finals OK
findSetter(cls, field, ftype)      write handle (Point,int)void; finals REJECTED here
findSpecial(cls, name, type, caller) caller's own super/private only
unreflect(Method/Field)            bridge from reflection (checks again at conversion)
```

All throw `NoSuchMethodException`/`IllegalAccessException` at
creation. Lookup objects are caller-sensitive: `lookup()` in one
class cannot mint handles to another's privates.

## MethodType construction

```java
MethodType.methodType(double.class, double.class)          // (double)double
MethodType.methodType(String.class, int.class, int.class)  // (int,int)String... note receiver:
MethodType.methodType(String.class, String.class, int.class, int.class) // substring w/ receiver
MethodType.methodType(void.class, int.class)               // ctor lookup (int)V
```

Printed forms: `(double)double`, `(String,int,int)String`,
`(int)ArrayList`, `(Point)int`, `(int,int)int`. The receiver is a
leading parameter in the type — `invokeExact("hello", 1, 3)` passes
it explicitly.

## Combinator signatures (exact arities)

```java
MethodHandles.insertArguments(target, pos, values...)  // boxes primitives
target.bindTo(refValue)                                // reference only, first arg
MethodHandles.filterArguments(target, pos, filters...) // filter count covers from pos
MethodHandles.filterReturnValue(target, filter)
target.asSpreader(arrayType, length) / target.asCollector(arrayType, length)
MethodHandles.guardWithTest(test, target, fallback)    // test: prefix; arms: full
MethodHandles.dropArguments(target, pos, droppedTypes...)
```

`guardWithTest` requires test return `boolean` and identical
target/fallback types; the composed handle carries that type.

## Call-site classes

```java
new ConstantCallSite(target)   // setTarget: throws/ignored; folds to direct
new MutableCallSite(target)    // setTarget(h2): relinks (volatile write)
new VolatileCallSite(target)   // every invocation re-reads target
site.dynamicInvoker()          // handle tracking (mutable) / fixed (constant) target
site.getTarget() / .setTarget(h)
```

Lambda linkage uses `ConstantCallSite` via `LambdaMetafactory`;
guard/caching frameworks hold `MutableCallSite`/`VolatileCallSite`
and swap targets under load.

## Invocation forms

`invokeExact(args...)` — signature-polymorphic: compiler stamps the
call site with static types, exact match or
`WrongMethodTypeException` at link. `invoke(args...)` — adapts via
`asType` (reference casts, primitive conversions, boxing).

## Bootstrap shape

```java
CallSite bootstrap(MethodHandles.Lookup caller, String name,
                   MethodType type, Object... staticArgs)
```

Caller lookup bounds privilege (a bootstrap cannot exceed its
caller's access); static args carry linkage discriminators
(capture shapes, concat recipes); the returned site's type must
equal the declared dynamic type or linkage fails fast.
