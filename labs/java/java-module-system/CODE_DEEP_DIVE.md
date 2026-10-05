# Code Deep Dive — JPMS

## 1. Source Tour
- `java.lang.Module`, `ModuleLayer`, `Configuration` (java.base).
- `jdk.internal.module.ModuleBootstrap` resolves boot layer.
- module-info compiled to `module-info.class` with `Module` attribute.

## 2. Bytecode: module-info
```java
module com.app { requires java.base; exports com.app.api; }
```
`javap -v module-info.class` shows `Module` attribute: requires/exports flags.
`jar --describe-module --file app.jar` prints same.

## 3. Resolution Trace
```bash
java --show-module-resolution --module-path mods -m com.app/com.app.Main
```
Shows root set → bindings → service wiring. Use to debug missing reads.

## 4. Encapsulation Enforcement
`IllegalAccessError` when accessing non-exported pkg; `InaccessibleObjectException` for reflection.
HotSpot check in `Class::isAccessibleTo`. Flag `--add-opens` patches at launch.

## 5. Service Binding
`ServiceLoader.load(S.class)` scans `provides` in module descriptors, not META-INF.
Inspect: `java --list-modules`, `jdeps --print-module-deps`.

## 6. jlink Plugins
`--strip-debug --compress=2 --no-header-files` are jlink plugin chain.
List: `jlink --list-plugins`. Measure: `du -sh img`, `img/bin/java -Xshare:dump`.

## 7. Layers Code
```java
Configuration cfg = ModuleLayer.boot().configuration()
  .resolve(ModuleFinder.of(dir), ModuleFinder.of(), Set.of("com.plugin"));
ModuleLayer layer = ModuleLayer.boot().defineModulesWithOneLoader(cfg, ClassLoader.getSystemClassLoader());
```
Each layer loader isolates plugin versions.

## 8. jdeps Flow
```bash
jdeps --module-path libs app.jar
jdeps --generate-module-info out app.jar
```
Fix split: rename package or shade with `jar --update`.

## 9. Flags Matrix
`-p` path, `-m` run, `--add-modules`, `--add-reads mod1=mod2`, `--patch-module mod=classes`.

## 10. Refs
JSR 376 (JPMS), JEP 261 (module system), `java.lang.module` javadoc.
