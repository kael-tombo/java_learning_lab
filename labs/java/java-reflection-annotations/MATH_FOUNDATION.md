# Math Foundation — Reflection

## 1. Invoke Cost
`T_reflect ≈ k × T_direct`, k≈10–100 pre-inflate, ~1–2 post-JIT handle.
1M calls: direct 5ms → reflect 200ms → handle 8ms (typical).

## 2. Inflation Threshold
Default 15 calls → bytecode accessor generated. `T(n)=n1·slow+n2·fast`.

## 3. Scan Cost
Classpath scan O(C×M): 10k classes × 20 methods = 200k checks (~100ms).

## 4. Cache Hit
`T_avg = h·T_cache + (1−h)·T_lookup`. Cache Methods → h≈1.

## 5. Proxy Overhead
Extra hop + array box: `+20–50ns` per call. Fine unless tiny hot loop.

## 6. Annotation Retention Size
RUNTIME annotations bloat constant pool ~50B each; 1k annotated → 50KB.

## 7. Startup Cost
Reflective DI scan adds `100–500ms`; AOT/processor removes it.

## Recap
```
T_refl = k·T_dir
T_avg = h·c+(1−h)·L
scan = C·M
```
Drill: 1M invokes at 100ns direct, k=30 → reflect time? Cache h=0.99 effect?
