# QUIZ — Class Loading

## 1. What is the delegation order in standard class loading?
<details><summary>Answer</summary>
Bootstrap → Platform → Application → Custom. Parent-first delegation.
</details>

## 2. Which classloader has no parent?
<details><summary>Answer</summary>
Bootstrap ClassLoader (returns `null` for `getParent()`). Implemented in native code.
</details>

## 3. When is a class initialized?
<details><summary>Answer</summary>On first **active use**: `new`, static field access, static method call, `Class.forName()`, or subclass initialization.
</details>

## 4. What triggers class initialization vs loading?
<details><summary>Answer</summary>
Loading: finding/reading `.class` bytes. Initialization: running `<clinit>`, static initializers. Loading happens first, init on first **active use**.
</details>

## 3. What breaks parent-first delegation?
<details><summary>Answer</summary>
Overriding `loadClass()` to call `findClass()` before `super.loadClass()`. Used in OSGi, app servers, hot reload.
</details>

## 4. What causes `LinkageError`?
<details><summary>Answer</summary>
Same class loaded by two different classloaders (identity includes classloader). Or binary incompatibility between loaded classes.
</details>

## 4. What causes `ClassLoader` memory leak?
<details><summary>Answer</summary>
Static reference to a class loaded by a custom classloader prevents GC of the classloader and its classes. `Metaspace` OOM.
</details>

## 5. How to fix classloader leak?
<details><summary>Answer</summary>
Clear static references, use `WeakReference`, avoid `ThreadLocal` with classloader-reachable keys, clear thread context classloader.
</details>

## 6. What triggers class initialization?
<details><summary>Answer</summary>
First **active use**: `new`, static field/method access, `Class.forName()`, subclass init, reflection. NOT: accessing `static final` compile-time constants.
</details>

## 8. How does parent-first delegation work?
<details><summary>Answer</summary>
Child asks parent first. If parent can't load, child tries `findClass()`. Ensures core classes loaded by bootstrap, prevents spoofing.
</details>

## 9. How to break delegation (child-first)?
<details><summary>Answer</summary>
Override `loadClass()`, call `findClass()` before `super.loadClass()`. Used in OSGi, app servers for isolation.
</details>

## 10. What causes `LinkageError`?
<details><summary>Answer</summary>
Same class loaded by two classloaders (identity = class + loader), or binary incompatibility between linked classes.
</details>