# THEORY — ASM Bytecode Manipulation

## Overview

ASM is a lightweight, high-performance Java bytecode manipulation framework. It uses the **Visitor pattern** to traverse and transform class files.

---

## 1. Core Architecture

### Visitor Pattern

ASM uses the Visitor pattern to separate structure traversal from operations:

```java
ClassReader cr = new ClassReader("MyClass");
ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS);

// Visitor chain: ClassReader → ClassVisitor → MethodVisitor → ...
ClassVisitor cv = new ClassVisitor(Opcodes.ASM9, cw) {
    @Override
    public MethodVisitor visitMethod(int access, String name, 
                                     String desc, String sig, String[] exc) {
        MethodVisitor mv = cv.visitMethod(access, name, desc, sig, exc);
        return new MethodVisitor(Opcodes.ASM9, mv) {
            @Override
            public void visitInsn(int opcode) {
                if (opcode == Opcodes.RETURN) {
                    mv.visitFieldInsn(Opcodes.GETSTATIC, 
                        "java/lang/System", "out", "Ljava/io/PrintStream;");
                    mv.visitLdcInsn("Method exit");
                    mv.visitMethodInsn(Opcodes.INVOKEVIRTUAL,
                        "java/io/PrintStream", "println", "(Ljava/lang/String;)V", false);
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
| `ClassVisitor` | Visit class structure (fields, methods, annotations) |
| `MethodVisitor` | Visit method bytecode instructions |
| `FieldVisitor` | Visit fields |
| `AnnotationVisitor` | Visit annotations |
| `TypeAnnotationVisitor` | Visit type annotations |

---

## 2. ClassReader / ClassWriter

### ClassReader

```java
// Read from file
ClassReader cr = new ClassReader("MyClass");

// From byte array
ClassReader cr = new ClassReader(bytes);

// Skip debug info, frames for speed
ClassReader cr = new ClassReader(bytes);
cr.accept(cv, ClassReader.SKIP_DEBUG | ClassReader.SKIP_FRAMES);
```

### ClassWriter

```java
// COMPUTE_MAXS: auto-calculate max_stack/max_locals
// COMPUTE_FRAMES: auto-generate stack map frames
ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS | ClassWriter.COMPUTE_FRAMES);
```

---

## 3. MethodVisitor — Instruction Manipulation

### Instruction Visiting

```java
public class MyMethodVisitor extends MethodVisitor {
    @Override
    public void visitInsn(int opcode) {
        if (opcode == Opcodes.INVOKEVIRTUAL) {
            // Intercept virtual calls
        }
        super.visitInsn(opcode);
    }
}
```

### Common Opcodes

| Category | Opcodes |
|----------|---------|
| **Constants** | `iconst_m1`, `iconst_0-5`, `bipush`, `sipush`, `ldc` |
| **Load/Store** | `iload`, `istore`, `aload`, `astore`, `lload`, `lastore` |
| **Arithmetic** | `iadd`, `isub`, `imul`, `idiv`, `irem` |
| **Logic** | `iand`, `ior`, `ixor`, `ishl`, `ishr` |
| **Stack** | `dup`, `pop`, `swap`, `dup2` |
| **Control** | `goto`, `ifeq`, `ifne`, `iflt`, `if_icmpeq`, `tableswitch` |
| **Calls** | `invokevirtual`, `invokestatic`, `invokespecial`, `invokeinterface`, `invokedynamic` |
| **Objects** | `new`, `newarray`, `checkcast`, `instanceof` |
| **Fields** | `getfield`, `putfield`, `getstatic`, `putstatic` |
| **Arrays** | `newarray`, `anewarray`, `iaload`, `iastore` |
| **Return** | `return`, `ireturn`, `areturn`, `lreturn`, `dreturn`, `freturn` |

---

## 4. Practical Patterns

### 1. Method Timing Adapter

```java
class TimingAdapter extends MethodVisitor {
    @Override
    public void visitCode() {
        mv.visitMethodInsn(INVOKESTATIC, "java/lang/System", "nanoTime", "()J", false);
        super.visitCode();
    }

    @Override
    public void visitInsn(int opcode) {
        if (opcode >= IRETURN && opcode <= RETURN) {
            mv.visitFieldInsn(GETSTATIC, "java/lang/System", "out", "Ljava/io/PrintStream;");
            mv.visitLdcInsn("Method took: ");
            mv.visitMethodInsn(INVOKESTATIC, "java/lang/System", "nanoTime", "()J", false);
            mv.visitInsn(LSUB);
            mv.visitMethodInsn(INVOKEVIRTUAL, "java/io/PrintStream", "println", "(J)V", false);
        }
        super.visitInsn(opcode);
    }
}
```

### 2. Null Check Injection

```java
public class NullCheckAdapter extends MethodVisitor {
    @Override
    public void visitVarInsn(int opcode, int var) {
        if (opcode == ALOAD) {
            mv.visitInsn(DUP);
            mv.visitInsn(ACONST_NULL);
            mv.visitJumpInsn(IF_ACMPNE, new Label());
            mv.visitTypeInsn(NEW, "java/lang/NullPointerException");
            mv.visitInsn(DUP);
            mv.visitMethodInsn(INVOKESPECIAL, "java/lang/NullPointerException", "<init>", "()V", false);
            mv.visitInsn(ATHROW);
            mv.visitLabel(new Label());
        }
        super.visitVarInsn(opcode, var);
    }
}
```

---

## 5. ClassWriter Flags

| Flag | Purpose |
|------|---------|
| `COMPUTE_MAXS` | Auto-calculate max_stack/max_locals |
| `COMPUTE_FRAMES` | Auto-generate stack map frames |
| `COMPOSITE` | Combine with other flags |

```java
ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS | ClassWriter.COMPUTE_FRAMES);
```

---

## 6. Debugging Tips

```bash
# Verify modified class
java -Xverify:all -cp modified.jar MyClass

# Dump bytecode
javap -c -p -v MyClass

# ASMifier: generate ASM code from existing class
java -cp asm.jar org.objectweb.asm.util.ASMifier MyClass
```

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Stack map frames missing | Use `COMPUTE_FRAMES` |
| max_stack/max_locals wrong | Use `COMPUTE_MAXS` |
| Stack map frames invalid | Ensure `COMPUTE_FRAMES` + valid bytecode |
| Local variable table missing | Use `ClassWriter.COMPUTE_MAXS` |
| Verify error | Run `java -Xverify:all` |