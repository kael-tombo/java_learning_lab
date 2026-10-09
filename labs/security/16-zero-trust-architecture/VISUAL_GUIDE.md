# VISUAL GUIDE: 16-zero-trust-architecture

## Visual Guide

### Architecture Diagram

`
+---------------------------------------------------------+
¦                    CLIENT LAYER                          ¦
¦  +----------+  +----------+  +--------------------+   ¦
¦  ¦ Browser  ¦  ¦ Mobile   ¦  ¦ External Service   ¦   ¦
¦  +----------+  +----------+  +--------------------+   ¦
¦       ¦              ¦                  ¦               ¦
+-------+--------------+------------------+---------------+
        ¦              ¦                  ¦
+-------+--------------+------------------+---------------+
¦       ?              ?                  ?               ¦
¦  +--------------------------------------------------+  ¦
¦  ¦              API GATEWAY / LB                     ¦  ¦
¦  ¦  +--------------------------------------------+  ¦  ¦
¦  ¦  ¦  Rate Limiter ? Auth Check ? Audit Log    ¦  ¦  ¦
¦  ¦  +--------------------------------------------+  ¦  ¦
¦  +--------------------------------------------------+  ¦
¦                         ¦                               ¦
¦  +----------------------?---------------------------+  ¦
¦  ¦              SECURITY FILTER CHAIN                ¦  ¦
¦  ¦  +--------+ +--------+ +--------+ +--------+   ¦  ¦
¦  ¦  ¦ CORS   ¦?¦ CSRF   ¦?¦ Auth   ¦?¦ Session¦   ¦  ¦
¦  ¦  ¦ Filter ¦ ¦ Filter ¦ ¦ Filter ¦ ¦ Mgt    ¦   ¦  ¦
¦  ¦  +--------+ +--------+ +--------+ +--------+   ¦  ¦
¦  +--------------------------------------------------+  ¦
¦                         ¦                               ¦
¦  +----------------------?---------------------------+  ¦
¦  ¦              AUTHENTICATION LAYER                  ¦  ¦
¦  ¦  +------------------+ +-----------------------+ ¦  ¦
¦  ¦  ¦  Auth Manager    ¦ ¦  Provider Manager     ¦ ¦  ¦
¦  ¦  +------------------+ +-----------------------+ ¦  ¦
¦  +--------------------------------------------------+  ¦
¦                         ¦                               ¦
¦  +----------------------?---------------------------+  ¦
¦  ¦              AUTHORIZATION LAYER                   ¦  ¦
¦  ¦  +------------------+ +-----------------------+ ¦  ¦
¦  ¦  ¦ Access Decision  ¦ ¦ Method Security       ¦ ¦  ¦
¦  ¦  ¦ Manager          ¦ ¦ @PreAuthorize         ¦ ¦  ¦
¦  ¦  +------------------+ +-----------------------+ ¦  ¦
¦  +--------------------------------------------------+  ¦
+---------------------------------------------------------+
`

### Data Flow Diagram

`
Registration Flow:
+------+     +----------+     +--------+     +--------+
¦ User ¦----?¦ Frontend ¦----?¦ Backend¦----?¦  DB    ¦
+------+     +----------+     +--------+     +--------+
    ¦              ¦               ¦              ¦
    ¦  1. Submit   ¦               ¦              ¦
    ¦--------------?               ¦              ¦
    ¦              ¦  2. API Call  ¦              ¦
    ¦              ¦---------------?              ¦
    ¦              ¦               ¦  3. Store   ¦
    ¦              ¦               ¦-------------?¦
    ¦              ¦               ¦  4. Confirm  ¦
    ¦              ¦               ¦?-------------¦
    ¦              ¦  5. Response  ¦              ¦
    ¦              ¦?---------------              ¦
    ¦  6. Display  ¦               ¦              ¦
    ¦?-------------¦               ¦              ¦
`

### Sequence Diagram (Authentication)

`
Client          SecurityFilter       AuthProvider        UserDetails
  ¦                   ¦                   ¦                  ¦
  ¦  1. POST /login   ¦                   ¦                  ¦
  ¦------------------?¦                   ¦                  ¦
  ¦                   ¦  2. Authenticate  ¦                  ¦
  ¦                   ¦------------------?¦                  ¦
  ¦                   ¦                   ¦  3. Load User    ¦
  ¦                   ¦                   ¦-----------------?¦
  ¦                   ¦                   ¦  4. User Details ¦
  ¦                   ¦                   ¦?-----------------¦
  ¦                   ¦  5. Token Created ¦                  ¦
  ¦                   ¦?------------------¦                  ¦
  ¦  6. 200 OK + JWT  ¦                   ¦                  ¦
  ¦?------------------¦                   ¦                  ¦
`

### Component Interaction

`
+------------------+     +------------------+
¦  SecurityConfig   ¦----?¦  SecurityFilter  ¦
+------------------+     +------------------+
                                  ¦
         +------------------------+--------------------+
         ?                        ?                    ?
+------------------+  +------------------+  +------------------+
¦  AuthProvider     ¦  ¦  TokenManager    ¦  ¦  PolicyEngine    ¦
+------------------+  +------------------+  +------------------+
         ¦                        ¦                    ¦
         +------------------------+--------------------+
                                  ?
                         +------------------+
                         ¦  UserDetails     ¦
                         ¦  Service         ¦
                         +------------------+
`
"@

System.Collections.Hashtable['INTERNALS.md'] = @"
## Internal Implementation Details

### Class Hierarchy

### Core Classes

**SecurityService** (com.security.XX.SecurityService)
- Package: com.security.XX
- Extends: AbstractSecurityService
- Implements: SecurityOperations
- Dependencies: AuthProvider, TokenManager, AuditLogger

**AuthProvider** (com.security.XX.AuthProvider)
- Package: com.security.XX
- Implements: AuthenticationProvider
- Methods: authenticate(), supports()
- Strategies: JWT, OAuth2, SAML (configurable)

**TokenManager** (com.security.XX.TokenManager)
- Package: com.security.XX
- Key storage: In-memory cache + DB
- Validation: Signature, expiry, issuer, audience
- Rotation: Automatic on security events

### Internal Data Flow

1. **Request Reception**: HttpServletRequest enters filter chain
2. **Authentication**: SecurityContextHolder populated with principal
3. **Authorization**: AccessDecisionManager checks permissions
4. **Response**: Security headers added, audit logged

### State Management

- Authentication state: SecurityContextHolder (ThreadLocal)
- Session state: SessionRegistry (ConcurrentHashMap)
- Token cache: Caffeine cache with TTL
- Audit queue: BlockingQueue for async logging

### Configuration Loading

1. application.yml loaded
2. SecurityProperties bound
3. Bean definitions created
4. Filter chain assembled
5. Provider manager configured
6. Endpoint security mapped

### Thread Safety

- SecurityContextHolder: InheritableThreadLocal for child threads
- TokenCache: ConcurrentHashMap + Caffeine
- AuditLogger: ConcurrentLinkedQueue for batch processing
- SessionManager: ReentrantReadWriteLock for session operations

### Error Handling Flow

1. Exception thrown in filter
2. ExceptionTranslationFilter catches
3. AuthenticationEntryPoint sends 401/403
4. Error details logged (not exposed)
5. Security metrics updated

### Extension Points

- Custom AuthenticationProvider
- Custom AccessDecisionVoter
- Custom SecurityFilter
- Custom AuthenticationEntryPoint
- Custom AccessDeniedHandler
