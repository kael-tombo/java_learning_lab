# Supply Chain Security - MINI PROJECT

## Project: ProvenPipe — a CI pipeline where every artifact carries verifiable provenance

Build a pipeline that pins dependencies, generates an SBOM, signs the image, attaches
provenance, and refuses to deploy anything unsigned. Then attack the pipeline to see
whether the controls hold.

### Architecture

```
  Commit ──> [verified build] ──> image (digest-pinned)
                │
                ├─▶ SBOM (CycloneDX) ──▶ stored with the image
                ├─▶ cosign signature (keyless, OIDC identity = the workflow)
                ├─▶ SLSA provenance (source repo, commit, builder)
                └─▶ publish
                          │
                          ▼
                [Admission verification]
                  signature valid? identity = our CI? provenance source = expected repo?
                  CVE gate vs threshold + exception registry
                  FAIL CLOSED otherwise
```

### Implementation

Maven dependency pinning so a build cannot silently pick up a different artifact:

```xml
<!-- Always pin by hash. A version range in a build is an unreviewed supply chain update. -->
<dependency>
  <groupId>com.fasterxml.jackson.core</groupId>
  <artifactId>jackson-databind</artifactId>
  <version>2.17.2</version>
  <!-- maven-enforcer fails the build if a checksum ever mismatches -->
</dependency>

<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-enforcer-plugin</artifactId>
  <executions><execution><goals><goal>enforce</goal></goals>
    <configuration><rules>
      <!-- Ban dynamic versions entirely: they are the mechanism of dependency confusion. -->
      <requireReleaseDeps><message>Dynamic versions are forbidden in a release build</message></requireReleaseDeps>
      <requireUpperBoundDeps/>
      <bannedDependencies>
        <excludes><exclude>commons-collections:commons-collections</exclude></excludes>
      </bannedDependencies>
      <requirePluginVersions/>
    </rules></configuration>
  </execution></executions>
</plugin>
```

The build workflow producing signed, attested artifacts:

```yaml
name: build-and-attest
on: [push]                       # runs on every push: review is a merge gate, not a release event
permissions:
  id-token: write                 # required for keyless signing (Sigstore OIDC)
  contents: read
  packages: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 1. SBOM for the JVM side, generated from the resolved dependency graph.
      - name: SBOM (CycloneDX)
        run: mvn -B cyclonedx:makeAggregateBom -DoutputFormat=json -DoutputName=bom.json
      - uses: actions/upload-artifact@v4
        with: { name: sbom, path: bom.json }

      # 2. Container build pinned by digest, not by floating tag.
      - name: Build and push by digest
        run: |
          docker buildx build --sbom true --provenance:mode=max \
            -t $IMAGE:$GITHUB_SHA .
          echo "DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' $IMAGE:$GITHUB_SHA)" >> $GITHUB_OUTPUT

      # 3. Keyless signature bound to the WORKFLOW identity, recorded in the transparency log.
      - name: Sign
        run: cosign sign --yes $IMAGE@${{ steps.build.outputs.DIGEST }}

      # 4. Attestation: links this image to this source commit.
      - run: cosign attest --yes --predicate provenance.json \
            --type slsaprovenance $IMAGE@${{ steps.build.outputs.DIGEST }}

      # 5. Admission will later require ALL of: signature, identity, provenance, SBOM.
      - run: |
          cosign save sbom --sbom bom.json $IMAGE@${{ steps.build.outputs.DIGEST }}
```

An admission verifier that fails closed, checking identity and source rather than
"is there a signature":

```java
public class ProvenanceVerifier {
    /**
     * Checks, in order, failing closed on any error:
     *   1. A signature exists for this digest.
     *   2. It was made by OUR CI identity, not by some other key that also signed it.
     *   3. Provenance names the expected source repo and the expected builder.
     *   4. An SBOM exists (so we can run the CVE gate against real components).
     */
    public VerificationResult verify(String imageRef) {
        if (!cosign.hasSignature(imageRef))
            return VerificationResult.reject("UNSIGNED", "no signature for " + imageRef);

        Identity id = cosign.identityOf(imageRef);
        if (!id.matches(expectedCiOidcPattern()))   // e.g. repo:org/platform/.github/workflows/build.yml@refs/heads/main
            return VerificationResult.reject("WRONG_IDENTITY", "signed by " + id);

        Provenance p = attestationStore.get(imageRef, "slsaprovenance");
        if (p == null)
            return VerificationResult.reject("NO_PROVENANCE", "no build provenance attached");
        if (!p.sourceRepository().equals(expectedRepo()))
            return VerificationResult.reject("WRONG_SOURCE", p.sourceRepository());
        if (!p.builderId().equals(expectedBuilderId()))
            return VerificationResult.reject("WRONG_BUILDER", p.builderId());

        Sbom sbom = sbomStore.get(imageRef);
        if (sbom == null)
            return VerificationResult.reject("NO_SBOM", "cannot evaluate vulnerability gate");
        var cves = cveGate.evaluate(sbom);
        if (cves.blocking().size() > 0)
            return VerificationResult.reject("CVE_THRESHOLD", cves.summary());

        return VerificationResult.accept(VerificationEvidence.of(id, p, sbom.componentCount()));
    }
}
```

Using the SBOM as a diff tool — its highest-value use, and the one teams skip:

```java
/** Fail the build when a release ADDS a new component or a new high/critical finding. */
boolean sbomDriftIsAcceptable(Sbom previous, Sbom current) {
    Set<String> added = new HashSet<>(current.components());
    added.removeAll(previous.components());
    if (!added.isEmpty()) {
        for (String c : added) {
            var finding = cveGate.lookup(c);
            if (finding.severity().atLeast(High)) {
                // A brand-new dependency with a known high CVE is a supply chain event,
                // not a routine diff. Requires an explicit, expiring exception.
                exceptions.requireTicketFor(c, finding);
            }
        }
        return false;   // force a human decision on newly introduced components
    }
    return cveGate.newHighFindings(previous, current).isEmpty();
}
```

### Test It

```java
@Test void unsignedImageIsRejected() {
    assertThat(verifier.verify("registry.internal/orders:latest").reason()).isEqualTo("UNSIGNED");
}

@Test void signatureFromAnotherIdentityIsRejected() {
    // Signed, but by a developer's laptop with a personal key: a valid signature, wrong identity.
    var res = verifier.verify(developerSignedImage);
    assertThat(res.reason()).isEqualTo("WRONG_IDENTITY");
}

@Test void imageFromAnotherRepositoryIsRejected() {
    // Signature and identity valid, but provenance says a fork was built.
    var res = verifier.verify(forkImage);
    assertThat(res.reason()).isEqualTo("WRONG_SOURCE");
}

@Test void newHighCveDependencyBlocksRelease() {
    assertThat(releaseGate.allows(sbomBefore, sbomWithNewVulnerableLib)).isFalse();
}

@Test void dependencyConfusionIsBlockedByLockfile() {
    // The internal artifact is resolved from the internal repo, not the public one.
    assertThat(resolvedArtifact("com.example:widget"))
        .isEqualTo("https://nexus.internal/repository/maven-releases/com/example/widget/1.4.2/widget-1.4.2.jar");
}
```

## Deliverables

- [ ] Enforcer rules banning dynamic versions, with lockfile/hash integrity verified
- [ ] CI workflow: build by digest, SBOM, keyless sign, SLSA provenance attest
- [ ] Admission verifier checking signature, identity, source repo, builder, and SBOM
- [ ] Fail-closed behaviour on every missing or mismatched element
- [ ] SBOM diff gate blocking releases that add a new high/critical component
- [ ] Exception registry with ticket, owner, and expiry for every suppressed finding
- [ ] Tests: unsigned, wrong identity, wrong source, CVE threshold, lockfile resolution
- [ ] Documented dependency inventory with an owner per top-level dependency
