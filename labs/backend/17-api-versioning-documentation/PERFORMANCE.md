# Performance: API Versioning & Documentation

## 1. SpringDoc Performance

### Caching
`yaml
springdoc:
  cache:
    disabled: false
  api-docs:
    path: /v3/api-docs
    enabled: true
    cache:
      ttl: 300000  # 5 minutes
`

### Lazy Initialization
`yaml
springdoc:
  lazy-init: true  # Only build docs when endpoint is called
`

## 2. Version Routing Performance

### URL Routing Overhead
URL-based versioning adds negligible overhead (path matching).
Header versioning requires interceptor which adds ~1-2ms.

### Content Negotiation
Parsing Accept headers is more expensive due to media type negotiation.

## 3. Memory Considerations

Each API version loaded in memory adds:
- Controller instances: ~50KB per controller
- OpenAPI spec: ~10-100KB per version
- Runtime overhead: ~5-10MB for 10 versions

## 4. Recommendation
- Use URL-based versioning for better performance
- Cache OpenAPI spec generation
- Limit active versions to 2-3
- Generate static docs for CI/CD instead of runtime generation
