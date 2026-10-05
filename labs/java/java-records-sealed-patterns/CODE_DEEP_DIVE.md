# Code Deep Dive — Records / Sealed / Patterns

## 1. Source Tour
- `java.lang.Record`, `Class::getRecordComponents`, `getPermittedSubclasses`.
- Compiler: `javac` generates canonical ctor, accessors, equals/hashCode/toString.
- Sealed: `PermittedSubclasses` class-file attribute.

## 2. Bytecode: Record
```java
record P(int x, int y) {}
```
`javap -v P.class` shows `Record` attribute + `final` fields + accessors.
`equals` uses `Objects.equals` per component; `hashCode` mixes.

## 3. Sealed Bytecode
`javap -v Shape.class` → `PermittedSubclasses: Circle, Rect`.
Non-permitted `implements Shape` → `IncompatibleClassChangeError` at compile.

## 4. Pattern instanceof
```java
if (o instanceof Circle c) c.area();
```
`javac` emits `instanceof + checkcast + store`; JIT folds when monomorphic.
Flags: `-XX:+PrintCompilation` to see bimorphic deopt if many variants.

## 5. Switch Patterns Codegen
Exhaustive switch → `tableswitch/lookupswitch` on type index + null check first.
`javap -c` the switch; dominant guard becomes `if` before dispatch.

## 6. Record Patterns
Deconstruction = chained accessors with null checks. Nested = nested null checks.
Cost: branch per level; JIT inlines accessors (final).

## 7. Serialization Path
Jackson uses canonical ctor via `ParameterNamesModule`; no-arg + setters not needed.
Pitfall: compact-ctor validation runs on deser — good.

## 8. Profiling
```bash
javap -v -p P.class | grep -A5 Record
java -XX:+PrintInlining -XX:+PrintCompilation Main | grep -i circle
```

## 9. HotSpot Notes
- Records are final-ish; escape analysis friendly (stack alloc).
- Sealed enables CHA devirtualization: monomorphic call → direct.

## 10. Refs
JEP 395 (records), 409 (sealed), 441 (patterns), `Class::isSealed` javadoc.
