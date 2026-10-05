# Quiz — Reflection & Annotations (20 Q)

1. getMethods vs getDeclaredMethods?
> Public incl. inherited vs all declared in class.
2. setAccessible(true) does?
> Suppresses access checks (needs opens).
3. InaccessibleObjectException fix?
> --add-opens pkg/target.
4. Retention types?
> SOURCE/CLASS/RUNTIME.
5. @Target use?
> Where annotation applies.
6. Proxy requirement?
> Interface-based; JDK dynamic proxy.
7. CGLIB vs JDK proxy?
> Subclass vs interface proxy.
8. MethodHandle vs Method?
> Handle is JIT-friendly, typed.
9. invoke vs invokeExact?
> Conversions vs exact type.
10. Annotation processor round?
> javac rounds generating sources.
11. Filer role?
> Creates new source/class files.
12. Retention for processor?
> SOURCE/CLASS suffices.
13. getAnnotation vs getDeclared?
> Inherited vs direct.
14. @Inherited?
> Only class-level inheritance.
15. Repeatable?
> Container annotation wrapper.
16. Deep reflect cost?
> ~10-100× direct until inflated.
17. Inflation?
> Native→bytecode accessor after threshold.
18. getRecordComponents?
> Record metadata without fields hack.
19. Module opens?
> `opens pkg to framework`.
20. When avoid reflection?
> Hot paths, public API exists, records/patterns suffice.
