package com.learning.blockchain;

import java.nio.charset.StandardCharsets;
import java.security.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

public class Lab {

    static class Block {
        final int index;
        final long timestamp;
        final List<Transaction> transactions;
        final String previousHash;
        String hash;
        final int nonce;

        Block(int index, List<Transaction> transactions, String previousHash, int nonce) {
            this.index = index;
            this.timestamp = Instant.now().toEpochMilli();
            this.transactions = transactions;
            this.previousHash = previousHash;
            this.nonce = nonce;
            this.hash = calculateHash();
        }

        String calculateHash() {
            return sha256("" + index + timestamp + transactions + previousHash + nonce);
        }

        static String sha256(String input) {
            try {
                var digest = MessageDigest.getInstance("SHA-256");
                var bytes = digest.digest(input.getBytes(StandardCharsets.UTF_8));
                var sb = new StringBuilder();
                for (var b : bytes) sb.append(String.format("%02x", b));
                return sb.toString();
            } catch (NoSuchAlgorithmException e) {
                throw new RuntimeException(e);
            }
        }
    }

    record Transaction(String from, String to, double amount, long timestamp) {}

    static class Blockchain {
        private final List<Block> chain = new ArrayList<>();
        private final int difficulty;
        private final AtomicInteger nonce = new AtomicInteger(0);

        Blockchain(int difficulty) {
            this.difficulty = difficulty;
            chain.add(createGenesisBlock());
        }

        private Block createGenesisBlock() {
            return new Block(0, List.of(new Transaction("genesis", "genesis", 0, System.currentTimeMillis())), "0", 0);
        }

        Block addBlock(List<Transaction> transactions) {
            var previous = chain.get(chain.size() - 1);
            var block = new Block(chain.size(), transactions, previous.hash, nonce.incrementAndGet());
            chain.add(block);
            return block;
        }

        boolean isValid() {
            for (int i = 1; i < chain.size(); i++) {
                var current = chain.get(i);
                var previous = chain.get(i - 1);
                if (!current.hash.equals(current.calculateHash())) return false;
                if (!current.previousHash.equals(previous.hash)) return false;
            }
            return true;
        }

        void tamper(int index, String newData) {
            if (index > 0 && index < chain.size()) {
                var block = new Block(
                    chain.get(index).index,
                    chain.get(index).transactions,
                    chain.get(index).previousHash,
                    chain.get(index).nonce
                );
                chain.set(index, block);
            }
        }

        int size() { return chain.size(); }
    }

    static class SimpleWallet {
        private final KeyPair keyPair;

        SimpleWallet() throws Exception {
            var kg = KeyPairGenerator.getInstance("RSA");
            kg.initialize(2048);
            keyPair = kg.generateKeyPair();
        }

        byte[] sign(String data) throws Exception {
            var sig = Signature.getInstance("SHA256withRSA");
            sig.initSign(keyPair.getPrivate());
            sig.update(data.getBytes());
            return sig.sign();
        }

        boolean verify(String data, byte[] signature, PublicKey publicKey) throws Exception {
            var sig = Signature.getInstance("SHA256withRSA");
            sig.initVerify(publicKey);
            sig.update(data.getBytes());
            return sig.verify(signature);
        }

        PublicKey getPublicKey() { return keyPair.getPublic(); }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("=== Blockchain Lab ===\n");

        blockStructure();
        blockchainChain();
        proofOfWork();
        transactionsAndWallet();
        smartContracts();
    }

    static void blockStructure() {
        System.out.println("--- Block Structure ---");
        var block = new Block(1, List.of(
            new Transaction("Alice", "Bob", 10.0, System.currentTimeMillis())
        ), "0000abc123", 42);

        System.out.println("  Block:");
        System.out.println("    Index: " + block.index);
        System.out.println("    Timestamp: " + block.timestamp);
        System.out.println("    Transactions: " + block.transactions.size());
        System.out.println("    Previous Hash: " + block.previousHash.substring(0, Math.min(16, block.previousHash.length())) + "...");
        System.out.println("    Hash: " + block.hash.substring(0, Math.min(16, block.hash.length())) + "...");
        System.out.println("    Nonce: " + block.nonce);
    }

    static void blockchainChain() {
        System.out.println("\n--- Blockchain ---");
        var chain = new Blockchain(2);

        chain.addBlock(List.of(new Transaction("Alice", "Bob", 50.0, System.currentTimeMillis())));
        chain.addBlock(List.of(new Transaction("Bob", "Carol", 25.0, System.currentTimeMillis())));

        System.out.println("  Chain valid: " + chain.isValid());
        System.out.println("  Blocks: " + chain.size());
        for (var block : chain.chain) {
            System.out.printf("    Block %d: %s... -> %s...%n",
                block.index, block.previousHash.substring(0, Math.min(8, block.previousHash.length())), block.hash.substring(0, Math.min(8, block.hash.length())));
        }

        chain.tamper(1, "hacked");
        System.out.println("  After tamper, chain valid: " + chain.isValid());
    }

    static void proofOfWork() {
        System.out.println("\n--- Proof of Work ---");
        var target = "0000";
        var nonce = new AtomicInteger(0);

        long start = System.nanoTime();
        String hash;
        do {
            var block = new Block(1, List.of(), "prev", nonce.incrementAndGet());
            hash = block.hash;
        } while (!hash.startsWith(target));
        long elapsed = System.nanoTime() - start;

        System.out.println("  Difficulty: " + target.length() + " leading zeros");
        System.out.println("  Nonce found: " + nonce.get());
        System.out.println("  Hash: " + hash);
        System.out.printf("  Time: %d ms%n", elapsed / 1_000_000);
        System.out.println("  Avg hashes/sec: ~" + (nonce.get() * 1_000_000_000L / elapsed));

        System.out.println("""
  Consensus mechanisms:
  PoW: compute-intensive (Bitcoin, Ethereum)
  PoS: stake-based (Ethereum 2.0, Cardano)
  DPoS: delegated voting (EOS, Tron)
  PBFT: Byzantine fault tolerance (Hyperledger)
    """);
    }

    static void transactionsAndWallet() throws Exception {
        System.out.println("\n--- Transactions & Digital Signatures ---");
        var alice = new SimpleWallet();
        var bob = new SimpleWallet();

        var txData = "Alice pays Bob 10 BTC";
        var signature = alice.sign(txData);

        boolean valid = alice.verify(txData, signature, alice.getPublicKey());
        boolean tampered = alice.verify(txData + "x", signature, alice.getPublicKey());
        boolean wrongKey = alice.verify(txData, signature, bob.getPublicKey());

        System.out.println("  Original signature valid: " + valid);
        System.out.println("  Tampered data valid:      " + tampered);
        System.out.println("  Wrong public key valid:   " + wrongKey);

        System.out.println("""
  UTXO model: each transaction consumes previous outputs, creates new outputs
  Account model: balance stored in account state (Ethereum)
  Merkle tree: efficient verification of transaction inclusion
    """);
    }

    static void smartContracts() {
        System.out.println("\n--- Smart Contracts ---");
        System.out.println("""
  Smart contract = code executed on blockchain (deterministic)

  Solidity (Ethereum):
    contract SimpleStorage {
        uint256 storedData;
        function set(uint256 x) public { storedData = x; }
        function get() public view returns (uint256) { return storedData; }
    }

  Hyperledger Fabric Chaincode (Go/Java):
    public class SimpleChaincode implements Chaincode {
        public Response invoke(ChaincodeStub stub) {
            String key = stub.getStringState("key");
            stub.putStringState("key", "value");
            return new Response(200, "OK", null);
        }
    }

  Gas: computational cost of contract execution
  Oracle: bridge real-world data to blockchain (Chainlink)
  DeFi: decentralized finance (Uniswap, Aave)
    """);
    }
}
