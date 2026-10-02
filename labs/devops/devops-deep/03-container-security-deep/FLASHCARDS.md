# Container Security Deep Dive - Flashcards

Spaced repetition: **Question** → **Answer**

---

## Image Security

**What is an SBOM?**
→ Software Bill of Materials - complete inventory of all packages, libraries, dependencies, versions, licenses in a container image. Formats: SPDX, CycloneDX. Tools: Syft (`syft image`), Trivy (`trivy image --format cyclonedx`), Docker Scout.

**How to generate SBOM?**
→ `syft <image> -o spdx-json > sbom.json`
→ `trivy image --format cyclonedx <image> > sbom.json`
→ `docker scout sbom <image>`

**What is image signing (cosign/sigstore)?**
→ Keyless signing using OIDC identity (GitHub Actions, GitLab CI). `cosign sign --yes $IMAGE` stores signature in registry (`$IMAGE.sig`). `cosign verify $IMAGE` validates. Integrates with admission controllers (Kyverno, Gatekeeper) for deploy-time verification.

**How to verify image provenance?**
→ `cosign verify --certificate-identity-regexp ".*github.com.*" --certificate-oidc-issuer-regexp ".*token.actions.githubusercontent.com.*" $IMAGE`
→ SLSA provenance: `cosign verify-attestation --type slsaprovenance $IMAGE`

**Base image pinning best practice?**
→ Use digest, not tag: `FROM ubuntu@sha256:abc123...` not `FROM ubuntu:22.04`. Tags are mutable; digests are immutable. Automate with Renovate/Dependabot.

---

## Dockerfile Hardening

**Multi-stage build pattern?**
```dockerfile
# Stage 1: Build
FROM golang:1.22 AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app .

# Stage 2: Runtime (distroless)
FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app /app
USER nonroot:nonroot
ENTRYPOINT ["/app"]
```
→ Final image: ~10MB vs ~800MB, no shell, no package manager, no build tools.

**Distroless vs Alpine vs Scratch?**
→ **scratch**: Empty, only your binary (statically linked). Smallest but no libc, no certs, no tzdata.
→ **distroless**: Minimal Debian-based, includes libc, certs, tzdata. Variants: static, nonroot, debug.
→ **alpine**: musl libc, apk package manager, ~5MB. Good compromise but has package manager.

**Dockerfile security best practices?**
→ 1. Pin base digest (`FROM ubuntu@sha256:...`)
→ 2. Multi-stage build
→ 3. Non-root user (`RUN useradd -u 1000 appuser && USER appuser`)
→ 4. `.dockerignore` (exclude `.git`, `*.pem`, `node_modules`, `.env`)
→ 5. `--mount=type=secret` for build-time secrets (SSH keys, tokens)
→ 6. No `apt-get upgrade` (reproducibility)
→ 7. Combine RUN layers (reduce layers, cache busting)
→ 8. `COPY --chown=appuser:appuser` for file ownership
→ 9. `HEALTHCHECK` for runtime health
→ 10. `LABEL` for metadata (maintainer, version, sbom-ref)

**Build-time secrets (BuildKit)?**
```dockerfile
# syntax = docker/dockerfile:1.4
FROM golang:1.22
RUN --mount=type=ssh ssh-keyscan github.com >> /root/.ssh/known_hosts
RUN --mount=type=secret,id=npmrc,dst=/root/.npmrc npm ci
```
→ `DOCKER_BUILDKIT=1 docker build --ssh default --secret id=npmrc,src=.npmrc .`

---

## Runtime Security

**Rootless containers?**
→ Container root (uid 0) maps to unprivileged host uid via user namespace (`/proc/<pid>/uid_map`).
→ Docker: `dockerd --userns-remap=default` (maps to `dockremap` user).
→ Podman: rootless by default (`podman run`).
→ Kubernetes: `runAsUser: 1000`, `runAsNonRoot: true`, `runAsGroup: 1000` in securityContext.
→ Limitation: Some syscalls unavailable, nested containers complex.

**Seccomp profiles?**
→ Default Docker profile: blocks ~44 syscalls (keyctl, bpf, ptrace, process_vm_readv/writev, etc.).
→ Custom profile (allowlist):
```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {"names": ["read", "write", "open", "close", "exit"], "action": "SCMP_ACT_ALLOW"}
  ]
}
```
→ Apply: `docker run --security-opt seccomp=profile.json`
→ Kubernetes: `seccompProfile.type: Localhost` + `localhostProfile: profile.json`

**AppArmor profiles?**
→ Path-based MAC: `#include <tunables/global>` `profile myapp { /usr/bin/myapp ix, /etc/** r, /var/log/** w, }`
→ Load: `apparmor_parser -r profile.apparmor`
→ Apply: `docker run --security-opt apparmor=myapp`
→ Kubernetes: `apparmor.security.beta.kubernetes.io/pod: myapp` (annotation)

**SELinux?**
→ Type enforcement: `container_t` type, `svirt_lxc_net_t` for network.
→ Labels: `docker run --security-opt label=type:custom_t`
→ Kubernetes: `seLinuxOptions: {level: "s0:c123,c456"}`

---

## Runtime Threat Detection (Falco)

**Falco rule structure?**
```yaml
- rule: Terminal Shell in Container
  desc: Detect shell spawn in container
  condition: >
    spawned_process and container
    and proc.name in (bash, sh, zsh, ksh)
    and not proc.name in (healthcheck-script)
  output: "Shell spawned in container (user=%user.name container=%container.name)"
  priority: WARNING
  tags: [process, shell]
```

**Key Falco rule categories:**
→ **Process**: `spawned_process`, `execve` (shell, compilers, package managers)
→ **File**: `open_write`, `mkdir` in sensitive paths (`/etc`, `/root`, `/boot`)
→ **Network**: `outbound_connection`, `inbound_connection` to unexpected ports
→ **K8s**: `k8s_pod_create`, `k8s_secret_read`, `k8s_service_account_token`
→ **Privilege**: `cap_add`, `privileged_container`, `namespace_change`

**Falco deployment:**
→ DaemonSet (host PID, host network, /var/run/docker.sock)
→ Sidecar (per-pod, limited visibility)
→ Falco Operator (CRD: Falco, FalcoProfile, FalcoRule)
→ Outputs: stdout, syslog, HTTP, gRPC, NATS, Kafka, Slack, CloudWatch

**Falco + k8s Audit Logs:**
→ Enable k8s audit policy → Falco reads audit events → detects RBAC abuse, secret access, privileged pod creation.

---

## Image Scanning

**Trivy scan types?**
→ `trivy image <image>` - vuln scan (OS packages, language pkgs: npm, pip, maven, go)
→ `trivy config <dir>` - IaC scan (Kubernetes, Terraform, Dockerfile, Helm)
→ `trivy fs <dir>` - filesystem scan
→ `trivy repo <url>` - Git repo scan
→ `trivy sbom <image>` - generate SBOM

**Trivy severity filtering:**
→ `trivy image --severity HIGH,CRITICAL <image>`
→ `trivy image --ignore-unfixed <image>`
→ `trivy image --vuln-type os,library <image>`

**CI/CD integration:**
```yaml
# GitHub Actions
- name: Trivy Scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE }}:${{ github.sha }}
    format: sarif
    output: trivy.sarif
    severity: HIGH,CRITICAL
- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: trivy.sarif
```

**Grype (alternative):**
→ `grype <image> -o json` - similar to Trivy, different vuln DB (Syft + Grype DB)

**Docker Scout:**
→ `docker scout cves <image>` - integrated with Docker Hub, base image recommendations
→ `docker scout quickview <image>` - summary
→ `docker scout recommendations <image>` - base image upgrades

---

## Admission Control

**Kyverno policies for container security?**
```yaml
# Require non-root
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-non-root
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-runAsNonRoot
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
```

**Gatekeeper (OPA) constraints?**
```yaml
# ConstraintTemplate for allowed registries
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8sallowedrepos
spec:
  crd:
    spec:
      names:
        kind: K8sAllowedRepos
      validation:
        properties:
          repos:
            type: array
            items: {type: string}
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        not startswith(container.image, input.parameters.repos[_])
        msg := sprintf("Image %v not from allowed repo %v", [container.image, input.parameters.repos])
      }
```

---

## Supply Chain Security

**SLSA (Supply Chain Levels for Software Artifacts)?**
→ Level 1: Build scripted, provenance generated
→ Level 2: Build service, tamper-resistant provenance
→ Level 3: Hardened build service, non-falsifiable provenance
→ Level 4: Hermetic, reproducible builds, two-person review

**Provenance generation (GitHub Actions + SLSA):**
```yaml
- uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v1.9.0
  with:
    base64-subjects: ${{ hashFiles('dist/*') }}
    upload-assets: true
```

**Dependency scanning (SCA):**
→ `trivy fs --scanners vuln,secret,config .`
→ `syft dir:. -o cyclonedx-json > sbom.json`
→ `grype sbom:sbom.json`
→ Renovate/Dependabot for automated PRs

---

## Commands Quick Reference

| Task | Command |
|------|---------|
| Scan image (Trivy) | `trivy image --severity HIGH,CRITICAL myapp:latest` |
| Scan config (Trivy) | `trivy config --severity HIGH,CRITICAL ./k8s` |
| Generate SBOM (Syft) | `syft myapp:latest -o spdx-json > sbom.json` |
| Sign image (cosign) | `cosign sign --yes myapp:latest` |
| Verify image (cosign) | `cosign verify myapp:latest` |
| Run rootless (Docker) | `dockerd --userns-remap=default & docker run -d nginx` |
| Run with seccomp | `docker run --security-opt seccomp=profile.json myapp` |
| Run with AppArmor | `docker run --security-opt apparmor=myprofile myapp` |
| Run Falco | `falco -c /etc/falco/falco.yaml` |
| Check image layers | `dive myapp:latest` |
| Check image config | `docker inspect myapp:latest | jq '.[0].Config'` |