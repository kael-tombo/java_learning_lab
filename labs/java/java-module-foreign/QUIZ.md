# Quiz — Foreign Function & Memory (20 Q)

1. MemorySegment vs ByteBuffer?
> Segment is bounds-checked, arena-scoped; Buffer is older API.
2. Arena.ofConfined vs ofShared?
> Confined: single-thread; shared: multi-thread safe.
3. What is Arena.global()?
> Unbounded lifetime, never freed — use sparingly.
4. Use-after-close behavior?
> IllegalStateException on access.
5. ValueLayout.JAVA_INT size/align?
> 4 bytes, 4-aligned.
6. allocateFrom(String)?
> NUL-terminated C string in arena.
7. Linker.downcallHandle?
> Java → native call binding.
8. Upcall stub?
> Native → Java callback handle.
9. SymbolLookup types?
> defaultLookup, libraryLookup(path).
10. FunctionDescriptor.of?
> (return, params) signature mapping.
11. Why keep upcall alive?
> GC of stub while native holds it = crash.
12. ADDRESS layout?
> Pointer-sized (64-bit) value.
13. SequenceLayout use?
> C array: layout + element count.
14. Struct padding?
> Aligned offsets; padding inserted.
15. VarHandle from layout?
> layout.varHandle(PathElement...) for fields.
16. mapFile arena role?
> Unmaps when arena closes.
17. --enable-native-access?
> Grants restricted native/memory access.
18. JNI vs FFM?
> FFM is safer, no JNI boilerplate, faster.
19. Thread ownership check?
> Confined arena throws on wrong thread.
20. Detect native leak?
> NMT, arena close discipline, `-XX:NativeMemoryTracking=detail`.
