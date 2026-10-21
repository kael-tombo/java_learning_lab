# Security: API Versioning & Documentation

## 1. Securing OpenAPI Documentation

### Restrict Access to Swagger UI
`yaml
springdoc:
  swagger-ui:
    enabled: false  # Disable in production
`
Or secure with Spring Security:
`java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) {
    http.authorizeHttpRequests(auth -> auth
        .requestMatchers("/swagger-ui/**", "/v3/api-docs/**")
        .hasRole("ADMIN")
        .anyRequest().authenticated()
    );
    return http.build();
}
`

## 2. API Key Validation

`java
@Configuration
public class ApiKeyFilter implements WebMvcConfigurer {
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new HandlerInterceptor() {
            @Override
            public boolean preHandle(HttpServletRequest request,
                                   HttpServletResponse response,
                                   Object handler) {
                String apiKey = request.getHeader("X-API-Key");
                if (!isValid(apiKey)) {
                    response.setStatus(401);
                    return false;
                }
                return true;
            }
        });
    }
}
`

## 3. Rate Limiting by API Version

`yaml
resilience4j:
  ratelimiter:
    instances:
      v1-api:
        limit-for-period: 100
        limit-refresh-period: 1m
      v2-api:
        limit-for-period: 1000
        limit-refresh-period: 1m
`

## 4. Input Validation

### OpenAPI Schema Validation
Define constraints in the OpenAPI spec:
`yaml
User:
  type: object
  properties:
    email:
      type: string
      format: email
      maxLength: 255
    age:
      type: integer
      minimum: 0
      maximum: 150
`

### Bean Validation Annotations
`java
public class CreateUserRequest {
    @NotBlank @Email
    private String email;
    @Min(0) @Max(150)
    private int age;
}
`

## 5. Versioned Security Policies

Different API versions may have different security requirements:
- v1: Basic API key only
- v2: OAuth2 with scopes
- v3: Mutual TLS required
- Legacy versions: Stricter rate limiting to encourage migration
