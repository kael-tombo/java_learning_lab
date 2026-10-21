# Security

## Security Considerations

### Input Validation

Always validate input at system boundaries. Check for null, empty, length limits, and format constraints. Reject invalid input immediately.

### Injection Prevention

- Use parameterized queries for database access
- Sanitize output for HTML/XML/JSON
- Validate file paths to prevent path traversal
- Use Pattern.quote() for regex with user input

### Secure Communication

- Use TLS/SSL for network connections
- Validate certificates
- Use secure random for session tokens
- Implement proper authentication and authorization

### Data Protection

- Encrypt data at rest and in transit
- Use char[] instead of String for passwords
- Clear sensitive data from memory after use
- Implement proper access controls

### Denial of Service Protection

- Set timeouts on all external calls
- Limit request sizes
- Implement rate limiting
- Use bounded thread pools

## Security Checklist

- All inputs validated at boundaries
- Parameterized queries for all database access
- Output properly encoded/escaped
- TLS/SSL for all network communication
- Passwords handled with char[] and cleared
- Authentication and authorization checked
- Timeouts configured for all external calls
- Rate limiting implemented where needed
- Sensitive data encrypted at rest
