# Mini Project — Modular CLI (hashdir)

## Goal
`hashdir <root>` prints SHA-256 per file. 3 modules, jlink image < 60MB.

## Modules
```
com.hash.api (exports api) ← com.hash.impl (provides Hasher)
com.hash.cli (requires api; uses Hasher)
```

## Steps
1. Write module-infos with uses/provides.
2. `javac -d mods --module-source-path src ...`
3. `jlink --module-path mods:$JAVA_HOME/jmods --add-modules com.hash.cli --output img`.
4. Run `img/bin/hashdir` (launcher via `--launcher hashdir=com.hash.cli/com.hash.cli.Main`).

## Skeleton
```java
// com.hash.api: public interface Hasher { String hash(Path p) throws Exception; }
// com.hash.cli: ServiceLoader.load(Hasher.class).findFirst().orElseThrow()
```

## Acceptance
- `img` runs without installed JDK; `du -sh` recorded.
- Swap impl jar → different algorithm without recompile.
- No split packages; `java --describe-module` clean.

## Stretch
- Layer-loaded extra hasher at runtime.
- `jpackage` installer from image.

## Demo (2 min)
Show module graph (`jdeps -s`) + image size + hash run.
