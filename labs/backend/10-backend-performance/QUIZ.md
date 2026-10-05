# Quiz

1. What is the core responsibility of Backend Performance?
2. Which Spring annotation or type is the entry point?
3. How are errors surfaced to callers?
4. What is the default lifecycle/scope of the main bean?
5. How do you make it configurable?
6. Which dependency manages its lifecycle?
7. How do you slice-test it?
8. What metric or log line signals health?
9. How do you handle partial failure?
10. When would you choose an alternative approach?

## Answers
1. See THEORY — Backend Performance core model.
2. The annotated controller/component/config class.
3. Via HTTP status mapping and a stable error body.
4. Singleton by default for Spring beans.
5. Via `application.yml` and `@ConfigurationProperties`.
6. The Spring container (ApplicationContext).
7. With a slice test annotation plus mocks.
8. A latency/error metric and a structured log.
9. With timeouts, retries with backoff, and fallbacks.
10. When scale, throughput, or consistency requirements change.
