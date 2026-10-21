# Step by Step: Security Configuration

## CSRF Configuration
`java
http.csrf(csrf -> csrf
    .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
    .csrfTokenRequestHandler(new CsrfTokenRequestAttributeHandler()));
`

## CORS Configuration
`java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://trusted.com"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
    config.setAllowedHeaders(List.of("*"));
    config.setAllowCredentials(true);
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return source;
}
`

## Rate Limiting with Bucket4j
`java
Bucket bucket = Bucket4j.builder()
    .addLimit(Bandwidth.classic(100, Refill.intervally(100, Duration.ofMinutes(1))))
    .build();

if (bucket.tryConsume(1)) {
    // process request
} else {
    response.setStatus(429);
}
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\20-backend-security-deep "CODE_DEEP_DIVE.md") @"
# Code Deep Dive: Security Implementation

## CSRF Token Repository
CookieCsrfTokenRepository stores CSRF token in a cookie. The token is sent to the client on first GET request. Client includes token in header for state-changing requests. Server validates token matches.

## Rate Limiter with Bucket4j
Bucket4j uses the token bucket algorithm internally. Tokens are added to the bucket at a fixed rate. Each request removes a token. When bucket is empty, requests are blocked. The bucket has a maximum capacity for burst handling.

## Input Validation Chain
Spring Boot validation: Controller method parameter with @Valid triggers validation. ConstraintViolationException is thrown. ExceptionHandler converts to proper error response.
