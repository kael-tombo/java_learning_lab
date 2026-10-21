# Security: Server-Sent Events

- Authenticate SSE connections (don't expose to unauthenticated users)
- Validate origin headers to prevent cross-origin abuse
- Rate limit SSE connections per client
- Set connection limits to prevent resource exhaustion
- Consider token-based auth for SSE endpoints
- Use HTTPS to prevent event interception
