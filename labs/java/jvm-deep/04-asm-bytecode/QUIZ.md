# QUIZ — ASM Bytecode Manipulation

## 1. What is the Visitor pattern in ASM?
<details><summary>Answer</summary>Separates traversal (ClassReader) from operations (ClassVisitor/MethodVisitor) — enables composable transformations.
</details>

## 2. What does ClassWriter.COMPUTE_MAXS do?
<details><summary>Answer</summary>Automatically calculates max_stack and max_locals for methods, so you don't have to compute them manually.
</details>

## 2. What does ClassWriter.COMPUTE_FRAMES do?
<details><summary>Answer</summary>Automatically generates StackMapTable attributes (stack map frames) for methods.
</details>

## 3. What's the difference between ClassReader and ClassWriter?
<details><summary>Answer</summary>ClassReader reads/parses .class files; ClassWriter generates/writes .class files. ClassReader accepts a ClassVisitor to traverse the class.
</details>

## 3. What is a MethodVisitor?
<details><summary>Answer</summary>Visitor interface for visiting method bytecode instructions; extends MethodVisitor to modify/inspect instructions.
</details>

## 4. How do you add a method timer with ASM?
<details><summary>Answer</summary>Extend MethodVisitor, override visitCode() to insert System.nanoTime() at start, visitInsn() to insert timing code before RETURN/ARETURN/IRETURN/LRETURN.
</details>

## 4. What is the Visitor pattern in ASM?
<details><summary>Answer</summary>ClassReader traverses class structure, calling visit methods on ClassVisitor/MethodVisitor; subclasses override visit methods to inspect/modify.
</details>

## 5. What's the difference between ClassReader and ClassWriter?
<details><summary>Answer</summary>ClassReader parses .class files and drives Visitors; ClassWriter generates .class bytes from Visitor calls.
</details>

## 5. What does COMPUTE_MAXS do?
<details><summary>Answer</summary>Automatically calculates max_stack and max_locals for each method.
</details>

## 6. What does COMPUTE_FRAMES do?
<details><summary>Answer</summary>Generates StackMapTable attributes (stack map frames) for stack map verification.
</details>

## 6. What is a MethodVisitor?
<details><summary>Answer</summary>Visitor for method bytecode; override visitInsn, visitVarInsn, etc. to inspect/modify instructions.
</details>

## 7. How to inject code before a method return?
<details><summary>Answer</summary>Override visitInsn(), check for RETURN/ARETURN/IRETURN/LRETURN/DRETURN/FRETURN, insert code before super.visitInsn().
</details>

## 7. What is a ClassVisitor?
<details><summary>Answer</summary>Visitor for class-level elements: fields, methods, annotations, inner classes.
</details>

## 8. How to inject a null check before field access?
<details><summary>Answer</summary>In visitVarInsn(ALOAD, var), insert DUP, ACONST_NULL, IF_ACMPNE, then throw NPE if null.
</details>

## 8. What is the purpose of ClassWriter.COMPUTE_MAXS?
<details><summary>Answer</summary>Automatically calculates max_stack and max_locals for each method.
</details>

## 9. How does ASMifier work?
<details><summary>Answer</summary>Reads a .class file and prints Java code that uses ASM API to generate an identical class.
</details>

## 9. What is ASMifier?
<details><summary>Answer</summary>Tool that reads a .class file and generates Java code that uses ASM API to recreate it.
</details>

## 10. How to fix StackMapTable errors?
<details><summary>Answer</summary>Use ClassWriter.COMPUTE_FRAMES flag; ensure bytecode is valid (stack depth consistent).
</details>