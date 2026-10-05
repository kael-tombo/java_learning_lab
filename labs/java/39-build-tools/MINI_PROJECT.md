# MINI PROJECT — Build Tools: Release-Train for Shop Modules

## Goal (2 weeks, ~8–10h)
Give a 4-module shop build (Maven or Gradle) hermetic CI: 5-min pipeline,
locked deps, cached layers, scanned + SBOM-signed `jlink` release.

## Requirements
### Functional
1. Multi-module: `shop-api/orders/payments/app` with BOM/version catalog;
   no `SNAPSHOT` on release branch; `dependency:tree` / `dependencies`
   committed as baseline.
2. Profiles/variants: `dev` (H2, pretty logs), `prod` (Postgres, JSON logs,
   jlink image); `./mvnw -Pprod package` / `./gradlew prodImage` one-shot.
3. CI (GitHub Actions/Jenkins): stages lint → unit → slice → image → scan;
   Maven `.m2` / Gradle home cached; Docker layer order deps-first.
4. Security: `dependency-check` or OWASP + `versions:display-dependency-updates`
   triage; CycloneDX SBOM per release; Sigstore/cosign sign (or checksum log).
5. Speed: build scan/timeline attached; parallel (`-T1C` / `--parallel`)
   + incremental justified with numbers; flaky-network tests quarantined.
6. Release: tag `vX.Y.Z` → versioned `jlink` image + SBOM + provenance note;
   rollback = previous tag re-run (tested once).

### Non-functional
- Clean-clone + offline (`-o`) build documented; pinned CI image digest.
- 12+ build-health tests: enforcer (no duplicate classes, no float),
  SBOM exists, image smoke (`--help` + checkout once).
- README: dep-add checklist + cache diagram + release runbook.

## Phases
### Week 1 — Hermetic Build (4–5h)
- Steps: catalog/BOM, profiles, tree baseline, local speed pass.
- Deliverable: one-shot prod image locally.

### Week 2 — CI + Release (4–5h)
- Steps: pipeline + cache, scan/SBOM/sign, tag release + rollback drill.
- Deliverable: green release with evidence links.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| Determinism | Locked, offline-proof | Mostly pinned | Floats/SNAPSHOT |
| Modularity | Clean graph, enforced | Builds | Cycles |
| CI speed | < 5 min w/ cache proof | Cached | 15-min snowflake |
| Security | Scan + SBOM + sign | Scanned | Skipped |
| Release | Tag → image + rollback tested | Tagged | Laptop zip |

Pass >= 70. Stretch: remote build cache; JFR-profiled test fork sizing
(`jcmd Thread.print` on stuck suite); SLSA provenance file.
