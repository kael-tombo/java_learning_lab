# Flashcards — Foreign Function & Memory

| Q | A |
|---|---|
| MemorySegment? | Bounded native/heap region |
| Arena? | Lifetime owner of segments |
| ofConfined? | Single-thread arena |
| ofShared? | Multi-thread arena |
| ofAuto? | GC-managed lifetime |
| global()? | Never-freed arena |
| allocate(n)? | Uninitialized memory |
| allocateFrom(str)? | C string alloc |
| get/set? | Typed access via layout |
| JAVA_INT? | 4B int layout |
| JAVA_LONG? | 8B long layout |
| ADDRESS? | Pointer layout |
| JAVA_BYTE? | 1B layout |
| StructLayout? | structLayout(members) |
| withName? | Name a layout member |
| SequenceLayout? | sequenceLayout(n, elem) |
| Padding? | MemoryLayout.paddingLayout(n) |
| Union? | unionLayout(members) |
| Alignment? | byteAlignment(n) |
| VarHandle path? | PathElement.groupElement("x") |
| Sequence index? | PathElement.sequenceElement() |
| Slice? | asSlice(offset, size) |
| reinterpret? | reinterpret(size) new bounds |
| getString(0)? | Read NUL-term string |
| Linker? | nativeLinker() binder |
| downcallHandle? | Java→C handle |
| upcallStub? | Java method as C ptr |
| FunctionDescriptor? | of(ret, params...) |
| SymbolLookup? | find symbol address |
| defaultLookup? | libc + loaded libs |
| libraryLookup? | Arena + System.loadLibrary |
| find(sym)? | Optional<MemorySegment> |
| invokeExact? | Must match MethodType |
| invoke? | Allows conversions |
| Critical(bool)? | Allow heap args |
| mapFile? | MemorySegment.mapFile |
| MapMode? | READ_ONLY/READ_WRITE |
| Scope leak? | Segment outlives arena |
| Wrong-thread? | Confined throws |
| Use-after-free? | IllegalStateException |
| Native access flag? | --enable-native-access |
| NMT detail? | -XX:NativeMemoryTracking |
| Cleaner alt? | Arena auto-close |
| malloc/free? | Arena replaces manual |
| strlen desc? | of(LONG, ADDRESS) |
| qsort needs? | Upcall comparator |
| Keep-alive? | Arena holds stub |
| Zero-copy? | Map + slice, no copy |
| Bounds check? | Always on get/set |
| Overflow addr? | ArithmeticException |
| Alignment fault? | Misaligned layout access |
| Endianness? | nativeOrder() default |
| LE/BE? | withOrder(ByteOrder) |
| Copy segment? | MemorySegment.copy |
| Fill byte? | fill(value) |
| Mismatch? | mismatch(other) index |
| toArray? | toArray(JAVA_INT) copy |
| ofArray? | Wrap heap array |
| Native string len? | strlen via downcall |
| Crash cause #1? | Freed upcall stub |
| Crash cause #2? | Wrong descriptor |
| Debug crash? | -Xcheck:jni, hs_err log |
| Panama docs? | openjdk.org/projects/panama |
| JEP 454? | FFM finalized (JDK 22) |
| reinterpret+cleanup? | Cleaner on scope exit |
| Best arena server? | Confined per-request |
| Best shared? | Cache across threads |
| Avoid global? | Leaks; test-only |
| Perf tip? | Reuse handles, batch gets |
| Safety rule? | Close arenas (try-res) |
