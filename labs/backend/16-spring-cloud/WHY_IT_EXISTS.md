# Why It Exists: Spring Cloud

Spring Cloud exists because building distributed systems is fundamentally harder than building monolithic applications.

## The Problem
In a monolith, all components run in the same process. Method calls are fast, configuration is local, and failures are contained. When you split a monolith into microservices, you introduce:
- **Network latency** between services
- **Partial failures** (some services up, others down)
- **Configuration sprawl** across many services
- **Discovery challenges** (finding where services are running)

## The Solution
Spring Cloud provides a cohesive set of tools to solve these problems:
- **Service Discovery**: Services find each other without hardcoded addresses
- **Configuration Management**: Centralize and version control all configurations
- **Resilience Patterns**: Protect against partial failures
- **API Gateway**: Single entry point for cross-cutting concerns
- **Distributed Tracing**: Understand request flows across services

## Why Not Just Use Kubernetes?
While Kubernetes provides built-in service discovery and configuration management, Spring Cloud offers:
1. **Framework-level integration**: Works at the application layer, not just infrastructure
2. **Circuit breakers and resilience**: Application-level patterns K8s doesn't provide
3. **Configuration encryption**: Built-in property-level encryption
4. **Load balancing with health awareness**: More sophisticated than K8s service proxying
5. **Developer experience**: Easier local development without a cluster
