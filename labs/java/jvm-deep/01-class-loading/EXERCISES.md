# Custom ClassLoader & Class Loading — Exercises

## Exercise 1: Directory-Based ClassLoader
Implement `DirectoryClassLoader extends ClassLoader`:
- Constructor: `Path classDir, ClassLoader parent`
- Override `findClass(String name)`: read `.class` file from `classDir`, call `defineClass(name, bytes, 0, bytes.length)`
- Test: Compile a `Hello.java` to `out/`, load it via your ClassLoader, invoke `main()` via reflection.

**Challenge**: Support nested packages (directories) and JAR files (use `JarFile` to read entries).

---

## Exercise 2: ClassLoader Isolation Demo
Create two `DirectoryClassLoader` instances pointing to different directories, each containing a different version of `com.example.Version`:
- `v1/Version.class` → `String get() { return "v1"; }`
- `v2/Version.class` → `String get() { return "v2"; }`

Load both, instantiate, call `get()`. Verify they are different classes:
```java
Class<?> v1Class = loader1.loadClass("com.example.Version");
Class<?> v2Class = loader2.loadClass("com.example.Version");
assert v1Class != v2Class;
assert !v1Class.isInstance(v2Class.newInstance());
```

**Insight**: Class identity includes the defining ClassLoader.

---

## Exercise 3: Breaking Delegation (Anti-Pattern)
Create a `ChildFirstClassLoader` that overrides `loadClass()` to check its own repository **before** delegating to parent.
- Place a class `com.example.OverrideMe` in both parent (system) and child loader directories with different behavior
- Show that child-first loads its own version
- Demonstrate the danger: load `java.lang.String` from child repo → `SecurityException` or `LinkageError`

**Reflection**: Why does Java enforce parent-first? (Security, consistency, avoid core class spoofing)

---

## Exercise 4: ServiceLoader with Context ClassLoader
Implement a simple plugin system:
1. Define interface `Plugin { String name(); void execute(); }`
2. Create two JARs with `META-INF/services/com.example.Plugin` listing implementations
3. Use `ServiceLoader.load(Plugin.class)` — fails if plugins only in child ClassLoader
4. Set `Thread.currentThread().setContextClassLoader(pluginLoader)` then `ServiceLoader.load()`
5. Verify plugins are discovered

**Real-world**: This is how JDBC drivers, logging frameworks, and JAXP parsers are discovered.

---

## Exercise 5: Hot-Reload Simulation
Build a mini hot-reload system:
1. `DirectoryClassLoader` watches a directory for `.class` file changes (use `WatchService`)
2. On change: create **new** ClassLoader instance, load updated class
3. Keep a reference to the **old** ClassLoader for existing instances
4. New requests use new ClassLoader; old instances remain functional
5. Simulate: run a loop that calls `Plugin.execute()` every 500ms; modify `.class` file; observe new behavior without restart

**Challenge**: Handle state migration — e.g., serialize old instance, deserialize into new class version.

---

## Starter Code Snippets

```java
// WatchService for hot reload
WatchService watcher = FileSystems.getDefault().newWatchService();
dir.register(watcher, StandardWatchEventKinds.ENTRY_MODIFY);

while (true) {
    WatchKey key = watcher.take();
    for (WatchEvent<?> event : key.pollEvents()) {
        Path changed = dir.resolve((Path) event.context());
        if (changed.toString().endsWith(".class")) {
            // Trigger reload: create new ClassLoader
        }
    }
    key.reset();
}
```

```java
// ServiceLoader pattern
// META-INF/services/com.example.Plugin contains:
// com.example.plugin.AuthPlugin
// com.example.plugin.LoggingPlugin

ServiceLoader<Plugin> loader = ServiceLoader.load(Plugin.class, contextClassLoader);
for (Plugin plugin : loader) {
    plugin.execute();
}
```

```xml
<!-- For compiling test classes at runtime -->
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-jexl</artifactId>
    <version>3.2.1</version>
</dependency>
<!-- Or use javax.tools.JavaCompiler API -->
```

---

## Reflection Questions
1. Why does `Class.forName("com.example.Foo", true, customLoader)` initialize the class, but `customLoader.loadClass("com.example.Foo")` does not (by default)?
2. What happens to static fields when a class is reloaded via a new ClassLoader?
3. Why can't you cast an object loaded by `loader1` to a class loaded by `loader2`, even if bytecode is identical?
4. In a web container (Tomcat/Jetty), how does each web app get its own ClassLoader hierarchy?