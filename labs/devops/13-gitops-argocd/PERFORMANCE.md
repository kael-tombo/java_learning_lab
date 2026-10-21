# Performance Optimization in ArgoCD

## Repository Server Performance

### Caching Strategies
- Git repositories are cloned and cached locally by the Repository Server
- Cache TTL is configurable (default 60 seconds)
- Webhook events can trigger immediate cache invalidation
- Large repositories benefit from sparse checkout and depth=1 cloning

### Scaling Repository Server
For organizations with many applications:
- Deploy multiple Repository Server replicas
- Use Redis for distributed repository cache
- Configure repository parallelism in argocd-cm
- Enable repository cache persistence

### Optimization Techniques
1. Set repo.server.timeout to appropriate value for large repos
2. Enable repo.server.parallelism.limit for concurrent repository processing
3. Use Git submodules carefully as they increase clone time
4. Minimize Helm chart complexity - reduce template count and nesting depth
5. Use Kustomize remote bases sparingly

## Application Controller Performance

### Sharding
ArgoCD supports Application Controller sharding for large-scale deployments:
- Each shard manages a subset of applications
- Shards are configured via controller replicas and shard numbers
- Enables horizontal scaling for thousands of applications
- Leader election coordinates shard assignment

### Cluster Reconciliation Interval
- Default reconciliation interval: 3 minutes
- Can be adjusted per cluster: argocd-cm clusters configuration
- More frequent reconciliation increases controller load
- Less frequent reconciliation increases drift exposure window

### Resource Monitoring
- Controller watches a subset of resources types
- Too many watched resources impact controller performance
- Use resource.customizations to limit which resources are monitored
- Configure health assessments only for necessary resources

## API Server Performance

### Rate Limiting
- API Server has configurable rate limits
- Default: 20 requests per second per client
- Burst limit: 30 requests
- Rate limits protect against abuse and ensure fair access

### Session Management
- Sessions stored in Redis for horizontal scaling
- Session TTL configurable (default 24 hours)
- Token revocation requires key rotation

## Network Optimization

### Git Clone Optimization
- Use `--depth 1` for shallow clones
- Enable reference repositories for common bases
- Use HTTP/2 for Git communication
- Place Git repositories in the same region as ArgoCD

### Manifest Generation
- Reduce the number of templates and YAML files
- Use Kustomize base+overlay pattern to share common configurations
- Pre-render Helm charts for static configurations
- Use config management plugins for custom generation needs

## Monitoring Performance

### Key Metrics to Monitor
- repo_server_request_duration_seconds
- controller_sync_duration_seconds
- api_server_request_duration_seconds
- cluster_connection_duration_seconds
- app_reconciliation_duration_seconds
- git_request_duration_seconds

### Performance Thresholds
- Repository clone time: < 30 seconds
- Manifest generation time: < 10 seconds
- Sync duration: < 2 minutes for typical applications
- Reconciliation loop: < 3 minutes
- API response time: < 500ms P95

## Best Practices for Large-Scale Deployments

### Application Organization
1. Group applications by team and environment using Projects
2. Use ApplicationSets to reduce resource count
3. Avoid thousands of individual Applications - prefer ApplicationSets
4. Use meaningful names and labels for searchability

### Resource Recommendations
- 100 applications: 2 CPU, 4GB RAM for controller
- 500 applications: 4 CPU, 8GB RAM, 2 controller replicas
- 1000+ applications: 8 CPU, 16GB RAM, sharded controller, 3+ replicas
- Repository Server: 2 CPU, 4GB RAM base, add for each concurrent generation
- API Server: 2 CPU, 2GB RAM base, scale based on user concurrency
- Redis: 1 CPU, 2GB RAM for up to 500 applications
