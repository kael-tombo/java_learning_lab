# Refactoring: Class Loading

## 1. Replace forName sweeps with lazy loading

Before (eager init at startup, slow and order-sensitive):

```java
for (String cls : ALL_PLUGINS) Class.forName(cls);  // initializes all
```

After (load references lazily, initialize on use):

```java
for (String cls : ALL_PLUGINS) Class.forName(cls, false, loader);
```

Effect: linking without `<clinit>` side effects. Each plugin still
initializes exactly once, on first active use.

## 2. Route framework lookups through the context loader

Before (platform-layer code blind to app classes):

```java
InputStream in = ParserFactory.class.getResourceAsStream("conf.xml");
```

After (down-channel to the app layer):

```java
ClassLoader ctx = Thread.currentThread().getContextClassLoader();
InputStream in = ctx.getResourceAsStream("conf.xml");
```

Effect: `ContextVsOwn`'s failing lookup becomes the succeeding one.

## 3. Narrow custom loaders to findClass

Before (accidental delegation break):

```java
class DirLoader extends ClassLoader {
    @Override public Class<?> loadClass(String n) throws ... {
        byte[] b = readBytes(n);  // checks self FIRST
        ...
    }
}
```

After (delegation preserved):

```java
class DirLoader extends ClassLoader {
    @Override protected Class<?> findClass(String n) throws ... {
        byte[] b = readBytes(n);
        if (b == null) throw new ClassNotFoundException(n);
        return defineClass(n, b, 0, b.length);
    }
}
```

Effect: `java.*` still resolves at bootstrap; sibling namespaces
appear only where genuinely wanted.

## 4. Convert computed statics to true constants

Before (every read pays initialization):

```java
static int PORT = Integer.parseInt("8080");  // forces <clinit>
```

After (inlined, zero init):

```java
static final int PORT = 8080;  // ConstantValue, no <clinit> on read
```

Effect: `ConstNoInit`'s first-read silence becomes the norm. Keep
parsing only where the value is genuinely dynamic.
