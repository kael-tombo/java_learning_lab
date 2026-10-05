# Exercises — JPMS Module System (9 hands-on)

## E1 — First module-info
```java
module com.greet { exports com.greet.api; }
```
Tasks: compile/run with --module-path. Try `java --describe-module com.greet`.

## E2 — exports vs opens
Tasks: reflective access fails without opens; fix with `opens pkg to framework`.

## E3 — requires transitive
```java
module a { exports a; } module b { requires transitive a; exports b; }
```
Tasks: consumer requires only b, uses a types — works via transitive.

## E4 — Services (provides/uses)
```java
module svc { exports svc; uses svc.Codec; }
module impl { requires svc; provides svc.Codec with impl.Zip; }
```
Tasks: load via ServiceLoader, run with/without impl on path.

## E5 — Split Package Fail
Tasks: same package in two modules → compile error. Fix by rename/merge.

## E6 — Unnamed/Automatic Modules
Tasks: put legacy jar on module-path → automatic module; `jdeps --generate-module-info`.

## E7 — jlink Minimal Image
```bash
jlink --module-path mods:$JAVA_HOME/jmods --add-modules com.app \
  --strip-debug --no-header-files --compress=2 --output img
img/bin/java -m com.app/com.app.Main
```
Tasks: compare `du -sh` JDK vs image.

## E8 — Layers (Plugin Load)
```java
ModuleLayer layer = ModuleLayer.boot().defineModulesWithOneLoader(cfg, List.of());
```
Tasks: load plugin module at runtime, list `layer.modules()`.

## E9 — Migration Capstone
Tasks: 3-jar app → modularize one jar at a time; flags `--add-opens/--add-exports` as bridge.
Checklist: [ ] jdeps clean [ ] jlink works [ ] no split packages
