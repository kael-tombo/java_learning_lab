# Custom ClassLoader & Class Loading — Flashcards

| # | Question | Answer |
|---|----------|--------|
| 1 | **Standard delegation model?** | Parent-first: parent `loadClass()` first, then `findClass()` |
| 2 | **Method to override for custom loading?** | `findClass(String name)` |
| 3 | **`defineClass()` does?** | Converts byte[] → Class<?>; verifies, links, initializes |
| 4 | **Same class name, two loaders = ?** | Distinct types — `instanceof` fails, casts fail |
| 5 | **Bootstrap ClassLoader loads?** | Core JDK (`java.*`, `javax.*`) — native, no parent (`null`) |
| 6 | **Platform ClassLoader loads?** | Platform modules / extensions — child of bootstrap |
| 7 | **System ClassLoader loads?** | Application classpath (`-cp`, `-jar`) — child of platform |
| 8 | **Override `loadClass()` without `super` = ?** | Breaks delegation — duplicate loading, security risk, LinkageError |
| 9 | **ClassNotFoundException vs NoClassDefFoundError?** | CNFE: checked, class not found by loader; NCDFE: error, class missing at runtime (static init failed / loader mismatch) |
| 10 | **Get defining ClassLoader?** | `MyClass.class.getClassLoader()` — returns `null` for bootstrap |
| 11 | **Class identity = ?** | Fully qualified name + defining ClassLoader |
| 12 | **LinkageError cause?** | Same class loaded by two loaders in same hierarchy; or incompatible binary changes |
| 13 | **Custom ClassLoader use cases?** | Hot reload, encrypted bytecode, network/db loading, plugin isolation, JSP compilation |
| 14 | **`defineClass` protection domain?** | Can pass `ProtectionDomain` for security permissions (sandboxing) |
| 15 | **`resolveClass(Class)` does?** | Triggers linking (verification, preparation, resolution) |
| 16 | **Class loading phases?** | Load → Link (Verify → Prepare → Resolve) → Initialize |
| 17 | **When is `<clinit>` run?** | Initialization phase — first active use (new, static field access, static method call, reflection) |
| 18 | **Context ClassLoader?** | `Thread.getContextClassLoader()` — for SPI/service loading (JDBC, JAXP, logging) |
| 19 | **Why context ClassLoader?** | Parent delegation can't find SPI impls on app classpath; context loader bridges |
| 20 | **Hot reload pattern?** | New ClassLoader per reload; old classes become unreachable (GC); instances must be recreated |

---

**Study tip**: Cover the Answer column and quiz yourself. Shuffle by picking random numbers.