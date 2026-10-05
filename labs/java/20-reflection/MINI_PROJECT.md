# MINI PROJECT — Reflection: Map-to-POJO Mapper + Plugin Loader

## Goal (2 weeks, ~8–10h)
Build a cached reflective mapper (nested generics correct) plus a `ServiceLoader`-style plugin loader — with benchmarks proving caching matters.

## Requirements
### Functional
1. `Mapper.toObject(Map<String,Object>, Class<T>)`: string→field coercion (int/long/boolean/enum/LocalDate), nested POJO, `List<Nested>` via `ParameterizedType`, `@JsonName` rename support.
2. Cache: `ConcurrentHashMap<Class<?>, BeanInfo>` (ctors, fields, generic types); `setAccessible` once; clear `InvocationTargetException` unwrap with field-path messages.
3. `Proxy` timing wrapper: `Timing.wrap(Service.class, impl)` logs per-method µs; handles `equals/hashCode/toString` correctly.
4. Plugin loader: `plugins/` dir, `URLClassLoader`, `META-INF/services`-style file listing `Plugin` impls; instantiate via no-arg ctor, run `execute()`.
5. CLI: map a JSON-ish file to POJO, list plugins, time both paths.
### Non-functional
- No `Class.forName` strings for known types; no per-call `getDeclaredField`; no swallowed `getCause`.
- 16+ tests: nested list mapping, rename, coercion failure message, private-field access, proxy equals, missing-plugin error, module-denied note.
- README: declared-vs-public table + cache benchmark (uncached vs cached vs MethodHandle if tried).
- Startup: mapper init < 200ms for 20 classes (cached).

## Phases
### Week 1 — Mapper (4–5h)
- BeanInfo cache, coercion, nested + list generics.
- Deliverable: 5-POJO mapping demo + 8 tests.
### Week 2 — Proxy + Plugins (4–5h)
- Timing proxy, loader, error messages, benchmark.
- Deliverable: plugin run + benchmark table.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Generics | ParameterizedType correct | Flat works | Raw casts |
| Caching | Once-lookup, measured win | Cached | Lookup per call |
| Errors | Field-path + cause unwrap | Clear messages | Wrapped stack only |
| Proxy/loader | Correct equals + isolation | Works | Classloader leak |
| Tests | 16+ | 10+ | Happy-path only |

Pass ≥ 70. Stretch: `MethodHandle` fast path with numbers; compile-time generator sketch replacing reflection for one DTO.
