# Visual Guide: GraalVM Native

`
Build Time (mvn -Pnative native:compile):
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Java Source â”‚â”€â–¶â”‚ AOT Analysis â”‚â”€â–¶â”‚ Native Image     â”‚
â”‚ + Config    â”‚  â”‚ (points-to)  â”‚  â”‚ Executable (25MB)â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Runtime:
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Native Executableâ”‚â”€â–¶ Instant startup (50ms)
â”‚ (No JVM needed)  â”‚â”€â–¶ Lower memory (50MB RSS)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â”€â–¶ Peak throughput (90%)
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\25-graalvm-native "DEBUGGING.md") @"
# Debugging: GraalVM Native

1. Build with -H:+ReportUnsupportedElementsAtRuntime
2. Enable verbose output: --verbose
3. Use native-image-agent to generate metadata
4. Check build.log for errors
5. Test with -Dspring.aot.enabled=true (AOT simulation)
6. Verify reflection config matches runtime usage
7. Use GraalVM Dashboard for optimization insights
