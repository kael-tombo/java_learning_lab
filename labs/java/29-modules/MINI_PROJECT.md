# MINI PROJECT — Modules: Modular Checkout with jlink Image

## Goal (2 weeks, ~8–10h)
Split a classpath checkout monolith into 4 JPMS modules and ship a `jlink`
runtime image half the size of the JDK with services wired via `ServiceLoader`.

## Requirements
### Functional
1. Modules: `shop.api` (exported DTOs + `PaymentService` interface),
   `shop.orders`, `shop.payments` (`provides PaymentService`), `shop.app`
   (main, `uses PaymentService` wiring at startup).
2. `module-info.java` per module: minimal `exports`, `requires transitive`
   only where API leaks types; `opens` exactly one package for Jackson.
3. ServiceLoader: two payment providers (card, wallet); select via config;
   no direct `requires shop.payments.card` from `shop.app`.
4. `jdeps` report: full module graph + offending automatic modules listed.
5. `jlink` image: `jlink --add-modules shop.app --strip-debug --compress=2`
   producing `image/bin/shop` launcher that runs end-to-end checkout.
6. CLI proof: `image/bin/shop order --sku X --pay card` prints receipt.

### Non-functional
- No split packages (`jdeps --check` clean); no `--add-opens` at runtime.
- Build reproducible with Maven `moditect` or Gradle `module-info` compile.
- 15+ tests: module-boundary (illegal access fails), provider selection,
  image smoke test script.
- README: module graph (ASCII) + image size/startup table vs full JDK.

## Phases
### Week 1 — Modularize (4–5h)
- Steps: carve packages, write module-info files, fix split packages,
  ServiceLoader wiring, jdeps iteration.
- Deliverable: `mvn/gradle build` green on module path.

### Week 2 — Image + Harden (4–5h)
- Steps: jlink image, startup/size bench, opens-scoping, smoke script.
- Deliverable: shippable `image/` + comparison memo.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| Encapsulation | Minimal exports, scoped opens | Mostly tight | Exports * |
| Services | provides/uses, pluggable | Works | Direct deps |
| jdeps hygiene | Clean, documented | Minor warns | Split pkgs |
| jlink image | Runs, sized + timed | Runs | Needs full JDK |
| Tests + docs | 15+ + graph + table | 10+ tests | No proof |

Pass >= 70. Stretch: `jpackage` installer; layered image per env;
versioned service negotiation.
