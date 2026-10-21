# Internals: Security

## SecurityFilterChain
Spring Security uses a chain of filters:
1. SecurityContextPersistenceFilter
2. CsrfFilter
3. CorsFilter
4. LogoutFilter
5. UsernamePasswordAuthenticationFilter
6. ExceptionTranslationFilter
7. FilterSecurityInterceptor

## Rate Limiter Internals
Bucket4j stores tokens as nanoseconds. Refill is calculated as wall-clock time * refill rate. The bucket implementation is lock-free using AtomicReference for high concurrency.
