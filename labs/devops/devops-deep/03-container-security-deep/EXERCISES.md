# Container Security Deep Dive - Exercises

Hands-on tasks for image scanning, Dockerfile hardening, runtime security, and supply chain.

---

## Prerequisites

- Docker 24+ with BuildKit (`DOCKER_BUILDKIT=1`)
- `trivy`, `syft`, `cosign`, `grype`, `dive` installed
- Kubernetes cluster (kind/k3d) with Falco Operator or DaemonSet
- GitHub/GitLab account for CI/CD examples

---

## Exercise 1: Scan Existing Images for Vulnerabilities

```bash
# Pull a vulnerable image for testing
docker pull vulnerables/web-dvwa

# Trivy scan (OS packages + language packages)
trivy image --severity HIGH,CRITICAL vulnerables/web-dvwa

# Trivy with JSON output for CI
trivy image --format json --output trivy-report.json vulnerables/web-dvwa

# Grype scan (different DB)
grype vulnerables/web-dvwa -o table

# Docker Scout (if Docker Hub image)
docker scout cves vulnerables/web-dvwa
docker scout recommendations vulnerables/web-dvwa

# Compare results
# Note: Different scanners use different vulnerability databases
```

**✅ Verify**: Identify at least 5 HIGH/CRITICAL CVEs; note which are fixable vs unfixed.

---

## Exercise 2: Generate and Analyze SBOM

```bash
# Generate SBOM with Syft (SPDX format)
syft vulnerables/web-dvwa -o spdx-json > dvwa-sbom.spdx.json

# Generate SBOM with Trivy (CycloneDX format)
trivy image --format cyclonedx vulnerables/web-dvwa > dvwa-sbom.cdx.json

# Inspect SBOM
jq '.packages | length' dvwa-sbom.spdx.json
jq '.packages[] | select(.name | contains("openssl"))' dvwa-sbom.spdx.json

# Cross-reference with vulnerabilities
grype sbom:dvwa-sbom.spdx.json -o table

# Query specific package versions
jq '.packages[] | {name: .name, version: .versionInfo}' dvwa-sbom.spdx.json | grep -E "(nginx|openssl|apache)"
```

**✅ Verify**: SBOM contains 100+ packages; can query specific component versions.

---

## Exercise 3: Harden a Dockerfile with Multi-Stage Build

**Starting Dockerfile (insecure):**
```dockerfile
# Dockerfile.insecure
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python3-pip curl
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8000
CMD ["python3", "app.py"]
```

**Task**: Create hardened version:
```dockerfile
# Dockerfile.hardened
# syntax = docker/dockerfile:1.4

# Stage 1: Build dependencies
FROM python:3.12-slim AS builder
WORKDIR /build
# Install build deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim AS runtime
# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1000 appuser
# Install runtime deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*
# Copy wheels from builder
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
# Copy app code
COPY --chown=appuser:appgroup . /app
WORKDIR /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["python3", "app.py"]
```

```bash
# Build both
DOCKER_BUILDKIT=1 docker build -f Dockerfile.insecure -t myapp:insecure .
DOCKER_BUILDKIT=1 docker build -f Dockerfile.hardened -t myapp:hardened .

# Compare sizes
docker images myapp:insecure myapp:hardened

# Scan both
trivy image --severity HIGH,CRITICAL myapp:insecure
trivy image --severity HIGH,CRITICAL myapp:hardened

# Inspect layers
dive myapp:hardened
```

**✅ Verify**: Hardened image <50% size, fewer vulnerabilities, non-root user, no build tools.

---

## Exercise 4: Distroless Base Image

```dockerfile
# Dockerfile.distroless
FROM golang:1.22 AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o /app .

# Distroless static (no libc) - for pure Go binaries
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /app /app
USER nonroot:nonroot
ENTRYPOINT ["/app"]
```

```bash
# Build
DOCKER_BUILDKIT=1 docker build -f Dockerfile.distroless -t myapp:distroless .

# Compare
docker images myapp:hardened myapp:distroless

# Scan
trivy image --severity HIGH,CRITICAL myapp:distroless

# Try to shell into it (should fail)
docker run --rm -it myapp:distroless sh
# Error: exec: "sh": executable file not found in $PATH
```

**✅ Verify**: Distroless image ~10MB, zero HIGH/CRITICAL vulns, no shell access.

---

## Exercise 5: Build-Time Secrets with BuildKit

```dockerfile
# Dockerfile.secrets
# syntax = docker/dockerfile:1.4
FROM golang:1.22 AS builder
WORKDIR /src
# Private Go module via SSH
RUN --mount=type=ssh \
    git config --global url."git@github.com:".insteadOf "https://github.com/" \
    && go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app .

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app /app
USER nonroot:nonroot
ENTRYPOINT ["/app"]
```

```bash
# Build with SSH agent forwarding
DOCKER_BUILDKIT=1 docker build \
  --ssh default \
  -f Dockerfile.secrets \
  -t myapp:secrets .

# NPM token example
# Dockerfile.npm
# syntax = docker/dockerfile:1.4
FROM node:20-alpine AS builder
WORKDIR /app
RUN --mount=type=secret,id=npmrc,dst=/root/.npmrc \
    npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

```bash
# Build with npm token
DOCKER_BUILDKIT=1 docker build \
  --secret id=npmrc,src=.npmrc \
  -f Dockerfile.npm \
  -t myapp:npm .
```

**✅ Verify**: Build succeeds with private deps; secrets not in image layers (`docker history --no-trunc`).

---

## Exercise 6: Image Signing and Verification with Cosign

```bash
# Generate keyless signature (uses GitHub OIDC in CI, or local gcloud/aws)
cosign sign --yes docker.io/youruser/myapp:latest

# Verify locally
cosign verify docker.io/youruser/myapp:latest

# Verify with specific identity (CI/CD)
cosign verify \
  --certificate-identity-regexp ".*github.com/yourorg/yourrepo.*" \
  --certificate-oidc-issuer-regexp ".*token.actions.githubusercontent.com.*" \
  docker.io/youruser/myapp:latest

# Attach SBOM as attestation
cosign attest --predicate dvwa-sbom.spdx.json --type spdx docker.io/youruser/myapp:latest

# Verify attestation
cosign verify-attestation --type spdx docker.io/youruser/myapp:latest

# Verify in Kubernetes (with Kyverno/Gatekeeper)
# Kyverno policy verifies cosign signature on Pod creation
```

**✅ Verify**: Signature stored in registry; verification passes with correct identity.

---

## Exercise 7: Rootless Container Runtime

### Docker Rootless Mode
```bash
# Install rootless Docker
curl -fsSL https://get.docker.com/rootless | sh
export PATH=/usr/bin:$PATH
export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock

# Start rootless daemon
systemctl --user start docker

# Run container
docker run -d -p 8080:80 nginx:alpine

# Verify process ownership on host
ps aux | grep nginx
# Should show your user, not root
```

### Podman (Rootless by Default)
```bash
# Podman is rootless by default
podman run -d -p 8080:80 nginx:alpine
podman ps

# Check user namespace mapping
podman top <container> huser
# Shows host UID (e.g., 100000) not 0
```

### Kubernetes Rootless (SecurityContext)
```yaml
# pod-rootless.yaml
apiVersion: v1
kind: Pod
metadata:
  name: rootless-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:hardened
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
      readOnlyRootFilesystem: true
```

```bash
kubectl apply -f pod-rootless.yaml
kubectl exec rootless-pod -- id
# Should show uid=1000(appuser) gid=1000(appgroup)
```

**✅ Verify**: Container processes run as unprivileged host user; no privilege escalation.

---

## Exercise 8: Seccomp Profile Customization

```bash
# 1. Get default Docker seccomp profile
curl -sSL https://raw.githubusercontent.com/moby/moby/master/profiles/seccomp/default.json > docker-default.json

# 2. Create custom restrictive profile (allowlist)
cat > my-seccomp.json <<'EOF'
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "defaultErrnoRet": 1,
  "architectures": ["SCMP_ARCH_X86_64", "SCMP_ARCH_X86", "SCMP_ARCH_X32"],
  "syscalls": [
    {"names": ["read", "write", "openat", "close", "exit", "exit_group", "rt_sigreturn", "futex", "nanosleep", "getpid", "getuid", "geteuid", "getgid", "getegid"], "action": "SCMP_ACT_ALLOW"},
    {"names": ["socket", "connect", "sendto", "recvfrom", "bind", "listen", "accept", "getsockopt", "setsockopt"], "action": "SCMP_ACT_ALLOW"}
  ]
}
EOF

# 3. Test with a simple app
cat > test-seccomp.c <<'EOF'
#include <unistd.h>
#include <sys/syscall.h>
int main() {
    // Allowed: write
    write(1, "hello\n", 6);
    // Blocked: ptrace
    syscall(SYS_ptrace, 0, 0, 0, 0);
    return 0;
}
EOF

docker run --rm -v $PWD:/src -w /src gcc:12 gcc test-seccomp.c -o test-seccomp
docker run --rm --security-opt seccomp=my-seccomp.json -v $PWD:/src -w /src gcc:12 ./test-seccomp
# Should print "hello" then crash with "Bad system call" (SIGSYS)
```

### Kubernetes Seccomp
```yaml
# pod-seccomp.yaml
apiVersion: v1
kind: Pod
metadata:
  name: seccomp-pod
  annotations:
    seccomp.security.alpha.kubernetes.io/pod: localhost/my-seccomp
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: my-seccomp.json
  containers:
  - name: app
    image: myapp:hardened
```

**✅ Verify**: Custom seccomp blocks dangerous syscalls; app still functions.

---

## Exercise 9: Runtime Threat Detection with Falco

### Install Falco (DaemonSet)
```bash
# Add Helm repo
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update

# Install with default rules
helm install falco falcosecurity/falco \
  --namespace falco --create-namespace \
  --set driver.kind=ebpf \
  --set ebpf.enabled=true

# Or install Falco Operator for CRD management
kubectl apply -f https://raw.githubusercontent.com/falcosecurity/falco-operator/master/deploy/crds/falcosecurity.com_falcos.yaml
```

### Test Detection Rules
```bash
# 1. Spawn shell in container (triggers "Terminal Shell in Container" rule)
kubectl run test-shell --image=ubuntu:22.04 --restart=Never -- /bin/bash
# Check Falco logs
kubectl logs -n falco -l app=falco -f | grep "Shell spawned"

# 2. Write to /etc (triggers "Write to /etc" rule)
kubectl exec test-shell -- touch /etc/test-file
kubectl logs -n falco -l app=falco -f | grep "Write to /etc"

# 3. Network connection to suspicious port
kubectl exec test-shell -- nc -zv 10.0.0.1 22
kubectl logs -n falco -l app=falco -f | grep "outbound_connection"

# 4. Privileged pod creation
kubectl run privileged-pod --image=ubuntu --restart=Never --overrides='{"spec":{"containers":[{"name":"c","image":"ubuntu","securityContext":{"privileged":true}}]}}'
kubectl logs -n falco -l app=falco -f | grep "privileged_container"
```

### Custom Falco Rule
```yaml
# custom-rule.yaml
apiVersion: falcosecurity.io/v1alpha1
kind: FalcoRule
metadata:
  name: custom-rules
  namespace: falco
spec:
  rules:
  - rule: Unauthorized ConfigMap Access
    desc: Detect reads of sensitive ConfigMaps
    condition: >
      k8s_configmap_read and k8s_configmap_name in (sensitive-config, secrets-config)
    output: "Unauthorized ConfigMap read (user=%ka.user.name ns=%ka.namespace configmap=%ka.configmap.name)"
    priority: ERROR
    tags: [k8s, configmap]
```

```bash
kubectl apply -f custom-rule.yaml
```

**✅ Verify**: Falco detects shell spawn, file writes, network connections, privileged pods.

---

## Exercise 10: Admission Control with Kyverno

```bash
# Install Kyverno
helm repo add kyverno https://kyverno.github.io/kyverno/
helm install kyverno kyverno/kyverno -n kyverno --create-namespace
```

### Policy: Require Non-Root + ReadOnly Root FS + Drop Capabilities
```yaml
# policy-container-security.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: container-security-baseline
spec:
  validationFailureAction: Enforce
  background: true
  rules:
  - name: require-non-root
    match:
      any:
      - resources:
          kinds: ["Pod"]
    validate:
      message: "runAsNonRoot must be true"
      pattern:
        spec:
          securityContext:
            runAsNonRoot: true
  - name: require-readonly-rootfs
    match:
      any:
      - resources:
          kinds: ["Pod"]
    validate:
      message: "containers must have readOnlyRootFilesystem=true"
      pattern:
        spec:
          containers:
          - securityContext:
              readOnlyRootFilesystem: true
  - name: drop-all-capabilities
    match:
      any:
      - resources:
          kinds: ["Pod"]
    validate:
      message: "containers must drop ALL capabilities"
      pattern:
        spec:
          containers:
          - securityContext:
              capabilities:
                drop: ["ALL"]
  - name: no-privilege-escalation
    match:
      any:
      - resources:
          kinds: ["Pod"]
    validate:
      message: "allowPrivilegeEscalation must be false"
      pattern:
        spec:
          containers:
          - securityContext:
              allowPrivilegeEscalation: false
```

```bash
kubectl apply -f policy-container-security.yaml

# Test: Try to deploy violating pod
cat > violating-pod.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: violating-pod
spec:
  containers:
  - name: app
    image: nginx:alpine
    securityContext:
      runAsNonRoot: false
      allowPrivilegeEscalation: true
EOF

kubectl apply -f violating-pod.yaml
# Should be REJECTED by Kyverno
```

### Policy: Verify Cosign Signature
```yaml
# policy-cosign.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signature
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-cosign-signature
    match:
      any:
      - resources:
          kinds: ["Pod"]
    verifyImages:
    - image: "docker.io/yourorg/*"
      key: |-
        -----BEGIN PUBLIC KEY-----
        MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...
        -----END PUBLIC KEY-----
      # Or use keyless verification
      # attestations:
      # - type: slsaprovenance
```

**✅ Verify**: Violating pods rejected; signed images allowed; unsigned images blocked.

---

## Exercise 11: CI/CD Pipeline Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/container-security.yml
name: Container Security
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write
      security-events: write
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Build image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: false
        tags: myapp:${{ github.sha }}
        load: true
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Run Trivy scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: myapp:${{ github.sha }}
        format: sarif
        output: trivy.sarif
        severity: HIGH,CRITICAL
        ignore-unfixed: true
    
    - name: Upload Trivy results to GitHub Security
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: trivy.sarif
    
    - name: Generate SBOM
      run: |
        syft myapp:${{ github.sha }} -o spdx-json > sbom.spdx.json
    
    - name: Upload SBOM
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: sbom.spdx.json
        category: sbom
    
    - name: Sign image (on main branch)
      if: github.ref == 'refs/heads/main'
      uses: sigstore/cosign-installer@v3
      with:
        cosign-release: 'v2.2.0'
    
    - name: Sign with cosign
      if: github.ref == 'refs/heads/main'
      env:
        COSIGN_EXPERIMENTAL: "true"
      run: |
        cosign sign --yes docker.io/${{ github.repository }}:${{ github.sha }}
```

---

## Exercise 12: Supply Chain - SLSA Provenance

```bash
# Install slsa-verifier
curl -LO https://github.com/slsa-framework/slsa-verifier/releases/latest/download/slsa-verifier-linux-amd64
chmod +x slsa-verifier-linux-amd64

# Generate provenance (GitHub Actions)
# Add to workflow:
# - uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v1.9.0

# Verify provenance locally
slsa-verifier verify-artifact \
  --provenance-path intoto-provenance.json \
  --source-uri github.com/yourorg/yourrepo \
  myapp.tar.gz
```

---

## Challenge Exercises

| # | Challenge | Description |
|---|-----------|-------------|
| 1 | **Custom Trivy Policies** | Write OPA/Rego policies for custom vulnerability filtering (e.g., ignore CVE-2023-xxxx in dev) |
| 2 | **Image Mutation Admission** | Kyverno mutate: auto-add `securityContext` to Pods missing it |
| 3 | **Runtime Encryption** | Use `gVisor` or `Kata Containers` for stronger isolation; compare syscall surface |
| 4 | **Notary v2 / Sigstore** | Set up Fulcio + Rekor for keyless signing with CT log transparency |
| 5 | **SBOM Diff in PR** | GitHub Action that compares SBOM between base and PR, fails on new HIGH vulns |

---

## Validation Checklist

- [ ] Scan images with Trivy/Grype/Docker Scout; interpret results
- [ ] Generate SBOM (SPDX/CycloneDX) with Syft/Trivy
- [ ] Harden Dockerfile: multi-stage, distroless, non-root, pinned digests
- [ ] Use BuildKit secrets for build-time credentials
- [ ] Sign images with cosign (keyless); verify signatures
- [ ] Run containers rootless (Docker rootless, Podman, K8s securityContext)
- [ ] Create and apply custom seccomp profiles
- [ ] Deploy Falco; test detection rules; write custom rule
- [ ] Install Kyverno; enforce container security policies
- [ ] Verify cosign signatures at admission time
- [ ] Integrate Trivy + SBOM + cosign in CI/CD pipeline
- [ ] Generate SLSA provenance for builds

---

## Resources

- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Distroless Images](https://github.com/GoogleContainerTools/distroless)
- [BuildKit Secrets](https://docs.docker.com/build/building/secrets/)
- [cosign/sigstore](https://docs.sigstore.dev/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Falco Rules](https://falco.org/docs/rules/)
- [Kyverno Policies](https://kyverno.io/policies/)
- [SLSA Framework](https://slsa.dev/)
- [NIST SP 800-190](https://csrc.nist.gov/publications/detail/sp/800-190/final) - Container Security Guide