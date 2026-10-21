# How It Works: Server-Sent Events

The browser opens an HTTP connection to the SSE endpoint. The server keeps the connection open and writes events as they occur. Each event is formatted as text with optional event type, ID, and data fields. The browser's EventSource API parses this stream and fires JavaScript events. If the connection drops, the browser automatically reconnects and sends the last received event ID via the Last-Event-ID header.
