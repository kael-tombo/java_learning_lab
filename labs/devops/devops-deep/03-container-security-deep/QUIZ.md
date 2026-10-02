# Container Security Deep Dive - Quiz

Test your understanding of container image scanning, Dockerfile hardening, runtime security, and compliance.

---

## Questions

### 1. What is an SBOM and why is it important for container security?
A) Software Bill of Materials - inventory of all components, libraries, dependencies in an image; enables vulnerability matching and license compliance
B) Secure Build Operations Manual - documentation for CI/CD pipeline security
C) Signed Binary Object Model - cryptographic signature format for container images
D) System Baseline Observation Metric - runtime performance baseline

### 2. Which Dockerfile instruction is most effective for reducing attack surface?
A) `FROM scratch` or `FROM gcr.io/distroless/*` (minimal base images)
B) `USER root` (run as root for simplicity)
C) `RUN apt-get update && apt-get install -y *` (install all packages)
D) `COPY . /app` (copy entire build context)

### 3. What is the purpose of multi-stage builds in Docker?
A) Build multiple images simultaneously
B) Separate build-time dependencies (compilers, build tools) from runtime image, reducing size and attack surface
C) Deploy to multiple environments (dev, staging, prod) in one build
D) Run multiple containers in a single build step

### 4. How does rootless container mode improve security?
A) Containers run without any user namespace mapping
B) Container processes run as non-root user on host (via user namespace), so root inside container != root on host
C) Containers cannot make any system calls
D) Containers run in a separate VM

### 5. What does a seccomp profile do?
A) Restricts which Linux system calls a container process can make (allowlist/denylist)
B) Encrypts container filesystem at rest
C) Manages container network policies
D) Scans container images for vulnerabilities

### 6. What is AppArmor and how does it differ from seccomp?
A) AppArmor is a Mandatory Access Control (MAC) system that confines programs via path-based profiles; seccomp filters syscalls
B) AppArmor is a container runtime; seccomp is a security module
C) They are the same thing
D) AppArmor only works on Red Hat; seccomp only on Ubuntu

### 7. What is Falco and what does it detect?
A) Runtime security tool that detects anomalous behavior via syscall monitoring (shell in container, file writes to /etc, network connections, privilege escalation)
B) Static image scanner for vulnerabilities
C) Kubernetes admission controller for policy enforcement
D) Container registry with built-in signing

### 8. Which of the following is NOT a Dockerfile security best practice?
A) Use `--mount=type=secret` for build-time secrets
B) Pin base image digests (`FROM ubuntu@sha256:...`)
C) Run `apt-get upgrade` in every build for latest patches
D) Use `.dockerignore` to exclude sensitive files

### 9. What is image signing and verification (cosign/sigstore)?
A) Cryptographically sign container images and verify signatures at deploy time to ensure provenance and integrity
B) Encrypt image layers for confidentiality
C) Compress images for faster pulls
D) Tag images with semantic versioning

### 10. What is the difference between `USER` instruction and `--user` runtime flag?
A) `USER` in Dockerfile sets default user for image; `--user` at runtime overrides it (both should be non-root)
B) `USER` is for build time; `--user` is for runtime only
C) They are identical
D) `USER` requires root; `--user` doesn't

---

## Answers

| Question | Answer | Explanation |
|----------|--------|-------------|
| 1 | **A** | SBOM (Software Bill of Materials) = complete inventory of packages, libraries, versions, licenses. Formats: SPDX, CycloneDX. Tools: Syft, Trivy, Docker Scout. Enables "what's in this image" queries for vuln matching. |
| 2 | **A** | Minimal base images (distroless, alpine, scratch) remove shell, package manager, unused binaries. No `apt`, `apk`, `bash` = smaller attack surface. |
| 3 | **B** | Multi-stage: `FROM golang AS builder` → compile → `FROM gcr.io/distroless/static` → `COPY --from=builder /app /app`. Final image has only runtime binary + deps. |
| 4 | **B** | Rootless: container root (uid 0) maps to unprivileged host uid (e.g., 100000) via user namespace. Container escape = unprivileged host user. Requires kernel 4.8+, `dockerd --userns-remap=default`. |
| 5 | **A** | Seccomp (secure computing mode) = kernel syscall filter. Default Docker profile blocks ~44 dangerous syscalls (keyctl, bpf, ptrace, etc.). Custom profiles: `docker run --security-opt seccomp=profile.json`. |
| 6 | **A** | AppArmor = LSM (Linux Security Module) with path-based rules (`/etc/** r,`, `/usr/bin/** ix`). Seccomp = syscall filter. Both can be used together. Docker default: `docker-default` AppArmor profile. |
| 7 | **A** | Falco = runtime threat detection. Rules: `spawned_process`, `file_write`, `network_connection`, `privilege_escalation`. Outputs: stdout, syslog, HTTP, gRPC. Integrates with k8s via Falco Operator. |
| 8 | **C** | `apt-get upgrade` in Dockerfile breaks reproducibility (different packages each build). Better: pin base image digest, rebuild on schedule, scan for vulns. |
| 9 | **A** | cosign (sigstore) = keyless signing using OIDC identity (GitHub Actions, GitLab CI). `cosign sign --yes $IMAGE` → stores signature in registry. `cosign verify $IMAGE` at deploy (admission controller). |
| 10 | **A** | `USER appuser` in Dockerfile sets default. `docker run --user 1000:1000` overrides. Best practice: both non-root. Kubernetes: `runAsUser: 1000`, `runAsNonRoot: true` in PodSecurityContext. |

---

## Scoring

- **9-10**: Container Security Expert - Deep knowledge of build-time, deploy-time, runtime controls
- **7-8**: Container Security Practitioner - Solid; review rootless, seccomp/AppArmor differences, cosign workflow
- **5-6**: Container Security Learner - Good foundation; focus on multi-stage builds, SBOM, Falco rules
- **<5**: Beginner - Re-read GUIDE; run `trivy image`, `docker scout`, `falco` locally