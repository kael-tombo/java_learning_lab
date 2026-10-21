# Architecture: GraalVM Native

`
Traditional JVM:                    Native Image:
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”            â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Java Source         â”‚            â”‚ Java Source         â”‚
â”‚         →“           â”‚            â”‚         →“           â”‚
â”‚   javac (bytecode)  â”‚            â”‚   javac (bytecode)  â”‚
â”‚         →“           â”‚            â”‚         →“           â”‚
â”‚   JIT at Runtime    â”‚            â”‚   AOT at Build Time â”‚
â”‚         →“           â”‚            â”‚         →“           â”‚
â”‚   Machine Code      â”‚            â”‚   Native Executable â”‚
â”‚   + JVM (200MB)     â”‚            â”‚   (~20-50MB)        â”‚
â”‚   + JIT Compiler    â”‚            â”‚   + SubstrateVM     â”‚
â”‚   + GC              â”‚            â”‚   + Minimal GC      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜            â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\25-graalvm-native "SECURITY.md") @"
# Security: GraalVM Native

- Smaller attack surface (less JVM functionality)
- No dynamic class loading (reduces certain attacks)
- But: reflection metadata can leak class structure
- Encrypted values still handled by Spring
- Regular dependency scanning still needed
