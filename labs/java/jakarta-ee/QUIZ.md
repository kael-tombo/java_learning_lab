# Quiz — Jakarta EE (20 Q)

1. JAX-RS core annotations?
> @Path,@GET/@POST,@Produces/@Consumes,@PathParam.
2. CDI bean discovery?
> Annotated scan; beans.xml in older versions.
3. Scope: app vs request?
> One instance vs per-request.
4. @Inject types?
> Constructor (best), field, setter.
5. Bean Validation trigger?
> @Valid on param/field cascades.
6. JPA EntityManager?
> Persistence context; container-managed tx.
7. N+1 fix?
> JOIN FETCH / EntityGraph.
8. @Transactional rollback?
> RuntimeException by default.
9. JTA vs RESOURCE_LOCAL?
> Container vs app-managed tx.
10. ExceptionMapper?
> Maps exception → Response.
11. Health checks?
> @Liveness/@Readiness probes.
12. Metrics annotations?
> @Counted/@Timed.
13. @Incoming/@Outgoing?
> Reactive messaging channels.
14. MP Config source?
> properties/env/secrets ordered.
15. @RolesAllowed?
> Method authz by role.
16. Stateless vs stateful EJB?
> Pooled vs conversational (rare now).
17. Servlet vs JAX-RS?
> Low-level vs REST resource model.
18. Filters/interceptors?
> Cross-cutting (auth/log) chain.
19. Spring vs Jakarta?
> Opinionated Boot vs spec + runtimes.
20. First prod checklist?
> Health, metrics, validation, tx, sec.
