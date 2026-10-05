# VISION — Abstraction & Interfaces

## Vision Statement
**Define what, hide how** — abstractions minimize the surface others depend on; good interfaces are small, stable, and hard to misuse.

---
## Mental Models
### 1. Interface as Capability
`Payable`, `Renderable` — roles, not identities. Classes can play many roles.
### 2. Abstract Class as Template
Shared skeleton + hooks (template method); interfaces can't hold state (except constants — avoid).
### 3. Default Methods = Evolution Tool
Defaults preserve binary compat; don't use as trait mixins for core logic.
### 4. Sealed = Closed World
`sealed interface` + `permits` enables exhaustive switch and domain completeness.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Multiple inheritance of type? | Interface |
| Shared code + state? | Abstract class or composition |
| API will evolve? | Interface + defaults, semantic versioning |
| Fixed domain set? | Sealed interface + records |

---
## Career Trajectory
- **L1:** implement interfaces, extend abstract classes.
- **L2:** default/static/private interface methods, functional interfaces.
- **L3:** SPI design, sealed modeling, versioning.
- **L4:** platform API stewardship.

---
## 4-Week Path
```
W1: Abstract classes vs interfaces, implements.
W2: Defaults, statics, functional interfaces.
W3: Sealed types, exhaustive switches.
W4: Notification-sender SPI kata with 3 providers.
```
## Success Metrics
- [ ] Design 5-method-max interface covering use case
- [ ] Evolve interface without breaking clients
- [ ] Model closed domain with sealed + records
