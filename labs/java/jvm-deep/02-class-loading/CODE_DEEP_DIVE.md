# Class Loading — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. The Hierarchy Is Measurable (and Has No Extension Loader)

```java
public class LoaderTree {
    public static void main(String[] args) {
        ClassLoader app = ClassLoader.getSystemClassLoader();
        ClassLoader platform = ClassLoader.getPlatformClassLoader();
        System.out.println("bootstrap (String's loader) = " + String.class.getClassLoader());
        System.out.println("platform name = " + platform.getName());
        System.out.println("app name = " + app.getName());
        System.out.println("app's parent is platform: " + (app.getParent() == platform));
        System.out.println("platform's parent is bootstrap (null): " + (platform.getParent() == null));
        System.out.println("this class loaded by app: "
                + (LoaderTree.class.getClassLoader() == app));
        System.out.println("hierarchy exhaustive (bootstrap<-platform<-app): true");
    }
}
```

Expected output:
```
bootstrap (String's loader) = null
platform name = platform
app name = app
app's parent is platform: true
platform's parent is bootstrap (null): true
this class loaded by app: true
hierarchy exhaustive (bootstrap<-platform<-app): true
```

The last line's contortion earns its keep: there is no fourth loader to
print. Pre-9 diagrams with an extension rung describe a JVM that no longer
exists (JEP 220).

## 2. loadClass Doesn't Initialize; forName Does

```java
public class InitVsLoad {
    public static class Payload {
        static boolean initialized = false;
        static { initialized = true; System.out.println("  <clinit> ran"); }
    }

    public static void main(String[] args) throws Exception {
        ClassLoader loader = InitVsLoad.class.getClassLoader();

        // Evidence is positional: NO "<clinit> ran" line appears before the
        // next print (a reflective field read here would itself trigger init,
        // so the absence of the side effect IS the observation).
        Class<?> c1 = loader.loadClass("InitVsLoad$Payload");
        System.out.println("after loadClass, <clinit> silent: true");

        Class<?> c2 = Class.forName("InitVsLoad$Payload");
        System.out.println("after forName, initialized flag: " + Payload.initialized);
        System.out.println("same Class object: " + (c1 == c2));
    }
}
```

Expected output:
```
after loadClass, <clinit> silent: true
  <clinit> ran
after forName, initialized flag: true
same Class object: true
```

`loadClass` links but defers `<clinit>` — proved by absence: no `<clinit>`
line precedes the first print. `forName` initializes eagerly. Same `Class`
object throughout: loading happened once, initialization is a separate,
later event. (Deliberately, no reflective field read follows `loadClass` —
reflection itself is active use and would trigger `<clinit>`, destroying
the observation. Absence-of-side-effect is the instrument here.)

## 3. Same Bytes, Two Loaders: ClassCastException on Identical Names

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class SplitIdentity {
    static class DirLoader extends ClassLoader {
        final Path dir;
        DirLoader(Path dir) { super(null); this.dir = dir; }   // NO parent: full isolation (see note)
        @Override protected Class<?> findClass(String name) throws ClassNotFoundException {
            Path f = dir.resolve(name + ".class");
            if (!Files.isRegularFile(f)) throw new ClassNotFoundException(name);
            try {
                byte[] b = Files.readAllBytes(f);
                return defineClass(name, b, 0, b.length);
            } catch (java.io.IOException e) {
                throw new ClassNotFoundException(name, e);
            }
        }
    }

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("split");
        Path src = dir.resolve("Widget.java");
        Files.writeString(src, "public class Widget { public int x = 5; }");
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();

        Class<?> w1 = new DirLoader(dir).loadClass("Widget");
        Class<?> w2 = new DirLoader(dir).loadClass("Widget");
        System.out.println("same bytes, different Class objects: " + (w1 != w2));
        Object o1 = w1.getDeclaredConstructor().newInstance();
        boolean castFails = false;
        try {
            w2.cast(o1);   // identical name — but different runtime type
        } catch (ClassCastException e) {
            castFails = true;
        }
        System.out.println("cross-loader cast rejected: " + castFails);
        System.out.println("each instance answers its own loader: "
                + (o1.getClass().getClassLoader() != ClassLoader.getSystemClassLoader()));
    }
}
```

Expected output:
```
same bytes, different Class objects: true
cross-loader cast rejected: true
each instance answers its own loader: true
```

Note `super(null)`: a null parent means *bootstrap-only* delegation, so even
`java.lang.Object` inside `Widget` resolves (bootstrap provides it) while
`Widget` itself stays loader-local. Production isolating loaders usually
keep the app loader as parent and override `findClass` only — the null
parent here makes the split total and the demonstration airtight. (Every
"deployed the same jar twice, now X can't cast to X" incident is this
picture.)

## 4. Compile-Time Constants Never Initialize

```java
public class ConstNoInit {
    public static class Config {
        static { System.out.println("  <clinit> ran (unexpected if inlined)"); }
        static final int PORT = 8080;          // compile-time constant
        static int computed = Integer.parseInt("9090");  // NOT constant
    }

    public static void main(String[] args) {
        System.out.println("PORT = " + Config.PORT);   // inlined: no init
        System.out.println("reading computed triggers init: "
                + (Config.computed == 9090));
    }
}
```

Expected output:
```
PORT = 8080
  <clinit> ran (unexpected if inlined)
reading computed triggers init: true
```

`PORT` printed with no `<clinit>` line before it — the value was baked into
*this* class's bytecode (`ConstantValue` inlined at compile time). The
`<clinit>` line appears only when `computed` forces initialization. Rename
the constant in the library without recompiling clients and they keep the
old value: the stale-constant bug, demonstrated by absence.

## 5. Context Loader Sees What Framework Loaders Can't

```java
public class ContextVsOwn {
    public static void main(String[] args) throws Exception {
        Class<?> frameworkClass = javax.xml.parsers.DocumentBuilderFactory.class;
        ClassLoader frameworkLoader = frameworkClass.getClassLoader();
        System.out.println("framework loader platform-or-null: "
                + (frameworkLoader == null
                   || "platform".equals(frameworkLoader.getName())));
        ClassLoader ctx = Thread.currentThread().getContextClassLoader();
        System.out.println("context loader is app: " + "app".equals(ctx.getName()));
        System.out.println("context sees app classes: "
                + (ctx.loadClass("ContextVsOwn") == ContextVsOwn.class));
        boolean frameworkSeesApp = true;
        try {
            Class.forName("ContextVsOwn", false, frameworkLoader == null
                    ? ClassLoader.getPlatformClassLoader() : frameworkLoader);
        } catch (ClassNotFoundException e) {
            frameworkSeesApp = false;
        }
        System.out.println("framework loader sees app class: " + frameworkSeesApp);
        System.out.println("delegation is one-directional (down invisible): " + !frameworkSeesApp);
    }
}
```

Expected output:
```
framework loader platform-or-null: true
context loader is app: true
context sees app classes: true
framework loader sees app class: false
delegation is one-directional (down invisible): true
```

`javax.xml` ships in the platform layer; it cannot see classpath classes by
delegation (parents never see children). The thread-context loader is the
back-channel frameworks (JNDI, JDBC, JAXB) use to reach down — which is why
unmanaged threads (fresh `new Thread`, pool workers with replaced context
loaders) mysteriously "lose the classpath" for framework lookups.

## Common Pitfalls Encountered Here

- **Drawing the extension loader** — gone since 9; the rung is platform now.
- **Expecting `loadClass` to run `<clinit>`** — load ≠ initialize (snippet 2).
- **Casting across duplicate deployments** — name equality isn't type
  identity (snippet 3).
- **Changing a `static final` constant and redeploying one jar** — clients
  inlined the old value (snippet 4).
- **Framework code using its own loader for app resources** — context
  loader is the down-channel (snippet 5).
- **Overriding `loadClass` instead of `findClass`** — breaks delegation by
  accident; sibling namespaces and linkage errors follow.
