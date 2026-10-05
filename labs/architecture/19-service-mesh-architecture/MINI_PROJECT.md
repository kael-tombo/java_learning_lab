# Mini Project — Service Mesh Architecture

## Goal

Deploy a microservices system on Kubernetes with a service mesh (Istio
or Linkerd). Demonstrate traffic management, security, and observability
features without changing application code.

## Requirements

### Microservices

1. **Frontend Service** — web UI backend
2. **API Service** — main API
3. **Auth Service** — authentication
4. **Database** — persistent storage

### Service Mesh Features

**Traffic Management:**
- Canary deployment (route 10% to new version)
- Circuit breaking (stop calling failing services)
- Retry policies (retry failed requests)
- Timeout configuration

**Security:**
- mTLS between all services
- Authorization policies (which services can talk to which)
- Encryption in transit

**Observability:**
- Metrics (request count, latency, error rate)
- Distributed tracing
- Access logging

## Technical Specifications

1. **Sidecar injection**
   - Automatic sidecar injection for all pods
   - Transparent traffic interception
   - Sidecar resource limits

2. **Traffic management**
   - VirtualServices for routing rules
   - DestinationRules for load balancing and circuit breaking
   - Canary deployment with gradual traffic shift

3. **Security**
   - PeerAuthentication for mTLS
   - AuthorizationPolicy for access control
   - RequestAuthentication for JWT validation

4. **Observability**
   - Prometheus metrics from sidecars
   - Jaeger/Zipkin distributed tracing
   - Grafana dashboards

## Steps

1. Set up Kubernetes cluster
2. Install service mesh (Istio/Linkerd)
3. Deploy microservices with sidecar injection
4. Configure canary deployment
5. Enable mTLS
6. Add authorization policies
7. Configure circuit breaking and retries
8. Set up observability (metrics, tracing, logging)
9. Test all features
10. Verify zero application code changes needed

## Acceptance Criteria

- [ ] All services have sidecar proxies
- [ ] Canary deployment routes traffic correctly
- [ ] mTLS is enabled for all service communication
- [ ] Authorization policies restrict traffic correctly
- [ ] Circuit breaking stops calls to failing services
- [ ] Metrics are collected for all traffic
- [ ] Distributed tracing works across services
- [ ] No application code changes required for any feature

## Stretch Goals

- Implement fault injection for chaos testing
- Add rate limiting per service
- Implement traffic mirroring for testing
- Add service mesh dashboard for visualization
