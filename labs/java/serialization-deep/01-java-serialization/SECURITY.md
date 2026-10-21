# Java Serialization -- Security

## Security Considerations

### 1. Deserialization Attacks
Deserialization of untrusted data is one of the most critical security vulnerabilities in Java. Attackers can craft malicious serialized streams that execute arbitrary code via gadget chains, cause denial of service, bypass authentication, or access restricted resources through Java reflection.

### 2. Gadget Chains
A gadget chain is a sequence of classes that when deserialized trigger unintended behavior:
- The chain starts with a commonly available class in the classpath
- Each step invokes a method on the next object in the chain
- The final step executes arbitrary code (RCE)
- Common gadget libraries include Commons Collections, Spring, Groovy, and Fastjson

### 3. Mitigation Strategies

#### ObjectInputFilter
Configure filters to whitelist allowed classes and reject dangerous ones:
- Create a filter pattern that allows only known-safe packages
- Use reject lists for known gadget libraries
- Set depth limits to prevent stack overflow attacks
- Set array size limits to prevent memory exhaustion

#### Serialization Proxy Pattern
The proxy pattern prevents direct deserialization of sensitive classes:
- The main class implements writeReplace to substitute a proxy
- The proxy handles serialization with validation
- readResolve on the proxy reconstructs the validated main class
- Attackers cannot bypass validation by targeting the main class

#### Validating readObject
Always implement readObject with validation logic:
- Check field values for validity after defaultReadObject
- Verify invariants that constructors normally establish
- Reject objects with invalid or suspicious field values
- Throw InvalidObjectException for validation failures

### 4. Best Practices
1. Never deserialize data from untrusted sources
2. Use ObjectInputFilter for all deserialization
3. Prefer alternative formats (JSON, Protobuf) over Java serialization
4. Sign and encrypt serialized data in transit
5. Validate all fields in readObject implementations
6. Mark sensitive fields as transient
7. Implement the Serialization Proxy pattern
8. Keep libraries updated to patch known gadget chains
9. Limit object graph depth and array sizes
10. Monitor deserialization exceptions for attack attempts

### 5. Security Checklist
- [ ] All serializable classes have been reviewed for security
- [ ] ObjectInputFilter configured on all deserialization points
- [ ] Sensitive fields marked as transient
- [ ] readObject implementations validate all input
- [ ] Gadget libraries (Commons Collections, etc.) removed or patched
- [ ] Serialization Proxy pattern used for critical classes
- [ ] Encrypted transport for serialized data
- [ ] Rate limiting on deserialization endpoints
- [ ] Monitoring and alerting for deserialization exceptions
- [ ] Regular security audits of serialization code paths
