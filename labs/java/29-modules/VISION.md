# VISION — Java Modules (JPMS)

## Vision Statement
**Modules make architecture enforceable** — `module-info.java` turns package
good-intentions into compiler errors, shrinking surface area, startup, and
supply-chain risk via `jlink` images.

---

## Mental Models
### 1. Encapsulation by Default
No `exports` = invisible, even if public. `exports` opens compile+runtime;
`opens` enables reflection (Spring/Hibernate). Design API packages first.
### 2. Requires Is a Contract
`requires com.foo` + `requires transitive` propagate readability. Split
packages (same package in two modules) are illegal — merge or rename.
### 3. Services Beat Classpath Scanning
`provides X with Y` / `uses X` + `ServiceLoader` replace fragile scanning.
Version conflicts surface at link time, not 2 a.m. `NoSuchMethodError`.
### 4. Image = App + Runtime Slice
`jlink` strips unused JDK modules → 40–80MB images, faster start. `jdeps`
reveals deps; unnamed-module jars become automatic modules (bridge path).

---

## Decision Framework
| Question | Rule |
|----------|------|
| New code? | Modularize API vs impl packages from day one |
| Reflection lib? | `opens` only that package, not whole module |
| Legacy jar? | Automatic module first, modularize top-down |
| Ship container? | `jlink` custom image over full JDK |
| Split package error? | Rename/merge — never hack with `--patch-module` in prod |

---

## Career Trajectory
- **L1:** `module-info`, exports/requires, compile+run modular app.
- **L2:** Services, `jdeps/jlink`, automatic-module migration.
- **L3:** Multi-module builds (Maven/Gradle), versioned images, layering.
- **L4:** Platform architecture (JDK upgrade trains, encapsulation policy).

---

## 4-Week Path
```
W1: module-info syntax, exports/opens, requires transitive.
W2: ServiceLoader migration, jdeps graph analysis.
W3: Legacy migration (automatic modules, split packages).
W4: jlink image + size/startup comparison capstone.
```
## Success Metrics
- [ ] Illegal access fails at compile, not runtime
- [ ] jdeps graph clean; jlink image runs with no full JDK
- [ ] Reflection scoped to opens packages only
