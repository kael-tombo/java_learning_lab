# Architecture: Method Handles

## Lookup layer (access checks once, at creation)

```text
MethodHandles.lookup()  (caller-sensitive: your own access rights)
  findStatic(cls, name, MethodType)        e.g. Math.sqrt: (double)double
  findVirtual(cls, name, MethodType)       e.g. substring: (String,int,int)String
  findConstructor(cls, MethodType(void,...)) -> handle (params...)Class
  findGetter / findSetter(cls, field, type)  setter rejects finals HERE
  findSpecial(cls, name, type, caller)     private/super of the caller only
```

Every lookup stamps the handle with the caller's rights. Invocation
performs no access check — the security decision is entirely at
creation (contrast reflection's per-call checks).

## Handle-type layer (MethodType is the contract)

```text
MethodType.methodType(return.class, param.classes...)
(double)double        sqrt handle
(String,int,int)String  substring handle (receiver = first arg)
(int)ArrayList        ctor handle (lookup said (int)V)
(Point)int            getter     (Point,int)void  setter
(int,int)int          guarded handle (== branch types)
```

`invokeExact` enforces this type at the *call site's* static types
(link time). `asType` derives adapted views (`(Object,Object)Object`
for the concat handle); `invoke` applies adaptation implicitly.

## Combinator layer (branching without bytecode)

```text
insertArguments(add, 0, 40)        (int,int)int -> (int)int   (primitives OK)
bindTo(handle, refValue)           first arg must be REFERENCE (use insert for int)
filterArguments(f, 0, g)           preprocess arg 0 through g (f(g(x), ...))
filterReturnValue(h, f)            postprocess: f(h(...))
asSpreader(int[].class, 2)         array -> spread args
asCollector(int[].class, 2)        args -> collected array
guardWithTest(test, target, fallback)  test takes PREFIX, branches take FULL list
dropArguments / asVarargsCollector    ignore / varargs shaping
```

The guarded handle is one JIT-optimizable unit: test + both arms
inline as a unit, no call-site bytecode for the branch.

## Call-site layer (invokedynamic linkage)

```text
bootstrap(Lookup caller, String name, MethodType type, Object... staticArgs)
  -> CallSite(target handle)
ConstantCallSite  immutable target, folds to direct call (lambdas)
MutableCallSite   setTarget relinks all callers (volatile semantics)
VolatileCallSite  volatile-read target (always sees latest)
dynamicInvoker()  handle bound to current target (mutable) / fixed (constant)
```

`LambdaMetafactory.metafactory` is the bootstrap for lambdas and
string concat: static args describe the functional shape, dynamic
args carry captures, the returned site folds like a constant.

## Cost layer (first call vs warm)

```text
first call: linkage (type check + target bind)     cold handle
warm call:  JIT-inlined to direct call             hot handle
args:       exact types, no boxing (primitives)    vs reflection Object[] boxing
security:   once at lookup                         vs per-invocation checks
```
