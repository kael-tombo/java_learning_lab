# VISION — Annotations

## Vision Statement
**Metadata, not magic** — annotations declare intent at the source; processors and frameworks turn that intent into validated, generated, boringly-correct code.

---
## Mental Models
### 1. Three Retentions, Three Worlds
`SOURCE` (lint/check) → `CLASS` (bytecode tools) → `RUNTIME` (reflection/DI). Wrong retention = invisible annotation at the moment you need it.
### 2. @Target Is the Contract
`TYPE/METHOD/FIELD/PARAMETER/TYPE_USE` — `TYPE_USE` enables nullness/generics checking (`List<@NonNull String>`). Narrow targets prevent misuse.
### 3. Repeatable + Meta-Annotations
`@Repeatable(Schedules.class)` replaces wrapper arrays; meta-annotations (`@Transactional` composed of smaller ones) build DSLs. Document with `@Documented`.
### 4. Processing Has Two Doors
Compile-time (`AbstractProcessor`, fail fast, generate code) vs runtime (reflect, validate, inject). Prefer compile-time for errors users should see in the IDE.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Enforceable at build? | Annotation processor, not runtime check |
| Framework config? | Annotation + validated processor, not stringly XML |
| Retention? | Lowest that works (SOURCE > CLASS > RUNTIME) |
| Default values? | Safe default; required = no default |

---
## Career Trajectory
- **L1:** Use `@Override/Deprecated/FunctionalInterface`, write simple `@NotBlank`-style marker.
- **L2:** Custom annotation + runtime validator; `@Retention/@Target` judgment.
- **L3:** `AbstractProcessor` + `AutoService`, generated builders/mappers.
- **L4:** Framework-grade annotation design (Spring-style composed annotations), migration/codemod tooling.

---
## 4-Week Path
```
W1: Built-ins deep: Override, SuppressWarnings scoping, SafeVarargs.
W2: Custom runtime annotations + reflective validator kata.
W3: Compile-time processor: @Builder-lite generator.
W4: Mini-framework: @Route + validation with composed annotations.
```
## Success Metrics
- [ ] Justify every retention/target choice aloud
- [ ] Processor error points at the exact element with fix hint
- [ ] Zero reflection where compile-time generation fits
