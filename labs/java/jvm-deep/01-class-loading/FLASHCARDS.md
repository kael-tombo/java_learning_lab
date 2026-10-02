# FLASHCARDS — Class Loading

| # | Front | Back |
|---|-------|------|
| 1 | Bootstrap loader parent? | `null` (native) |
| 2 | Delegation order? | Bootstrap → Platform → App → Custom |
| 3 | Init trigger? | First active use: `new`, static access, `Class.forName()` |
| 4 | Passive use? | Accessing `static final` compile-time constant |
| 4 | Parent-first delegation? | Child asks parent FIRST, then `findClass()` |
| 5 | Child-first loader? | Override `loadClass()`, call `findClass()` before `super.loadClass()` |
| 6 | `LinkageError` cause? | Same class + two loaders, or binary incompatibility |
| 6 | Classloader leak? | Static ref to class → loader + classes stuck in Metaspace |
| 6 | Leak fix? | Clear static refs, `WeakReference`, clear `ThreadLocal`, clear TCCL |
| 6 | Init triggers? | `new`, static access, `Class.forName()`, subclass init |
| 6 | Passive use? | `static final` compile-time constant access |
| 6 | Leak fix | Clear statics, `WeakReference`, clear `ThreadLocal`, clear TCCL |
| 6 | Init order? | Parent class before child; `<clinit>` once per class |
| 6 | `<clinit>` runs? | Once per class, thread-safe, before first active use |
| 6 | `ClassLoader` identity? | Class identity = (binary name, classloader) |
| 6 | `LinkageError`? | Same class + two loaders, or binary incompatibility |
| 6 | Java 9+ modules? | Each module has own loader; `requires` = delegation edge |
| 7 | `defineClass` vs `loadClass`? | `defineClass`: bytes→Class; `loadClass`: delegates + finds |
| 8 | `ClassLoader` leak fix? | Clear statics, `WeakReference`, clear `ThreadLocal`, clear TCCL |
| 8 | `Class` identity? | Binary name + defining loader |
| 8 | Hot reload pattern? | New loader per version, atomic swap, old loader GC'd |
| 9 | Module loader? | Each module has own loader; `requires` = delegation edge |
| 10 | Debug: `java -verbose:class` | Shows every class load |