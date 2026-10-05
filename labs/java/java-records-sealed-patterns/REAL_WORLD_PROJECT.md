# Real-World Project — Pricing Rules Engine

## Problem
Price orders with combinable rules (VIP, coupon, bulk, region) — auditable, exhaustive.

## Model
```java
sealed interface Customer permits Regular, Vip, Staff {}
sealed interface Coupon permits None, Pct, Fixed {}
record Order(Customer c, Coupon k, double subtotal, String region) {}
double price(Order o) {
  return switch (o) {
    case Order(Vip v, Pct(double p), double s, String r) when s > 100 -> s*(1-p)-5;
    case Order(Customer c, None n, double s, String r) -> s;
    case Order(Customer c, Coupon k, double s, String r) -> s - discount(k);
  };
}
```

## Milestones
1. **M1 Domain**: records for Money/Order, sealed Customer/Coupon/Region.
2. **M2 Engine**: single exhaustive switch; property tests (no negative totals).
3. **M3 Audit**: each decision returns `Decision(price, appliedRules)` record.
4. **M4 API**: REST `POST /price` (Spring/Micronaut), JSON records, validation in compact ctor.
5. **M5 Ops**: rule-change diff test; dashboard of rule hit rates.

## Testing
- Exhaustiveness: add variant → compile fails (CI asserts no default).
- 100+ parameterized cases; fuzz subtotal/region.
- Run: `./mvnw test`, `java -Xmx512m -jar app.jar`.

## Ops
- Docker eclipse-temurin:21; K8s 512Mi; alert on `unmatched_rule` counter.
- Version rules; canary new rule set 5% traffic.

## Interview Angles
- Why sealed over enums/strings? How guards ordered? Audit trail design?

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Oracle records: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Record.html
- JEP 395 (records): https://openjdk.org/jeps/395
- JEP 441 (patterns): https://openjdk.org/jeps/441
