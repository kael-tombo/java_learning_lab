# EXERCISES — Bytecode Introduction

## 1. Bytecode Reading (Beginner)

**Goal**: Read and understand a simple method's bytecode.

```bash
# Compile
javac Hello.java

# Disassemble
javap -c Hello.class
```

**Tasks**:
1. Identify each instruction in `main` method
2. Map bytecode to Java source lines
3. Explain stack state at each instruction

---

## 2. Bytecode Modification (Intermediate)

**Goal**: Use ASM to add timing to a method.

```java
public class TimingAdapter extends MethodVisitor {
    @Override
    public void visitCode() {
        mv.visitMethodInsn(INVOKESTATIC, "java/lang/System", "nanoTime", "()J", false);
        super.visitCode();
    }
    
    @Override
    public void visitInsn(int opcode) {
        if (opcode == RETURN || opcode == ARETURN || opcode == IRETURN || opcode == LRETURN) {
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

**Tasks**:
1. Apply to a test class
2. Verify timing output
3. Handle void/primitive/object return types

---

## 3. Bytecode Verification (Intermediate)

**Goal**: Understand bytecode verification.

```bash
# Verify class file
java -Xverify:all MyClass

# Verbose verification
java -Xverify:all -verbose:verification MyClass
```

**Tasks**:
1. Create invalid bytecode (e.g., stack underflow)
2. Run verifier, observe error
3. Fix bytecode, verify passes

---

## 4. ASM Bytecode Generation (Advanced)

**Goal**: Generate a class at runtime.

```java
ClassWriter cw = new ClassWriter(0);
cw.visit(V1_8, ACC_PUBLIC, "DynamicClass", null, "java/lang/Object", null);

// Add field
FieldVisitor fv = cw.visitField(ACC_PRIVATE, "value", "I", null, null);
fv.visitEnd();

// Add method
MethodVisitor mv = cw.visitMethod(ACC_PUBLIC, "getValue", "()I", null, null);
mv.visitCode();
mv.visitVarInsn(ALOAD, 0);
mv.visitFieldInsn(GETFIELD, "Generated", "value", "I");
mv.visitInsn(IRETURN);
mv.visitMaxs(1, 1);
mv.visitEnd();

// Load and use
byte[] bytes = cw.toByteArray();
Class<?> clazz = new CustomClassLoader().defineClass("Dynamic", bytes);
Object instance = clazz.getDeclaredConstructor().newInstance();
```

**Challenge**: Generate a class implementing `Runnable` that prints a message.