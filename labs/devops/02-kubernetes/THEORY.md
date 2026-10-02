# Kubernetes Theory

## Core Concepts
- **Cluster**: Set of nodes (masters + workers) running containerized applications.
- **Pod**: Smallest deployable unit — one or more containers sharing network/storage.
- **Deployment**: Declarative update for Pods and ReplicaSets (rolling updates, rollbacks).
- **Service**: Stable network endpoint to access a set of Pods (ClusterIP, NodePort, LoadBalancer).
- **ConfigMap**: Key-value config data injected into Pods as env vars or volumes.
- **Secret**: Similar to ConfigMap but base64-encoded, intended for sensitive data.
- **Ingress**: HTTP/HTTPS routing rules to Services (with optional TLS termination).

## Control Plane Components
- **kube-apiserver**: REST API frontend (all components communicate through it).
- **etcd**: Distributed key-value store (cluster state).
- **kube-scheduler**: Assigns Pods to Nodes based on resource requirements.
- **kube-controller-manager**: Runs controller processes (Deployment, ReplicaSet, etc.).
- **cloud-controller-manager**: Integrates with cloud provider APIs.

## Node Components
- **kubelet**: Agent that ensures containers are running in Pods.
- **kube-proxy**: Network proxy maintaining network rules on each node.
- **Container runtime**: containerd, CRI-O, or Docker (via cri-dockerd).

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Concepts overview — Kubernetes docs (living reference, accessed Oct 2026) — https://kubernetes.io/docs/concepts/ — Takeaway for Pod/Deployment exercises: Pods are the smallest deployable unit with a defined lifecycle; use Deployment/ReplicaSet controllers rather than managing Pods directly.
- Declarative desired state — Kubernetes docs / What Kubernetes is not (living reference, accessed Oct 2026) — https://kubernetes.io/docs/concepts/overview/ — Takeaway for rolling-update/rollback exercises: declare desired state and let controllers drive actual → desired at a controlled rate instead of scripting A-then-B-then-C orchestration.
- Services, load balancing and networking — Kubernetes docs (living reference, accessed Oct 2026) — https://kubernetes.io/docs/concepts/services-networking/ — Takeaway for Service/Ingress exercises: Service gives a stable endpoint over changing Pod IPs; Ingress/Gateway API exposes HTTP routes while NetworkPolicy controls Pod-to-Pod traffic.
- Cluster components — Kubernetes docs (living reference, accessed Oct 2026) — https://kubernetes.io/docs/concepts/overview/components/ — Takeaway for kube-apiserver/etcd/scheduler/kubelet/kube-proxy exercises: all control-plane traffic flows through kube-apiserver with etcd as state store and kubelet/kube-proxy as per-node agents.
