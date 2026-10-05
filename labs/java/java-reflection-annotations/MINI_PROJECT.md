# Mini Project — Mini DI Container (80 lines core)

## Goal
Ctor-injection container: `@Inject`, `@Singleton`, cycle error.

## API
```java
@Retention(RUNTIME) @Target({CONSTRUCTOR,FIELD}) @interface Inject {}
@Retention(RUNTIME) @Target(TYPE) @interface Singleton {}
class Ctx { public <T> T get(Class<T> t) { ... } }
```

## Steps
1. Find @Inject ctor (or default); recurse args via get().
2. Singleton cache map; in-progress set → cycle exception.
3. Field injection fallback if no inject ctor.
4. Tests: singleton identity, transient, cycle message.

## Skeleton
```java
Map<Class<?>,Object> singletons = new HashMap<>();
Set<Class<?>> busy = new HashSet<>();
// get(): if singleton cached return; if busy throw; else construct
```

## Acceptance
- 10-bean graph resolves; cycle test fails clearly.
- No framework deps; startup < 50ms.

## Stretch
- `@Provides` methods, qualifier annotations.
- Compile-time validation processor.

## Demo (2 min)
Wire Svc→Repo→Db, show singleton + cycle error.
