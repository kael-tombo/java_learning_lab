# Code Deep Dive: 19-siem-monitoring

## ThreatDetectionEngine.java

### Purpose
Core correlation engine for processing security events, applying detection rules, and generating alerts in a SIEM system.

### Key Implementation Details

**Event Processing Pipeline**:
1. Receive normalized security events from log shippers
2. Enrich events with context (geo IP, threat intelligence, asset info)
3. Apply correlation rules (threshold, sequence, temporal, trend)
4. Score events for severity and confidence
5. Generate alerts for policy violations

### Class Structure

The ThreatDetectionEngine implements:
- processEvent(SecurityEvent event) - Main event processing
- enrichEvent(SecurityEvent event) - Context enrichment
- pplyCorrelationRules(SecurityEvent event) - Rule matching
- calculateSeverity(SecurityEvent event) - Severity scoring
- generateAlert(CorrelationMatch match) - Alert creation

### Correlation Rule DSL

`json
{
  "rule": {
    "name": "brute_force_detection",
    "type": "threshold",
    "source": ["authentication.log"],
    "condition": "count($.event_type == 'LOGIN_FAILURE') > 5",
    "window": "5m",
    "groupBy": ["$.source_ip", "$.target_user"],
    "severity": "HIGH",
    "actions": ["alert", "block_ip"]
  }
}
`

### Event Enrichment

- GeoIP lookup: Maps IP to country, city, ASN
- Threat intel: Checks IP, domain, hash against known IOCs
- Asset DB: Matches IP/hostname to asset criticality
- User context: Role, department, typical behavior baseline

### Alert Severity Scoring

- Impact: System criticality × data sensitivity
- Urgency: Active exploitation vs reconnaissance
- Confidence: Rule match strength × signal quality
- Overall: weighted average of impact, urgency, confidence

### Log Normalization

- Common schema: ECS (Elastic Common Schema)
- Field mapping: original_field ? ecs.field
- Data type conversion: string ? date, string ? IP
- Enrichable fields: geo, user_agent, os, device

### Common Patterns

The codebase demonstrates several important security patterns:

1. **Defensive Programming**: Validate all inputs, assume nothing
2. **Separation of Concerns**: Security logic separated from business logic
3. **Fail Secure**: Default to denying access on any error
4. **Audit Trail**: Log all security-relevant events
5. **Minimize Attack Surface**: Only expose what is necessary

### Error Handling

Proper security error handling:
`java
try {
    securityOperation();
} catch (SecurityException e) {
    log.warn("Security operation failed: {}", e.getMessage());
    throw new AccessDeniedException("Access denied");
}
`

### Testing Considerations

Key testing scenarios for this code:
1. Valid authentication flow
2. Invalid credentials rejection
3. Expired token handling
4. Missing/invalid signature
5. Authorization boundary testing
6. Race condition testing
7. Error message information leakage
8. Performance under load

### Thread Safety

Thread safety is achieved through:
- Immutable objects where possible
- Thread-local storage for security context
- Concurrent collections for shared state
- Atomic operations for counters
- Reentrant locks for critical sections

### Configuration

Configuration loading follows this order:
1. Command line arguments (highest priority)
2. Environment variables
3. Application properties file
4. Profile-specific overrides
5. Default values (lowest priority)

This ensures flexibility across different environments while maintaining secure defaults.

### Security Hardening

Additional hardening measures applied:
1. Disable unnecessary features
2. Minimum permission service accounts
3. Resource limits on all operations
4. Timeout configuration for all external calls
5. Retry limits with exponential backoff
6. Input size limits
7. Rate limiting per client
8. IP allowlisting for admin functions

### Integration Points

This component integrates with:
- Spring Security filter chain
- Authentication providers
- User details service
- Token repository
- Audit event publisher
- Metrics exporter (Micrometer)
- Health indicators (Actuator)
- External identity providers
