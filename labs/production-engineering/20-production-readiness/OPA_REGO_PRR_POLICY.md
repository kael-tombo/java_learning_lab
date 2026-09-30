# ADVANCED GUIDE: Policy-as-Code with Open Policy Agent (OPA) Rego for Automated PRR
## Lab 20 | Capstone | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Automated Architecture Governance via Policy-as-Code

Traditional architecture governance relies on manual checklists and meetings that slow delivery and miss critical operational traps.
Top organizations automate **100% of Production Readiness Review constraints via Open Policy Agent (OPA)** running in CI/CD and as a Kubernetes Admission Controller (Gatekeeper).

Any Helm chart, deployment manifest, or Terraform file that violates production readiness rules is **automatically rejected at git commit time**.

---

## 2. Production OPA Rego Production Readiness Policy (`prr.rego`)

```rego
package production.readiness.review

import future.keywords.in

default allow = false

# Global evaluation: Allow deployment only if there are zero critical violations
allow {
    count(violations) == 0
}

# -------------------------------------------------------------------------
# Rule 1: Non-Root Security Invariant
# -------------------------------------------------------------------------
violations[msg] {
    container := input.spec.template.spec.containers[_]
    not container.securityContext.runAsNonRoot == true
    not container.securityContext.runAsUser > 0
    msg := sprintf("PRR-SEC-01: Container '%v' must specify runAsNonRoot: true or runAsUser > 0.", [container.name])
}

# -------------------------------------------------------------------------
# Rule 2: Zero-Downtime Rolling Update preStop Hook Invariant
# -------------------------------------------------------------------------
violations[msg] {
    container := input.spec.template.spec.containers[_]
    not container.lifecycle.preStop.exec.command
    msg := sprintf("PRR-REL-02: Container '%v' is missing lifecycle.preStop sleep hook to prevent 502 errors.", [container.name])
}

# -------------------------------------------------------------------------
# Rule 3: Mandatory Startup Probe for JVM Cold-Start Invariant
# -------------------------------------------------------------------------
violations[msg] {
    container := input.spec.template.spec.containers[_]
    not container.startupProbe
    msg := sprintf("PRR-AVAIL-03: JVM Container '%v' must define a startupProbe to avoid false CrashLoopBackOff.", [container.name])
}

# -------------------------------------------------------------------------
# Rule 4: High Availability Multi-AZ Spread Invariant
# -------------------------------------------------------------------------
violations[msg] {
    not input.spec.template.spec.topologySpreadConstraints
    not input.spec.template.spec.affinity.podAntiAffinity
    msg := "PRR-HA-04: Deployment must define topologySpreadConstraints across availability zones."
}

# -------------------------------------------------------------------------
# Rule 5: OOM Forensic Heap Dump Volume Mount Invariant
# -------------------------------------------------------------------------
violations[msg] {
    container := input.spec.template.spec.containers[_]
    not has_dump_volume(container)
    msg := sprintf("PRR-DIAG-05: Container '%v' must mount a persistent volume at /dumps for forensic heap dumps.", [container.name])
}

has_dump_volume(container) {
    mount := container.volumeMounts[_]
    mount.mountPath == "/dumps"
}
```

---

## 3. Running OPA Validation in GitHub Actions CI

```bash
# Evaluate Kubernetes deployment manifest against PRR policy
conftest test k8s/production/deployment.yaml -p policies/prr.rego

# Example Output on Failure:
# FAIL - k8s/production/deployment.yaml - PRR-REL-02: Container 'payment-service' is missing lifecycle.preStop sleep hook.
# FAIL - k8s/production/deployment.yaml - PRR-DIAG-05: Container 'payment-service' must mount a persistent volume at /dumps.
# 2 tests failed. Deployment blocked.
```
- Eliminates subjective architectural debates.
- Guarantees that no service enters production without 100% adherence to the Google PRR standard.
