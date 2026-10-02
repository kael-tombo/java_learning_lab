# EXERCISES — Class Loading

## 1. Custom ClassLoader (Beginner)

Create a `FileSystemClassLoader` that loads `.class` files from a directory:

```java
class DirClassLoader extends ClassLoader {
    private final Path root;

    public DirClassLoader(Path root) {
        this.root = root;
    }

    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        Path path = root.resolve(name.replace('.', '/') + ".class");
        byte[] bytes = Files.readAllBytes(path);
        return defineClass(null, bytes, 0, bytes.length);
    }
}
```

**Test**: Create a class file in temp dir, load it, instantiate.

---

## 2. Class Loader Hierarchy (Beginner)

Write a program that prints the classloader hierarchy:

```java
ClassLoader cl = MyClass.class.getClassLoader();
while (cl != null) {
    System.out.println(cl.getClass().getName() + " -> " + cl.getParent());
    cl = cl.getParent();
}
```

**Observe**: Bootstrap (null) → Platform → App → Custom

---

## 3. Delegation Order (Intermediate)

Create a `ChildFirstLoader` that loads from its own path BEFORE delegating:

```java
class ChildFirstLoader extends ClassLoader {
    @Override
    protected Class<?> loadClass(String name, boolean resolve) 
            throws ClassNotFoundException {
        // Try self first
        Class<?> c = findLoadedClass(name);
        if (c != null) return c;

        try {
            return findClass(name);
        } catch (ClassNotFoundException e) {
            // Fall back to parent
        }
        return super.loadClass(name, true);
    }
}
```

**Test**: Create a class in both parent and child paths. Which wins?

---

## 3. Classloader Leak Detection (Intermediate)

Create a leak:
```java
// Leaks: static reference holds classloader
static List<Class<?>> leaked = new ArrayList<>();
for (int i = 0; i < 1000; i++) {
    ClassLoader cl = new MyLoader();
    Class<?> c = cl.loadClass("SomeClass");
    leaked.add(c); // Holds reference to classloader!
}
```

**Detect**: Use `jcmd <pid> GC.class_histogram` or `jmap -histo:live <pid>`. Look for accumulating classloaders.

**Fix**: Use `WeakReference`, clear caches, or `ClassLoader.getDefinedPackage()`.

---

## 4. Hot Reload (Advanced)

Implement hot-reload for a service:

```java
class HotReloadManager {
    private volatile Class<?> currentImpl;
    private final Path classDir;
    private final WatchService watcher;

    public void watch(Path dir) throws IOException {
        watcher = FileSystems.getDefault().newWatchService();
        dir.register(watcher, ENTRY_MODIFY);
        new Thread(this::watchLoop).start();
    }

    private void watchLoop() {
        while (true) {
            WatchKey key = watcher.take();
            for (WatchEvent<?> e : key.pollEvents()) {
                if (e.kind() == ENTRY_MODIFY) {
                    reload();
                }
            }
            key.reset();
        }
    }

    private void reload() {
        ClassLoader cl = new URLClassLoader(new URL[]{dir.toUri().toURL()});
        Class<?> newImpl = cl.loadClass("com.example.ServiceImpl");
        currentImpl = newImpl; // Atomic swap
    }
}
```

---

## 5. Plugin System (Advanced)

Build a plugin framework:

```java
interface Plugin {
    String name();
    void execute();
}

class PluginManager {
    private final List<Plugin> plugins = new ArrayList<>();

    void loadPlugins(Path pluginsDir) throws IOException {
        try (Stream<Path> files = Files.list(pluginsDir)) {
            files.filter(p -> p.toString().endsWith(".jar"))
                 .forEach(this::loadPlugin);
        }
    }

    private void loadPlugin(Path jar) {
        URLClassLoader cl = new URLClassLoader(new URL[]{jar.toUri().toURL()}, 
            getClass().getClassLoader());
        ServiceLoader<Plugin> loader = ServiceLoader.load(Plugin.class, cl);
        loader.forEach(plugins::add);
    }
}
```

---

## 6. Debugging Classloader Issues (Challenge)

Write a diagnostic tool that prints:

1. All classloaders in hierarchy
2. Classes loaded by each
3. Which loader loaded a given class
4. Detects duplicate classes across loaders

```java
class ClassLoaderDiagnostic {
    static void diagnose(Class<?> clazz) {
        ClassLoader cl = clazz.getClassLoader();
        System.out.println("Class: " + clazz.getName());
        System.out.println("Loader: " + cl);
        System.out.println("Loader class: " + cl.getClass().getName());
        System.out.println("Protection domain: " + clazz.getProtectionDomain());
        System.out.println("Code source: " + clazz.getProtectionDomain().getCodeSource());
    }
}
```

**Bonus**: Detect duplicate classes across loaders (same class name, different loaders).