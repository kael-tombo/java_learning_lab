# Visual Guide: Method Handles

## Lookup trio (shapes)

```text
findStatic(Math, "sqrt", (double)double)
  lookup descriptor == handle type:  (double)double
findVirtual(String, "substring", (String,int,int)String)
  receiver FIRST:  invokeExact("hello", 1, 3) -> "el"
findConstructor(ArrayList, (int)V)   // void at lookup, ALWAYS
  handle type:     (int)ArrayList     // adapted on return
```

## Field handles

```text
findGetter(Point, "x", int)   -> (Point)int        read: getX.invokeExact(p)
findSetter(Point, "x", int)   -> (Point,int)void   write: setX.invokeExact(p, 42)
findGetter(Point, "y", int)   -> (Point)int        final read OK (= 7)
findSetter(Point, "y", int)   -> IllegalAccessException AT LOOKUP (final)
```

## Combinators (data flow)

```text
insertArguments(add, 0, 40):   (int,int)int --bind 40--> (int)int
  add40(2) = add(40, 2) = 42
filterArguments(add, 0, dbl):  arg0 -> dbl -> add
  addDblFirst(21, 0) = add(42, 0) = 42
guardWithTest(isBig, add, mul):       test: prefix (int)boolean
  (200,1): big(200)=T -> add(200,1)=201    arms: FULL (int,int)int
  (1,3):   big(1)=F   -> mul(1,3)=3
```

## Call sites

```text
MutableCallSite(h1):   invoker -> one --setTarget(h2)--> invoker -> two
ConstantCallSite(h1):  invoker -> one --setTarget(h2)--> rejected/ignored -> one
  (lambdas use constant: JIT folds to direct call)
```

## Invocation strictness

```text
invokeExact("a","b")            static (String,String) == (String,String) OK -> "ab"
invokeExact((Object)"a","b")    static (Object,String) != handle -> WrongMethodTypeException
invoke("a","c")                 adapts (asType rules) -> "ac"
asType view: (Object,Object)Object   (explicit adaptation, same rules)
```

## Origin line

```text
JSR 292 (Java 7):  invokedynamic + handles ORIGIN (JRuby/Nashorn era)
Java 8:            LambdaMetafactory rides the substrate (lambdas, concat later)
JEP 274 (Java 9):  ENHANCEMENT (combinators, loops) — not the origin
```
