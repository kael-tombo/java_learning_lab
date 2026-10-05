# EXERCISES — Java Migration

Ten exercises in migration order: inventory, compile, behavioural de-risking,
rollout. Each has a mechanically checkable pass condition. If you cannot
evaluate it, you have a hope, not a result.

Scaffold once and reuse: `mkdir -p sample/src/main/java/com/acme/{core,io,xml} && cd sample && git init`.

---

## 1. `jdeps --jdk-internals` inventory

**Goal.** The typed list of internal JDK APIs the sample touches — Stage 0 of
THEORY.md §2, and the highest-value command in any migration.

```bash
mkdir -p target && javac --release 8 -d target/classes $(find src/main/java -name '*.java')
jar --create --file target/app-8.jar -C target/classes .
jdeps --jdk-internals --multi-release 17 -R target/app-8.jar | sort -u > inventory.txt
```

**Expected output.** A table headed `JDK Internal API / Used in` listing e.g.
`sun.misc.Unsafe` → `java.util.concurrent.ThreadPool` and
`sun.nio.ch.DirectBuffer` → `com.acme.io.FastBuffer`. A clean project instead
prints `-> No dependencies inside the JDK internal API.` That is the goal state,
and it takes work.

**Pass.** Every line classified *replace* / *upgrade the library* /
*needs `--add-opens`* (debt, with a ticket).

---

## 2. Compile one tree at four `--release` levels

**Goal.** Demonstrate that "it compiles" is version-relative.

```bash
for r in 8 11 17 21; do
  javac --release $r -Xlint:all -d out/$r $(find src/main/java -name '*.java') 2> err-$r.txt
  echo "release $r -> $(grep -c 'error:' err-$r.txt) errors"
done
diff err-11.txt err-17.txt
```

**Expected output.** Errors present at 17 but not 11: `cannot find symbol ...
newInstance()` (`Class.newInstance`, gone since 9) and
`package javax.xml.bind does not exist` (gone since 11).

**Pass.** For each new error you can name the compatibility surface and the JDK
release that caused it. Unexplainable errors are the real work.

---

## 3. Migrate a JAXB project off `javax.xml.bind`

**Goal.** Move off JDK-bundled JAXB to explicit `jakarta.xml.bind`. A dependency
problem wearing a code problem's clothes.

```bash
mvn dependency:get -Dartifact=jakarta.xml.bind:jakarta.xml.bind-api:4.0.2
mvn dependency:get -Dartifact=org.glassfish.jaxb:jaxb-runtime:4.0.5
grep -rl 'javax\.xml\.bind' src/ | xargs sed -i 's/javax\.xml\.bind/jakarta.xml.bind/g'
grep -rn 'javax\.xml\.bind' src/ ; echo "leftovers: $?"   # expect 1 (no matches)
mvn generate-sources && mvn -q clean test                 # maven-jaxb2-plugin: XSD -> classes
```

**Expected output.** `leftovers: 1` and a green `mvn test`. Skip
`generate-sources` and you hand-maintain 40 annotations until the next schema
change.

**Pass.** `mvn dependency:tree | grep -c javaee` is `0`, and a marshal/unmarshal
round-trip passes against a fixture captured *before* the migration.

---

## 4. Fix `sun.misc.Unsafe` under JDK 17

**Goal.** Reproduce the strong-encapsulation failure, then fix it properly with
`VarHandle` (CODE_DEEP_DIVE.md §2) rather than `--add-opens`.

```bash
javac --release 21 -d out21 src/main/java/com/acme/io/FastBuffer.java
java -cp out21 com.acme.io.Demo
```

**Expected output.**

```
java.lang.reflect.InaccessibleObjectException: Unable to make field
private final sun.misc.Unsafe theUnsafe accessible: module java.base
does not "opens java.lang" to unnamed module @0x1b6d3586
```

`--add-opens java.base/jdk.internal.misc=ALL-UNNAMED` hides it — which is why it
is debt, not a fix. JDK 24 warns on those memory-access methods.

**Pass.** The demo runs on JDK 21 with zero `--add-opens`/`--add-exports`.

---

## 5. Install the two static gates

**Goal.** Turn "remember not to do that" into a build failure.

```bash
mvn org.codehaus.mojo:animal-sniffer-maven-plugin:1.23:check \
  -Danimal.sniffer.signature.artifactId=java11 -Danimal.sniffer.signature.version=1.0
java -jar forbidden-apis-3.6.1.jar --target 11 -classpath target/app.jar target/app.jar
```

**Expected output.** Silent when clean; add one JDK 17-only call and Animal
Sniffer fails with
`[ERROR] Undefined reference: java.nio.file.Files readString(java.nio.file.Path)`.

**Pass.** Both run on `main` in under 5 minutes and each fails on a deliberate
violation.

---

## 6. UTF-8 / ISO-8859-1 parity test (JDK 18 default charset)

**Goal.** Catch the worst silent break here: JEP 400 changed the default charset
from platform locale to UTF-8. Legacy-encoded data changes or throws
`MalformedInputException` — no exception, wrong data.

```bash
printf 'caf\xe9 order %s\n' 42 > src/test/resources/order-legacy.txt
```

```java
@Test void legacyEncodedFixtureSurvivesUpgrade() throws Exception {
    byte[] raw = Files.readAllBytes(Path.of("src/test/resources/order-legacy.txt"));
    String decoded = new String(raw, StandardCharsets.ISO_8859_1);
    assertThat(decoded).isEqualTo("café order 42\n");
    assertThat(decoded.getBytes(StandardCharsets.ISO_8859_1)).isEqualTo(raw);
}
```

**Expected output.** Green on 17 and 21. Remove the explicit charset: passes on
17, fails on 21. That asymmetry *is* the risk.

**Pass.** `grep -rn 'new String(' src/main/java | grep -v StandardCharsets`
returns zero hits.

---

## 7. Audit `Locale`/CLDR formatting with golden files

**Goal.** Detect the other silent break: JEP 252 (JDK 9) switched the default
locale provider to CLDR, changing date/number/casing output.

```java
@Test void numberAndDateFormattingIsPinned() {
    for (Locale l : List.of(Locale.US, Locale.GERMANY, Locale.FRANCE,
                            new Locale("tr"), Locale.JAPAN)) {
        assertThat(String.format(l, "%,.2f", 1234567.891))
              .as("number[%s]", l.toLanguageTag())
              .isEqualTo(NumberFormat.getNumberInstance(l).format(1234567.891));
    }
}
```

**Expected output.** Failures on locales whose CLDR output differs from JRE data.
Turkish dotless-i casing (`i` → `İ`) is the reliable offender.

**Pass.** Golden files committed per locale, `tr` casing asserted explicitly, and
every parse site uses a fixed locale plus an explicit `DateTimeFormatter`.

---

## 8. Maven `--release` and Gradle toolchains

**Goal.** Make compile JDK and declared target agree, so you cannot link against
an API missing from the runtime you ship.

```bash
mvn -X clean compile -Dmaven.compiler.release=17 | grep -m1 'release ='
./gradlew compileJava -PtargetRelease=17 --info | grep -m1 'Compiling with JDK'
javap -v -cp out/17 com.acme.Main | grep major   # 61 for 17, 65 for 21
```

**Expected output.** `[DEBUG] Options: ... --release 17 ...` and
`[INFO] Compiling with JDK Java 21.0.5 (toolchain: languageVersion=17)`.

**Pass.** No `javaee-api`/`jaxb-api` shims in `mvn dependency:tree`, the
toolchain resolves without a manual `JAVA_HOME`, and class-file major versions
match the declared targets.

---

## 9. Rollback-without-rebuild canary drill

**Goal.** Prove the rollback path *before* you need it.

```bash
docker build -t app:jdk8 . && docker push app:jdk8    # both tags pre-pushed
docker build -t app:jdk21 . && docker push app:jdk21
kubectl -n prod set image deploy/app app=app:jdk21 --record
# simulate regression, then:
kubectl -n prod set image deploy/app app=jdk8; kubectl -n prod rollout status deploy/app --timeout=120s
```

**Expected output.** `deployment "app" successfully rolled out` — measured, not
asserted from memory.

**Pass.** Rollback with no build, registry repackage, or redeploy step, under 5
minutes, across a full business cycle including weekend traffic. Weekend traffic
is a different shape; a canary that only saw Tuesday proved nothing. Record the
wall-clock time — Exercise 10 needs it.

---

## 10. Build the blocker risk ledger

**Goal.** Turn exercises 1–7 into a scored ledger using MATH_FOUNDATION.md §1.

```csv
id,item,type,blast,detect,effort,owner
B1,FastBuffer uses sun.misc.Unsafe,internal-api,3,4,2,platform
B2,OrderXml marshals with JAXB,removed-module,4,5,3,billing
B3,Locale-sensitive invoice text,cldr,5,5,2,billing
B4,Legacy CSV reader assumes platform charset,encoding,5,5,4,data
B5,Hibernate 4 proxy generation,bytecode-gen,3,3,6,orders
```

```
score = 100 * (0.6 * (blast*detect*effort)/125 + 0.4 * (0.4*blast + 0.3*detect + 0.3*effort)/5)
```

**Expected output.** `B4` (silent, high-blast, hard-to-detect) outranks `B1`
even though `B1` is easier to fix. That ordering is the point: the items that
survive testing are the ones you must schedule first.

**Pass.** Every row has a type and an owner, total effort matches your calendar,
and you can say which single item would be most expensive to discover in
production.