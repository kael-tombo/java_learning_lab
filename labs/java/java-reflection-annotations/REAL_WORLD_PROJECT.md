# Real-World Project — Validation + Plugin Framework

## Problem
Declarative validation (`@NotNull,@Min,@Size`) + plugin loading for a service, fast + safe.

## Architecture
```
annotations (@NotNull,@Min,@Size) → Validator (cached Handles)
plugins: ServiceLoader + @Plugin meta → isolated URLClassLoader per plugin
app: validate(input) → execute plugins → audit errors
```

## Milestones
1. **M1 Annotations**: define + retention/target; unit-test visibility.
2. **M2 Validator**: Field scan once, cache VarHandles; `List<Violation>` result.
3. **M3 Plugins**: `Plugin { String name(); void run(Ctx c); }` via ServiceLoader.
4. **M4 Isolation**: child-first loader per plugin; deny `setAccessible(java.*)`.
5. **M5 Ops**: validation latency p99, plugin load dashboard; GraalVM metadata file.

## Key Code
```java
MethodHandles.Lookup lk = MethodHandles.privateLookupIn(cls, MethodHandles.lookup());
VarHandle vh = MethodHandles.privateLookupIn(cls, lk.lookupClass())
  .findVarHandle(cls, field.getName(), field.getType());
// validate: vh.get(obj) null/range checks
```
Run: `java --add-opens java.base/java.lang=ALL-UNNAMED -Xmx512m App`.

## Testing
- Fuzz objects: 10k random → 0 exceptions, violations deterministic.
- Malicious plugin (System.exit/reflect attack) contained.
- Bench: handle-validator vs raw-reflect — document 5×+ win.

## Ops
- Docker temurin:21; K8s 512Mi; alert p99 validate > 5ms.
- Plugin signing: verify jar signature before load.

## Interview Angles
- Why handles over Method? Opens strategy? Plugin isolation model?

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Oracle reflection: https://docs.oracle.com/javase/tutorial/reflect/
- MethodHandles: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/invoke/MethodHandles.html
- OpenJDK Leyden (AOT): https://openjdk.org/projects/leyden/
