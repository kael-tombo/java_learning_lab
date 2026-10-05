# VISION — Supply Chain Security: Trusting the Build, Not the Artifact
> Where this lab takes you: from "we scan dependencies" to a pipeline where provenance is verifiable end to end.

## The Arc
1. **The problem** — the modern compromise surface: dependencies, build systems, CI, and artifacts.
2. **Dependency risk** — confusion, typosquatting, transitive depth, and lockfile integrity.
3. **Build integrity** — reproducible builds, hermetic pipelines, and the build-vs-runtime split.
4. **Provenance & signing** — SLSA levels, Sigstore/cosign, SBOM, and admission verification.
5. **Governance** — policy, exceptions with expiry, and the human process around all of it.

## Milestones (checkable)
- [ ] M1: pull a transitive dependency tree to depth 20 and identify your highest-risk package.
- [ ] M2: demonstrate dependency confusion and explain the fix.
- [ ] M3: generate an SBOM and diff it against the previous release.
- [ ] M4: sign an image and verify it at admission, failing closed on an unsigned artifact.
- [ ] M5: state your build's SLSA level and name exactly what that level does not prove.

## Core Competencies
- Dependency confusion, typosquatting, and lockfile/hash pinning.
- SBOM generation (CycloneDX/SPDX) and using it as a diff tool rather than a report.
- Signing and verification workflows: keys, transparency logs, and admission-time policy.
- SLSA provenance and the incremental trust each build level actually adds.

## Anti-Goals
- A scan that reports vulnerabilities with no remediation path or ownership.
- A security-review process that only runs on release, not on every merge.
- Trusting a signature without checking *which* identity signed it.

## Interview Lens
- "How do you know the JAR inside your container came from your source commit?"
- "A transitive dependency is compromised. What do you do in the first hour?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: dependency tree, SBOM, and a first signature.
- Wk2 QUIZ/FLASHCARDS to 90%+; configure admission verification.
- Wk3 MINI_PROJECT building a verified pipeline.
- Wk4 REAL_WORLD_PROJECT: SLSA level increase with exception governance.

## Done = You Can
- Explain the provenance chain for a running artifact, from source commit to deployed
  image, and identify every place a guarantee is currently missing.
