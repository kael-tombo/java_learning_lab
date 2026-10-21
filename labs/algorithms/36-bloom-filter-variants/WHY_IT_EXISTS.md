# Why Bloom Filter Variants Exist
The original Bloom filter solved set membership with far less memory. Real-world systems demanded more: deletion support (Counting BF), dynamic scaling (Scalable BF), higher density (Cuckoo/XOR filters), and merging (Quotient filter). Each variant reflects diverse constraints: memory, latency, deletion frequency, and scalability.
