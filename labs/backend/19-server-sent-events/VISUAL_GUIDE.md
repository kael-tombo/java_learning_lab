# Visual Guide: SSE

`
Time â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¶
Server  [Event1] [Event2] [Event3] [Event4] ...
          â”‚        â”‚        â”‚        â”‚
Client    â—€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€
          EventSource.onmessage()
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\19-server-sent-events "REFACTORING.md") @"
# Refactoring: SSE

Before: Polling with setInterval
After: SSE with EventSource

Before: WebSocket for simple notifications
After: SSE with event types
