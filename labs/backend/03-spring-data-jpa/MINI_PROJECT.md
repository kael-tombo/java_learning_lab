# Mini Project: Spring Data Jpa

## Moving parts

- Repository interfaces with derived queries supporting the film-rental persistence service.
- Entity relationship mapping supporting the film-rental persistence service.
- Transactional service boundary.
- Paged rental history.
- Schema generation for development.

## Build brief

This Spring Data JPA mini build produces a working app you can run locally.
Scope stays deliberately small so every Spring Data JPA behavior remains observable.
Budget roughly one focused evening for the implementation.
Success means demonstrating Spring Data JPA judgment, not just compiling code.
Keep a lab journal noting each Spring Data JPA surprise encountered.
Acceptance checks define the edge, and no additions go past them.

## Sequence

1. Map films, customers, and rentals as related entities for the service.
2. Declare repositories using derived query method names.
3. Place rental checkout inside one transaction.
4. Expose paged rental history per customer.
5. Verify generated schema matches the intended model.

## Done when

- [ ] 50 films and 25 customers seed without constraint errors in the solution.
- [ ] Derived finder locates rentals by customer and status in the platform.
- [ ] Checkout of 3 films commits atomically or rolls back fully.
- [ ] History pages cover every rental exactly once.
- [ ] Lazy-loading access outside transactions is eliminated.

## If time remains

One realistic complication of your choosing goes into the project.
Write the two-paragraph retro: which Spring Data JPA decision proved hardest.
A peer reads only the acceptance checks, then watches the system demo.
