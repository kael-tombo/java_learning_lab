# VISION — Reflection

## Vision Statement
**Inspect last, generate first** — reflection trades compile-time safety for runtime flexibility; use it at boundaries (plugins, mappers), never in hot loops.

---
## Mental Models
### 1. Class Is the Mirror
`Class<?>`, `Method`, `Field`, `Constructor` — `getMethod` (public+inherited) vs `getDeclaredMethod` (all-declared). Wrong one = `NoSuchMethodException` mystery.
### 2. Access Has a Price
`setAccessible(true)` defeats encapsulation; modules (JPMS) can deny it (`InaccessibleObjectException`). Cache `Method` handles; never look up per call.
### 3. Generics Erase, Signatures Remain
`getGenericType/GenericReturnType` expose `ParameterizedType`/`TypeVariable`; raw `getType` hides them. Mappers must read generic metadata, not raw classes.
### 4. Exceptions Are Wrapped
Reflective calls wrap everything in `InvocationTargetException` — unwrap `getCause()` or your logs lie about the failure site.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Known at compile time? | No reflection — direct call / codegen |
| Plugin/mapper boundary? | Reflect once, cache, validate |
| Hot path? | `MethodHandle`/`LambdaMetafactory` or generated code |
| Module boundary? | `--add-opens` is a smell; prefer exported API |

---
## Career Trajectory
- **L1:** `Class.forName`, `newInstance` replacement (`getDeclaredConstructor().newInstance()`), field read.
- **L2:** Generic-type token (`TypeReference`-style), annotation-driven mapping, exception unwrapping.
- **L3:** `MethodHandle/VarHandle`, `Proxy` dynamics, module-access debugging.
- **L4:** Codegen (annotation processor/bytecode) to eliminate runtime reflection; startup-time budgets.

---
## 4-Week Path
```
W1: Class/Method/Field lookup, declared vs public, accessible rules.
W2: Mini-mapper: JSON-ish map→POJO with generic List<> support.
W3: Dynamic proxy: logging/timing proxy + InvocationHandler pitfalls.
W4: Plugin-loader kata + MethodHandle speedup benchmark.
```
## Success Metrics
- [ ] Diagnose NoSuchMethod vs InaccessibleObject in < 5 min
- [ ] Mapper handles nested generics without ClassCastException
- [ ] Prove cached-handle path ≥ 10x faster than lookup-per-call
