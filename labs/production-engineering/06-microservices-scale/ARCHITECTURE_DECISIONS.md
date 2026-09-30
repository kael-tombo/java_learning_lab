# ARCHITECTURE DECISIONS: Microservices Communication & Scale
## Lab 06 | Production Engineering Academy

---

## ADR-01: Inter-Service Communication Standard (gRPC vs REST/JSON)

### Status: ACCEPTED

### Context
Internal service-to-service communication consumes 45% of total cluster network bandwidth and accounts for significant JSON serialization CPU overhead.

### Decision
1. **External Boundary (Ingress / Public Clients)**:
   - Standardize on **REST/JSON and GraphQL** via API Gateway for browser/mobile compatibility.
2. **Internal Service-to-Service (East-West)**:
   - Standardize on **gRPC over HTTP/2 with Protocol Buffers**.
   - Prohibit synchronous internal REST for high-throughput transactional flows.
3. **API Contract Management**:
   - Centralized Git repository for `.proto` definitions.
   - CI pipeline generates Java and Go client SDKs with semver versioning.
   - Breaking changes forbidden; field deprecation protocol strictly enforced.

### Consequences
- CPU time spent in serialization/deserialization drops by 70%.
- Wire payload sizes reduced by 65%.
- Requires developers to manage Protobuf schemas and gRPC stubs.
