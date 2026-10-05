# MINI PROJECT — Class Loading & Bytecode: Isolated Plugin Host

## Goal (2 weeks, ~8–10h)
Build a plugin host that loads two versions of the same `Pricer`
interface (v1 + v2 jars) side by side, instruments them with a
javaagent timer, and unloads cleanly with no loader leak.

## Requirements
### Functional
1. `PluginHost` with one `URLClassLoader` (child-first, `Closeable`)
   per plugin; v1 and v2 `com.lab43.Pricer` coexist; service lookup
   via loader-scoped `ServiceLoader` or explicit class load.
2. Demonstrate identity split: cast across loaders fails with
   `ClassCastException`; host communicates only via host-loaded
   interface (parent) — test asserts this boundary.
3. Bytecode exhibit: `javap -c -p` dumps for lambda + string-concat
   + switch in README with 5-line annotations (which `invokedynamic`
   does what).
4. Javaagent (`premain`) with ByteBuddy/ASM: times
   `Pricer.price(..)` and records `jdk.JavaExceptionThrow` safe;
   agent attaches with zero plugin source change.
5. Unload: `loader.close()` + null refs; prove collection with heap
   dump (loader + classes gone) and metaspace drop via NMT/JFR.
6. Conflict case: host shades Guava v31 while plugin bundles v32 —
   child-first resolves correctly; `-verbose:class` log excerpt saved.

### Non-functional
- 14+ tests: isolation, version coexistence, agent timing present,
  unload (weak-ref to loader cleared after GC), shading resolution.
- Artifacts: `verbose_class.log`, `javap/` dumps, JFR
  (`jdk.ClassLoad`, `jdk.ClassDefine`) screenshot/excerpt.
- README: delegation diagram + leak-checklist (static fields,
  threads, JDBC drivers as classic leak vectors).
- No `System.exit`; loaders closed in try-with-resources in tests.

## Starter Layout
```
host/src/main/java/com/lab43/host/{PluginHost,ChildFirstLoader}.java
plugins/pricer-v1, plugins/pricer-v2 (separate jars)
agent/src/main/java/com/lab43/agent/TimingAgent.java
src/test/java/.../{IsolationTest,UnloadTest,AgentTest}.java
```

## Phases
### Week 1 — Loaders + Bytecode (4–5h)
- Child-first loader, dual-version coexistence, javap exhibits.
- Deliverable: both pricers respond with correct versions isolated.
### Week 2 — Agent + Unload (4–5h)
- Timing agent, unload proof, shading case.
- Deliverable: leak-free report with heap + metaspace numbers.

## Test Plan
- Load v1 → price → unload → GC → weak ref cleared (3/3 runs).
- Cross-loader cast test expects CCE with loader-hash message assert.
- Agent test: timed span exists for each price call (in-memory registry).

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Isolation | Dual versions coexist | One isolated | Classpath soup |
| Identity | Boundary + CCE demo | Understood | Leaks across |
| Bytecode | Annotated javap trio | Dumps only | No reading |
| Agent | Zero-change timing | Works w/ changes | No agent |
| Unload | Heap+metaspace proof | Close impl | Loader leak |

Pass ≥ 70. Stretch: JPMS layer-based plugins; retransform already
loaded class via `retransformClasses` demo.

## Demo Checklist
- [ ] Both versions price differently in one JVM
- [ ] `javap` walkthrough of one invokedynamic site
- [ ] Agent timings printed per call
- [ ] Unload: loader weak-ref cleared live

## Common Traps
Casting plugin impl to plugin class (not host interface), static
cache pinning the loader, JDBC-driver-style registration leak.
