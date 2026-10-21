# Architecture: Performance

`
Performance Testing Pipeline:
  [JMH Microbenchmarks] → [Integration Tests] → [Load Tests] → [Production Monitoring]
         Unit-level           Service-level        System-level       Real-world

Profiling Tools:
  - Async Profiler (CPU, allocation, wall-clock)
  - JFR (JDK Flight Recorder)
  - JMX Monitoring
  - Micrometer/Prometheus
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\24-backend-performance "SECURITY.md") @"
# Security: Performance

- Rate limiting protects against DoS
- Cache authorization results to reduce auth overhead
- Timeout configuration prevents thread starvation
- Monitor cache hit rates to detect cache poisoning
