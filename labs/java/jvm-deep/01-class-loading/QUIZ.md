# Custom ClassLoader & Class Loading — Quiz

> **Instructions**: Answer each question before revealing the solution.

<details>
<summary><strong>1. What is the standard class-loading delegation model?</strong></summary>
**Answer: Parent-first** — `loadClass()` delegates to parent ClassLoader first; only if parent fails, `findClass()` is called. Prevents core class spoofing.
</details>

<details>
<summary><strong>2. Which method must a custom ClassLoader override to define custom loading logic?</strong></summary>
**Answer: `findClass(String name)`** — Called by `loadClass()` after parent delegation fails. Should read bytecode and call `defineClass()`.
</details>

<details>
<summary><strong>3. What does `defineClass(byte[] bytecode, ...)` do?</strong></summary>
**Answer: Converts raw bytecode into a `Class<?>` object** — JVM verifies format, resolves symbolic references, prepares static fields. Returns the defined Class.
</details>

<details>
<summary><strong>4. Can two different ClassLoaders load the same class name?</strong></summary>
**Answer: Yes — they are distinct types at runtime.** `ClassA` loaded by `Loader1` ≠ `ClassA` loaded by `Loader2`. `instanceof` and casts fail across loaders.
</details>

<details>
<summary><strong>5. What is the bootstrap ClassLoader?</strong></summary>
**Answer: Loads core JDK classes (`java.*`, `javax.*`)** — Implemented in native code (C++), has no parent, represented as `null` in Java.
</details>

<details>
<summary><strong>6. What is the platform (extension) ClassLoader?</strong></summary>
**Answer: Loads platform modules / extension classes** — Child of bootstrap. In Java 9+, replaces the old extension mechanism.
</details>

<details>
<summary><strong>7. What is the system (application) ClassLoader?</strong></summary>
**Answer: Loads classes from classpath (`-cp`, `-jar`)** — Child of platform ClassLoader. Default parent for custom ClassLoaders.
</details>

<details>
<summary><strong>8. What happens if you override `loadClass()` without calling `super.loadClass()`?</strong></summary>
**Answer: Breaks delegation model** — Parent is not consulted first. Can lead to duplicate loading, security issues, or `LinkageError` if same class loaded twice.
</details>

<details>
<summary><strong>9. What is `ClassNotFoundException` vs `NoClassDefFoundError`?</strong></summary>
**Answer: `ClassNotFoundException` — checked, thrown when class not found by ClassLoader (e.g., `Class.forName()`). `NoClassDefFoundError` — error, thrown when class existed at compile time but missing at runtime (static init failed, or loader mismatch).**
</details>

<details>
<summary><strong>10. How do you access the ClassLoader that loaded a given class?</strong></summary>
**Answer: `MyClass.class.getClassLoader()`** — Returns the defining ClassLoader, or `null` for bootstrap-loaded classes.
</details>

---
*Quiz complete. Review incorrect answers and re-read the THEORY.md for deeper understanding.*