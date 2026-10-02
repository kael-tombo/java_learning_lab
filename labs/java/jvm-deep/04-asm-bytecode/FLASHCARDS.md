# FLASHCARDS — ASM Bytecode Manipulation

| # | Front | Back |
|---|-------|------|
| 1 | Visitor pattern in ASM? | Separates traversal (ClassReader) from operations (ClassVisitor/MethodVisitor) — composable transforms. |
| 2 | ClassWriter.COMPUTE_MAXS? | Auto-calculates max_stack/max_locals. |
| 3 | ClassWriter.COMPUTE_FRAMES? | Auto-generates StackMapTable (stack map frames). |
| 4 | ClassReader vs ClassWriter? | Reader: parses .class → Visitor. Writer: generates .class from Visitor calls. |
| 5 | MethodVisitor? | Visits method bytecode; override visitInsn, visitVarInsn, etc. |
| 6 | Method timing? | visitCode() → nanoTime; visitInsn(RETURN) → nanoTime, print diff. |
| 7 | Null check injection? | visitVarInsn(ALOAD) → DUP, ACONST_NULL, IF_ACMPNE, throw NPE. |
| 8 | ASMifier? | Reads .class, generates ASM API code to recreate it. |
| 9 | ClassReader vs ClassWriter? | Reader: parses .class → visits. Writer: generates .class from visitor calls. |
| 10 | MethodVisitor? | Visits method bytecode; override visitInsn, visitVarInsn, etc. |
| 11 | Timer injection? | visitCode() → nanoTime; visitInsn(RETURN) → nanoTime, print diff. |
| 12 | Null check injection? | visitVarInsn(ALOAD) → DUP, ACONST_NULL, IF_ACMPNE, throw NPE. |
| 13 | ASMifier? | Reads .class, emits ASM API code to recreate it. |
| 14 | ClassReader vs ClassWriter? | Reader: parses → visits. Writer: visit calls → generates .class. |
| 15 | MethodVisitor? | Visits method bytecode; override visitInsn, visitVarInsn, etc. |
| 16 | Timer injection? | visitCode() → nanoTime; visitInsn(RETURN) → nanoTime + print diff. |
| 17 | Null check injection? | visitVarInsn(ALOAD) → DUP, ACONST_NULL, IF_ACMPNE, throw NPE. |
| 18 | ASMifier? | Reads .class, emits ASM API code to recreate it. |
| 19 | ClassReader vs ClassWriter? | Reader: parses → visits. Writer: visits → generates .class. |
| 20 | MethodVisitor? | Visits bytecode; override visitInsn, visitVarInsn, etc. |
| 21 | Timer injection? | visitCode() → nanoTime; visitInsn(RETURN) → nanoTime + print diff. |
| 22 | Null check injection? | visitVarInsn(ALOAD) → DUP, ACONST_NULL, IF_ACMPNE, throw NPE. |
| 23 | ASMifier? | Reads .class, emits ASM API code to recreate it. |
| 24 | COMPUTE_MAXS? | Auto max_stack/max_locals. |
| 25 | COMPUTE_FRAMES? | Auto StackMapTable. |
| 26 | Verify class? | java -Xverify:all. |