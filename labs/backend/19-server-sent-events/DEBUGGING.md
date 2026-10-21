# Debugging: SSE

1. Check Content-Type header is text/event-stream
2. Verify events are flushed (not buffered)
3. Use curl: curl -N http://localhost:8080/stream
4. Check browser's EventSource readyState
5. Monitor connection count on server
