# Supply Chain Security - REAL WORLD PROJECT

## Project: ChainOfRecord — raising a Java platform's build integrity to SLSA L3

A platform team builds and ships artifacts for 60 product teams: container images, JARs,
Helm charts, and infrastructure modules. Today a compromise in any one team's build
pipeline would reach every production environment undetected. The programme makes the
build itself trustworthy and provable.

### Architecture

```
  Source (protected branch, CODEOWNERS + review)
        │  signed commits
        ▼
  ┌───────────────────── Hermetic build (no network at compile time) ─────────────────────┐
  │  pinned base images by digest   │  pinned JDK + Maven container                    │
  │  all dependencies from an internal mirror, hash-verified   │  SBOM generated         │
  │  no secrets available to the build step   │  build outputs written to a fresh layer │
  └────────────────────────────────────┬─────────────────────────────────────────────────┘
                                       ▼
                        Attestation + signature (Sigstore, keyless,
                        OIDC identity = the specific reusable workflow)
                                       │
                       Transparency log (public, tamper-evident)
                                       │
  ┌────────────────────────────────────┴─────────────────────────────────────────────────┐
  │ Deployment: admission verifies signature + identity + provenance + SBOM              │
  │ BEFORE the pod is scheduled. Unsigned or unproven artifacts never reach a node.     │
  └─────────────────────────────────────────────────────────────────────────────────┘
```

### Implementation

Egress-denied build, which is the single change that makes the build hermetic:

```yaml
# The build job has no package-registry network access. Dependencies are pre-fetched
# into a verified cache by a separate, less-privileged step. A compromised build script
# cannot reach the internet to exfiltrate, to resolve a hijacked dependency, or to phone home.
jobs:
  fetch-dependencies:            # network-allowed, but runs only the resolver
    permissions: { contents: read }
    steps:
      - run: mvn -B -Dmaven.repo.local=/cache dependency:go-offline
      - run: mvn -B dependency:verify          # checks recorded checksums
  build:                        # network-DENIED
    permissions: { id-token: write, contents: read }   # only signing needs the network
    steps:
      - run: mvn -B -o -Dmaven.repo.local=/cache package   # -o = offline mode
      - run: ./generate-sbom.sh
      - run: cosign sign --yes $IMAGE@$DIGEST
      - run: cosign attest --yes --predicate provenance.json --type slsaprovenance $IMAGE@$DIGEST
# A network policy for the runner enforces "no egress" - configuration alone is a suggestion.
```

Policy as code, so the security rules are reviewable and testable:

```rego
package pipeline.admission

default decision := {"allow": false, "reason": "default deny"}

# Only artifacts built by our own workflows, in our own repo, from a protected branch.
decision := {"allow": true} if {
    input.attestation.predicate.buildDefinition.externalParameters.workflow.repository == "github.com/example/platform"
    input.attestation.predicate.buildDefinition.externalParameters.workflow.ref == "refs/heads/main"
    input.attestation.predicate.materials[0].uri == "git+https://github.com/example/orders"
}

# Every admitted image must have an SBOM and a CVE decision.
decision := {"allow": false, "reason": "no sbom"} if {
    not input.sbom
}

decision := {"allow": false, "reason": "cve: " + input.cve.summary} if {
    input.cve.critical > 0
    not exceptions.covers(input.image, input.cve)
}

# Time-bound exceptions: the policy stops honouring a waiver automatically.
decision := {"allow": true} if {
    input.attestation.verified
    input.sbom
    input.cve.critical == 0
}
```

Dependency governance, because the SBOM is only useful with someone accountable for it:

```java
@Component
class DependencyOwnershipEnforcer {
    // Every top-level dependency has a named owning team and a review date. Unowned
    // dependencies are flagged for the owning service team, not for the platform team -
    // otherwise the platform team becomes a bottleneck nobody bypasses correctly.
    @Scheduled(cron = "0 0 4 * * MON")
    void reportUnownedDependencies() {
        for (Artifact a : catalog.allComponents()) {
            if (a.isTransitive()) continue;
            if (!ownershipRegistry.hasOwner(a.coordinates())) {
                report.flag("UNOWNED_DEPENDENCY", a.coordinates(), a.usageSummary());
                catalog.tag(a.coordinates(), RiskTier.TIER_2);   // lower trust, faster CVE review
            }
        }
    }

    /** Golden rule: a new dependency needs a justification, an owner, and a licence check. */
    Decision onNewDependencyProposal(Proposal p) {
        if (!licences.isApproved(p.licence())) return Decision.reject("licence not approved: " + p.licence());
        if (maintainers().isSingleMaintainer(p.coordinates())) return Decision.flag("single-maintainer risk");
        if (cveHistory().hasRecentCritical(p.coordinates())) return Decision.flag("recent critical CVE");
        return Decision.accept(requiresOwner: true);
    }
}
```

### Non-functional requirements

- **Build integrity**: L3 target — builds are hermetic and isolated, so a compromised
  source repo cannot reach the network during compilation.
- **Coverage**: 100% of production artifacts carry signature, provenance, and SBOM.
  Verification happens at admission, so a misconfigured deploy path still cannot ship.
- **Transparency**: keyless signatures in a public transparency log, so a rogue key
  cannot be quietly added and cannot erase history.
- **Blast radius**: per-artifact identity (`workflow path + ref`), so a compromised
  experimental branch cannot sign something that looks like a release build.
- **CVE SLA**: critical 48 h, high 7 d. Waivers require a named owner, a compensating
  control, and a 30-day expiry enforced by the policy engine.
- **Caching**: the dependency pre-fetch step is hash-verified and immutable, so
  reproducibility improves without pinning us to a stale mirror.
- **Adoption**: the platform provides a reusable workflow and a conformance test, so a
  team does not have to reimplement provenance to be compliant.
- **Measurement**: report on provenance coverage, waiver count and age, and mean time to
  re-issue a verified artifact during an incident.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- SLSA (Supply-chain Levels for Software Artifacts) defines build provenance and the
  build-level requirements this pipeline is designed to satisfy, up to hermetic/isolated builds.
  https://slsa.dev/spec/v1.0/
- Kubernetes admission control and the Kubernetes security documentation describe enforcing
  policy before workload creation, which is where signature and provenance checks run.
  https://kubernetes.io/docs/concepts/security/

## Deliverables

- [x] Hermetic build: network-denied compile step, verified offline dependency cache
- [x] Keyless signing and SLSA provenance attestation with per-workflow identity
- [x] Admission verification of signature, identity, source, and SBOM before scheduling
- [x] Policy-as-code for the admission decision, with time-bounded automatic exceptions
- [x] Dependency ownership registry, golden-rule new-dependency process, licence checking
- [x] SBOM drift gate blocking releases that introduce new high/critical components
- [x] Reusable workflow plus conformance test so teams inherit provenance
- [x] Compliance dashboard: provenance coverage, waiver count and age, CVE remediation SLA
