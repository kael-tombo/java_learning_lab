# Flashcards — Reflection & Annotations

| Q | A |
|---|---|
| Class.forName? | Load by name |
| .class literal? | Compile-time class |
| getSuperclass? | Direct super |
| getInterfaces? | Direct ifaces |
| getDeclaredField? | Own field any vis |
| getField? | Public incl inherit |
| getDeclaredMethod? | Own method |
| getMethod? | Public incl inherit |
| getConstructors? | Public ctors |
| newInstance? | Deprecated, use ctor |
| ctor.newInstance? | Create object |
| setAccessible? | Skip access check |
| trySetAccessible? | Safe variant bool |
| InaccessibleObject? | Needs add-opens |
| add-opens flag? | --add-opens pkg/to |
| Method.invoke? | Reflective call |
| Field.get/set? | Reflective access |
| Modifier.isPrivate? | Check mods |
| Retention SOURCE? | Discard after compile |
| Retention CLASS? | Bytecode, no runtime |
| Retention RUNTIME? | Reflective visible |
| Target METHOD? | Methods only |
| Target FIELD? | Fields only |
| Target TYPE? | Classes/ifaces |
| Documented? | In javadoc |
| Inherited? | Class inherit only |
| Repeatable? | Multiple same annot |
| getAnnotation? | Find incl inherit |
| getAnnotations? | All runtime |
| getDeclaredAnnot? | Direct only |
| Proxy.newProxy? | Interface proxy |
| InvocationHandler? | invoke(p,m,args) |
| MethodHandles? | lookup() entry |
| findVirtual? | Instance method |
| findStatic? | Static method |
| MethodType? | (ret, params) |
| invokeExact? | Exact types |
| invoke? | Conversions |
| VarHandle? | FieldCAS access |
| Lookup modes? | PRIVATE/MODULE |
| privateLookupIn? | Cross-module lookup |
| Annotation proc? | extends Processor |
| SupportedAnnot? | @SupportedAnnotationTypes |
| RoundEnv? | Elements per round |
| Filer? | createSourceFile |
| Messager? | Compile errors |
| -processor? | javac processor opt |
| -proc:none? | Disable processing |
| Service file? | META-INF/services |
| AutoService? | Generates service file |
| Inflation thresh? | -Dsun.reflect.inflationThreshold |
| NoInflation? | -Dsun.reflect.noInflation |
| Cost reflect? | 10-100× direct |
| Cost handle? | ~direct after JIT |
| CGlib? | Subclass proxy |
| ByteBuddy? | Runtime codegen |
| ASM? | Bytecode lib |
| Javassist? | Simple codegen |
| isRecord? | Record check |
| getRecordComps? | Components meta |
| getPermittedSubs? | Sealed variants |
| isSealed? | Sealed check |
| isAnnotation? | Class.isAnnotation |
| getEnclosing? | Enclosing method/class |
| isSynthetic? | Compiler-generated |
| isBridge? | Generics bridge |
| Generic string? | getGenericType |
| Parameterized? | ParameterizedType |
| TypeVariable? | Generic var |
| Wildcard? | ? extends/super |
| Array class? | [Ljava.lang.String; |
| Primitive class? | int.class |
| Void? | void.class/Void |
| Classloader? | getClassLoader() |
| Boot loader? | null loader |
| Layer modules? | layer.modules() |
| Best hot path? | MethodHandle/cache |
| Cache Method? | Map<String,Method> |
| Secure rule? | Allowlist pkgs |
