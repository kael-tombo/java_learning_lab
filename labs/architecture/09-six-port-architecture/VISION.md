# Vision — Six-Port Architecture

## The Big Picture

Six-Port Architecture extends hexagonal architecture by defining six
distinct ports: three driving (input) ports and three driven (output)
ports. This creates a symmetric, fully decoupled design where the core
application logic is completely isolated from all external concerns.

## Why This Matters

- **Maximum decoupling** — every external interaction goes through a port.
- **Symmetric design** — clear separation of input and output concerns.
- **Testability** — every port can be mocked for isolated testing.
- **Flexibility** — any port implementation can be swapped independently.
- **Clarity** — the architecture explicitly defines all integration points.

## Guiding Principles

1. **Six ports** — three driving (input) and three driven (output).
2. **Core in the center** — business logic has zero external dependencies.
3. **Ports are contracts** — interfaces define what the core needs and offers.
4. **Adapters implement ports** — technology-specific code lives in adapters.
5. **Symmetry** — driving and driven ports follow the same design principles.

## Success Criteria

- All six ports are clearly defined interfaces.
- The core has zero dependencies on any adapter.
- Each port can be tested in isolation.
- Swapping any adapter requires no core changes.
- The architecture is symmetric and balanced.

## Trade-offs to Keep in Mind

| Benefit | Cost |
|---------|------|
| Maximum decoupling | More interfaces and classes |
| Testability | Initial design effort |
| Flexibility | Potential over-engineering |
| Clear contracts | Learning curve |

## The Road Ahead

Six-Port Architecture provides the most explicit and symmetric approach
to decoupling. It's ideal for complex systems with many integration points
where clarity and testability are paramount.
