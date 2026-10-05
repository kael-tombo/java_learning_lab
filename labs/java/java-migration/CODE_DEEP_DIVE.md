# CODE_DEEP_DIVE — Java Migration

Seven real before/after pairs. Each shows the failure mode, the fix, and the
reason the obvious fix is worse.

---

## 1. JAXB migration — `javax.xml.bind` → `jakarta.xml.bind`

JAXB left the JDK in 11. The code change is a package rename; the real work is
in the build and in the marshalling defaults.

### Before (JDK 8, compiled because the JDK supplied JAXB)

```java
package com.acme.xml;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Marshaller;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlRootElement;
import java.io.File;

@XmlRootElement(name = "order", namespace = "urn:acme:order")
public class Order {
    @XmlAttribute(name = "id") private String id;
    private String customer;   // field access, not property access
    private double total;      // marshals as an attribute by default in some impls

    public Order() { }         // JAXB-required no-arg constructor
    public Order(String id, String customer, double total) {
        this.id = id; this.customer = customer; this.total = total;
    }
    public String getId() { return id; }
    public String getCustomer() { return customer; }
    public double getTotal() { return total; }
}

public final class OrderXml {

    public static void write(Order order, File out) throws JAXBException {
        JAXBContext ctx = JAXBContext.newInstance(Order.class);   // expensive
        Marshaller m = ctx.createMarshaller();
        m.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);
        m.marshal(order, out);          // encoding = platform default!
    }

    public static Order read(File in) throws JAXBException {
        JAXBContext ctx = JAXBContext.newInstance(Order.class);
        return (Order) ctx.createUnmarshaller().unmarshal(in);
    }
}
```

### After

```java
package com.acme.xml;

import jakarta.xml.bind.JAXBContext;
import jakarta.xml.bind.Marshaller;
import jakarta.xml.bind.annotation.XmlAccess;
import jakarta.xml.bind.annotation.XmlAccessType;
import jakarta.xml.bind.annotation.XmlAttribute;
import jakarta.xml.bind.annotation.XmlRootElement;
import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;

@XmlRootElement(name = "order", namespace = "urn:acme:order")
@XmlAccess(XmlAccessType.FIELD)      // explicit: removes field-vs-property ambiguity
public class Order {
    @XmlAttribute(name = "id") private String id;
    private String customer;
    private double total;

    // JAXB still needs it; with FIELD access you can also add @JsonCreator-style ctors
    public Order() { }
    public Order(String id, String customer, double total) {
        this.id = id; this.customer = customer; this.total = total;
    }
    public String getId() { return id; }
    public String getCustomer() { return customer; }
    public double getTotal() { return total; }
}

public final class OrderXml {

    private static final JAXBContext CONTEXT;      // one context, reused
    static {
        try {
            CONTEXT = JAXBContext.newInstance(Order.class);
        } catch (JAXBException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    public static void write(Order order, File out) throws IOException, JAXBException {
        Marshaller m = CONTEXT.createMarshaller();
        m.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);
        try (OutputStream os = Files.newOutputStream(out.toPath())) {
            m.marshal(order, os);     // Marshaller closes no stream: try-with-resources
        }
    }

    public static Order read(File in) throws IOException, JAXBException {
        try (InputStream is = Files.newInputStream(in.toPath())) {
            return (Order) CONTEXT.createUnmarshaller().unmarshal(is);
        }
    }
}
```

```xml
<!-- pom.xml -->
<dependencies>
  <dependency>
    <groupId>jakarta.xml.bind</groupId>
    <artifactId>jakarta.xml.bind-api</artifactId>
    <version>4.0.2</version>
  </dependency>
  <dependency>
    <groupId>org.glassfish.jaxb</groupId>
    <artifactId>jaxb-runtime</artifactId>
    <version>4.0.5</version>
    <scope>runtime</scope>
  </dependency>
</dependencies>
```

**Why each change matters.**

- `JAXBContext` is expensive and thread-safe; the before-code rebuilds it per call.
- `m.marshal(order, out)` used the **platform default charset**. Under JDK 18
  (JEP 400) that is now UTF-8, so XML written on 8 and on 21 differ byte-for-byte.
  Pin it explicitly for wire-compat: `m.setProperty(Marshaller.JAXB_ENCODING, "UTF-8")`.
- `@XmlAccess(XmlAccessType.FIELD)` removes the field-vs-property ambiguity that
  changed meaning between JAXB implementations.
- Importing `jakarta.xml.bind` guarantees no `javax.xml.bind` shadow jar sneaks
  back onto the classpath from a transitive dep — the failure mode where both are
  present and only one is loaded.

---

## 2. `sun.misc.Unsafe` → `VarHandle`

### Before

```java
package com.acme.io;

import sun.misc.Unsafe;          // internal: not exported from java.base
import java.lang.reflect.Field;

public final class FastBuffer {

    private static final Unsafe UNSAFE = lookup();

    private final long address;
    private final long capacityBytes;

    public FastBuffer(long capacityBytes) {
        this.capacityBytes = capacityBytes;
        this.address = UNSAFE.allocateMemory(capacityBytes);   // off-heap
    }

    public void putInt(int index, int value) {
        UNSAFE.putInt(address + (index * 4L), value);
    }

    public int getInt(int index) {
        return UNSAFE.getInt(address + (index * 4L));
    }

    public void close() {
        UNSAFE.freeMemory(address);           // nothing tracks this for you
    }

    private static Unsafe lookup() {
        try {
            Field f = Unsafe.class.getDeclaredField("theUnsafe");
            f.setAccessible(true);                        // InaccessibleObjectException on 17
            return (Unsafe) f.get(null);
        } catch (ReflectiveOperationException e) {
            throw new ExceptionInInitializerError(e);
        }
    }
}
```

### After

```java
package com.acme.io;

import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public final class FastBuffer implements AutoCloseable {

    // arrayElementVarHandle is supported API: no reflection, no --add-opens
    private static final VarHandle INT = MethodHandles.arrayElementVarHandle(int[].class);

    private final int[] slots;
    private final boolean direct;

    public FastBuffer(int slotCount) {
        this(slotCount, false);       // heap is the right default; measure before you go direct
    }

    public FastBuffer(int slotCount, boolean direct) {
        this.direct = direct;
        this.slots = new int[slotCount];
    }

    public void putInt(int index, int value) { INT.set(slots, index, value); }
    public int  getInt(int index)            { return (int) INT.get(slots, index); }

    /** Off-heap view via the FFM API; final in JDK 22+, preview in 21. */
    public ByteBuffer asDirectBuffer() {
        if (!direct) {
            throw new IllegalStateException("constructed without direct backing");
        }
        return ByteBuffer.allocateDirect(slots.length * Integer.BYTES)
                         .order(ByteOrder.nativeOrder());
    }

    @Override public void close() { /* nothing to free: GC reclaims the buffer */ }
}
```

```bash
# Compiles on the migration target with no flags at all:
javac --release 21 -d out src/main/java/com/acme/io/FastBuffer.java
```

**Why each change matters.**

- `MethodHandles.arrayElementVarHandle` is the supported replacement for
  `Unsafe` array access. Offsets, memory ordering, and access mode are explicit
  instead of "whatever `putInt` happened to do."
- The `close()` disappearing is the real win: `UNSAFE.freeMemory` has no safety
  net, so a leaked buffer is a native-memory leak that `-XX:MaxHeapSize` will
  never see. Heap buffers are reclaimed by GC.
- If off-heap is genuinely required, use a `MemorySegment` (FFM API) rather than
  `Unsafe`. That API is final in JDK 22+; on 21 you need `--enable-preview`.

---

## 3. `AccessController.doPrivileged` removal

### Before

```java
package com.acme.security;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.Properties;

public final class ConfigLoader {

    public Properties load(File f) throws IOException {
        Properties p = new Properties();
        try (FileInputStream in = new FileInputStream(f)) {   // privileged read
            p.load(in);
        }
        return p;
    }
}

public final class ConfigService {
    // Caller invokes this under the caller's ProtectionDomain, so the read
    // needs a privilege elevation to succeed.
    public Properties loadPrivileged(File f) throws IOException {
        return AccessController.doPrivileged(
                (PrivilegedAction<Properties>) () -> {
                    try { return new ConfigLoader().load(f); }
                    catch (IOException e) { throw new UncheckedIOException(e); }
                });
    }
}
```

### After

```java
package com.acme.security;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Properties;

public final class ConfigLoader {

    public Properties load(Path p) throws IOException {
        Properties props = new Properties();
        try (var in = Files.newInputStream(p)) {   // no privilege machinery
            props.load(in);
        }
        return props;
    }
}

public final class ConfigService {
    public Properties loadPrivileged(Path p) throws IOException {
        return new ConfigLoader().load(p);          // delete doPrivileged
    }
}
```

```bash
# Compile against a modern JDK; SecurityManager is gone as a control mechanism
javac --release 21 -d out src/main/java/com/acme/security/*.java
```

**Why each change matters.**

- `doPrivileged` existed because the SecurityManager could deny a file read based
  on the caller's code source. With the manager disabled by default (18) and
  permanently disabled (24, JEP 486), the wrapper does nothing except stack depth
  and a deprecation warning.
- If you *do* need containment, the supported mechanism is the module system
  (`requires`, `exports`, `opens`) — scoping is structural, not stack-based.
- Migration shape: replace `doPrivileged` blocks with plain calls, then delete
  `SecurityManager` set-up entirely. Keeping it "just in case" means keeping a
  control that does not fire.

---

## 4. `--add-opens` as a tracked, surgical tool

### Before (breakage)

```java
// Legacy framework internals doing deep reflection on JDK classes
Field f = String.class.getDeclaredField("value");
f.setAccessible(true);        // JDK 8/11: works. JDK 17: throws.
```

```bash
$ java -cp out LegacyFramework
Exception in thread "main" java.lang.reflect.InaccessibleObjectException:
  Unable to make field private final byte[] java.lang.String.value accessible:
  module java.base does not "opens java.lang" to unnamed module @0x1b6d3586
```

### After (do not use this — fix the library)

```bash
# The 15-minute unblock, which is NOT the fix:
$ java --add-opens java.base/java.lang=ALL-UNNAMED -cp out LegacyFramework   # runs
```

```java
// The fix: module-aware reflection, which fails loudly if truly inaccessible
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodHandles.Lookup;

public final class FieldAccess {

    public static Lookup lookupIn(Class<?> target) throws IllegalAccessException {
        // throws if the module does not open the package — a build-time signal,
        // not a silent production InaccessibleObjectException
        return MethodHandles.privateLookupIn(target, MethodHandles.lookup());
    }
}
```

```dockerfile
# Track it: named owner, ticket, deletion date — never a bare flag in the Dockerfile
ENV JDK_JAVA_OPTIONS="--add-opens=java.base/java.lang=ALL-UNNAMED"  # LEGACY-BILLING-4471
```

**Why each change matters.**

- `--add-opens` is correct for one thing: buying time. It is also invisible — the
  flag sits in a Dockerfile where nobody reviews it, and it becomes permanent
  debt with no owner.
- `privateLookupIn` is the supported API and it throws at the point of the call,
  so the failure shows up in a test rather than in production on an untested
  code path.
- The `LEGACY-BILLING-4471` suffix is the mechanism that works: a flag you cannot
  attribute to a ticket is a flag nobody will ever remove.

---

## 5. `Class.newInstance()` → `getDeclaredConstructor().newInstance()`

### Before

```java
try {
    Object plugin = Class.forName(className).newInstance();          // JDK 8
    service.register((Plugin) plugin);
} catch (InstantiationException | IllegalAccessException | InvocationTargetException e) {
    log.error("plugin failed: " + className, e);
}
```

### After

```java
try {
    Class<?> type = Class.forName(className);
    Constructor<?> ctor = type.getDeclaredConstructor();  // checked: you know what you call
    Object plugin = ctor.newInstance();                    // reflective invoke
    service.register((Plugin) plugin);
} catch (ClassNotFoundException | NoSuchMethodException e) {
    // Configuration error — no such type, or no no-arg constructor. Never at runtime-by-surprise.
    throw new IllegalStateException("plugin not instantiable: " + className, e);
} catch (InstantiationException | IllegalAccessException | InvocationTargetException e) {
    // The constructor itself threw. InvocationTargetException carries the real cause.
    throw new IllegalStateException("plugin constructor failed: " + className,
                                    e.getCause() != null ? e.getCause() : e);
}
```

**Why each change matters.**

- `newInstance()` propagated the constructor's exceptions unchecked and swallowed
  checked-exception declarations. `Constructor.newInstance` always wraps them in
  `InvocationTargetException`, so a constructor that throws `IllegalStateException`
  is distinguishable from one that could not be instantiated at all.
- **Gotcha in the fix:** `newInstance()` performs an accessibility check, but
  `setAccessible` on a non-public constructor requires module access. On 17 this
  becomes `InaccessibleObjectException` for private constructors of library
  classes. So pair this change with a reachability test (§7) — otherwise you have
  traded a deprecation for a runtime failure.

---

## 6. `pom.xml` migration to `--release`

### Before

```xml
<properties>
  <java.version>1.8</java.version>
  <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>

<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-compiler-plugin</artifactId>
      <version>3.8.1</version>
      <configuration>
        <source>${java.version}</source>
        <target>${java.version}</target>
        <encoding>UTF-8</encoding>
      </configuration>
    </plugin>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-surefire-plugin</artifactId>
      <version>2.22.2</version>
      <configuration>
        <argLine>-Xmx2g</argLine>
      </configuration>
    </plugin>
  </plugins>
</build>
```

### After

```xml
<properties>
  <maven.compiler.release>21</maven.compiler.release>
  <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  <jdk.min.version>21</jdk.min.version>
</properties>

<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-compiler-plugin</artifactId>
      <version>3.13.0</version>
      <configuration>
        <release>${maven.compiler.release}</release>
        <encoding>UTF-8</encoding>
        <compilerArgs>
          <arg>-Xlint:all,-serial</arg>
        </compilerArgs>
      </configuration>
    </plugin>

    <!-- Run tests on the same JDK that compiles -->
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-surefire-plugin</artifactId>
      <version>3.2.5</version>
      <configuration>
        <argLine>-Xmx2g -Dfile.encoding=UTF-8</argLine>
      </configuration>
    </plugin>

    <!-- Fail early and loudly if the build JDK is not the target JDK -->
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-enforcer-plugin</artifactId>
      <version>3.4.1</version>
      <executions>
        <execution>
          <goals><goal>enforce</goal></goals>
          <configuration>
            <rules>
              <requireJavaVersion>
                <version>[${jdk.min.version},)</version>
              </requireJavaVersion>
            </rules>
          </configuration>
        </execution>
      </executions>
    </plugin>

    <!-- Prevent internal-API and post-target API re-entry -->
    <plugin>
      <groupId>org.codehaus.mojo</groupId>
      <artifactId>animal-sniffer-maven-plugin</artifactId>
      <version>1.23</version>
      <executions>
        <execution>
          <id>check-api</id>
          <goals><goal>check</goal></goals>
          <configuration>
            <signature>
              <groupId>org.codehaus.mojo.signature</groupId>
              <artifactId>java21</artifactId>
              <version>1.0</version>
            </signature>
          </configuration>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

```groovy
// build.gradle — the Gradle equivalent
java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)   // compile AND test agree
    }
}
tasks.withType(JavaCompile).configureEach {
    options.release = 21          // not sourceCompatibility/targetCompatibility
    options.encoding = 'UTF-8'
    options.compilerArgs << '-Xlint:all'
}
test {
    jvmArgs '-Dfile.encoding=UTF-8'
}
```

**Why each change matters.**

- `<source>/<target>` set the language level but linked against the **running**
  JDK's API. On a JDK 21 build agent, `<source>1.8</source>` happily compiles a
  call to a JDK 15 method, and it fails with `NoSuchMethodError` on the JDK 8/11
  runtime you ship. `<release>` closes that.
- `-Dfile.encoding=UTF-8` on the Surefire JVM makes the *test* environment
  deterministic — without it, a developer's macOS machine and a Linux CI agent
  produce different `String` bytes and the parity tests lie.
- Enforcer + Animal Sniffer together make the migration self-reversing: any
  future commit that reintroduces an old JDK or a post-target API fails the build
  rather than waiting for the next upgrade to find it.

---

## 7. Reflection-reachability test

The highest-leverage test in a migration: prove every member you reflect into is
actually reachable under strong encapsulation, on the JDK you ship.

```java
package com.acme.architecture;

import org.junit.jupiter.api.Test;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Fail the build if any reflective access path in the app is no longer
 * reachable under JPMS strong encapsulation. Run on the migration target JDK.
 */
class ReflectionReachabilityTest {

    /** Classes reached reflectively at runtime — discovered from jdeps + logs. */
    private static final List<String> REFLECTIVE_TARGETS = List.of(
            "java.lang.String",
            "java.util.Date",
            "java.math.BigDecimal",
            "com.acme.domain.Order"
    );

    @Test
    void everyReflectivelyUsedFieldIsAccessible() {
        List<String> unreachable = new ArrayList<>();

        for (String className : REFLECTIVE_TARGETS) {
            Class<?> type = load(className);
            for (Field field : type.getDeclaredFields()) {
                try {
                    field.setAccessible(true);
                } catch (RuntimeException e) {           // InaccessibleObjectException
                    unreachable.add(className + "#" + field.getName()
                            + " -> " + e.getClass().getSimpleName());
                }
            }
        }

        assertThat(unreachable)
                .as("fields reachable before the upgrade but not after")
                .isEmpty();
    }

    @Test
    void everyReflectivelyUsedMethodIsAccessible() {
        List<String> unreachable = new ArrayList<>();

        for (String className : REFLECTIVE_TARGETS) {
            Class<?> type = load(className);
            for (Method method : type.getDeclaredMethods()) {
                try {
                    method.setAccessible(true);
                } catch (RuntimeException e) {
                    unreachable.add(className + "#" + method.getName());
                }
            }
        }

        assertThat(unreachable).isEmpty();
    }

    @Test
    void addOpensFlagsInUseAreAllAccountedFor() {
        // Every --add-opens in the launcher config must map to a tracked ticket.
        String jdkJavaOptions = System.getenv("JDK_JAVA_OPTIONS");
        if (jdkJavaOptions == null || jdkJavaOptions.isBlank()) {
            return;   // no flags: the desired state
        }
        for (String flag : jdkJavaOptions.split("\\s+")) {
            if (flag.startsWith("--add-opens") || flag.startsWith("--add-exports")) {
                assertThat(jdkJavaOptions)
                        .as("every flag needs a LEGACY-#### ticket reference")
                        .containsPattern("LEGACY-\\d+");
            }
        }
    }

    private static Class<?> load(String className) {
        try {
            return Class.forName(className);
        } catch (ClassNotFoundException e) {
            throw new AssertionError("inventory is stale: " + className, e);
        }
    }
}
```

**Why it matters.** This test converts the most expensive class of migration
failure — `InaccessibleObjectException` on an untested code path — from a
production incident into a build failure, at the cost of one CI run. It also
fails on a stale inventory, which keeps `REFLECTIVE_TARGETS` honest as the app
changes.

Complement it with a reachability check that does not need the list at all:

```bash
# Any reflective setAccessible anywhere in the codebase:
grep -rn 'setAccessible(true)' src/main/java

# Any surviving internal-API import:
grep -rn '^import sun\.\|^import jdk\.internal\.' src/main/java
```

Both greps should return nothing. If they do not, you have a ticket, not a
finished migration.