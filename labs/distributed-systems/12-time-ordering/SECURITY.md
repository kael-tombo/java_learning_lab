# Security — Time Ordering

## 1. Attack Vectors
- **NTP Spoofing**: Fake NTP responses skew clocks
- **Clock Drift Injection**: Extreme logical clock values
- **Rollback Attacks**: Force clock to previous value

## 2. Implications
- Causality violations hide or fabricate relationships
- Conflict resolution bypass in CRDT systems
- Replay attacks with rolled-back clocks

## 3. Defenses
- NTP authentication (symmetric keys or AutoKey)
- Enforce clock monotonicity at application level
- Sign clock values with HMAC
- Validate received timestamps within bounds
- Epoch tracking for restarted processes
- Rate limiting on clock value increases

## 4. Security Checklist
- [ ] All clock values authenticated
- [ ] NTP sources authenticated
- [ ] Clock drift monitoring enabled
- [ ] Message timestamps validated
- [ ] Rollback detection implemented
- [ ] Recovery procedures documented
- [ ] Epoch tracking for restarts
