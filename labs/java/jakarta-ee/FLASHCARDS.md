# Flashcards — Jakarta EE

| Q | A |
|---|---|
| @Path? | Resource URI |
| @GET/@POST? | HTTP methods |
| @Produces? | Response media |
| @Consumes? | Accept media |
| @PathParam? | URI variable |
| @QueryParam? | ?k=v param |
| @HeaderParam? | Header inject |
| Response.ok? | 200 builder |
| ExceptionMapper? | Ex→Response |
| @Provider? | Auto-discovered ext |
| @ApplicationScoped? | One per app |
| @RequestScoped? | Per request |
| @SessionScoped? | Per session |
| @Inject? | CDI injection |
| @Produces (CDI)? | Producer method |
| @Disposes? | Cleanup producer |
| @Alternative? | Override bean |
| @Priority? | Alternative order |
| Interceptor? | @AroundInvoke |
| @Valid? | Cascade validate |
| @NotNull? | Non-null |
| @Size? | Length/range |
| @Min/@Max? | Numeric bounds |
| @Entity? | JPA entity |
| @Id? | Primary key |
| @GeneratedValue? | Key strategy |
| @OneToMany? | Collection rel |
| Fetch LAZY? | Load on access |
| JOIN FETCH? | Fix N+1 |
| @Transactional? | Tx boundary |
| Rollback? | RuntimeException |
| REQUIRES_NEW? | Suspend+new tx |
| PersistenceUnit? | EMF inject |
| PersistenceContext? | EM inject |
| @Liveness? | Alive probe |
| @Readiness? | Ready probe |
| @Counted? | Counter metric |
| @Timed? | Timer metric |
| @Incoming? | Consume channel |
| @Outgoing? | Produce channel |
| @RolesAllowed? | Role authz |
| @PermitAll? | Open endpoint |
| @DenyAll? | Closed endpoint |
| MP Config? | @ConfigProperty |
| RestClient? | @RegisterRestClient |
| Fault tolerance? | @Retry/@CircuitBreaker |
| @Retry? | Retry policy |
| @Timeout? | Call timeout |
| OpenAPI? | /q/openapi spec |
| Health path? | /q/health |
| Metrics path? | /q/metrics |
| WildFly? | Full EE runtime |
| GlassFish? | Reference impl |
| OpenLiberty? | IBM runtime |
| Quarkus? | Cloud-native EE |
| Helidon/Micronaut? | Modern EE-adjacent |
| Boot vs EE? | Auto-config vs spec |
| War vs jar? | Deploy vs runnable |
