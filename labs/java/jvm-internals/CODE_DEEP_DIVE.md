# CODE_DEEP_DIVE — JVM Internals

## 1. HotSpot Source Code Navigation

### Key Directories
```
hotspot/
├── src/
│   ├── share/vm/
│   │   ├── oops/           # Object representations (oop.hpp, instanceKlass.hpp)
│   │   ├── memory/         # GC, heap, metaspace
│   │   ├── runtime/        # Threads, safepoints, JVM entry points
│   │   ├── interpreter/    # Template interpreter
│   │   ├── c1/             # Client compiler
│   │   ├── op/             # Optimizing compiler (C2)
│   │   ├── classfile/      # Class loading, verification
│   │   ├── services/       # JFR, JMX, diagnostics
│   │   └── primitive/      # JNI, native methods
│   └── cpu/x86/vm/         # x86-specific code
```

### Essential Files for Object Layout
```cpp
// oop.hpp - Base object pointer
class oopDesc {
    markOop _mark;      // Mark word
    union _metadata {   // Klass pointer (compressed or narrow)
        wideKlassOop _klass;
        narrowKlass _compressed_klass;
    } _metadata;
};

// instanceKlass.hpp - Class metadata
class InstanceKlass : public Klass {
    // VTable, ITable, methods, fields, annotations
    Array<Method*> _methods;
    Array<Field*> _fields;
    vtableEntry* _vtable;
    itableEntry* _itable;
};
```

---

## 2. Mark Word Implementation

### markOop.hpp
```cpp
class markOopDesc {
    // Bit layout (64-bit):
    // [63:25] hash/thread/ptr | [24:23] age | [22] biased_lock | [21:20] lock_state
    
    // Lock states:
    // 00 - lightweight locked
    // 01 - unlocked / biased
    // 10 - heavyweight locked
    // 11 - marked for GC
    
    static const uintptr_t lock_bits = 3;      // 2 bits
    static const uintptr_t locked_value = 0;   // 00
    static const uintptr_t unlocked_value = 1; // 01
    static const uintptr_t monitor_value = 2;  // 10
    static const uintptr_t marked_value = 3;   // 11
    
    // Biased locking bits
    static const uintptr_t biased_lock_bit = 1 << 22;
    static const uintptr_t age_shift = 23;
    
    bool is_neutral() { return (value() & lock_bits) == unlocked_value; }
    bool has_bias_pattern() { return (value() & (biased_lock_bit | lock_bits)) == (biased_lock_bit | unlocked_value); }
};
```

### Lock Inflation (ObjectMonitor)
```cpp
// objectMonitor.cpp
void ObjectMonitor::inflate(Thread* Self, oop object) {
    // Allocate ObjectMonitor from free list or OS
    ObjectMonitor* m = omAlloc(Self);
    
    // Install mark word pointing to monitor
    markOop mark = object->mark();
    markOop new_mark = markOopDesc::encode(m);
    object->cas_set_mark(mark, new_mark);
    
    // Initialize monitor
    m->_object = object;
    m->_owner = Self;
    m->_recursions = 1;
}
```

---

## 3. Safepoint Implementation

### SafepointSynchronize.cpp
```cpp
// Main safepoint entry
void SafepointSynchronize::begin() {
    // 1. Set global request flag
    _safepoint_requested = true;
    
    // 2. Wait for all threads to block
    while (!_all_threads_blocked) {
        // Spin/wait
    }
    
    // 3. Execute VM operation
    _vm_operation->doit();
    
    // 4. Release threads
    _safepoint_requested = false;
    _all_threads_blocked = false;
}

// Thread polling (generated in interpreter/c1/c2)
void Thread::check_safepoint_and_suspend_for_native_trans() {
    if (SafepointSynchronize::is_synchronizing()) {
        SafepointSynchronize::block(this);
    }
}
```

### Safepoint Polling in Generated Code
```assembly
; x86_64 safepoint poll (from template table)
test    %eax, -16384(%r15)    ; Polling page (16KB guard page)
jne     safepoint_handler     ; Jump if page protected

; In C1/C2: same pattern at loop backedges, method returns
```

---

## 4. TLAB Allocation Fast Path

### Generated Assembly (C2)
```assembly
; Allocate 32 bytes in TLAB
mov     %r10, [%r15 + thread::tlab_top_offset]    ; Load top
add     %r10, 32                                    ; Bump pointer
cmp     %r10, [%r15 + thread::tlab_limit_offset]    ; Check limit
ja      slow_path                                   ; Jump if overflow
mov     [%r15 + thread::tlab_top_offset], %r10      ; Store new top
; Object header initialization follows...
```

### Slow Path (C++)
```cpp
// thread.cpp
HeapWord* Thread::allocate_slow(size_t size, bool is_tlab) {
    if (is_tlab) {
        // Refill TLAB from shared eden
        return Universe::heap()->allocate_new_tlab(this, size);
    }
    // Direct allocation in shared eden (with lock)
    return Universe::heap()->mem_allocate(size, this);
}
```

---

## 5. Inline Cache Implementation

### Call Site Data Structure
```cpp
// inlineCache.cpp
class InlineCache {
    enum State { uninitialized, monomorphic, bimorphic, megamorphic };
    
    State _state;
    Klass* _monomorphic_klass;
    methodHandle _monomorphic_method;
    Klass* _bimorphic_klass1;
    methodHandle _bimorphic_method1;
    Klass* _bimorphic_klass2;
    methodHandle _bimorphic_method2;
    
    void update(Klass* receiver_klass, methodHandle method) {
        switch (_state) {
            case uninitialized:
                _state = monomorphic;
                _monomorphic_klass = receiver_klass;
                _monomorphic_method = method;
                break;
            case monomorphic:
                if (receiver_klass == _monomorphic_klass) return;
                _state = bimorphic;
                _bimorphic_klass1 = _monomorphic_klass;
                _bimorphic_method1 = _monomorphic_method;
                _bimorphic_klass2 = receiver_klass;
                _bimorphic_method2 = method;
                break;
            case bimorphic:
                if (receiver_klass == _bimorphic_klass1 || 
                    receiver_klass == _bimorphic_klass2) return;
                _state = megamorphic;
                break;
            case megamorphic:
                return; // No further tracking
        }
    }
};
```

### Generated Dispatch Code
```assembly
; Monomorphic inline cache
mov     %rax, [%receiver + oopDesc::klass_offset]   ; Load klass
cmp     %rax, <cached_klass>                        ; Compare
jne     miss_handler                                ; Miss -> runtime
; Fast path: direct call to cached method
call    <cached_method_entry>

; Bimorphic
cmp     %rax, <klass1>
je      call_method1
cmp     %rax, <klass2>
je      call_method2
jmp     miss_handler

; Megamorphic -> invokeinterface (vtable/itable lookup)
```

---

## 6. Escape Analysis in C2

### Escape State
```cpp
// escape.hpp
enum EscapeState {
    NoEscape,       // Scalar replaceable
    ArgEscape,      // Escapes as argument
    GlobalEscape    // Stored globally or returned
};

// Analysis result per allocation
class EscapeInfo {
    EscapeState _state;
    bool _captured_in_loop;
    bool _synchronized_on;
};
```

### Scalar Replacement
```cpp
// escape.cpp
void EscapeAnalysis::do_scalar_replacement(Compile* C, Node* alloc) {
    // 1. Find all uses of allocation
    // 2. Replace field loads/stores with local variables
    // 3. Remove allocation node
    // 4. Update control flow
    
    for (Field* f : alloc->fields()) {
        Node* load = find_load(alloc, f);
        Node* store = find_store(alloc, f);
        
        if (load && !store) {
            // Read-only field -> constant
            replace_with_constant(load, f->initial_value());
        } else if (load && store) {
            // Read-write -> SSA variable
            create_ssa_variable(load, store);
        }
    }
    
    // Remove allocation if fully replaced
    if (all_uses_replaced(alloc)) {
        C->remove_node(alloc);
    }
}
```

### Lock Elision
```cpp
// If object doesn't escape and is synchronized on:
if (escape_state == NoEscape && synchronized_on) {
    // Replace monitorenter/monitorexit with no-op
    // Add uncommon trap for deoptimization if assumption fails
    replace_with_nop(monitorenter);
    replace_with_nop(monitorexit);
}
```

---

## 7. Card Table & Remembered Sets

### Card Table (Generational GC)
```cpp
// cardTable.cpp
class CardTableModRefBS : public CardTable {
    static const int card_size = 512;  // bytes
    static const int card_shift = 9;   // log2(512)
    
    byte* _byte_map;  // 1 byte per card
    
    void write_ref_field_gc(oop* field, oop new_value) {
        // Write barrier
        *field = new_value;
        dirty_card(field);
    }
    
    void dirty_card(oop* addr) {
        byte* card = byte_for(addr);
        if (*card != dirty_card_val) {
            *card = dirty_card_val;
        }
    }
    
    // Scanning during young GC
    void scan_cards_for_region(HeapRegion* region) {
        for (card = region->first_card(); card <= region->last_card(); card++) {
            if (is_dirty(card)) {
                scan_card(card);
                clean_card(card);
            }
        }
    }
};
```

### G1 Remembered Sets
```cpp
// g1RemSet.cpp
class G1RemSet {
    // Per-region hash table of source regions
    // Key: source region, Value: card indices
    
    void add_reference(HeapRegion* from, HeapRegion* to, int card_index) {
        // Log buffer for concurrent refinement
        DirtyCardQueue::log(from, to, card_index);
    }
    
    // Concurrent refinement threads process log buffers
    void refine() {
        while (DirtyCardQueue::has_cards()) {
            CardEntry e = DirtyCardQueue::pop();
            HeapRegion* to = e.target_region();
            to->rem_set()->add(e.source_region(), e.card_index());
        }
    }
};
```

---

## 8. ZGC Colored Pointers

### Pointer Encoding
```cpp
// zgc.cpp
class ZColoredPointer {
    // 64-bit layout:
    // [63:42] address (42 bits = 4TB)
    // [41:38] metadata (4 bits)
    // [37:0]  unused/alignment
    
    enum Metadata : uintptr_t {
        Finalizable = 1 << 38,
        Remapped    = 1 << 39,
        Marked0     = 1 << 40,
        Marked1     = 1 << 41,
        GoodMask    = (1 << 42) - 1  // Address bits
    };
    
    static inline uintptr_t decode(uintptr_t ptr) {
        return ptr & GoodMask;
    }
    
    static inline bool is_marked(uintptr_t ptr) {
        return (ptr & (Marked0 | Marked1)) != 0;
    }
    
    static inline uintptr_t mark(uintptr_t ptr, bool marked0, bool marked1) {
        return (ptr & GoodMask) | 
               (marked0 ? Marked0 : 0) | 
               (marked1 ? Marked1 : 0);
    }
};
```

### Load Barrier (Read)
```assembly
; ZGC load barrier (generated by C2)
mov     %rax, [%object + offset]        ; Load reference
test    %rax, MARKED_BITS               ; Check marked bits
jne     slow_path                       ; If marked -> fixup
; Fast path: use directly
```

### Relocation Phase
```cpp
// ZRelocate.cpp
void ZRelocate::relocate_objects() {
    for (ZPage* page : _pages_to_relocate) {
        // 1. Allocate new page
        ZPage* new_page = ZPage::allocate();
        
        // 2. Copy live objects
        for (Object* obj : page->live_objects()) {
            Object* new_obj = new_page->allocate(obj->size());
            memcpy(new_obj, obj, obj->size());
            
            // 3. Install forwarding pointer
            obj->set_forwarding_pointer(new_obj);
        }
        
        // 4. Update remapped bit
        page->set_remapped();
    }
}
```

---

## 9. JFR Event Implementation

### Event Definition (Java)
```java
// jdk/jfr/internal/Event.java
@Label("GC Pause")
@Description("GC pause phase")
@StackTrace(false)
class GCPhasePause extends Event {
    @Label("Pause Type")
    String pauseType;  // Young, Mixed, Full, Remark, etc.
    
    @Label("Duration")
    @Timespan(Timespan.MILLISECONDS)
    long duration;
    
    @Label("Cause")
    String cause;  // Allocation Failure, G1 Humongous, etc.
}
```

### Native Event Commit
```cpp
// jfr.cpp
void Jfr::record_gc_pause(const char* phase, double duration_ms, const char* cause) {
    if (!JfrRecorder::is_recording()) return;
    
    // Allocate event from thread-local buffer
    Event* event = ThreadLocalAllocator::allocate<GCPhasePauseEvent>();
    event->set_phase(phase);
    event->set_duration(duration_ms * 1'000'000); // nanos
    event->set_cause(cause);
    event->commit();
}
```

---

## 10. Diagnostic Commands Implementation

### jcmd GC.heap_info
```cpp
// jcmd.cpp
void GCHeapInfo::execute(JavaThread* thread, const char* args) {
    G1CollectedHeap* g1h = G1CollectedHeap::heap();
    
    print("Heap Regions: %d", g1h->n_regions());
    print("Region Size: %d KB", g1h->heap_region_size() / 1024);
    print("Used: %d MB", g1h->used() / 1024 / 1024);
    print("Capacity: %d MB", g1h->capacity() / 1024 / 1024);
    
    for (HeapRegion* r : g1h->regions()) {
        print("Region %p: %s, used=%dKB", r, r->type_str(), r->used() / 1024);
    }
}
```

### jcmd Compiler.codecache
```cpp
void CodeCacheInfo::execute(JavaThread* thread, const char* args) {
    CodeCache* cc = CodeCache::code_cache();
    
    print("CodeCache: size=%d KB, used=%d KB, free=%d KB",
          cc->reserved_size()/1024, cc->used_size()/1024, cc->free_size()/1024);
    
    for (CodeBlob* cb : cc->blobs()) {
        print("  %s: %s, size=%d KB, tier=%d",
              cb->name(), cb->kind_str(), cb->size()/1024, cb->tier());
    }
}
```

---

## Key Source Files Reference

| Area | Key Files |
|------|-----------|
| Object Layout | `oop.hpp`, `instanceKlass.hpp`, `markOop.hpp` |
| Synchronization | `objectMonitor.hpp/cpp`, `basicLock.hpp`, `biasedLocking.cpp` |
| Safepoints | `safepoint.cpp`, `safepointMechanism.cpp`, `thread.cpp` |
| Allocation | `thread.cpp`, `collectedHeap.cpp`, `g1CollectedHeap.cpp` |
| JIT/C2 | `opto/*.cpp`, `c2/Compile.cpp`, `c2/EscapeAnalysis.cpp` |
| Inline Caches | `inlineCache.cpp`, `methodHandles.cpp` |
| GC Barriers | `barrierSet.cpp`, `g1BarrierSet.cpp`, `zgc/*.cpp` |
| Class Loading | `classLoader.cpp`, `systemDictionary.cpp`, `moduleSystem.cpp` |
| JFR | `jfr.cpp`, `jfrEvents.cpp`, `recorder.cpp` |
| Diagnostics | `jcmd.cpp`, `diagnosticCommand.cpp`, `vm_operations.cpp` |