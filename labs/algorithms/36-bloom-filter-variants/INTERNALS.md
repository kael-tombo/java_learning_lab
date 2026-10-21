# Internals
4-bit counters packed in byte[]. Cuckoo bucket size c=4 yields ~95% load. Fingerprint f=8 gives 1/256 fp rate. Scalable layers grow O(log n). XOR peeling retries with new seeds if stuck.
