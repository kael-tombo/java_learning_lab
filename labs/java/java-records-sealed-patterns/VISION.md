# Vision — Records / Sealed / Patterns

## Direction
- Data-oriented programming: records + sealed + patterns = default modeling.
- Deconstruction + `with` (wither) proposals reduce boilerplate further.
- Valhalla value types will make records even cheaper.

## 5-Year Bets
1. DTOs/builders replaced by records + compact ctors.
2. Sealed event/state hierarchies standard in services.
3. Exhaustive switches enforced in CI (no default).

## Constants
- Immutability first; validate in compact ctor.
- Keep switches exhaustive and guard-pure.

## Signals
- Valhalla, withers, deconstruction assignment JEPs.
- Framework support: Jackson/Spring record-first.

## Career
Clean domain modeling with sealed/records is a senior signal. Ship pricing engine.

## Anti-Vision
Don't seal everything — open interfaces still fit plugins.
Don't nest patterns 5 deep — extract methods.

## 30/60/90
- 30d: records + sealed basics + switches.
- 60d: AST evaluator with nested patterns.
- 90d: pricing engine with exhaustive rules.
