# VISION — Build Tools (Maven, Gradle)

## Vision Statement
**Builds are contracts: hermetic, reproducible, fast** — declarative deps,
locked versions, cached layers, and signed SBOMs so `main` builds anywhere
and releases are boring.

---

## Mental Models
### 1. Declare, Don't Script
`pom.xml`/`build.gradle.kts` state intent (deps, plugins, profiles); custom
shell in CI is debt. Convention (standard layout) beats configuration.
### 2. Versions Are Pinned Graphs
BOMs + lockfiles (`mvn -o`, Gradle version catalogs) make transitive graphs
deterministic. `SNAPSHOT`/ranges float — releases never float.
### 3. Cache Is Architecture
Local `.m2`/Gradle cache + remote cache + layer caching (deps before code)
cut minutes. Parallel + incremental + daemon: measure, then tune.
### 4. Release Is Evidence
`jlink/jpackage` artifacts + SBOM (CycloneDX) + provenance (SLSA/Sigstore) +
pinned CI image = auditable supply chain, not a zip on a laptop.

---

## Decision Framework
| Question | Rule |
|----------|------|
| Maven or Gradle? | Maven for convention; Gradle for speed/customization at scale |
| Add a dep? | Check CVE + size + transitive fan-out first |
| Slow build? | Profile (scan/timeline), cache, parallelize — not new hardware |
| Release? | Locked versions + SBOM + signed, from CI only |
| Flaky CI? | Quarantine network-dependent tests; retry nothing blindly |

---

## Career Trajectory
- **L1:** Build/test/package locally, read dependency tree.
- **L2:** Multi-module builds, profiles, version catalogs/BOMs.
- **L3:** CI caching, perf tuning, SBOM/signing, release trains.
- **L4:** Build platform (standards, remote cache, supply-chain policy).

---

## 4-Week Path
```
W1: Maven lifecycle, dependency tree, Gradle wrapper + tasks.
W2: Multi-module build, BOM/catalog, profiles per env.
W3: CI pipeline (cache, test split, jlink image), scan + SBOM.
W4: Release-train capstone (version → sign → verify).
```
## Success Metrics
- [ ] Clean-clone build green, no `latest`/float
- [ ] CI < 5 min with cache; SBOM + scan attached
- [ ] Release reproducible from tag by a stranger
