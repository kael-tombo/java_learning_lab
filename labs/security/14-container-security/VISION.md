# VISION — Container Security: Isolation, Least Privilege, Provenance
> Where this lab takes you: from "it runs in Docker" to a workload whose image, runtime, and identity are all defensible.

## The Arc
1. **Isolation** — namespaces, cgroups, capabilities, seccomp/AppArmor, and what a container is not.
2. **Image integrity** — base image choice, pinning by digest, scanning, and signature verification.
3. **Runtime hardening** — read-only filesystem, non-root, dropped capabilities, no host mounts.
4. **Secrets in containers** — why env vars and image layers leak, and what to do instead.
5. **Orchestration** — Kubernetes pod security, admission control, network policy, and supply chain.

## Milestones (checkable)
- [ ] M1: run a container as non-root with a read-only root filesystem and no capabilities.
- [ ] M2: explain why "it's in a container" is not a security boundary by itself.
- [ ] M3: pin a base image by digest and prove the image's provenance.
- [ ] M4: write a Pod Security Admission policy and show a violating pod is rejected.
- [ ] M5: find a secret that leaked into an image layer.

## Core Competencies
- Linux namespaces and cgroups as the isolation substrate; shared-kernel risk.
- Capability dropping, seccomp profiles, and the AppArmor/SELinux distinction.
- Image supply chain: digest pinning, SBOM, signing, and admission verification.
- Kubernetes security contexts, resource limits, and network policies as enforceable controls.

## Anti-Goals
- Running as root "because the Dockerfile says so".
- `imagePullPolicy: Always` with a floating tag and no digest pin.
- Passing secrets as environment variables baked into a layer.

## Interview Lens
- "What does dropping NET_RAW actually prevent?"
- "How do you know the image running in production is the one you built?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: harden a Dockerfile, inspect layers, break a container safely.
- Wk2 QUIZ/FLASHCARDS to 90%+; write a pod security policy.
- Wk3 MINI_PROJECT: a hardened image pipeline with scan gates.
- Wk4 REAL_WORLD_PROJECT: cluster-wide adoption with admission control and exception management.

## Done = You Can
- Take any containerised Java service and produce a hardening baseline with an
  evidence trail showing each control is actually enforced.
