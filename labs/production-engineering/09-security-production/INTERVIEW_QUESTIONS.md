# INTERVIEW QUESTIONS: Production Security & Cryptography
## Lab 09 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: What is Envelope Encryption and why is it preferred over encrypting data directly with a cloud KMS key?
**Answer**:
Direct encryption with KMS requires sending every plaintext payload over the network to the KMS API.
- *Performance & Quota*: Cloud KMS APIs have rate limits (e.g. 10,000 requests/sec) and add 10–30ms network latency per encryption call.
- *Envelope Encryption*: The service requests a single Data Encryption Key (DEK) from KMS. The KMS returns the DEK in plaintext and also encrypted under the master Key Encryption Key (KEK). The service uses the plaintext DEK to locally encrypt gigabytes of data in microseconds using AES-GCM, securely discards the plaintext DEK from memory, and stores the encrypted DEK alongside the ciphertext. Decryption follows the reverse: send the encrypted DEK to KMS to unwrap, then decrypt locally.

### Q2: How does a Java Deserialization vulnerability lead to Remote Code Execution (RCE)?
**Answer**:
When Java deserializes an object graph via `ObjectInputStream.readObject()`, it instantiates classes present on the application's classpath without invoking their standard business methods. Vulnerable classes (gadgets) implement `readObject()`, `hashCode()`, or `equals()` in ways that trigger dynamic method invocation, reflection, or classloading (e.g. InvokerTransformer in Commons Collections). An attacker chains these gadget classes together so that the act of deserialization automatically executes arbitrary OS commands or downloads external bytecode.

---

## Staff / Principal Level (8+ Years)

### Q3: Design a zero-trust secret rotation architecture for database passwords in a 200-pod Java microservices deployment without dropping active queries.
**Answer**:
1. **Dynamic Secret Engine (HashiCorp Vault)**: Vault maintains administrative access to PostgreSQL and dynamically generates two alternating role users (`app_user_A`, `app_user_B`).
2. **Dual-User Rotation Protocol**:
   - Vault creates `app_user_B` with identical permissions and a 4-hour lease, pushing credentials to Kubernetes Secret or Spring Cloud Vault.
   - The Java microservice's DataSource manager receives an event via Spring Cloud Bus or a background rotation thread.
   - The application creates a *new* HikariCP connection pool initialized with `app_user_B`.
   - New incoming web requests switch to the new pool.
   - The old connection pool (`app_user_A`) enters graceful draining: it completes all active in-flight transactions and closes idle connections over a 60-second grace period.
   - Once the old pool reaches 0 connections, it is destroyed.
   - Vault deletes `app_user_A` at the end of the lease.
3. This achieves 100% zero downtime, zero dropped transactions, and guarantees no database credential lives longer than 4 hours.
