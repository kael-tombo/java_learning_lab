# MATH_FOUNDATION — ASM Bytecode Mathematics

## 1. Bytecode Size Analysis

### Instruction Size Distribution

| Category | Typical Bytes | Frequency |
|----------|---------------|-----------|
| `iconst_0` - `iconst_5` | 1 | High |
| `bipush` / `sipush` | 2-3 | Medium |
| `ldc` / `ldc_w` | 2-3 | Medium |
| `aload` / `astore` | 2-4 | High |
| `invoke*` | 3-5 | High |
| `invokedynamic` | 5+ | Low |

### Average Instruction Size

| Program Type | Avg bytes/instruction |
|--------------|----------------------|
| Typical Java | ~2.5 bytes |
| Generated code | ~3.5 bytes |
| Optimized | ~2.0 bytes |

---

## 1. Stack Depth Analysis

### Stack Depth Calculation

For a method with bytecode instructions, max stack depth = max stack height during execution.

**Algorithm**:
```
depth = 0
for each instruction:
    depth += stack_delta(instruction)
    max_depth = max(max_depth, depth)
```

### Stack Delta Table

| Instruction | Delta |
|-------------|-------|
| `iconst_0` - `iconst_5` | +1 |
| `bipush` / `sipush` | +1 |
| `ldc` / `ldc_w` | +1 |
| `iload` / `fload` / `aload` | +1 |
| `lload` / `dload` | +2 |
| `iadd` / `iand` / `ior` | -1 |
| `imul` / `idiv` | -1 |
| `dup` | +1 |
| `pop` | -1 |
| `swap` | 0 |
| `invoke*` | -(args) + return |
| `new` | +1 |
| `newarray` | 0 |

---

## 1. Bytecode Size Estimation

### Average Instruction Size

| Instruction Category | Bytes | Frequency |
|----------------------|-------|-----------|
| `iconst_0` - `iconst_5` | 1 | High |
| `bipush` / `sipush` | 2-3 | Medium |
| `ldc` / `ldc_w` | 2-3 | Medium |
| `iload` / `istore` | 2-4 | High |
| `invoke*` | 3-5 | High |
| `invokeinterface` / `invokedynamic` | 5+ | Low |

**Typical average**: ~2.5 bytes/instruction for typical Java code.

### Method Size Estimation

For a method with `N` bytecode instructions:
```
Estimated bytes = N × 2.5 + header + stack_map
```

Typical Java method: 10-50 bytecode instructions → 25-125 bytes.

---

## 2. Stack Depth Mathematics

### Stack Depth Calculation

For each bytecode instruction, stack depth changes by `delta`:

```
depth += delta(instruction)
max_depth = max(max_depth, current_depth)
```

| Instruction | Stack Delta |
|-------------|-------------|
| `iconst_0` - `iconst_5` | +1 |
| `bipush` / `sipush` | +1 |
| `ldc` / `ldc_w` | +1 |
| `iload` / `fload` / `aload` | +1 |
| `lload` / `dload` | +2 |
| `iadd` / `iand` / `ior` | -1 |
| `imul` / `idiv` | -1 |
| `dup` | +1 |
| `pop` | -1 |
| `swap` | 0 |
| `invoke*` | -(args) + return_count |
| `new` | +1 |
| `newarray` | 0 |

### Max Stack Depth Formula

```
max_stack = max(0, Σ delta_i) over all paths
```

Must compute for all control flow paths; `ClassWriter.COMPUTE_MAXS` does this.

---

## 2. Code Size Estimation

### Average Instruction Size

| Category | Avg Bytes | % of Instructions |
|--------|-----------|-------------------|
| Single-byte (iconst, pop, dup) | 1 | ~30% |
| Two-byte (iload, istore) | 2 | ~25% |
| Three-byte (ldc, invoke*) | 3 | ~30% |
| Wide (invokeinterface) | 5+ | ~15% |

**Typical average**: ~2.5 bytes/instruction.

### Method Size Estimation

```
Method_Size ≈ 10 + N_instructions × 2.5 + StackMapFrames
```

Typical Java method: 10-50 bytecode instructions → 25-125 bytes bytecode.

---

## 2. Stack Depth Mathematics

### Stack Effect Function

```
delta(insn) = pushes - pops
```

| Category | Instruction | Delta |
|----------|-------------|-------|
| Constants | iconst_0-5, bipush, ldc | +1 |
| Loads | iload, fload, aload | +1 |
| | lload, dload | +2 |
| Arithmetic | iadd, isub, imul, idiv | -1 |
| Logic | iand, ior, ixor | -1 |
| Stack | dup, dup2 | +1, +2 |
| | pop, pop2 | -1, -2 |
| | swap | 0 |
| Calls | invokevirtual (n args, ret) | -n + ret |
| | invokestatic (n args, ret) | -n + ret |
| | invokeinterface | -(n+1) + ret |
| Object | new, anewarray | +1 |
| Arrays | newarray, iaload | 0, -1 |
| Return | ireturn, areturn | -1 |
| | lreturn, dreturn | -2 |
| | return | 0 |

### Maximum Stack Depth Algorithm

```
depth = 0
max_depth = 0
for insn in bytecode:
    depth += delta(insn)
    max_depth = max(max_depth, depth)
```

For branches/loops: compute for all paths, take maximum.

---

## 2. Instruction Encoding Efficiency

### Bytecode Density

| Encoding | Bytes/inst | Description |
|--------|------------|-------------|
| Single-byte | 1 | `iconst_0-5`, `pop`, `dup` |
| Short | 2-3 | `iload`, `ldc`, `invokestatic` |
| Wide | 4-5 | `invokedynamic`, `tableswitch` |

**Average**: ~2.5 bytes/instruction for typical Java.

### Compression Potential

| Technique | Savings |
|-----------|---------|
| Packed frames (StackMapTable) | 10-20% |
| LEB128 for indices | 10-20% |
| Delta encoding (PC offsets) | 5-10% |
| Shared constant pool | 10-30% |
| **Combined** | **25-50%** |