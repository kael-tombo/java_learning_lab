# INTERVIEW QUESTIONS: Microservices Architecture at Scale
## Lab 06 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: Why does standard Kubernetes L4 load balancing fail for gRPC services, and how do you solve it?
**Answer**:
Kubernetes `ClusterIP` services operate at Layer 4 (TCP). When a gRPC client connects, it establishes a long-lived HTTP/2 TCP connection to one backend pod. All subsequent RPC requests are multiplexed over that single TCP stream. As a result, even if Kubernetes scales the deployment to 50 pods, all traffic from that client remains pinned to the single pod chosen during the initial TCP handshake.
**Solutions**:
1. **Client-Side Load Balancing**: The gRPC client uses `dns:///service-name` to resolve all backend pod IPs and manages subchannels to each pod directly.
2. **Layer 7 Proxy / Service Mesh**: Route traffic through an L7 proxy (Envoy, Linkerd, or Kubernetes Ingress) that understands HTTP/2 frames and balances individual RPC streams across pods.

---

## Staff / Principal Level (8+ Years)

### Q2: Compare Service Mesh (Envoy sidecar) vs Proxyless gRPC. Which would you choose for an enterprise with 500 microservices?
**Answer**:
- **Service Mesh (Envoy Sidecars)**:
  - *Pros*: Language-agnostic; transparent to developers; centralized mTLS, telemetry, and traffic routing rules pushed via xDS control plane (Istio).
  - *Cons*: Additional hop latency ($0.5-2\text{ms}$ per hop); massive resource footprint ($500\text{ services} \times \text{hundreds of pods} \times 100\text{MB RAM}$ for Envoy sidecars adds up to gigabytes of wasted cluster memory); complex debugging.
- **Proxyless gRPC (gRPC xDS)**:
  - gRPC client libraries natively implement the xDS API to communicate directly with Istio control plane, achieving client-side load balancing and mTLS directly without a sidecar.
  - *Pros*: Eliminates sidecar latency and memory overhead.
  - *Cons*: Tied to languages supported by gRPC xDS; more complex library configuration.
- **Recommendation**: Proxyless gRPC for high-throughput, latency-critical tier-1 microservices; Envoy sidecars for heterogeneous polyglot services and edge boundaries.
