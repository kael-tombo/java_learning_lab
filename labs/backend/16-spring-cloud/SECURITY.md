# Security: Spring Cloud Infrastructure

## 1. Eureka Security

### Authentication
Eureka does not have built-in security. Secure it by:
- Placing behind Spring Security with HTTP Basic or OAuth2
- Using mutual TLS between Eureka server and clients
- Restricting network access with firewall rules

### Configuration for Basic Auth
`yaml
spring:
  security:
    user:
      name: eureka
      password: secret
`

Client registration:
`yaml
eureka:
  client:
    service-url:
      defaultZone: http://eureka:secret@localhost:8761/eureka/
`

## 2. Config Server Encryption

### Sensitive Properties
Encrypt sensitive configuration values using the config server's encryption endpoint:
`ash
curl -X POST http://localhost:8888/encrypt -d 'mysecretpassword'
`

### Encrypted Values
`yaml
spring:
  datasource:
    password: '{cipher}AQA...encrypted_value...'
`

### Key Management
- Store encryption key in bootstrap.yml (not in Git)
- Use environment variable ENCRYPT_KEY
- Rotate keys periodically
- Separate encryption keys per environment

## 3. API Gateway Security

### Authentication at Gateway Level
Route all requests through gateway which handles authentication:
`java
@Bean
public SecurityWebFilterChain securityFilterChain(ServerHttpSecurity http) {
    http
        .authorizeExchange(exchanges -> exchanges
            .pathMatchers("/public/**").permitAll()
            .anyExchange().authenticated()
        )
        .oauth2ResourceServer(oauth2 -> oauth2
            .jwt(Customizer.withDefaults())
        );
    return http.build();
}
`

### Rate Limiting
Prevent abuse with rate limiting:
`yaml
spring:
  cloud:
    gateway:
      routes:
        - id: product-service
          filters:
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 100
                redis-rate-limiter.burstCapacity: 200
`

## 4. Inter-Service Communication Security

### Service-to-Service Authentication
Use OAuth2 client credentials flow:
`yaml
spring:
  security:
    oauth2:
      client:
        registration:
          internal-client:
            authorization-grant-type: client_credentials
            scope: internal
`

### Mutual TLS
For high-security environments:
1. Generate certificates for each service
2. Configure truststore with allowed CAs
3. Enable client-cert authentication in service configuration
4. Reject connections without valid certificates

## 5. Circuit Breaker Security

### Preventing Cascading Security Failures
- Circuit breakers on authentication service calls
- Fallback to cached permissions when auth service is down
- Rate limiting on login endpoints
- separate thread pools for authentication calls

## 6. Secure Configuration Best Practices

### Environment-Specific Secrets
`yaml
# application-prod.yml
encrypt:
  key: 
spring:
  datasource:
    url: jdbc:postgresql://:5432/
    password: '{cipher}'
`

### Never Store in Git
- Database passwords
- API keys and tokens
- Private keys and certificates
- Encryption keys
