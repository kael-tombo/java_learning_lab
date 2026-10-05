# Quiz — JPMS (20 Q)

1. module-info purpose?
> Declares deps + exported packages.
2. requires vs requires transitive?
> Direct dep vs re-exported dep.
3. exports vs opens?
> Compile+runtime access vs reflection-only.
4. qualified exports?
> `exports p to m` — only m sees p.
5. uses/provides?
> Service consumption/declaration.
6. Split package?
> Same package in 2 modules — forbidden.
7. Automatic module?
> Plain jar on module-path, exports all.
8. Unnamed module?
> Classpath code, reads all.
9. jlink input?
> Module-path + root modules → custom runtime.
10. jdeps role?
> Analyze deps, generate module-info.
11. --add-opens?
> CLI escape hatch for reflection.
12. --add-exports?
> CLI export without module-info change.
13. Module path vs classpath?
> Path enforces encapsulation; classpath doesn't.
14. ServiceLoader with layers?
> Each layer has own loader wiring.
15. Open module?
> `open module m` — all packages reflective.
16. Transitive harm?
> Leaks API; prefer plain requires.
17. Version in module?
> No version semantics — build-tool concern.
18. Boot layer?
> Modules resolved at startup.
19. jlink compress?
> `--compress=2` shrinks image.
20. Migration first step?
> `jdeps` + automatic modules, then modularize leaves-up.
