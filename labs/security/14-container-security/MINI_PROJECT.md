# Container Security - MINI PROJECT

## Project: HardenedJVM — a Dockerfile and Kubernetes manifest you can defend line by line

Start with a deliberately weak Java image, show each weakness, then produce a hardened
replacement plus a Pod Security Admission policy and a scanner gate.

### Architecture

```
  BASELINE (vulnerable)                 HARDENED
  ──────────────────────                ────────────────────────────────
  FROM eclipse-temurin:21-jre           FROM eclipse-temurin:21-jre@sha256:...
  USER root                             USER 10001:10001
  ENV DB_PASSWORD=supersecret           ARG version (build-time, not secret)
  ADD app.jar                           COPY --chown=10001 app.jar /app/app.jar
  (secrets in layer)                    (no secrets; env from mounted store)
  no healthcheck                        HEALTHCHECK with a real endpoint
  root capabilities available            securityContext: drop ALL, readOnlyRootFs
```

### Implementation

The hardened Dockerfile:

```dockerfile
# Pin by digest: a floating tag can be repointed to a compromised image.
FROM eclipse-temurin:21.0.5_11-jre@sha256:<digest> AS runtime

# Create a dedicated unprivileged account. UID must be explicit so a read-only rootfs
# can be enforced (no shell user, no home directory writes).
RUN groupadd -g 10001 app && useradd -u 10001 -g app -M -s /usr/sbin/nologin app

# Build in a separate stage so the compiler, source, and build cache never ship.
FROM eclipse-temurin:21.0.5_11-jdk@sha256:<digest> AS build
WORKDIR /build
COPY pom.xml ./
RUN --mount=type=cache,target=/root/.m2 mvn -B dependency:go-offline
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -B -DskipTests package

FROM runtime AS final
WORKDIR /app
COPY --from=build --chown=10001:10001 /build/target/app.jar /app/app.jar
# Read-only root filesystem means the app must not write anywhere under /app.
RUN mkdir -p /tmp/app && chown 10001:10001 /tmp/app
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=45s --retries=3 \
  CMD ["/bin/sh","-c","exec 3<>/dev/tcp/127.0.0.1/8080 && echo -e 'GET /actuator/health HTTP/1.0\\r\\n\\r\\n' >&3 && grep -q '\"status\":\"UP\"' <&3"]
ENTRYPOINT ["java","-XX:MaxRAMPercentage=75.0","-XX:+UseContainerSupport","-Djava.security.egd=file:/dev/./urandom","-jar","/app/app.jar"]
# Note: no ENV holding a secret. Secrets arrive as mounted files or the orchestrator's
# identity mechanism - never baked into a layer, where `docker history` reveals them.
```

Kubernetes security context and network policy:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: orders-api
spec:
  automountServiceAccountToken: false     # no API access unless needed
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
    seccompProfile: { type: RuntimeDefault }
  containers:
    - name: app
      image: registry.example.com/orders-api@sha256:<digest>   # digest, never a tag
      imagePullPolicy: IfNotPresent
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        privileged: false
        runAsNonRoot: true
        capabilities: { drop: ["ALL"] }        # no NET_RAW, no SYS_ADMIN, nothing
      resources:
        requests: { cpu: 250m, memory: 512Mi }  # cgroup limits: no noisy-neighbour escape
        limits:   { cpu: "1",  memory: 1Gi }
      volumeMounts:
        - { name: tmp, mountPath: /tmp }
        - { name: secrets, mountPath: /etc/secrets, readOnly: true }
  volumes:
    - name: tmp
      emptyDir: { medium: Memory }             # tmpfs, disappears on restart
    - name: secrets
      secret: { secretName: orders-api-secrets, defaultMode: 0400 }
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: orders-api }
spec:
  podSelector: { matchLabels: { app: orders-api } }
  policyTypes: [Ingress, Egress]
  ingress:
    - from: [{ podSelector: { matchLabels: { app: gateway } } }]
      ports: [{ port: 8080 }]
  egress:
    - to: [{ podSelector: { matchLabels: { app: postgres } } }]
      ports: [{ port: 5432 }]                  # only the database. DNS is handled separately.
```

An admission policy that makes the above mandatory instead of aspirational:

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata: { name: pod-security-baseline }
spec:
  failurePolicy: Fail
  validations:
    - expression: "has(object.spec.securityContext) && object.spec.securityContext.runAsNonRoot == true"
      message: "runAsNonRoot must be true"
    - expression: "object.spec.containers.all(c, !c.securityContext.privileged)"
      message: "privileged containers are forbidden"
    - expression: "object.spec.containers.all(c, has(c.securityContext.capabilities) && c.securityContext.capabilities.drop.exists(d, d == 'ALL'))"
      message: "all capabilities must be dropped"
    - expression: "object.spec.containers.all(c, c.securityContext.readOnlyRootFilesystem == true)"
      message: "readOnlyRootFilesystem must be true"
    - expression: "!has(object.spec.automountServiceAccountToken) || object.spec.automountServiceAccountToken == false"
      message: "service account tokens must not be auto-mounted"
```

### Test It

```java
@Test void imageRunsAsNonRoot() {
    var info = docker.inspectContainer(runningContainer());
    assertThat(info.config().user()).isNotEqualTo("root");
}

@Test void noSecretsInImageLayers() throws Exception {
    // The exact technique from the breach postmortems: run a busybox image and read /proc/1/environ
    var layers = docker.imageHistory(imageTag());
    assertThat(layers).noneMatch(l -> l.createdBy().contains("DB_PASSWORD"));
    var env = docker.exec(runningContainer(), List.of("env"));
    assertThat(env.stdout()).doesNotContain("PASSWORD");
}

@Test void readOnlyRootFilesystemIsEnforced() {
    var mounts = docker.inspectContainer(runningContainer()).mounts();
    assertThat(mounts).filteredOn(m -> m.destination().equals("/app")).isEmpty();
    assertThat(docker.exec(runningContainer(), List.of("touch","/app/evil")).exitCode()).isNotZero();
}

@Test void admissionPolicyRejectsViolations() {
    assertThatThrownBy(() -> kubectl.apply(violatingPodWithRoot()))
        .hasMessageContaining("runAsNonRoot must be true");
}
```

## Deliverables

- [ ] Hardened multi-stage Dockerfile with digest-pinned base images
- [ ] Non-root user, read-only root filesystem, all capabilities dropped
- [ ] No secrets in any layer; secrets via mounted volumes
- [ ] Kubernetes manifest with full `securityContext`, resource limits, tmpfs for `/tmp`
- [ ] Ingress and egress NetworkPolicies restricting traffic to named peers
- [ ] `ValidatingAdmissionPolicy` enforcing the baseline cluster-wide
- [ ] Tests: non-root, no layer secrets, read-only enforcement, admission rejection
- [ ] Vulnerability scan in CI with a documented exception process and expiry dates
