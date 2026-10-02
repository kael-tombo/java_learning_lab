# Theory: Spring Data JPA

## Repository Abstraction
Spring Data JPA provides a powerful repository abstraction that eliminates boilerplate DAO code.

### Core Interfaces
- **Repository<T, ID>**: Marker interface
- **CrudRepository<T, ID>**: Basic CRUD operations
- **PagingAndSortingRepository<T, ID>**: Pagination and sorting
- **JpaRepository<T, ID>**: Full JPA support with flush, batch operations

### Query Methods
Spring Data JPA generates queries from method names:
- `findByName(String name)` -> WHERE name = ?
- `findByNameContaining(String partial)` -> WHERE name LIKE ?
- `findByAgeBetween(int min, int max)` -> WHERE age BETWEEN ? AND ?
- `findByDepartmentName(String dept)` -> JOIN with department.name = ?

### Entity Mapping
- @Entity: Marks class as JPA entity
- @Table: Specifies table name
- @Id: Primary key
- @GeneratedValue: ID generation strategy
- @Column: Column mapping with constraints
- @OneToMany, @ManyToOne: Relationship mappings
- @JoinColumn: Foreign key specification

## Sourced field notes (fetched Oct 2026 — verify before citing)
- "Query Methods :: Spring Data Commons" — Spring Data Commons reference v4.1.1 (Spring Data JPA track; fetched Oct 2026) — https://docs.spring.io/spring-data/jpa/reference/data-commons/repositories/query-methods.html — Takeaway tied to Repository Abstraction in this lab: the four-step flow is declare interface (`Repository<Person, Long>`), declare query methods, enable proxies via `@EnableJpaRepositories`, then inject and call — proxies implement the interface at startup.
- "Query Methods :: Spring Data Commons" (same page, query-method declaration; fetched Oct 2026) — https://docs.spring.io/spring-data/jpa/reference/data-commons/repositories/query-methods.html — Takeaway tied to Query Methods in this lab: `findByLastname(String)` derives the store query from the method name, so `findByNameContaining` / `findByAgeBetween` / `findByDepartmentName` in this lab follow the same subject (`find…By`) + predicate parsing rather than hand-written JPQL.
- "Query Methods :: Spring Data Commons" (same page, store namespaces; fetched Oct 2026) — https://docs.spring.io/spring-data/jpa/reference/data-commons/repositories/query-methods.html — Takeaway tied to JpaRepository vs other stores in this lab: the same repository abstraction works across stores by swapping the namespace/config (e.g. `jpa` vs `mongodb`); JavaConfig defaults the scan package to the config class package unless `basePackage…` is set.
