# THEORY — JVM Bytecode Introduction

## Overview

This lab introduces JVM bytecode fundamentals — the instruction set, execution model, and how Java source maps to bytecode. Understanding bytecode is essential for debugging, performance tuning, and building tools.

---

## 1. JVM Execution Model

### Stack-Based Architecture

The JVM is a **stack machine** — operations push/pop values on an operand stack rather than using registers.

```
iload 1      // Push local variable 1 onto stack
iconst 2     // Push constant 2
iadd         // Pop two, add, push result
istore 3     // Store result in local variable 3
```

### Stack vs Register Machines

| Aspect | Stack Machine (JVM) | Register Machine (x86, ARM) |
|--------|---------------------|----------------------------|
| Instruction size | Compact (1-3 bytes) | Larger (registers in opcode) |
| Portability | High (abstract) | Architecture-specific |
| Execution | Stack manipulation | Register allocation |
| JIT potential | High (easy to optimize) | Complex |

---

## 2. Bytecode Structure

### Class File Format

```
ClassFile {
    u4 magic;              // 0xCAFEBABE
    u2 minor_version;
    u2 major_version;
    u2 constant_pool_count;
    cp_info constant_pool[];
    u2 access_flags;
    u2 this_class;
    u2 super_class;
    u2 interfaces_count;
    u2 interfaces[];
    u2 fields_count;
    field_info fields[];
    u2 methods_count;
    method_info methods[];
    u2 attributes_count;
    attribute_info attributes[];
}
```

### Method Structure

```
method_info {
    u2 access_flags;
    u2 name_index;
    u2 descriptor_index;
    u2 attributes_count;
    attribute_info attributes[];
}
```

### Code Attribute

```java
Code_attribute {
    u2 attribute_name_index;
    u4 attribute_length;
    u2 max_stack;
    u2 max_locals;
    u4 code_length;
    u1 code[code_length];
    u2 exception_table_length;
    exception_table[];
    u2 attributes_count;
    attribute_info attributes[];
}
```

---

## 2. Bytecode Instructions

### Instruction Categories

| Category | Examples | Purpose |
|----------|----------|---------|
| **Load/Store** | `iload`, `istore`, `aload`, `astore` | Move data between stack and locals |
| **Arithmetic** | `iadd`, `isub`, `imul`, `idiv` | Integer math |
| **Stack** | `dup`, `pop`, `swap` | Stack manipulation |
| **Control** | `goto`, `if_icmpge`, `tableswitch` | Branching |
| **Method** | `invokevirtual`, `invokestatic`, `invokedynamic` | Method calls |
| **Object** | `new`, `getfield`, `putfield`, `checkcast` | Object ops |
| **Array** | `newarray`, `iaload`, `iastore` | Array ops |
| **Conversion** | `i2l`, `l2d`, `d2i` | Type conversion |

---

## 3. Method Descriptors

### Descriptor Grammar

```
MethodDescriptor = "(" {ParameterDescriptor} ")" ReturnDescriptor

ParameterDescriptor = BaseType | ObjectType | ArrayType
ReturnDescriptor = ParameterDescriptor | "V" (void)

BaseType: B=byte, C=char, D=double, F=float, I=int, J=long, S=short, Z=boolean
ObjectType: L fully-qualified-class-name ;
ArrayType: [ Descriptor
```

### Examples

| Java Signature | Descriptor |
|----------------|------------|
| `void main(String[])` | `([Ljava/lang/String;)V` |
| `int add(int, int)` | `(II)I` |
| `String concat(String, String)` | `(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;` |
| `List<String> get()` | `()Ljava/util/List;` |

---

## 3. Constant Pool

The constant pool is the "symbol table" of a class file:

| Tag | Type | Description |
|-----|------|-------------|
| 1 | `CONSTANT_Utf8` | UTF-8 string |
| 3 | `CONSTANT_Integer` | 4-byte int |
| 4 | `CONSTANT_Float` | 4-byte float |
| 5 | `CONSTANT_Long` | 8-byte long |
| 6 | `CONSTANT_Double` | 8-byte double |
| 7 | `CONSTANT_Class` | Class reference |
| 8 | `CONSTANT_String` | String literal |
| 9 | `CONSTANT_Fieldref` | Field reference |
| 10 | `CONSTANT_Methodref` | Method reference |
| 11 | `CONSTANT_InterfaceMethodref` | Interface method |
| 11 | `CONSTANT_InvokeDynamic` | invokedynamic bootstrap |

---

## 3. Stack Map Frames (Java 6+)

Stack map frames enable **type verification without interpretation**:

```
StackMapTable {
    u2 number_of_entries;
    stack_map_frame entries[];
}
```

Frame types:
- `same_frame`: Same locals, empty stack
- `same_locals_1_stack_item`: Same locals, 1 stack item
- `full_frame`: Full locals + stack state

Enables **single-pass verification** — critical for startup performance.

---

## 4. Bytecode Verification

### Verification Phases

1. **Format check**: Valid class file structure
2. **Constraint check**: Final fields, finalize, superclass, etc.
3. **Bytecode verification**: Type safety, stack consistency
4. **Symbolic reference resolution**: On first use (lazy)

### Verification Types

| Type | When | Scope |
|------|------|-------|
| **Static** | Class load | Full bytecode scan |
| **Dynamic** | Runtime | Link-time resolution |

---

## 4. Invokedynamic & Method Handles

### invokedynamic (JVMS 5.4.3.5; lambdas landed with JEP 126)

```java
// Java source
Runnable r = () -> System.out.println("hello");

// Compiles to invokedynamic:
// Bootstrap: LambdaMetafactory.metafactory
// Static args: (Ljava/lang/Runnable;)V, ()V
```

### Method Handles

```java
MethodHandles.Lookup lookup = MethodHandles.lookup();
MethodHandle mh = lookup.findStatic(Math.class, "sqrt", 
    MethodType.methodType(double.class, double.class));
double result = (double) mh.invokeExact(4.0); // 2.0
```

---

## 4. ASM Bytecode Manipulation

### ASM Core API

```java
// Read class
ClassReader cr = new ClassReader("MyClass");
ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS);

// Visitor pattern
ClassVisitor cv = new ClassVisitor(Opcodes.ASM9, cw) {
    @Override
    public MethodVisitor visitMethod(int access, String name, 
                                     String desc, String signature, 
                                     String[] exceptions) {
        MethodVisitor mv = cv.visitMethod(access, name, desc, sig, exc);
        return new MethodVisitor(Opcodes.ASM9, mv) {
            @Override
            public void visitInsn(int opcode) {
                if (opcode == Opcodes.RETURN) {
                    mv.visitFieldInsn(Opcodes.GETSTATIC, 
                        "java/lang/System", "out", "Ljava/io/PrintStream;");
                    mv.visitLdcInsn("Method exit");
                    mv.visitMethodInsn(Opcodes.INVOKEVIRTUAL,
                        "java/io/PrintStream", "println", 
                        "(Ljava/lang/String;)V", false);
                }
                mv.visitInsn(opcode);
            }
        };
    }
};
cr.accept(cv, 0);
byte[] modified = cw.toByteArray();
```

### Core Visitors

| Visitor | Purpose |
|---------|---------|
| `ClassVisitor` | Visit class structure |
| `MethodVisitor` | Visit method bytecode |
| `AnnotationVisitor` | Visit annotations |
| `FieldVisitor` | Visit fields |

---

## 5. Bytecode Verification

### Verification Phases

1. **Format check**: Valid class file structure
2. **Constraint check**: Final fields, finalize, superclass
3. **Bytecode verification**: Type safety, stack consistency
4. **Symbolic reference resolution**: Lazy, on first use

### Stack Map Frames

Enable single-pass verification:

```java
// Frame types
same_frame                    // Same locals, empty stack
same_locals_1_stack_item      // Same locals, 1 stack item
same_locals_1_stack_item_extended
same_locals_1_stack_item_extended
append_frame                  // New locals
full_frame                    // Full locals + stack
```

Enables single-pass verification — critical for startup performance.