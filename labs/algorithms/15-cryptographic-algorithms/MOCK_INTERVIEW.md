# Mock Interview: Cryptographic Algorithms: Hashing, Modular Exponentiation, XOR Secrecy
> Three worked questions on crypto primitives at a conceptual level. Each answer is complete runnable Java; outputs below were observed.

## Q1: Hash a fixed string with SHA-256 from the standard library.
Key insight: A cryptographic hash is deterministic, fixed-size, preimage-resistant, and collision-resistant; even one input bit flips about half the output bits. Using the platform provider (never a hand-rolled hash) is the point of the exercise.
Complexity: Time O(n) in the message length; space O(1) digest state.
```java
import java.security.MessageDigest;
public class L15Q1Sha {
    public static void main(String[] args) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] h = md.digest("abc".getBytes("UTF-8"));
        StringBuilder s = new StringBuilder();
        for (byte b : h) s.append(String.format("%02x", b));
        System.out.println("sha256(abc)=" + s);
    }
}
```
Observed output: `sha256(abc)=ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
Follow-up: What breaks if two different inputs share a digest, and why does 256-bit output make that infeasible to find?

## Q2: Compute modular exponentiation by square-and-multiply.
Key insight: Repeated squaring keeps every intermediate value below m^2 by reducing mod m each step, so huge exponents stay cheap: O(log e) multiplications. This trick is what makes public-key-size exponents computable at all.
Complexity: Time O(log e) modular multiplications; space O(1).
```java
public class L15Q2ModPow {
    static long modpow(long x, long e, long m) {
        long r = 1;
        x %= m;
        while (e > 0) {
            if ((e & 1) == 1) r = (r * x) % m;
            x = (x * x) % m;
            e >>= 1;
        }
        return r;
    }
    public static void main(String[] args) {
        System.out.println("4^13 mod 497=" + modpow(4, 13, 497) + " 2^16 mod 17=" + modpow(2, 16, 17));
    }
}
```
Observed output: `4^13 mod 497=445 2^16 mod 17=1`
Follow-up: Why must x be reduced mod m before the loop, and what overflow guard do you need for 64-bit inputs?

## Q3: Encrypt and decrypt with a fixed XOR keystream (roundtrip demo).
Key insight: XOR with a keystream is its own inverse: ciphertext XOR key = plaintext. This demo only shows the mechanism; real secrecy needs a fresh random key as long as the message (one-time pad) or a proper stream cipher - key reuse leaks plaintext structure.
Complexity: Time O(n); space O(n) for the output.
```java
public class L15Q3Xor {
    public static void main(String[] args) {
        byte[] msg = "HELLO".getBytes();
        byte[] key = {0x1F, 0x2A, 0x33, 0x48, 0x55};
        byte[] enc = new byte[msg.length];
        for (int i = 0; i < msg.length; i++) enc[i] = (byte) (msg[i] ^ key[i]);
        byte[] dec = new byte[msg.length];
        for (int i = 0; i < msg.length; i++) dec[i] = (byte) (enc[i] ^ key[i]);
        System.out.println("roundtrip=" + new String(dec) + " matches=" + new String(dec).equals("HELLO"));
    }
}
```
Observed output: `roundtrip=HELLO matches=true`
Follow-up: Show with two ciphertexts under the same key how XORing them cancels the key and exposes plaintext relations.

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
