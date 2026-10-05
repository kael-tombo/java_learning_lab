# VISION — Class Loading & Bytecode

## Vision Statement
**The JVM runs bytecode, not source** — whoever understands loaders,
linking, and `javap` output can debug "works on my machine",
plugin isolation, and agent magic that source-level thinking cannot.

---
## Mental Models
### 1. Loading Is Delegation
Bootstrap → platform → app → custom. Parent-first by default;
child-first (web containers) and module layers break it on purpose.
### 2. Identity = Name + Loader
Same FQN in two loaders = two types → `ClassCastException` with
identical names. Leaks live as long as the loader lives.
### 3. Linking Has Three Steps
Verification → preparation → resolution. `NoSuchMethodError` at
runtime means compile-time and runtime classpaths diverged.
### 4. Bytecode Is a Stack Machine
`javap -c` shows pushes/pops/invokes. `invokedynamic` + constant
pool explain lambdas, string concat, and agent rewrites.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Plugin isolation? | One child-first loader per plugin, closeable |
| Duplicate class bug? | `-verbose:class` + loader-hash dump first |
| Transform at load? | javaagent + ASM/ByteBuddy, never custom javac hack |
| Reflection heavy? | MethodHandles/Lookup; cache, check modules |

---
## Career Trajectory
- **L1:** classpath vs modulepath, `javap -c`, `-verbose:class`.
- **L2:** Custom loaders, parent-first/child-first, shading.
- **L3:** Instrumentation agents, retransformation, JPMS layers.
- **L4:** Plugin platforms, hot-reload safety, loader-leak forensics.

---
## 4-Week Path
```
W1: javap + constant-pool reading; verbose:class duplicate hunt.
W2: Custom loader (child-first plugin) with isolation + close test.
W3: Javaagent timing agent (ByteBuddy/ASM) + retransform demo.
W4: Plugin host with unload + metaspace/loader-leak drill (JFR + dump).
```
## Success Metrics
- [ ] Read `javap -c` for lambda/switch and explain invokes
- [ ] `ClassCastException` diagnosed to loader pair in minutes
- [ ] Agent adds timing with zero source change
- [ ] Unloaded plugin's loader GC'd (heap + metaspace proof)

## What This Is Not
Writing bytecode by hand daily. It is loader forensics fluency.

> Mantra: **Same name, different loader, different type.**
