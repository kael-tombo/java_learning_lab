# Math Foundation: 17-blockchain-security

## Mathematics of Blockchain Security

### Cryptographic Primitives

**Elliptic Curve Digital Signature Algorithm (ECDSA)**
- Curve: secp256k1 (Ethereum, Bitcoin)
- Equation: y² = x³ + 7 (mod p)
- Private key: random 256-bit integer
- Public key: K = k × G (scalar multiplication)
- Address: hash of public key (last 20 bytes for Ethereum)

**Keccak-256 (SHA-3)**:
- Output: 256 bits
- Used for: address derivation, transaction hashing
- Block size: 1088 bits (rate) + 512 bits (capacity)

### Reentrancy Attack Economics

Gas cost analysis:
- External call minimum gas: 2300
- State modification gas: varies (5000-50000)
- Profit = stolen_value - attack_cost
- Attack_cost = gas_price × gas_used

### Flash Loan Arithmetic

- Collateral: 0 (uncollateralized)
- Fee: typically 0.09% of loan amount
- Repayment: amount + fee (must succeed within one transaction)
- Minimum profit: fee + slippage + gas costs

### 51% Attack Probability

P(attack) = S(C(n,k) × p^k × (1-p)^(n-k)) for k > n/2

Where:
- n = total blocks in confirmation window
- p = attacker's hash power proportion
- C(n,k) = binomial coefficient

### AMM Price Impact

Constant Product: x × y = k
- x: reserve of token X
- y: reserve of token Y
- k: constant product
- Price impact: ?y = (?x × y) / (x + ?x)
- Slippage = 1 - (output/expected_output)

### MEV (Maximal Extractable Value)

- Sandwich profit = buy_price_delta × amount
- Frontrunning cost = gas_price × (block_gas_limit)
- MEV = S(profitable opportunities) - costs

### Cryptographic Hash Functions

Hash functions are fundamental to security protocols:
- **SHA-256**: 256-bit output, 64-bit blocks, 64 rounds
- **SHA-3**: Sponge construction, arbitrary output length
- **BLAKE2**: Faster alternative to SHA-3 with comparable security

### Random Number Generation

Secure random numbers require:
- Entropy source: OS-provided (SecureRandom in Java)
- Minimum 128 bits for challenge values
- 256 bits recommended for key material
- Never use java.util.Random for security

### Key Derivation Functions

KDFs stretch passwords into cryptographic keys:
- PBKDF2: Iterated HMAC, configurable work factor
- bcrypt: Blowfish-based, adaptive cost
- scrypt: Memory-hard, resists ASIC attacks
- Argon2: Modern, winner of PHC competition

### Timing Attacks Prevention

Constant-time operations prevent side-channel attacks:
- XOR operations instead of branching
- Fixed-time memory access patterns
- MessageDigest.isEqual() for hash comparison
- Avoid short-circuit boolean evaluation

### Encoding Overhead

Base64 encoding increases size by exactly 33%:
- 3 bytes ? 4 characters
- Padding: 0-2 '=' characters
- Used in: SAML assertions, JWT tokens, certificates

### Use Case: This Lab

For this specific lab's mathematical requirements:
- [Specific math topic 1]: Applied in [context]
- [Specific math topic 2]: Applied in [context]
- [Specific math topic 3]: Applied in [context]
- [Specific math topic 4]: Applied in [context]
- [Specific math topic 5]: Applied in [context]

### Further Reading

- Handbook of Applied Cryptography (Menezes, van Oorschot, Vanstone)
- Cryptography Engineering (Ferguson, Schneier, Kohno)
- NIST SP 800-57: Recommendations for Key Management
- NIST SP 800-107: Recommendation for Applications Using Hash Functions
- RFC 8017: PKCS #1 v2.2 RSA Cryptography Standard
