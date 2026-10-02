# EXERCISES — ASM Bytecode Manipulation

## 1. Class Reader/Writer (Beginner)

**Goal**: Read a class, modify it, write it back.

```bash
# 1. Compile a simple class
javac Hello.java

# 2. Use ASM to read and write
java -cp asm.jar:asm-util.jar:. ReadWriteClass Hello.class HelloModified.class

# 3. Verify
javap -c HelloModified
```

**Tasks**:
1. Write a program that reads a .class file and writes it back
2. Verify the output class works identically
3. Add `COMPUTE_MAXS` and `COMPUTE_FRAMES` flags, verify they work

---

## 2. Method Timer Adapter (Beginner)

**Goal**: Create a MethodVisitor that adds timing to every method.

```java
public class TimingAdapter extends MethodVisitor {
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

**Tasks**:
1. Apply to a class with multiple methods
2. Run the modified class, verify timing output
3. Handle void, primitive, and object return types

---

## 2. Null Check Injection (Intermediate)

**Goal**: Inject null checks before field access.

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

**Tasks**:
1. Apply to a class with field accesses
2. Test with null and non-null values
3. Verify NPE thrown at correct location

---

## 3. ASMifier (Intermediate)

**Goal**: Use ASMifier to generate ASM code from existing class.

```bash
# Generate ASM code for a class
java -cp asm.jar:asm-util.jar org.objectweb.asm.util.ASMifier MyClass
```

**Tasks**:
1. Run ASMifier on a simple class
2. Examine generated code
3. Modify generated code to add a feature
3. Recompile and test

---

## 3. Custom ClassLoader (Advanced)

**Goal**: Create a ClassLoader that loads modified bytecode.

```java
class ASMClassLoader extends ClassLoader {
    private final Map<String, byte[]> modifiedClasses = new HashMap<>();

    public void register(String className, byte[] bytes) {
        modifiedClasses.put(className, bytes);
    }

    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        byte[] bytes = modifiedClasses.get(name);
        if (bytes != null) {
            return defineClass(name, bytes, 0, bytes.length);
        }
        return super.findClass(name);
    }
}
```

**Tasks**:
1. Implement ASMClassLoader
2. Register a modified class
3. Load and execute it